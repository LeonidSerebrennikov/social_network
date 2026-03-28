from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional
import re


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = Field(None, max_length=255)
    username: Optional[str] = Field(
        None, 
        min_length=3, 
        max_length=50
    )
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not re.match(r"^[a-zA-Z0-9_]+$", v):
                raise ValueError("Username must contain only letters, numbers and underscore")
            return v.lower()
        return v
    

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    password_confirm: str = Field(..., min_length=8, max_length=100)
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[a-zA-Z]", v):
            raise ValueError("Password must contain at least one letter")
        return v
    
    @field_validator("password_confirm")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if "password" not in info.data:
            raise ValueError("Enter password")
        if v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)

class UserResponse(BaseModel):
    id: UUID
    username: str
    full_name: str | None
    is_active: bool
    is_verified: bool
    last_login: datetime | None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserPrivateResponse(UserResponse):
    email: EmailStr
    is_superuser: bool

class UserAuthResponse(BaseModel):
    user: UserPrivateResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str  # user_id
    exp: int
    type: str  # "access" or "refresh"
    