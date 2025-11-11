from cmath import e

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
