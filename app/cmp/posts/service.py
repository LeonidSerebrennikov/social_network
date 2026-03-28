from datetime import datetime
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.cmp.posts.repository import (
    create_post as repo_create_post,
    get_post_by_id,
    get_posts as repo_get_posts,
    get_user_posts as repo_get_user_posts,
    update_post as repo_update_post,
    delete_post as repo_delete_post,
    check_post_author,
)
from app.cmp.posts.schemas import PostCreate, PostUpdate, PostResponse
from app.cmp.users.repository import get_user_by_id


async def create_post(session: AsyncSession, author_id: UUID, post_data: PostCreate) -> PostResponse:
    user = await get_user_by_id(session, author_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # if not user.is_active:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="User account is disabled"
    #     )

    post = await repo_create_post(session=session, title=post_data.title, content=post_data.content, author_id=author_id)

    post_with_media = await get_post_by_id(session, post.id)
    
    return PostResponse.model_validate(post_with_media)


async def get_post(session: AsyncSession, post_id: UUID) -> PostResponse:
    post = await get_post_by_id(session, post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    if post.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    return PostResponse.model_validate(post)


async def get_posts(session: AsyncSession, skip: int = 0, limit: int = 20, author_id: UUID | None = None, search: str | None = None) -> list[PostResponse]:
    posts = await repo_get_posts(
        session=session,
        skip=skip,
        limit=limit,
        author_id=author_id,
        search=search
    )

    return [PostResponse.model_validate(post) for post in posts]


async def get_user_posts(session: AsyncSession, user_id: UUID, skip: int = 0, limit: int = 20) -> list[PostResponse]:
    user = await get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    posts = await repo_get_user_posts(
        session=session,
        user_id=user_id,
        skip=skip,
        limit=limit
    )

    return [PostResponse.model_validate(post) for post in posts]


async def update_post(session: AsyncSession, post_id: UUID, author_id: UUID, post_data: PostUpdate) -> PostResponse:
    post = await get_post_by_id(session, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    if post.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    if post.author_id != author_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to edit this post"
        )

    updated_post = await repo_update_post(
        session=session,
        post_id=post_id,
        title=post_data.title,
        content=post_data.content
    )

    return PostResponse.model_validate(updated_post)


async def delete_post(session: AsyncSession, post_id: UUID, author_id: UUID) -> None:
    post = await get_post_by_id(session, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    if post.author_id != author_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this post"
        )

    if post.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post already deleted"
        )

    await repo_delete_post(session, post_id)


async def restore_post(session: AsyncSession, post_id: UUID, author_id: UUID) -> PostResponse:
    post = await get_post_by_id(session, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    if post.author_id != author_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to restore this post"
        )

    if not post.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post is not deleted"
        )

    from app.cmp.posts.repository import restore_post as repo_restore_post
    restored_post = await repo_restore_post(session, post_id)

    return PostResponse.model_validate(restored_post)
