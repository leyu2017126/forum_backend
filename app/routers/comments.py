# app/routers/comment.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.comment import Comment
from app.models.post import Post
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentUpdate, CommentOut
from app.utils.security import get_current_user
from app.services.comment_service import CommentService

router = APIRouter(tags=["Comments"])


@router.post("/posts/{post_id}/comments",
             response_model=CommentOut,
             status_code=status.HTTP_201_CREATED,
             summary="Create a new comment",
             responses={
                 404: {"description": "Post or parent comment not found"},
                 403: {"description": "Not authorized"}
             })
async def create_comment(
        post_id: int,
        comment: CommentCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Create a new comment (supports nested comments)"""
    service = CommentService(db, current_user)
    new_comment = service.create_comment(post_id, comment.content, comment.parent_id)
    return new_comment


@router.get("/posts/{post_id}/comments",
            response_model=List[CommentOut],
            summary="Get post comments",
            responses={404: {"description": "Post not found"}})
async def read_comments(
        post_id: int,
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    """Get paginated comments for a post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return db.query(Comment) \
        .options(joinedload(Comment.author)) \
        .filter(Comment.post_id == post_id) \
        .offset(skip) \
        .limit(limit) \
        .all()


@router.get("/comments/{comment_id}",
            response_model=CommentOut,
            summary="Get comment by ID",
            responses={404: {"description": "Comment not found"}})
async def read_comment(
        comment_id: int,
        db: Session = Depends(get_db)
):
    """Get a single comment with replies"""
    comment = db.query(Comment) \
        .options(joinedload(Comment.author)) \
        .filter(Comment.id == comment_id) \
        .first()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    return comment


@router.put("/comments/{comment_id}",
            response_model=CommentOut,
            summary="Update a comment",
            responses={
                403: {"description": "Not authorized to update"},
                404: {"description": "Comment not found"}
            })
async def update_comment(
        comment_id: int,
        comment: CommentUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Update comment content (must be comment owner)"""
    service = CommentService(db, current_user)
    updated_comment = service.update_comment(comment_id, comment.content)
    return updated_comment


@router.delete("/comments/{comment_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete a comment",
               responses={
                   403: {"description": "Not authorized to delete"},
                   404: {"description": "Comment not found"}
               })
async def delete_comment(
        comment_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Delete a comment (must be comment owner or admin)"""
    service = CommentService(db, current_user)
    service.delete_comment(comment_id)
    return
