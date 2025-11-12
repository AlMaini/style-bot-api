from pydantic import BaseModel


class TryOnResponse(BaseModel):
    job_id: str
    status: str
