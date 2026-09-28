from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_root():
    return {"status": "ok"}


@router.get("/api/health")
async def health_api():
    return {"status": "ok"}
