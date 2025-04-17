from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from src.associations.models import PostCategories
from src.backend.db import Base


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True)

    posts = relationship('Post', secondary=PostCategories.__table__, back_populates='category')
