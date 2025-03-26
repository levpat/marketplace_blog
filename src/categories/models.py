import uuid

from sqlalchemy import Column, UUID, String
from sqlalchemy.orm import relationship

from src.backend.db import Base


class Category(Base):
    __tablename__ = 'categories'

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(String, unique=True, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)

    posts = relationship('Post', back_populates='categories')
