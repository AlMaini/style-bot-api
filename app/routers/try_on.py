import asyncio
import os
import uuid
from typing import Any, List

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from app.models.status import AddJob
from app.models.try_on import TryOnResponse
from app.services.try_on import process_try_on_single_outfit
from app.utils.auth import get_current_user
from app.utils.database import has_available_usage
from app.utils.image_utils import async_save_uploadfile_to_disk
from app.utils.status_utils import job_manager

router = APIRouter(prefix="/api/try-on")


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

    if len(clothing_files) == 0:
        raise HTTPException(status_code=400, detail="No clothing images provided")

    if not await has_available_usage(uuid.UUID(user.id)):
        raise HTTPException(
            status_code=402,
            detail="No available usage left. Please upgrade your plan.",
        )

    try:
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
            process_try_on_single_outfit,
            uuid.UUID(user.id),
            job_id,
            person_path,
            clothing_paths,
        )

        return {"job_id": str(job_id), "status": "pending"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
