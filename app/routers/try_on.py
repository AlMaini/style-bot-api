import asyncio
import os
from random import randint
from typing import Any, List

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from services.try_on import generate_try_on_image
from utils.auth import verify_user_perms
from utils.image_utils import async_save_uploadfile_to_disk, open_images
from utils.status_utils import add_job

router = APIRouter(prefix="/api/try-on")


async def process_try_on_single_outfit(
    job_id: int, person_path: str, clothing_paths: List[str]
):
    loop = asyncio.get_running_loop()
    all_paths = [person_path] + list(clothing_paths)

    try:
        # Open images in executor (Pillow work off the event loop)
        images = await loop.run_in_executor(None, open_images, all_paths)
        person_img = images[0]
        clothing_imgs = images[1:]

        await generate_try_on_image(job_id, person_img, clothing_imgs)
    finally:
        # Try to remove temporary files; swallow errors
        for p in all_paths:
            try:
                os.remove(p)
            except Exception:
                pass


async def test_process_try_on_single_outfit(*args, **kwargs):
    pass


@router.post("/single-outfit")
async def try_on(
    background_tasks: BackgroundTasks,
    images_files: List[UploadFile] = File(...),
    authorization: bool = Depends(verify_user_perms),
):
    if authorization:
        try:
            if not images_files:
                raise HTTPException(status_code=400, detail="No images provided")

            person_upload = images_files[0]
            clothing_uploads = images_files[1:]

            # Persist uploads to disk (while request context is active)
            person_path = await async_save_uploadfile_to_disk(person_upload)
            clothing_paths = []
            for f in clothing_uploads:
                p = await async_save_uploadfile_to_disk(f)
                clothing_paths.append(p)

            job_id = randint(0, 1_000_000)
            add_job(job_id, status="pending", result=None)

            # Schedule background task passing file paths
            background_tasks.add_task(
                process_try_on_single_outfit, job_id, person_path, clothing_paths
            )

            return {"job_id": job_id, "status": "pending"}

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=401, detail="Unauthorized, invalid token")
