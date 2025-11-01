from PIL import Image
import os


def pad_image_to_aspect_ratio(img, target_width=None, target_height=None):
    """
    Pad any PIL Image to match a target aspect ratio by adding white padding

    Args:
        img: PIL Image object
        target_width: Target width for the output image (optional)
        target_height: Target height for the output image (optional)

    If both target_width and target_height are provided, the image will be padded to that exact size.
    If only one is provided, the other dimension will be calculated to maintain the target aspect ratio.
    If neither is provided, defaults to square based on the larger dimension (original behavior).

    Returns:
        PIL Image object that matches the target aspect ratio
    """
    try:
        width, height = img.size

        print(f"Processing image (original size: {width}x{height})")

        # Determine target dimensions
        if target_width is None and target_height is None:
            # Default behavior: make it square based on larger dimension
            target_width = target_height = max(width, height)
        elif target_width is None:
            # Calculate width based on target height and original aspect ratio
            aspect_ratio = width / height
            target_width = int(target_height * aspect_ratio)
        elif target_height is None:
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
        return None
