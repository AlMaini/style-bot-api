from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse
from app.models.status import ProgressResponse
from app.utils.auth import get_user_id, verify_user_perms
from app.utils.status_utils import job_manager

router = APIRouter(prefix="/api/status")


@router.get("/progress/{job_id}", response_model=ProgressResponse)
async def get_status(job_id: UUID, valid=Depends(verify_user_perms)):
    if not valid:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        job = job_manager.get_job(job_id)
        return ProgressResponse(job_id=job.job_id, status=job.status)

    except ValueError:
        raise HTTPException(status_code=404, detail="Job ID not found")


@router.get(
    "/result/{job_id}",
    response_class=FileResponse,
    responses={
        200: {"content": {"image/png": {}}},
        404: {"description": "Job not completed yet or not found"},
        500: {"description": "Server error"},
    },
)
async def get_result(job_id: UUID, valid=Depends(verify_user_perms)):
    if not valid:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        job = job_manager.get_job(job_id)

        if job.status != "completed":
            raise HTTPException(status_code=404, detail="Job not completed yet")

        job_manager.remove_job(job_id)
        return FileResponse(path=job.result, media_type="image/png")

    except ValueError:
        raise HTTPException(status_code=404, detail="Job ID not found")


@router.get("/jobs_dict")
async def get_jobs_dict():
    return {"jobs dict": job_manager.jobs, "users jobs": job_manager.users_jobs}


@router.get("/jobs/{user_id}")
async def get_user_jobs(user_id: str, token_id=Depends(get_user_id)):
    if not token_id or token_id != user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        jobs = job_manager.get_user_jobs(user_id)
        return {"job_ids": list(jobs)}

    except ValueError:
        raise HTTPException(status_code=404, detail="User ID not found")
