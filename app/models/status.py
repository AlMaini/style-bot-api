from typing import Any
from uuid import UUID

from pydantic import BaseModel


class ProgressResponse(BaseModel):
    job_id: UUID
    status: str


class Job(BaseModel):
    job_id: UUID
    status: str
    result: Any
    user_id: UUID


class AddJob(BaseModel):
    user_id: UUID
    status: str = "pending"
    result: Any = None


class UpdateJob(BaseModel):
    job_id: UUID
    status: str = "pending"
    result: Any = None
