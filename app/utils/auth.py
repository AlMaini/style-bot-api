from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .clients import get_supabase_client

supabase_client = get_supabase_client()
security = HTTPBearer()


async def verify_user_perms(
    authorization: HTTPAuthorizationCredentials = Depends(security),
):
    token = authorization.credentials

    try:
        return bool(supabase_client.auth.get_user(token))

    except Exception as e:
        return False


async def get_current_user(
    authorization: HTTPAuthorizationCredentials = Depends(security),
):
    """Verify JWT token and return current user."""
    token = authorization.credentials

    try:
        response = supabase_client.auth.get_user(token)
        return response.user if response else None
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},  # Optional but good practice
        )
