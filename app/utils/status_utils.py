import uuid
from collections import deque
from typing import Any, Dict, Optional


class JobManager:
    def __init__(self):
        self.jobs: Dict[uuid.UUID, Dict[str, Any]] = {}
        self.users_jobs: Dict[uuid.UUID, set[uuid.UUID]] = {}
        self.queue: deque[uuid.UUID] = deque()

    def add_job(
        self,
        user_id: str,
        status: str = "pending",
        result: Any = None,
    ):
        user_uuid = uuid.UUID(user_id)
        job_id = uuid.uuid4()

        self.jobs[job_id] = {"status": status, "result": result, "user_id": user_uuid}

        if user_uuid not in self.users_jobs:
            self.users_jobs[user_uuid] = set()

        self.users_jobs[user_uuid].add(job_id)
        self.queue.append(job_id)

        return job_id

    def update_job(
        self,
        job_id: uuid.UUID,
        status: Optional[str] = "pending",
        result: Any = None,
    ):
        if job_id in self.jobs:
            if status is not None:
                self.jobs[job_id]["status"] = status
            if result is not None:
                self.jobs[job_id]["result"] = result

        else:
            raise ValueError("Job ID not found")

    def get_job(self, job_id: uuid.UUID):
        job = self.jobs.get(job_id, None)

        if job is None:
            raise ValueError("Job ID not found")

        return job

    def get_user_jobs(self, user_id: str):
        user_uuid = uuid.UUID(user_id)

        return self.users_jobs.get(user_uuid, set())

    def remove_job(self, job_id: uuid.UUID):
        job = self.jobs.pop(job_id, None)

        if job is None:
            raise ValueError("Job ID not found")

        user_id = job["user_id"]
        if user_id in self.users_jobs:
            self.users_jobs[user_id].discard(job_id)

    def get_next_job(self) -> Optional[uuid.UUID]:
        if self.queue:
            current_job = self.queue.popleft()
            self.remove_job(current_job)
            return current_job

        return None


job_manager = JobManager()
