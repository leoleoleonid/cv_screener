from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
def health():
    return {"message": "Hello from FastAPI backend 👋"}
