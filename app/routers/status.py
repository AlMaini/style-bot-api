from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse
from utils.status_utils import get_job

router = APIRouter(prefix="/api/status")


@router.get("/progress/{job_id}")
async def get_status(job_id: str):
    job = get_job(int(job_id))

    if job is None:
        return HTTPException(status_code=404, detail="Job ID not found")

    return job


@router.get("/result/{job_id}")
async def get_result(job_id: str):
    job = get_job(int(job_id))

    if job is None:
        return HTTPException(status_code=404, detail="Job ID not found")

    if job["status"] != "completed":
        return {"error": "Job not completed yet"}

    return FileResponse(path=job["result"], media_type="image/png")
