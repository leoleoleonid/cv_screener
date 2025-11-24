from pydantic import BaseModel


class CVListResponse(BaseModel):
    files: list[str]
