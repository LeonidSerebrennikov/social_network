import re
from uuid import UUID
from fastapi import HTTPException, status
from app.core.redis_client import redis_client

from app.cmp.users.repository import *

from app.cmp.users.schemas import UserCreate, UserLogin, UserAuthResponse, UserPrivateResponse
from app.cmp.users.utils import hash_password, verify_password, create_access_token, create_refresh_token, verify_token, decode_token



async def register_user(session, user_data: UserCreate) -> UserAuthResponse:
    existing_email = await has_user_by_email(session, user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    username = user_data.username
    if username:
        existing_username = await has_user_by_username(session, user_data.username)
        if existing_username:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exist"
        )
    else:
        username = user_data.email.split('@')[0]
        username = re.sub(r'[^a-zA-Z0-9_]', '_', username)

    user_data.username = username
    
    user = await create_user(session, user_data, hash_password(user_data.password))
    
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    
    return UserAuthResponse(
        user=UserPrivateResponse.model_validate(user),
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

async def login_user(session, login_data: UserLogin) -> UserAuthResponse:
    user = await get_user_by_email(session, login_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    await update_last_login(session, user.id)
    
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    
    return UserAuthResponse(
        user=UserPrivateResponse.model_validate(user),
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

async def logout_user(session, access_token: str, refresh_token: Optional[str] = None
) -> None:
    await _add_token_to_blacklist(access_token, token_type="access")
    if refresh_token:
        await _add_token_to_blacklist(refresh_token, token_type="refresh")

async def refresh_access_token(
    session,
    refresh_token: str
) -> dict:
    user_id = verify_token(refresh_token, token_type="refresh")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user = await get_user_by_id(session, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    new_access_token = create_access_token(user_id)
    
    return {"access_token": new_access_token}

async def _add_token_to_blacklist(token: str, token_type: str) -> None:
    payload = decode_token(token)
    if not payload:
        return
    
    exp = payload.get("exp")
    if not exp:
        return

    current_time = datetime.utcnow().timestamp()
    ttl_seconds = int(exp - current_time)

    if ttl_seconds <= 0:
        return

    key = f"blacklist:{token_type}:{token}"
    await redis_client.setex(key, ttl_seconds, "revoked")
