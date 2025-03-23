from fastapi import HTTPException, status

from sqlalchemy import insert

from src.posts.models import Post


class PostManager:

    @staticmethod
    async def create_post(db, create_post):
        try:
            await db.execute(insert(Post).values(
                title=create_post.title,
                text=create_post.text,
                category=create_post.category,
                image_url=create_post.image
            ))

            await db.commit()

        except Exception as error:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error during creating post: {str(error)}"

            )

        return {
            "status_code": status.HTTP_201_CREATED,
            "transaction": "Success"
        }


pm = PostManager
