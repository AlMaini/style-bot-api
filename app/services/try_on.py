import asyncio
import uuid
from io import BytesIO
from typing import List

from PIL import Image
from utils.clients import editing_model, get_gemini_client
from utils.status_utils import job_manager


async def generate_try_on_image(
    uid: str, person: Image.Image, clothes: List[Image.Image]
):
    # assert uid is int and person is Image.Image and clothes is List[Image.Image]

    client = get_gemini_client()

    prompt = "Generate an image of a person trying on clothes. The person is represented by the first image, and the clothes to try on are represented by the subsequent images. Combine them realistically. Do not alter the identity of the person, including the face, body size etc. Do not add any additional clothing items or accessories."
    content = [prompt] + [person] + clothes

    response = await asyncio.to_thread(
        client.models.generate_content, model=editing_model, contents=content
    )

    image_data = None

    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            image_data = Image.open(BytesIO(part.inline_data.data))

    if image_data is None:
        raise ValueError("No image data received from Gemini API")

    image_path = f"app/images/{uid}.png"
    image_data.save(image_path)
    job_manager.update_job(uuid.UUID(uid), status="completed", result=image_path)
