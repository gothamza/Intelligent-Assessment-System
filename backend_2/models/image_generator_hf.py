import os
import io
import base64
from huggingface_hub import InferenceClient
from PIL import Image
import uuid


# Initialize the client
# Note: The 'token' parameter is often used instead of 'api_key'.
# Using 'token' is generally recommended.
hf_client = InferenceClient(
    provider="nebius", 
    token=os.getenv("HF_TOKEN")
)

def generate_image_with_hf(prompt: str, chat_id: str, model: str = "stabilityai/stable-diffusion-xl-base-1.0"):
    """
    Generates an image using a Hugging Face Inference Endpoint.
    Returns a base64 encoded image string.
    """
    try:
        # Generate the image, which returns a PIL.Image object
        pil_image = hf_client.text_to_image(prompt, model=model)
        
        # Define a unique path for the image inside a chat-specific directory
        save_dir = os.path.join("data/generated_images", chat_id)
        os.makedirs(save_dir, exist_ok=True)
        image_id = str(uuid.uuid4())
        file_path = os.path.join(save_dir, f"{image_id}.png")
        
        # Save the image to the specified path
        pil_image.save(file_path, "PNG")
        # Return the relative path
        return file_path
    except Exception as e:
        print(f"Error generating image with Hugging Face: {e}")
        return None



import os
import uuid
import shutil
from gradio_client import Client, handle_file

# Initialize the client once to be reused
try:
    gradio_client = Client("black-forest-labs/FLUX.1-Kontext-Dev")
    # gradio_client = Client("kontext-community/kontext-relight")
    gradio_client = Client("black-forest-labs/FLUX.1-Kontext-Dev")

    # # --- TEMPORARY DEBUGGING STEP ---
    # # This will print all available API endpoints to your backend log.
    # print("--- [DEBUG] AVAILABLE GRADIO API ENDPOINTS ---")
    # gradio_client.view_api(print_info=True)
    # print("--------------------------------------------")
    # # ----------- END DEBUGGING STEP -----------

except Exception as e:
    print(f"Failed to initialize Gradio client: {e}")
    gradio_client = None

def generate_image_with_gradio(prompt: str, id_image_path: str, chat_id: str):
    """
    Generates an image using the Gradio PuLID-FLUX model.
    Saves the image to a chat-specific folder and returns its relative path.
    """
    if not gradio_client:
        print("Gradio client not available.")
        return None
        
    # try:
    #     # The predict method returns a temporary file path for the generated image
        
    #     client = Client("black-forest-labs/FLUX.1-dev")
    #     temp_result_path = client.predict(
    #             prompt=prompt,
    #             seed=0,
    #             randomize_seed=True,
    #             width=1024,
    #             height=1024,
    #             guidance_scale=3.5,
    #             num_inference_steps=28,
    #             api_name="/infer"
    #     )
       
    try:
        # The predict method returns a temporary file path for the generated image
        # Update the predict call with the new model's parameters
        result_tuple = gradio_client.predict(
                input_image=handle_file(id_image_path), # Parameter name changed from id_image
                prompt=prompt,
                seed=0,
                randomize_seed=True,
                guidance_scale=2.5,
                steps=28,
                api_name="/infer" # API name changed
        )
        temp_result_path = result_tuple[0]
        temp_result_path = temp_result_path[1]
        # Define a unique path for the image inside the chat-specific directory
        save_dir = os.path.join("data/generated_images", chat_id)

        # Define a unique path for the image inside the chat-specific directory
        # save_dir = os.path.join("data/generated_images", chat_id)
        os.makedirs(save_dir, exist_ok=True)
        image_id = str(uuid.uuid4())
        _, extension = os.path.splitext(temp_result_path)
        file_path = os.path.join(save_dir, f"{image_id}{extension}")

        # Copy the generated file from its temporary location to our data directory
        shutil.copy(temp_result_path, file_path)

        # Clean up the temporary file created by gradio_client
        if os.path.exists(temp_result_path):
            os.remove(temp_result_path)

        return file_path
    except Exception as e:
        print(f"Error generating image with Gradio: {e}")
        return None