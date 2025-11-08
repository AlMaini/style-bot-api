from io import BytesIO
from random import randint
from typing import Any, List

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response
from PIL import Image
from services.try_on_service import generate_try_on_image

router = APIRouter(prefix="/api")


@router.post("/try-on")
async def try_on(images_files: List[UploadFile] = File(...)) -> Response:
    try:
        if not images_files:
            raise HTTPException(status_code=400, detail="No images provided")

        images = []
        for upload in images_files:
            img = Image.open(upload.file)
            images.append(img.convert("RGB"))

        result = generate_try_on_image(images[0], images[1:])  # this is a PIL image
        result_bytes = BytesIO()
        result.save(result_bytes, format="PNG")
        result_bytes.seek(0)

        return Response(content=result_bytes.getvalue(), media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
