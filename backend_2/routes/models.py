from fastapi import APIRouter, Depends
from auth.oauth2 import get_current_user

router_models = APIRouter(tags=["models"])


# Static catalogs (align with Streamlit and Next.js selectors)
CATALOG_ADMIN = {
    "Groq": [
        "llama-3.1-8b-instant",
        "llama-3.1-70b-versatile",
        "deepseek-r1-distill-llama-70b",
        "qwen3-32b",
        "gpt-oss-20b",
        "gpt-oss-120b",
    ],

    "OpenAI": [
        "gpt-4o",
        "o4-mini-2025-04-16",
        "deepseek-chat-v3-0324:free",
    ],
    "GitHub": [
        "qwen/qwen3-32b",
        "gpt-4o",
        "openai/gpt-oss-120b",
        

    ],
    "Ollama": [
        "llama3.2:1b",
        "llama3.2:latest",
        "deepseek-r1:7b",
    ],
    "stabilityai": [
        "stable-diffusion-xl-base-1.0",
        "stable-image-ultra",
    ],
}

CATALOG_BASIC = {
    "Groq": [
        "llama-3.1-8b-instant",
    ],
    "OpenAI": [
        "o4-mini-2025-04-16",
    ],
    "Ollama": [
        "llama3.2:1b",
    ],
}


@router_models.get("/models")
async def list_models(current_user: dict = Depends(get_current_user)):
    """Return provider/model catalog based on user role.
    Admin gets full catalog; other roles get a reduced set.
    """
    role = current_user.get("role", "Employee").lower()
    providers = CATALOG_ADMIN if role == "admin" else CATALOG_BASIC
    return {"providers": providers}


