from datetime import datetime, timezone
import uuid

from sqlalchemy import Column, String, Integer, UUID, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.backend.db import Base
from src.associations.models import PostCategories


class Post(Base):
    __table_name__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    text = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    image_url = Column(String)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.now(timezone.utc))

    category = relationship('Category', secondary=PostCategories.__table__ ,back_populates='posts')


class DeletedPost(Base):
    __table_name__ = "deleted_posts"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    text = Column(String, nullable=False)
    category_id = Column(Integer)
    image_url = Column(String)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    deleted_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
