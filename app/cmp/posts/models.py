import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Index, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class Post(Base):
    __tablename__ = 'posts'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    media = relationship("PostMedia", back_populates="post", cascade="all, delete-orphan", lazy="selectin")
    author = relationship("User", back_populates="posts")

    __table_args__ = (
        Index("ix_posts_author_id", "author_id"),
        Index("ix_posts_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Post {self.title[:50]}>"
    
    def __str__(self) -> str:
        return self.title
    

class PostMedia(Base):
    __tablename__ = "post_media"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    
    file_url = Column(String(500), nullable=False)
    file_type = Column(String(20), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_name = Column(String(255), nullable=False)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    
    is_primary = Column(Boolean, default=False, nullable=False)
    order = Column(Integer, default=0, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Связи
    post = relationship("Post", back_populates="media")
    
    def __repr__(self) -> str:
        return f"<PostMedia {self.file_name}>"