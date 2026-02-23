from fastapi import APIRouter, HTTPException, status, Depends
from typing import Optional
from pydantic import BaseModel
from ..schemas.auth import LoginRequest, RegisterRequest, LoginResponse, LogoutResponse
from ..dependencies import get_current_user_id
from ..config import settings
from jose import jwt
from datetime import datetime, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["auth"])

@router.post("/auth/register", response_model=LoginResponse)
async def register(user_data: RegisterRequest):
    """
    Register a new user.
    This endpoint simulates registration with Better Auth.
    In a real implementation, this would integrate with Better Auth service.
    """
    # In a real implementation, this would call Better Auth API
    # For now, we'll simulate the process

    # Generate a user ID
    user_id = str(uuid.uuid4())

    # Create a JWT token (simulating Better Auth token)
    expire = datetime.utcnow() + timedelta(hours=24)  # 24-hour expiry per NFR-003
    token_data = {
        "user_id": user_id,
        "exp": expire.timestamp(),
        "iat": datetime.utcnow().timestamp(),
        "sub": user_data.email
    }

    token = jwt.encode(token_data, settings.better_auth_secret, algorithm="HS256")

    return LoginResponse(access_token=token)


class SignInEmailRequest(BaseModel):
    """
    Schema for sign-in email request, matching frontend expectations.
    """
    email: str
    password: str
    callbackURL: Optional[str] = None


class SignUpEmailRequest(BaseModel):
    """
    Schema for sign-up email request, matching frontend expectations.
    """
    name: str
    email: str
    password: str
    callbackURL: Optional[str] = None



@router.post("/auth/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """
    Authenticate a user and return JWT token.
    This endpoint simulates login with Better Auth.
    In a real implementation, this would integrate with Better Auth service.
    """
    # In a real implementation, this would call Better Auth API to verify credentials
    # For now, we'll simulate the process

    # Generate a user ID (in real app, this would come from DB after validation)
    user_id = str(uuid.uuid4())

    # Create a JWT token (simulating Better Auth token)
    expire = datetime.utcnow() + timedelta(hours=24)  # 24-hour expiry per NFR-003
    token_data = {
        "user_id": user_id,
        "exp": expire.timestamp(),
        "iat": datetime.utcnow().timestamp(),
        "sub": login_data.email
    }

    token = jwt.encode(token_data, settings.better_auth_secret, algorithm="HS256")

    return LoginResponse(access_token=token)


@router.post("/auth/logout", response_model=LogoutResponse)
async def logout(user_id: str = Depends(get_current_user_id)):
    """
    Logout the current user.
    This endpoint simulates logout with Better Auth.
    In a real implementation, this would integrate with Better Auth service.
    """
    # In a real implementation, this would call Better Auth API to invalidate the token
    # For now, we just return a success message

    return LogoutResponse(message="Successfully logged out")


@router.post("/auth/sign-out", response_model=LogoutResponse)
async def sign_out(user_id: str = Depends(get_current_user_id)):
    """
    Sign out the current user (alternative logout endpoint).
    This endpoint is used by the frontend for session termination.
    """
    return LogoutResponse(message="Successfully signed out")


# Add endpoints that better-auth client expects
@router.post("/auth/sign-up/email", response_model=LoginResponse)
async def better_auth_sign_up(signup_data: SignUpEmailRequest):
    """
    Sign-up endpoint that matches better-auth client expectations.
    Creates a JWT token for the user.
    """
    try:
        logger.info(f"Sign-up attempt for email: {signup_data.email}")

        # Validate input data
        if not signup_data.email or "@" not in signup_data.email:
            logger.warning("Invalid email provided")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid email is required"
            )

        if not signup_data.password or len(signup_data.password) < 6:
            logger.warning("Password too short")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters"
            )

        if not signup_data.name or len(signup_data.name.strip()) < 2:
            logger.warning("Name too short")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Name must be at least 2 characters"
            )

        # Generate a user ID
        user_id = uuid.uuid4()

        logger.info(f"Creating user with ID: {user_id}")

        # Create a JWT token
        expire = datetime.utcnow() + timedelta(hours=24)  # 24-hour expiry per NFR-003
        token_data = {
            "user_id": str(user_id),
            "exp": expire.timestamp(),
            "iat": datetime.utcnow().timestamp(),
            "sub": signup_data.email,
            "name": signup_data.name
        }

        token = jwt.encode(token_data, settings.better_auth_secret, algorithm="HS256")

        return LoginResponse(access_token=token)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sign-up error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sign-up failed: {str(e)}"
        )


@router.post("/auth/sign-in/email", response_model=LoginResponse)
async def better_auth_sign_in(signin_data: SignInEmailRequest):
    """
    Sign-in endpoint that matches better-auth client expectations.
    For simplicity, we create users on-the-fly without database persistence.
    The user will be created in the database on first task creation.
    """
    try:
        # Validate input data
        if not signin_data.email or "@" not in signin_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid email is required"
            )

        if not signin_data.password or len(signin_data.password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters"
            )

        # Generate a user ID
        user_id = uuid.uuid4()

        # Create a JWT token
        expire = datetime.utcnow() + timedelta(hours=24)  # 24-hour expiry per NFR-003
        token_data = {
            "user_id": str(user_id),
            "exp": expire.timestamp(),
            "iat": datetime.utcnow().timestamp(),
            "sub": signin_data.email,
            "name": signin_data.email.split('@')[0]
        }

        token = jwt.encode(token_data, settings.better_auth_secret, algorithm="HS256")

        logger.info(f"User signed in successfully: {signin_data.email}")
        return LoginResponse(access_token=token)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sign-in error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sign-in failed: {str(e)}"
        )


from fastapi import Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


# Create a security scheme for token validation
security = HTTPBearer(auto_error=False)


@router.get("/auth/get-session")
async def get_session(request: Request, token_credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get the current user session.
    This endpoint is used by the frontend to check if user is authenticated.
    Returns session status without throwing error if not authenticated.
    """
    if token_credentials is None:
        # No token provided
        return {
            "authenticated": False,
            "session_valid": False,
            "error": "No authentication token provided"
        }

    try:
        # Use the same secret as configured in settings
        secret = settings.better_auth_secret

        # Verify the token
        token = token_credentials.credentials
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        user_id = payload.get("user_id")

        if user_id is None:
            return {
                "authenticated": False,
                "session_valid": False,
                "error": "Invalid token: no user_id"
            }

        # Token is valid
        return {
            "user_id": user_id,
            "authenticated": True,
            "session_valid": True
        }

    except jwt.JWTError:
        # Invalid token
        return {
            "authenticated": False,
            "session_valid": False,
            "error": "Invalid or expired token"
        }
    except Exception as e:
        # Other error
        return {
            "authenticated": False,
            "session_valid": False,
            "error": "Session validation failed"
        }