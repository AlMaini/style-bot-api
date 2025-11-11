import asyncio
import os
import uuid
from typing import Any, List

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from models.status import AddJob
from models.try_on import TryOnResponse
from services.try_on import generate_try_on_image
from utils.auth import get_current_user
from utils.image_utils import async_save_uploadfile_to_disk, open_images
from utils.status_utils import job_manager

router = APIRouter(prefix="/api/try-on")


async def process_try_on_single_outfit(
    job_id: uuid.UUID, person_path: str, clothing_paths: List[str]
):
    loop = asyncio.get_running_loop()
    all_paths = [person_path] + list(clothing_paths)

    try:
        # Open images in executor (Pillow work off the event loop)
        images = await loop.run_in_executor(None, open_images, all_paths)
        person_img = images[0]
        clothing_imgs = images[1:]

        await generate_try_on_image(str(job_id), person_img, clothing_imgs)
    finally:
        # Try to remove temporary files; swallow errors
        for p in all_paths:
            try:
                os.remove(p)
            except Exception:
                pass


async def test_process_try_on_single_outfit(*args, **kwargs):
    pass


@router.post("/single-outfit", response_model=TryOnResponse)
async def try_on(
    background_tasks: BackgroundTasks,
    person_file: UploadFile = File(...),
    clothing_files: List[UploadFile] = File(...),
    user=Depends(get_current_user),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized, invalid token")

    try:
        if not person_file:
            raise HTTPException(status_code=400, detail="No person image provided")

        if not clothing_files or len(clothing_files) == 0:
            raise HTTPException(status_code=400, detail="No clothing images provided")

        # Persist uploads to disk (while request context is active)
        person_path = await async_save_uploadfile_to_disk(person_file)
        clothing_paths = []
        for f in clothing_files:
            p = await async_save_uploadfile_to_disk(f)
            clothing_paths.append(p)

        job_id = job_manager.add_job(
            AddJob(user_id=user.id, status="pending", result=None)
        )

        # Schedule background task passing file paths
        background_tasks.add_task(
            process_try_on_single_outfit, job_id, person_path, clothing_paths
        )

        return {"job_id": str(job_id), "status": "pending"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
