import os
from itertools import cycle
import requests
from fastapi import HTTPException
# filepath: backend/groq_manager.py
class GroqKeyManager:
    def __init__(self):
        # Try to get GROQ_API_KEYS first (comma-separated list)
        keys_str = os.getenv("GROQ_API_KEYS")
        if keys_str:
            self.keys = [k.strip() for k in keys_str.split(",") if k.strip()]
        else:
            # Fallback to individual keys (GROQ_API_KEY, GROQ_API_KEY2, GROQ_API_KEY3)
            self.keys = []
            for key_name in ["GROQ_API_KEY", "GROQ_API_KEY2", "GROQ_API_KEY3"]:
                key = os.getenv(key_name)
                if key and key.strip():
                    self.keys.append(key.strip())
        
        if not self.keys:
            raise RuntimeError("No GROQ_API_KEYS or individual GROQ_API_KEY variables provided in environment variables.")
        
        self.key_cycle = cycle(self.keys)
        self.current_key = next(self.key_cycle)
    def get_key(self):
        return self.current_key

    def rotate_key(self):
        self.current_key = next(self.key_cycle)
        return self.current_key

groq_key_manager = GroqKeyManager()

import httpx

async def call_groq_api(prompt):
    for _ in range(len(groq_key_manager.keys)):
        api_key = groq_key_manager.get_key()
        headers = {"Authorization": f"Bearer {api_key}"}
        data = {"prompt": prompt}
        async with httpx.AsyncClient() as client:
            response = await client.post("https://api.groq.com/v1/llm", json=data, headers=headers)
        if response.status_code == 200:
            return response.json()["response"]
        elif response.status_code == 429:
            groq_key_manager.rotate_key()
        else:
            raise HTTPException(status_code=500, detail=f"GroqAPI error: {response.text}")
    raise HTTPException(status_code=500, detail="All GroqAPI keys exhausted.")


from langchain_groq import ChatGroq

groq_api_key = os.getenv('GROQ_API_KEY')
# llm=ChatGroq(groq_api_key=groq_api_key,model_name="llama3-70b-8192")
llm_groq = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.1-8b-instant")

llm_groq2 = ChatGroq(
    groq_api_key=groq_api_key,
    model="llama-3.1-8b-instant",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)



async def call_groq_chat(messages, model="mixtral-8x7b-32768"):
    url = "https://api.groq.com/openai/v1/chat/completions"
    for _ in range(len(groq_key_manager.keys)):
        api_key = groq_key_manager.get_key()
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {
            "model": model,
            "messages": messages
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=60)
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        elif response.status_code == 429:
            groq_key_manager.rotate_key()
        else:
            raise HTTPException(status_code=500, detail=f"GroqAPI error: {response.text}")
    raise HTTPException(status_code=500, detail="All GroqAPI keys exhausted.")

from langchain_groq import ChatGroq

def get_rotating_llm_groq(model_name="llama-3.1-8b-instant", temperature=0):
    """
    Returns a ChatGroq instance with the current API key.
    """
    api_key = groq_key_manager.get_key()
    return ChatGroq(groq_api_key=api_key, model_name=model_name, temperature=temperature)

def invoke_groq_with_rotation(messages, model_name="llama-3.1-8b-instant", temperature=0):
    """
    Try all Groq API keys in rotation until one succeeds or all fail.
    """
    last_exception = None
    for _ in range(len(groq_key_manager.keys)):
        llm = get_rotating_llm_groq(model_name=model_name, temperature=temperature)
        try:
            return llm.invoke(messages)
        except Exception as e:
            last_exception = e
            groq_key_manager.rotate_key()
    raise HTTPException(status_code=500, detail=f"All Groq API keys exhausted. Last error: {last_exception}")