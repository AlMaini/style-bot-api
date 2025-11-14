from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from models.auth import LoginResponse, ProfileResponse, SignupResponse, User
from pydantic import BaseModel, EmailStr
from utils.clients import get_supabase_client
from utils.database import get_profile_from_db

router = APIRouter(prefix="/api/auth")

client = get_supabase_client()
security = HTTPBearer()


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


@router.post("/login", response_model=LoginResponse)
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


@router.post("/signup", response_model=SignupResponse)
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


@router.get("/google")
async def google_login(
    redirect_to: str = Query(default="http://127.0.0.1:8080/api/auth/callback"),
):
    """
    Initiate Google OAuth login.
    The redirect_to parameter specifies where to redirect after successful login.
    """
    try:
        # Generate the OAuth URL for Google
        response = client.auth.sign_in_with_oauth(
            {
                "provider": "google",
                "options": {
                    "redirect_to": f"{redirect_to}"  # Your frontend callback URL
                },
            }
        )

        return {"url": response.url}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"OAuth initiation failed: {str(e)}"
        )


@router.get("/callback")
async def auth_callback(
    code: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    error_description: Optional[str] = Query(None),
):
    """
    Handle OAuth callback from Google.
    Supabase automatically handles the token exchange.
    """
    if error:
        raise HTTPException(
            status_code=400, detail=f"OAuth error: {error_description or error}"
        )

    if not code:
        raise HTTPException(status_code=400, detail="No authorization code provided")

    try:
        # Exchange the code for a session
        response = client.auth.exchange_code_for_session({"auth_code": code})

        if response.session and response.user:
            return {
                "message": "Google login successful!",
                "user_id": response.user.id,
                "email": response.user.email,
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "expires_in": response.session.expires_in,
            }
        else:
            raise HTTPException(status_code=401, detail="Failed to create session")

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to exchange code for session: {str(e)}"
        )


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(current_user=Depends(get_current_user)):
    user_id = current_user.user.id
    try:
        profile = await get_profile_from_db(user_id)
        if profile:
            return ProfileResponse(
                email=current_user.user.email,
                subscription_plan=profile["subscription_plan"],
                image_limit=profile["image_limit"],
                image_usage=profile["image_usage"],
            )
        else:
            raise HTTPException(status_code=404, detail="Profile not found")
    except Exception as e:
        print(f"Error fetching profile: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching profile: {str(e)}")
