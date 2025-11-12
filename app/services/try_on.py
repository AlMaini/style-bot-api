import asyncio
import os
import uuid
from io import BytesIO
from typing import List
from uuid import UUID

from models.status import UpdateJob
from PIL import Image
from utils.clients import editing_model, get_gemini_client
from utils.database import increment_image_usage
from utils.image_utils import open_images, upload_image
from utils.prompts import try_on_prompt
from utils.status_utils import job_manager


async def generate_try_on_image(
    uid: UUID, person: Image.Image, clothes: List[Image.Image]
):
    """Generate a try-on image and update job status."""

    client = get_gemini_client()

    prompt = try_on_prompt
    content = [prompt] + [person] + clothes

    response = await client.aio.models.generate_content(
        model=editing_model, contents=content
    )

    image_data = None

    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            image_data = Image.open(BytesIO(part.inline_data.data))

    if image_data is None:
        raise ValueError("No image data received from Gemini API")

    image_path = f"app/images/{uid}.png"
    image_data.save(image_path)
    return image_path


async def process_try_on_single_outfit(
    user_id: uuid.UUID, job_id: uuid.UUID, person_path: str, clothing_paths: List[str]
):
    loop = asyncio.get_running_loop()
    all_paths = [person_path] + list(clothing_paths)

    try:
        # Open images in executor (Pillow work off the event loop)
        images = await loop.run_in_executor(None, open_images, all_paths)
        person_img = images[0]
        clothing_imgs = images[1:]

        image_path = await generate_try_on_image(str(job_id), person_img, clothing_imgs)
        job_manager.update_job(
            UpdateJob(job_id=job_id, status="completed", result=image_path)
        )
        await upload_image(str(user_id), Image.open(image_path))
    finally:
        _ = await increment_image_usage(user_id)
        # Try to remove temporary files; swallow errors
        for p in all_paths:
            try:
                os.remove(p)
            except Exception:
                pass
