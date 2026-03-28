from fastapi import APIRouter, Depends, status, Request, Response, HTTPException
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.cmp.users import service as user_service
from app.cmp.users.schemas import UserCreate,UserLogin, UserAuthResponse, UserPrivateResponse, RefreshTokenRequest
from app.cmp.users.dependencies import get_db, get_current_user
# from app.router_registry import register_component

router = APIRouter(tags=["users"])

#register_component(router, tags=["users"])

@router.post("/register", response_model=UserAuthResponse, status_code=status.HTTP_201_CREATED, summary="Register new user")
async def register(
    user_data: UserCreate,
    session: Annotated[AsyncSession, Depends(get_db)]
) -> UserAuthResponse:
    return await user_service.register_user(session, user_data)

@router.post("/login", response_model=UserAuthResponse, summary="Login user")
async def login(
    login_data: UserLogin,
    session: Annotated[AsyncSession, Depends(get_db)]
) -> UserAuthResponse:
    return await user_service.login_user(session, login_data)

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    current_user: Annotated[UserPrivateResponse, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> None:
    auth_header = request.headers.get("Authorization")
    access_token = None
    if auth_header and auth_header.startswith("Bearer "):
        access_token = auth_header.split(" ")[1]
    
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token and request.method == "POST":
        body = await request.json() if request.headers.get("content-type") == "application/json" else {}
        refresh_token = body.get("refresh_token")

    await user_service.logout_user(session, access_token, refresh_token)

@router.post("/refresh", response_model=dict)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    session: Annotated[AsyncSession, Depends(get_db)]
) -> dict:
    return await user_service.refresh_access_token(session, refresh_request.refresh_token)