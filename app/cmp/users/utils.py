from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from uuid import UUID
from typing import Optional, Dict, Any
import bcrypt

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'),hashed_password.encode('utf-8'))


def create_access_token(user_id: UUID) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access"
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(user_id: UUID) -> str:
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh"
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def verify_token(token: str, token_type: str = "access") -> Optional[UUID]:
    payload = decode_token(token)
    
    if not payload:
        return None
    
    if payload.get("type") != token_type:
        return None
    
    exp = payload.get("exp")
    if exp and datetime.utcnow().timestamp() > exp:
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    try:
        return UUID(user_id)
    except ValueError:
        return None


def is_token_expired(token: str) -> bool:
    payload = decode_token(token)
    if not payload:
        return True
    
    exp = payload.get("exp")
    if not exp:
        return True
    
    return datetime.utcnow().timestamp() > exp


def get_token_expiration(token: str) -> Optional[datetime]:
    payload = decode_token(token)
    if not payload:
        return None
    
    exp = payload.get("exp")
    if not exp:
        return None
    
    return datetime.fromtimestamp(exp)


def get_token_type(token: str) -> Optional[str]:
    payload = decode_token(token)
    if not payload:
        return None
    
    return payload.get("type")