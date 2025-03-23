from functools import wraps

from src.posts.schemas import PostPaginator


def pagination(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        limit = kwargs["limit"] or 10
        offset = kwargs["offset"] or 0
        all_items = func(*args, **kwargs)
        total_items = len(all_items)
        pagination_items = list(all_items)[offset: offset + limit]
        return PostPaginator(items=pagination_items, total=total_items, offset=offset, limit=limit)

    return wrapper
