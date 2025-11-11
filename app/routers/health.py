from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/")
async def root():
    return {"message": "Drip Drop Image Generator API", "status": "running"}

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "image-generator"}