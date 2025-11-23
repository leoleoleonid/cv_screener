from fastapi import APIRouter, Depends

from app.core.deps import (
    get_cv_generator,
    get_mock_cv_generator,
)
from app.services.cv_generator import CVGeneratorService

router = APIRouter(prefix="/cv", tags=["CV"])


@router.get("")
def list_cvs(
    generator: CVGeneratorService = Depends(get_cv_generator),
):
    return {"files": generator.list_pdf_files()}


@router.post("/generate")
def generate_cv(
    generator: CVGeneratorService = Depends(get_cv_generator),
):
    pdf_path = generator.generate()
    return {"message": "Generated CV", "file": pdf_path.name}


@router.post("/generate-mock")
def generate_mock_cv(
    generator: CVGeneratorService = Depends(get_mock_cv_generator),
):
    pdf_path = generator.generate()
    return {"message": "Generated mock CV", "file": pdf_path.name}

