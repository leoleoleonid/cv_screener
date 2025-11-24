from fastapi import APIRouter, Depends

from app.api.schemas.cv import CVListResponse
from app.api.schemas.tasks import TaskSubmissionResponse
from app.core.deps import get_cv_generator
from app.services.cv_generator import CVGeneratorService
from app.tasks.cv_tasks import generate_cv_task, generate_mock_cv_task

router = APIRouter(prefix="/cv", tags=["CV"])


@router.get("", response_model=CVListResponse)
def list_cvs(
    generator: CVGeneratorService = Depends(get_cv_generator),
) -> CVListResponse:
    return CVListResponse(files=generator.list_pdf_files())


@router.post("/generate", response_model=TaskSubmissionResponse)
def generate_cv() -> TaskSubmissionResponse:
    task = generate_cv_task.delay()
    return TaskSubmissionResponse(task_id=task.id, status=task.status)


@router.post("/generate-mock", response_model=TaskSubmissionResponse)
def generate_mock_cv() -> TaskSubmissionResponse:
    task = generate_mock_cv_task.delay()
    return TaskSubmissionResponse(task_id=task.id, status=task.status)
