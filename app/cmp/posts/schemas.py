from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class PostMediaBase(BaseModel):
    file_url: str
    file_type: str
    mime_type: str
    file_size: int
    file_name: str
    width: Optional[int] = None
    height: Optional[int] = None
    is_primary: bool = False
    order: int = 0


class PostMediaCreate(PostMediaBase):
    post_id: UUID


class PostMediaResponse(PostMediaBase):
    id: UUID
    post_id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)


class PostCreate(PostBase):
    media: Optional[List[PostMediaCreate]] = Field(default_factory=list)
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)


class PostResponse(BaseModel):
    id: UUID
    title: str
    content: str
    author_id: UUID
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    media: List[PostMediaResponse] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)