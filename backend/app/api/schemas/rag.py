from pydantic import BaseModel


class RagIngestResponse(BaseModel):
    task_id: str
    status: str
