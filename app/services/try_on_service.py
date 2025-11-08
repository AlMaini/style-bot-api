from io import BytesIO
from typing import List

from PIL import Image
from services.clients import get_gemini_client


def generate_try_on_image(person: Image.Image, clothes: List[Image.Image]):
    # assert uid is int and person is Image.Image and clothes is List[Image.Image]

    client = get_gemini_client()
    editing_model = "gemini-2.5-flash-image-preview"

    prompt = "Generate an image of a person trying on clothes. The person is represented by the first image, and the clothes to try on are represented by the subsequent images. Combine them realistically. Do not alter the identity of the person, including the face, body size etc. Do not add any additional clothing items or accessories."
    content = [prompt] + [person] + clothes

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=content,
    )

    image_data = None

    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            image_data = Image.open(BytesIO(part.inline_data.data))

    if image_data is None:
        raise ValueError("No image data received from Gemini API")

    return image_data
