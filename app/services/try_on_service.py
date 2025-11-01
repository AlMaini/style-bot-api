from typing import List
from PIL import Image


def try_on_clothes(images: List[Image.Image]):
    return f"recieved {len(images)} images"
