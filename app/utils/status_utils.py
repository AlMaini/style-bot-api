import uuid
from collections import deque
from typing import Any, Dict, Optional

from models.status import AddJob, Job, UpdateJob


class JobManager:
    def __init__(self):
        self.jobs: Dict[uuid.UUID, Job] = {}
        self.users_jobs: Dict[uuid.UUID, set[uuid.UUID]] = {}
        self.queue: deque[uuid.UUID] = deque()

    def add_job(self, job: AddJob) -> uuid.UUID:
        job_id = uuid.uuid4()

        self.jobs[job_id] = Job(
            job_id=job_id, status=job.status, result=job.result, user_id=job.user_id
        )

        if job.user_id not in self.users_jobs:
            self.users_jobs[job.user_id] = set()

        self.users_jobs[job.user_id].add(job_id)
        self.queue.append(job_id)

        return job_id

    def update_job(self, incoming_job_info: UpdateJob) -> None:
        if incoming_job_info.job_id in self.jobs:
            self.jobs[incoming_job_info.job_id].status = incoming_job_info.status
            if incoming_job_info.result is not None:
                self.jobs[incoming_job_info.job_id].result = incoming_job_info.result

        else:
            raise ValueError("Job ID not found")

    def get_job(self, job_id: uuid.UUID) -> Job:
        job = self.jobs.get(job_id, None)

        if job is None:
            raise ValueError("Job ID not found")

        return job

    def get_user_jobs(self, user_id: str) -> set[uuid.UUID]:
        user_uuid = uuid.UUID(user_id)

        return self.users_jobs.get(user_uuid, set())

    def remove_job(self, job_id: uuid.UUID) -> None:
        job = self.jobs.pop(job_id, None)

        if job is None:
            raise ValueError("Job ID not found")

        user_id = job.user_id
        if user_id in self.users_jobs:
            self.users_jobs[user_id].discard(job_id)

    def get_next_job(self) -> Optional[uuid.UUID]:
        if self.queue:
            current_job = self.queue.popleft()
            self.remove_job(current_job)
            return current_job

        return None


job_manager = JobManager()
