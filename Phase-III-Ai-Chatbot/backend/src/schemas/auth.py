from pydantic import BaseModel
from typing import Optional
import uuid


class JWTPayload(BaseModel):
    """
    Schema for JWT payload data.
    """
    user_id: str
    exp: Optional[int] = None
    iat: Optional[int] = None
    sub: Optional[str] = None


class LoginRequest(BaseModel):
    """
    Schema for login request.
    """
    email: str
    password: str


class RegisterRequest(BaseModel):
    """
    Schema for registration request.
    """
    email: str
    password: str
    name: Optional[str] = None


class LoginResponse(BaseModel):
    """
    Schema for login response.
    """
    access_token: str
    token_type: str = "bearer"


class LogoutResponse(BaseModel):
    """
    Schema for logout response.
    """
    message: str = "Successfully logged out"