from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import select, update, func, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.cmp.posts.models import Post


async def create_post(session: AsyncSession, title: str, content: str, author_id: UUID) -> Post:
    now = datetime.utcnow()

    post = Post(
        id=uuid4(),
        title=title,
        content=content,
        author_id=author_id,
        created_at=now,
        updated_at=now,
        is_deleted=False
    )

    session.add(post)
    await session.flush()
    await session.refresh(post)

    return post


async def get_post_by_id(session: AsyncSession, post_id: UUID) -> Optional[Post]:
    query = select(Post).where(Post.id == post_id).options(selectinload(Post.media))
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_posts(session: AsyncSession, skip: int = 0, limit: int = 20, author_id: Optional[UUID] = None, search: Optional[str] = None) -> List[Post]:
    query = select(Post).where(Post.is_deleted == False).options(selectinload(Post.media))

    if author_id:
        query = query.where(Post.author_id == author_id)

    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Post.title.ilike(search_term),
                Post.content.ilike(search_term)
            )
        )

    query = query.order_by(Post.created_at.desc())

    query = query.offset(skip).limit(limit)

    result = await session.execute(query)
    return list(result.scalars().all())


async def get_user_posts(session: AsyncSession, user_id: UUID, skip: int = 0, limit: int = 20) -> List[Post]:
    query = (select(Post).where(Post.author_id == user_id, Post.is_deleted ==
             False).options(selectinload(Post.media)).order_by(Post.created_at.desc()).offset(skip).limit(limit))

    result = await session.execute(query)
    return list(result.scalars().all())


async def update_post(session: AsyncSession, post_id: UUID, title: Optional[str] = None, content: Optional[str] = None) -> Optional[Post]:
    update_data = {}

    if title is not None:
        update_data["title"] = title
    if content is not None:
        update_data["content"] = content

    if not update_data:
        return await get_post_by_id(session, post_id)

    update_data["updated_at"] = datetime.utcnow()

    query = (update(Post).where(Post.id == post_id).values(
        **update_data).returning(Post))

    result = await session.execute(query)
    await session.flush()

    post = result.scalar_one_or_none()
    if post:
        await session.refresh(post, attribute_names=["media"])
    
    return post


async def delete_post(session: AsyncSession, post_id: UUID) -> bool:
    query = (update(Post).where(Post.id == post_id, Post.is_deleted ==
             False).values(is_deleted=True, updated_at=datetime.utcnow()))

    result = await session.execute(query)
    await session.flush()

    return result.rowcount > 0


async def restore_post(session: AsyncSession, post_id: UUID) -> Optional[Post]:
    query = (update(Post).where(Post.id == post_id, Post.is_deleted == True).values(
        is_deleted=False, updated_at=datetime.utcnow()).returning(Post))

    result = await session.execute(query)
    await session.flush()

    return result.scalar_one_or_none()


async def check_post_author(session: AsyncSession, post_id: UUID, author_id: UUID) -> bool:
    query = select(Post).where(Post.id == post_id,
                               Post.author_id == author_id, Post.is_deleted == False)
    result = await session.execute(query)
    return result.scalar_one_or_none() is not None
