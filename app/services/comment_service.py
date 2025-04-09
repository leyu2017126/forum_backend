# app/services/comment_service.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.post import Post
from app.models.comment import Comment
from app.models.user import User


class CommentService:
    def __init__(self, db: Session, current_user: User = None):
        self.db = db
        self.current_user = current_user

    def get_post(self, post_id: int) -> Post:
        post = self.db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return post

    def get_comment(self, comment_id: int) -> Comment:
        comment = self.db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        return comment

    def check_comment_owner_or_admin(self, comment: Comment):
        if comment.user_id != self.current_user.id and not self.current_user.is_admin:
            raise HTTPException(status_code=403, detail="Not authorized")

    def create_comment(self, post_id: int, content: str, parent_id: int = None) -> Comment:
        post = self.get_post(post_id)

        # Validate parent comment if provided
        if parent_id:
            parent = self.db.query(Comment).filter(
                Comment.id == parent_id,
                Comment.post_id == post_id
            ).first()
            if not parent:
                raise HTTPException(status_code=404, detail="Parent comment not found in this post")

        new_comment = Comment(content=content, post_id=post_id, user_id=self.current_user.id, parent_id=parent_id)

        try:
            self.db.add(new_comment)
            self.db.commit()
            self.db.refresh(new_comment)
        except Exception:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to create comment")

        return new_comment

    def update_comment(self, comment_id: int, content: str) -> Comment:
        comment = self.get_comment(comment_id)
        self.check_comment_owner_or_admin(comment)

        comment.content = content

        try:
            self.db.commit()
            self.db.refresh(comment)
        except Exception:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to update comment")

        return comment

    def delete_comment(self, comment_id: int):
        comment = self.get_comment(comment_id)
        self.check_comment_owner_or_admin(comment)

        try:
            self.db.delete(comment)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to delete comment")
