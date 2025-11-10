jobs = {}
from typing import Any


def add_job(job_id: int, status: str = "pending", result: Any = None):
    jobs[job_id] = {"status": status, "result": result}


def update_job(job_id: int, status: str, result: Any = None):
    if job_id in jobs:
        jobs[job_id]["status"] = status
        jobs[job_id]["result"] = result

    else:
        raise ValueError("Job ID not found")


def get_job(job_id: int):
    job = jobs.get(job_id, None)
    return job
