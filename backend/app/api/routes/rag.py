from fastapi import APIRouter

from app.api.schemas.tasks import TaskSubmissionResponse
from app.tasks.cv_tasks import ingest_rag_task

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/ingest", response_model=TaskSubmissionResponse)
def ingest_rag() -> TaskSubmissionResponse:
    task = ingest_rag_task.delay()
    return TaskSubmissionResponse(task_id=task.id, status=task.status)
