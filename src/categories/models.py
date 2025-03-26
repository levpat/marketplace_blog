from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from src.backend.db import Base


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, unique=True, index=True, nullable=False)
    title = Column(String, unique=True, nullable=False)

    posts = relationship('Post', back_populates='category')
