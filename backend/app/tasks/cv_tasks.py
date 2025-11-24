from app.core.celery_app import celery_app
from app.core.config import AppSettings
from app.wiring.container import (
    build_cv_generator,
    build_mock_cv_generator,
    build_rag_service,
)

settings = AppSettings()
settings.ensure_directories()


@celery_app.task(name="cv.generate")
def generate_cv_task():
    service = build_cv_generator(settings)
    pdf_path = service.generate()
    return {"message": "Generated CV", "file": pdf_path.name}


@celery_app.task(name="cv.generate_mock")
def generate_mock_cv_task():
    service = build_mock_cv_generator(settings)
    pdf_path = service.generate()
    return {"message": "Generated mock CV", "file": pdf_path.name}


@celery_app.task(name="rag.ingest")
def ingest_rag_task():
    service = build_rag_service(settings)
    documents = service.ingest()
    return {"message": "RAG index rebuilt.", "documents": documents}
