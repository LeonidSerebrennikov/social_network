from typing import Optional
from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.redis_client import redis_client

from app.cmp.users.models import User
from app.cmp.users.schemas import UserCreate


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    query = select(User).where(User.email == email)
    result = await session.execute(query)
    return result.scalar_one_or_none()

async def has_user_by_email(session: AsyncSession, email: str) -> bool: 
    query = select(select(User).where(User.email == email).exists())
    result = await session.execute(query) 
    return result.scalar_one()

async def get_user_by_username(session: AsyncSession, username: str) -> Optional[User]:
    query = select(User).where(User.username == username)
    result = await session.execute(query)
    return result.scalar_one_or_none()

async def has_user_by_username(session: AsyncSession,username: str) -> bool: 
    query = select(select(User).where(User.username == username).exists())
    result = await session.execute(query) 
    return result.scalar_one()

async def get_user_by_id(session: AsyncSession, id: str) -> Optional[User]:
    query = select(User).where(User.id == id)
    result = await session.execute(query)
    return result.scalar_one_or_none()

async def create_user(session: AsyncSession, user_data: UserCreate, hashed_password: str) -> User:
    user_dict = user_data.model_dump(exclude={"password", "password_confirm"})
    user_dict["hashed_password"] = hashed_password
    user = User(**user_dict)
    
    session.add(user)
    await session.flush()
    await session.refresh(user)
    
    return user

async def update_last_login(session: AsyncSession, user_id: UUID) -> None:
    from datetime import datetime
    
    query = (
        update(User)
        .where(User.id == user_id)
        .values(last_login=datetime.utcnow())
    )
    await session.execute(query)
    await session.flush()
