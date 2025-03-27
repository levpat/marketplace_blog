from sqlalchemy import func, String
from sqlalchemy.types import TypeDecorator


class SearchableText(TypeDecorator):
    impl = String
    cache_ok = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def column_expression(self, col):
        return func.to_tsvector('english', col)
