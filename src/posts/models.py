from datetime import datetime, timezone
import uuid

from sqlalchemy import Column, String, UUID, Text, TIMESTAMP

from src.backend.db import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    category = Column(String)
    image_url = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.now(timezone.utc))
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=datetime.now(timezone.utc))
