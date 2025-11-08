from io import BytesIO
from typing import Any, List
from random import randint
from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response
from PIL import Image
from services.try_on import generate_try_on_image

jobs = {}

router = APIRouter(prefix="/api/try-on")


@router.post("/single-item")
async def try_on(
    background_tasks: BackgroundTasks,  # No default - comes first
    images_files: List[UploadFile] = File(...),  # Has default - comes last
):
    try:
        if not images_files:
            raise HTTPException(status_code=400, detail="No images provided")

        images = []
        for upload in images_files:
            img = Image.open(upload.file)
            images.append(img.convert("RGB"))

        person = images[0]
        clothing = images[1:]

        job_id = randint(0, 1_000_000)
        jobs[job_id] = {"status": "pending", "result": None}

        # Start background task
        background_tasks.add_task(generate_try_on_image, job_id, person, clothing)

        return {"job_id": job_id, "status": "pending"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{job_id}")
async def get_status(job_id: str):
    if job_id not in jobs:
        return {"error": "Job not found"}
    return jobs[job_id]


@router.get("/result/{job_id}")
async def get_result(job_id: str):
    if job_id not in jobs:
        return {"error": "Job not found"}

    job = jobs[job_id]
    if job["status"] != "completed":
        return {"error": "Job not completed yet"}

    return FileResponse(path=f"{job_id}.png", media_type="image/png")
