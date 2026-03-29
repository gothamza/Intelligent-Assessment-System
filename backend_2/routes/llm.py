
from models.models import *
router_llm= APIRouter(tags=["🤖LLM "])


@router_llm.post("/llm", response_model=LLMResponse)
async def llm_endpoint(request: LLMRequest, current_user: dict = Depends(get_current_user)):
    """
    Simple endpoint to get a response from the LLM (no RAG, just LLM completion).
    """
    try:
        result = ollama_llm.invoke(request.prompt)
        return LLMResponse(response=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")
    
    
# @router_llm.post("/llm", response_model=LLMResponse)
# async def llm_endpoint(request: LLMRequest, current_user: dict = Depends(get_current_user)):
#     """
#     Simple endpoint to get a response from the LLM (no RAG, just LLM completion).
#     """
#     try:
#         # Wrap the prompt in a HumanMessage for ChatOllama
#         result = llm.invoke([
#             HumanMessage(content=request.prompt)
#         ])
#         # The result is an AIMessage, so we access its content
#         return LLMResponse(response=result.content)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"LLM error: {e}")


@router_llm.post("/llm-langchain-groq", response_model=LLMResponse)
async def llm_langchain_groq(request: LLMRequest, current_user: dict = Depends(get_current_user)):
    """
    Simple endpoint to get a response from the LLM (no RAG, just LLM completion).
    """
    try:
        result = llm_groq.invoke(request.prompt)
        return LLMResponse(response=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")