from celery.result import AsyncResult
from fastapi import APIRouter

from app.api.schemas.tasks import TaskStatusResponse
from app.core.celery_app import celery_app

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/{task_id}", response_model=TaskStatusResponse)
def get_task(task_id: str) -> TaskStatusResponse:
    result = AsyncResult(task_id, app=celery_app)
    payload = TaskStatusResponse(task_id=task_id, status=result.state)
    if result.state == "SUCCESS":
        payload.result = result.result
    elif result.state == "FAILURE":
        payload.error = str(result.info) if result.info else "Task failed."
    return payload
