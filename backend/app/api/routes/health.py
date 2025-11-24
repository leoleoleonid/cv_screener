from fastapi import APIRouter

from app.api.schemas.health import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(message="Hello from FastAPI backend 👋")
