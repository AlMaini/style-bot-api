from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
)
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr
from utils.clients import get_supabase_client

router = APIRouter(prefix="/api/auth")

client = get_supabase_client()
security = HTTPBearer()


class User(BaseModel):
    email: EmailStr
    password: str


async def get_current_user(
    authorization: HTTPAuthorizationCredentials = Depends(security),
):
    """Verify JWT token and return current user."""
    token = authorization.credentials

    try:
        user = client.auth.get_user(token)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},  # Optional but good practice
        )


@router.post("/login")
async def login(user: User):
    response = client.auth.sign_in_with_password(
        {"email": user.email, "password": user.password}
    )
    if response.session and response.user:
        return {
            "message": "Login successful!",
            "user_id": response.user.id,
            "email": response.user.email,
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "expires_in": response.session.expires_in,
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@router.post("/signup")
async def signup(user: User):
    response = client.auth.sign_up({"email": user.email, "password": user.password})
    if response.user:
        return {
            "message": "User created successfully! Check your email to confirm your account.",
            "user_id": response.user.id,
            "email": response.user.email,
            # this is so that if email confirmation is not required, we can still return the access token, refresh token, and expires_in
            "access_token": response.session.access_token if response.session else None,
            "refresh_token": response.session.refresh_token
            if response.session
            else None,
            "expires_in": response.session.expires_in if response.session else None,
        }
    else:
        raise HTTPException(status_code=400, detail="Signup failed")


@router.get("/profile")
async def get_profile(current_user=Depends(get_current_user)):
    user = current_user.user

    return {
        "profile": {
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at,
            "last_sign_in": user.last_sign_in_at,
        }
    }
