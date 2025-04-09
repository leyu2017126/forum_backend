# app/services/post_service.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.post import Post
from app.models.user import User


class PostService:
    def __init__(self, db: Session, current_user: User = None):
        self.db = db
        self.current_user = current_user

    def get_post(self, post_id: int) -> Post:
        post = self.db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return post

    def check_post_owner_or_admin(self, post: Post):
        if post.user_id != self.current_user.id and not self.current_user.is_admin:
            raise HTTPException(status_code=403, detail="Not authorized")

    def create_post(self, title: str, content: str) -> Post:
        new_post = Post(title=title, content=content, user_id=self.current_user.id)

        try:
            self.db.add(new_post)
            self.db.commit()
            self.db.refresh(new_post)
        except Exception:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to create post")

        return new_post

    def update_post(self, post_id: int, title: str, content: str) -> Post:
        post = self.get_post(post_id)
        self.check_post_owner_or_admin(post)

        post.title = title
        post.content = content

        try:
            self.db.commit()
            self.db.refresh(post)
        except Exception:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to update post")

        return post

    def delete_post(self, post_id: int):
        post = self.get_post(post_id)
        self.check_post_owner_or_admin(post)

        try:
            self.db.delete(post)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to delete post")
