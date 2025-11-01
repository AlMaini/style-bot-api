from typing import List
from PIL import Image


def generate_try_on_image(uid: int, images: List[Image.Image]):
    return f"recieved {len(images)} images for user {uid}"
