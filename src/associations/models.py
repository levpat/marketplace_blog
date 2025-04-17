from sqlalchemy import Column, ForeignKey, Integer, UUID
from src.backend.db import Base


class PostCategories(Base):
    __tablename__ = "post_categories"

    id = Column(Integer, primary_key=True)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
