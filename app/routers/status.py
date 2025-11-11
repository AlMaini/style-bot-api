from uuid import UUID

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse
from utils.status_utils import job_manager

router = APIRouter(prefix="/api/status")


@router.get("/progress/{job_id}")
async def get_status(job_id: str):
    try:
        job = job_manager.get_job(UUID(job_id))
        return job

    except ValueError:
        return HTTPException(status_code=404, detail="Job ID not found")


@router.get("/result/{job_id}")
async def get_result(job_id: str):
    try:
        job = job_manager.get_job(UUID(job_id))

        if job["status"] != "completed":
            return HTTPException(status_code=404, detail="Job not completed yet")

        job_manager.remove_job(UUID(job_id))
        return FileResponse(path=job["result"], media_type="image/png")

    except ValueError:
        return HTTPException(status_code=404, detail="Job ID not found")


@router.get("/jobs_dict")
async def get_jobs_dict():
    return {"jobs dict": job_manager.jobs, "users jobs": job_manager.users_jobs}
