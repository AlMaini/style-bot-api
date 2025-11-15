from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

import supabase

from .clients import get_supabase_client

supabase_client: supabase.Client = get_supabase_client()

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


async def get_user_id(
    authorization: HTTPAuthorizationCredentials = Depends(security),
):
    """Get user ID from JWT token."""
    token = authorization.credentials

    try:
        response = supabase_client.auth.get_user(token)
        if response and response.user:
            return response.user.id
        else:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},  # Optional but good practice
        )
