import os
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()

class LLMProviderManager:
    """Manages multiple LLM providers with automatic switching on failures."""
    
    def __init__(self, custom_api_keys=None):
        self.custom_api_keys = custom_api_keys or {}
        self.current_provider_index = -1
        self.reload_env()
        
        # Define available providers
        self.providers = [
            {
                "name": "Groq (Llama3 70B)",
                "base_url": "https://api.groq.com/openai/v1",
                "model": "openai/gpt-oss-120b",
                "api_key_env": "GROQ_API_KEY",
                "api_key_custom": "groq"
            },
            {
                "name": "Groq (Llama3 70B)",
                "base_url": "https://api.groq.com/openai/v1",
                "model": "openai/gpt-oss-120b",
                "api_key_env": "GROQ_API_KEY2",
                "api_key_custom": "groq"
            },
            {
                "name": "Groq (Llama3 8B)",
                "base_url": "https://api.groq.com/openai/v1", 
                "model": "openai/gpt-oss-120b",
                "api_key_env": "GROQ_API_KEY3",
                "api_key_custom": "groq"
            },
            {
                "name": "OpenRouter (DeepSeek)",
                "base_url": "https://openrouter.ai/api/v1",
                "model": "deepseek/deepseek-chat-v3-0324:free",
                "api_key_env": "OPENROUTER_API_KEY",
                "api_key_custom": "openrouter"
            },
            {
                "name": "OpenRouter (DeepSeek2)",
                "base_url": "https://openrouter.ai/api/v1",
                "model": "deepseek/deepseek-chat-v3-0324:free",
                "api_key_env": "OPENROUTER_API_KEY2",
                "api_key_custom": "openrouter"
            },
            {
                "name": "OpenRouter (DeepSeek3)",
                "base_url": "https://openrouter.ai/api/v1",
                "model": "deepseek/deepseek-chat-v3-0324:free",
                "api_key_env": "OPENROUTER_API_KEY3",
                "api_key_custom": "openrouter"
            },
            {
                "name": "OpenRouter (DeepSeek4)",
                "base_url": "https://openrouter.ai/api/v1",
                "model": "deepseek/deepseek-chat-v3-0324:free",
                "api_key_env": "OPENROUTER_API_KEY4",
                "api_key_custom": "openrouter"
            },
            {
                "name": "OpenAI (GPT-4)",
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-4",
                "api_key_env": "OPENAI_API_KEY", 
                "api_key_custom": "openai"
            }
        ]
        
        self.llm = None
        self.switch_llm()
    
    def reload_env(self):
        """Reload environment variables from .env file."""
        load_dotenv(override=True)
    
    def get_api_key(self, provider):
        """Get API key from custom input or environment."""
        if self.custom_api_keys.get(provider["api_key_custom"]):
            key = self.custom_api_keys[provider["api_key_custom"]]
            if key and key.strip() and key != "YOUR_API_KEY_HERE":
                return key
        
        key = os.getenv(provider["api_key_env"])
        if key and key.strip() and key != "YOUR_API_KEY_HERE":
            return key
        return None
    
    def switch_llm(self):
        """Switch to the next available LLM provider."""
        # Find next available provider
        attempts = 0
        failed_providers = set()
        
        while attempts < len(self.providers):
            self.current_provider_index = (self.current_provider_index + 1) % len(self.providers)
            provider = self.providers[self.current_provider_index]
            
            # Skip if we already know this provider failed
            if provider['name'] in failed_providers:
                attempts += 1
                continue
            
            api_key = self.get_api_key(provider)
            if api_key:
                try:
                    self.llm = ChatOpenAI(
                        base_url=provider["base_url"],
                        model=provider["model"],
                        openai_api_key=api_key,
                        temperature=0.3,
                        max_tokens=500
                    )
                    print(f"✅ Switched to: {provider['name']}")
                    return True
                except Exception as e:
                    print(f"❌ Failed to initialize {provider['name']}: {e}")
                    failed_providers.add(provider['name'])
                    attempts += 1
            else:
                print(f"⚠️ No API key for {provider['name']}")
                failed_providers.add(provider['name'])
                attempts += 1
        
        raise Exception("No working LLM providers available")
    
    def create_llm_with_params(self, temperature=0.3, max_tokens=500):
        """Create LLM instance with custom parameters."""
        if self.llm:
            # Update current LLM with new parameters
            provider = self.providers[self.current_provider_index]
            api_key = self.get_api_key(provider)
            
            return ChatOpenAI(
                base_url=provider["base_url"],
                model=provider["model"],
                openai_api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens
            )
        return None
    
    def invoke_with_retry(self, chain, params, max_retries=None):
        """Invoke chain with automatic provider switching on failure."""
        if max_retries is None:
            max_retries = len(self.providers)
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                return chain.invoke(params)
            except Exception as e:
                last_error = e
                error_msg = str(e)
                
                # Check if it's a rate limit or API error
                if "429" in error_msg or "rate_limit" in error_msg.lower() or "quota" in error_msg.lower():
                    print(f"🔄 Rate limit hit with {self.providers[self.current_provider_index]['name']}, switching...")
                    time.sleep(2)  # Simple backoff
                else:
                    print(f"❌ Error with {self.providers[self.current_provider_index]['name']}: {error_msg}")
                
                # Switch to next provider
                if attempt < max_retries - 1:
                    try:
                        self.switch_llm()
                        # Recreate chain with new LLM
                        chain = self.recreate_chain_with_current_llm(chain)
                    except Exception as switch_error:
                        print(f"❌ Failed to switch provider: {switch_error}")
                        break
        
        raise last_error
    
    def recreate_chain_with_current_llm(self, original_chain):
        """Recreate the chain with the current LLM instance."""
        # For now, we'll recreate the chain using the current LLM
        # This is a simplified approach - in practice, you'd need to extract
        # the prompt template and recreate the chain
        if hasattr(original_chain, 'steps') and len(original_chain.steps) >= 2:
            # Extract prompt and parser from the chain
            prompt = original_chain.steps[0]
            parser = original_chain.steps[2] if len(original_chain.steps) > 2 else StrOutputParser()
            return prompt | self.llm | parser
        return original_chain

def create_enhanced_llm_manager(custom_api_keys=None):
    """Create an enhanced LLM manager with provider switching."""
    return LLMProviderManager(custom_api_keys)

def create_feedback_chain_enhanced(llm_manager, temperature=0.3, max_tokens=500):
    """Create feedback chain with enhanced LLM manager."""
    feedback_template = """
Tu es un professeur de mathématiques bienveillant, patient et encourageant.
Ton objectif est de fournir un feedback constructif à un élève qui a fait une erreur.
Ne donne PAS la réponse directe. Guide l'élève pour qu'il trouve la solution par lui-même.

**Question :**
{question}

**Réponse de l'élève :**
{reponse_eleve}

**Instructions pour le feedback :**
1. Commence par une phrase positive et encourageante.
2. Identifie l'erreur principale de l'élève de manière simple et claire.
3. Pose une question ou donne un indice pour l'aider à corriger son erreur.
4. Ton feedback doit être court, en 2 ou 3 phrases maximum.

**Feedback Pédagogique :**
"""
    
    feedback_prompt = PromptTemplate(
        input_variables=["question", "reponse_eleve"],
        template=feedback_template
    )
    
    llm = llm_manager.create_llm_with_params(temperature, max_tokens)
    return feedback_prompt | llm | StrOutputParser()

def create_global_summary_chain_enhanced(llm_manager, temperature=0.3, max_tokens=500):
    """Create global summary chain with enhanced LLM manager."""
    global_feedback_template = """
Tu es un tuteur expert qui analyse une série de feedbacks pour créer un plan d'action personnalisé.

Voici la liste des feedbacks :
---
{individual_feedbacks}
---

**Ta mission :**
1. Identifie 1 ou 2 concepts clés avec lesquels l'élève a des difficultés.
2. Pour chaque concept, propose une mini-leçon, un exercice d'application, et sa solution détaillée.
3. Termine avec un message d'encouragement.
4. Structure ta réponse en Markdown.

**Plan d'Action Personnalisé :**
"""
    
    global_feedback_prompt = PromptTemplate(
        input_variables=["individual_feedbacks"],
        template=global_feedback_template
    )
    
    llm = llm_manager.create_llm_with_params(temperature, max_tokens)
    return global_feedback_prompt | llm | StrOutputParser()
