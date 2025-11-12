import asyncio
import os
import shutil
import tempfile
import uuid
from io import BytesIO
from typing import List

from fastapi import UploadFile
from PIL import Image
from utils.clients import get_supabase_client

upload_dir = "app/images/"

image_supabase_client = get_supabase_client()


async def async_save_uploadfile_to_disk(upload_file: UploadFile) -> str:
    """
    Create a temp file path and copy the UploadFile content to it using a threadpool.
    Returns the temp file path.
    """
    tmp = tempfile.NamedTemporaryFile(
        delete=False, suffix=".png", prefix="process_image", dir=upload_dir
    )
    tmp_path = tmp.name
    tmp.close()

    def _save_uploadfile_to_disk(upload_file: UploadFile, dest_path: str):
        """
        Synchronous function to copy upload_file.file to dest_path.
        Runs in threadpool to avoid blocking event loop.
        """
        # Ensure we're at start
        try:
            upload_file.file.seek(0)
        except Exception:
            raise ValueError("UploadFile file is not seekable")
        with open(dest_path, "wb") as dest:
            shutil.copyfileobj(upload_file.file, dest)

    loop = asyncio.get_running_loop()
    # Copy in executor to avoid blocking
    await loop.run_in_executor(None, _save_uploadfile_to_disk, upload_file, tmp_path)
    return tmp_path


def open_images(paths: List[str]) -> List[Image.Image]:
    """
    Open and convert images synchronously (to be run in executor).
    """
    imgs = []
    for p in paths:
        img = Image.open(p)
        imgs.append(img.convert("RGB"))
    return imgs


def adjust_aspect_ratio(
    img: Image.Image, target_width: int = -1, target_height: int = -1
) -> Image.Image:
    """
    Pad any PIL Image to match a target aspect ratio by adding white padding

    Args:
        img: PIL Image object
        target_width: Target width for the output image (optional)
        target_height: Target height for the output image (optional)

    If both target_width and target_height are provided, the image will be padded to that exact size.
    If only one is provided, the other dimension will be calculated to maintain the target aspect ratio.
    If neither is provided, defaults to square based on the larger dimension.

    Returns:
        PIL Image object that matches the target aspect ratio
    """
    try:
        width, height = img.size

        print(f"Processing image (original size: {width}x{height})")

        # Determine target dimensions
        if target_width == -1 and target_height == -1:
            # Default behavior: make it square based on larger dimension
            target_width = target_height = max(width, height)
        elif target_width == -1:
            # Calculate width based on target height and original aspect ratio
            aspect_ratio = width / height
            target_width = int(target_height * aspect_ratio)
        elif target_height == -1:
            # Calculate height based on target width and original aspect ratio
            aspect_ratio = height / width
            target_height = int(target_width * aspect_ratio)

        # If the image is already the target size, return it as is
        if width == target_width and height == target_height:
            print(f"Image already matches target size: {target_width}x{target_height}")
            return img

        # Create a new white image with the target size
        padded_img = Image.new("RGB", (target_width, target_height), "white")

        # Scale the image to fit within the target dimensions while maintaining aspect ratio
        img_aspect = width / height
        target_aspect = target_width / target_height

        if img_aspect > target_aspect:
            # Image is wider than target aspect ratio - fit to width
            new_width = target_width
            new_height = int(target_width / img_aspect)
        else:
            # Image is taller than target aspect ratio - fit to height
            new_height = target_height
            new_width = int(target_height * img_aspect)

        # Resize the image to fit
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Calculate position to center the resized image
        x_offset = (target_width - new_width) // 2
        y_offset = (target_height - new_height) // 2

        # Paste the resized image onto the white background
        padded_img.paste(resized_img, (x_offset, y_offset))

        print(f"Successfully padded to size: {target_width}x{target_height}")

        return padded_img

    except Exception as e:
        print(f"Error processing image: {str(e)}")
        raise e


async def upload_image(user_id: str, image: Image.Image) -> str | None:
    try:
        # Convert PIL Image to bytes
        img_byte_arr = BytesIO()

        # Determine format (default to PNG if not available)
        image_format = image.format if image.format else "PNG"

        # Save image to BytesIO object
        image.save(img_byte_arr, format=image_format)
        img_byte_arr.seek(0)  # Reset pointer to beginning

        # Get the bytes
        contents = img_byte_arr.getvalue()

        filename = f"{uuid.uuid4()}.png"

        # Define storage path (organize by user)
        file_path = f"{user_id}/{filename}"

        content_type = "image/png"

        # Upload to Supabase Storage
        response = image_supabase_client.storage.from_("user-images").upload(
            path=file_path,
            file=contents,
            file_options={"content-type": content_type},
        )

        # For PRIVATE buckets, create a signed URL instead
        url = image_supabase_client.storage.from_("user-images").create_signed_url(
            path=file_path,
            expires_in=3600,  # URL valid for 1 hour (in seconds)
        )

        return url

    except Exception as e:
        # Log the error if you have logging set up
        print(f"Error uploading image for user {user_id}: {str(e)}")
        return None


async def get_user_images(user_id: str) -> List[str]:
    try:
        # List all files in the user's directory
        response = image_supabase_client.storage.from_("user-images").list(path=user_id)

        image_urls = []
        for file_info in response:
            file_path = f"{user_id}/{file_info['name']}"
            url_response = image_supabase_client.storage.from_(
                "user-images"
            ).create_signed_url(
                path=file_path,
                expires_in=3600,  # URL valid for 1 hour (in seconds)
            )
            image_urls.append(url_response["signedURL"])

        return image_urls

    except Exception as e:
        print(f"Error fetching images for user {user_id}: {str(e)}")
        return []


async def delete_user_image(user_id: str, filename: str) -> bool:
    try:
        file_path = f"{user_id}/{filename}"
        response = image_supabase_client.storage.from_("user-images").remove(
            [file_path]
        )
        if response.get("error"):
            print(f"Error deleting image {file_path}: {response['error']}")
            return False
        return True
    except Exception as e:
        print(f"Exception deleting image {file_path}: {str(e)}")
        return False
