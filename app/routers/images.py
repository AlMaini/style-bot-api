from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from app.utils.auth import get_current_user
from app.utils.image_utils import get_user_images

router = APIRouter(prefix="/api/images")


@router.get("/")
async def get_image(user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_images = await get_user_images(user.id)
    if not user_images:
        raise HTTPException(status_code=404, detail="No images found for user")

    try:
        return {"images": user_images}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Image not found: {str(e)}")
