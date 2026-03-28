from fastapi import APIRouter, Depends, status, Query, HTTPException
from typing import Annotated, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.cmp.users.schemas import UserPrivateResponse
from app.cmp.users.dependencies import get_db, get_current_user
from app.cmp.posts.models import Post, PostMedia
import app.cmp.posts.service as post_service
from app.cmp.posts.schemas import PostCreate, PostUpdate, PostResponse


router = APIRouter(tags=["posts"])

@router.post("/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED, summary="Create new post")
async def create_post(post_data: PostCreate, current_user: Annotated[UserPrivateResponse, Depends(get_current_user)], session: Annotated[AsyncSession, Depends(get_db)]) -> PostResponse:
    return await post_service.create_post(session=session, author_id=current_user.id, post_data=post_data)

@router.get("/posts",response_model=List[PostResponse],summary="Get posts list")
async def get_posts(session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserPrivateResponse, Depends(get_current_user)],
    skip: int = Query(0, ge=0, description="Number of posts to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of posts to return"),
    author_id: Optional[str] = Query(None, description="Filter by author ID (UUID format)"), 
    search: Optional[str] = Query(None, description="Search in title and content")
) -> List[PostResponse]:
    author_uuid = None
    if author_id:
        try:
            author_uuid = UUID(author_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid author_id format"
            )
    return await post_service.get_posts(session=session, skip=skip, limit=limit, author_id=author_uuid, search=search)


@router.get("/posts/{post_id}", response_model=PostResponse, summary="Get post by ID")
async def get_post(post_id: UUID, current_user: Annotated[UserPrivateResponse, Depends(get_current_user)], session: Annotated[AsyncSession, Depends(get_db)]) -> PostResponse:
    return await post_service.get_post(session=session, post_id=post_id)


@router.put("/posts/{post_id}", response_model=PostResponse, summary="Update post")
async def update_post(post_id: UUID, post_data: PostUpdate, current_user: Annotated[UserPrivateResponse, Depends(get_current_user)], session: Annotated[AsyncSession, Depends(get_db)]) -> PostResponse:
    return await post_service.update_post(session=session, post_id=post_id, author_id=current_user.id, post_data=post_data)


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete post"
)
async def delete_post(post_id: UUID, current_user: Annotated[UserPrivateResponse, Depends(get_current_user)], session: Annotated[AsyncSession, Depends(get_db)]) -> None:
    await post_service.delete_post(session=session, post_id=post_id, author_id=current_user.id)


@router.get("/{user_id}/posts",response_model=List[PostResponse], summary="Get posts by user")
async def get_user_posts(session: Annotated[AsyncSession, Depends(get_db)], current_user: Annotated[UserPrivateResponse, Depends(get_current_user)], user_id: UUID, skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100)) -> List[PostResponse]:
    return await post_service.get_user_posts(session=session, user_id=user_id, skip=skip, limit=limit)
