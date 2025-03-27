from datetime import datetime, timezone
import uuid

from sqlalchemy import Column, String, Integer, UUID, TIMESTAMP, ForeignKey, Index, schema, event
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TSVECTOR

from src.backend.db import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    text = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    image_url = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.now(timezone.utc))
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=datetime.now(timezone.utc))

    category = relationship('Category', back_populates='posts')

    search_vector = Column(TSVECTOR)

    __table_args__ = (
        Index(
            'ix_posts_search',
            'search_vector',
            postgresql_using='gin'
        ),
    )


event.listen(
    Post.__table__,
    'after_create',
    schema.DDL(
        "CREATE TRIGGER tsvector_update "
        "BEFORE INSERT OR UPDATE "
        "ON posts "
        "FOR EACH ROW "
        "EXECUTE PROCEDURE "
        "tsvector_update_trigger(search_vector, 'public.pg_to_tsvector', title, text)"
    )
)
