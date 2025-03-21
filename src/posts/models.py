from datetime import datetime, timezone
import uuid

from sqlalchemy import Column, String, UUID, DateTime

from src.backend.db import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(String)
    slug = Column(String, unique=True, index=True)
    text = Column(String(100))
    category = Column(String)
    image_url = Column(String)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
