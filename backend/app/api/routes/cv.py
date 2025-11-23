from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import (
    get_cv_texts_use_case,
    get_generate_cv_use_case,
    get_generate_mock_cv_use_case,
    get_list_static_files_use_case,
)
from app.use_cases.generate_cv import GenerateCvUseCase
from app.use_cases.generate_mock_cv import GenerateMockCvUseCase
from app.use_cases.get_cv_texts import GetCvTextsUseCase
from app.use_cases.list_static_files import ListStaticFilesUseCase

router = APIRouter(prefix="/cv", tags=["CV"])


@router.get("")
def list_cvs(
    use_case: ListStaticFilesUseCase = Depends(get_list_static_files_use_case),
):
    return {"files": use_case.execute()}


@router.post("/generate")
def generate_cv(
    use_case: GenerateCvUseCase = Depends(get_generate_cv_use_case),
):
    pdf_path = use_case.execute()
    return {"message": "Generated CV", "file": pdf_path.name}


@router.post("/generate-mock")
def generate_mock_cv(
    use_case: GenerateMockCvUseCase = Depends(get_generate_mock_cv_use_case),
):
    pdf_path = use_case.execute()
    return {"message": "Generated mock CV", "file": pdf_path.name}


@router.get("/texts")
def get_cv_texts(
    use_case: GetCvTextsUseCase = Depends(get_cv_texts_use_case),
):
    try:
        return use_case.execute()
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail="Failed to read CV files") from exc
