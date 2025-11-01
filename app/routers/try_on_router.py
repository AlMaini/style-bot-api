from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import List, Any
from PIL import Image

from app.services.try_on_service import try_on_clothes

router = APIRouter(prefix="/api")


@router.post("/try-on")
async def try_on(images_files: List[UploadFile] = File(...)) -> dict[str, Any]:
    try:
        if not images_files:
            raise HTTPException(status_code=400, detail="No images provided")

        images = []
        for upload in images_files:
            img = Image.open(upload.file)
            images.append(img.convert("RGB"))

        result = try_on_clothes(images)
        return {"message": "Try-on successful", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
