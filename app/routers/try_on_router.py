from fastapi import APIRouter, File, FileResponse, UploadFile, HTTPException
from typing import List, Any
from random import randint
from PIL import Image

from app.services.try_on_service import generate_try_on_image

router = APIRouter(prefix="/api")


@router.post("/try-on")
async def try_on(images_files: List[UploadFile] = File(...)) -> FileResponse:
    try:
        if not images_files:
            raise HTTPException(status_code=400, detail="No images provided")

        images = []
        for upload in images_files:
            img = Image.open(upload.file)
            images.append(img.convert("RGB"))

        uid = randint(1, 2**32)  # Example UID generation
        result = generate_try_on_image(uid, images)
        file_path = f"{uid}_result.png"
        result.save(file_path)
        return FileResponse(f"{uid}_image.png", media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
