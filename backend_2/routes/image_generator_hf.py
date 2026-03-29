from models.image_generator_hf import generate_image_with_hf,generate_image_with_gradio
from pydantic import BaseModel
from models.langgraph_models import *

PUBLIC_BACKEND_URL = os.getenv("PUBLIC_BACKEND_URL")

router_image_generator_hf= APIRouter(tags=["🖼️ Image Generation with Hugging Face"])
class ImageRequest(BaseModel):
    prompt: str
    chat_id: str
    model: Optional[str] = "stabilityai/stable-diffusion-xl-base-1.0"

@router_image_generator_hf.post("/generate-hf-image")
async def http_generate_hf_image(request: ImageRequest, current_user: dict = Depends(get_current_user)):
    """
    Endpoint to generate an image using a Hugging Face model.
    """
    if not request.prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    relative_path = generate_image_with_hf(request.prompt, request.chat_id, request.model)

    if not relative_path:
        raise HTTPException(status_code=500, detail="Failed to generate image.")

    # The relative path might look like 'data/generated_images/some-uuid.png'
    # We need to remove the 'data/' part for the URL
    url_path = relative_path.replace("data/", "")
    
    # Construct the full URL for the frontend
    full_image_url = f"{PUBLIC_BACKEND_URL}/{url_path}"
    content_string = f"{request.prompt}\n\nimage : {full_image_url}"
    return {"image_url": content_string}

import tempfile
import shutil

@router_image_generator_hf.post("/generate-gradio-image")
async def http_generate_gradio_image(
    prompt: str = Form(...),
    chat_id: str = Form(...),
    id_image: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Endpoint to generate an image using the Gradio PuLID-FLUX model.
    """
    # Save the uploaded ID image to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(id_image.filename)[1]) as tmp:
        shutil.copyfileobj(id_image.file, tmp)
        temp_id_image_path = tmp.name

    try:
        relative_path = generate_image_with_gradio(prompt, temp_id_image_path, chat_id)
    finally:
        # Ensure the temporary uploaded file is deleted
        os.remove(temp_id_image_path)

    if not relative_path:
        raise HTTPException(status_code=500, detail="Failed to generate image with Gradio model.")

    # Construct the full, publicly accessible URL for the frontend
    url_path = relative_path.replace("data/", "")
    full_image_url = f"{PUBLIC_BACKEND_URL}/{url_path}"

    return {"image_url": full_image_url}