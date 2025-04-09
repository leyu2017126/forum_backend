# app/routers/post.py

from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostOut, PostCreate, PostUpdate
from app.services.post_service import PostService
from app.utils.security import get_current_user

router = APIRouter(tags=["Posts"])


@router.post("/posts/",
             response_model=PostOut,
             status_code=status.HTTP_201_CREATED,
             summary="Create a new post",
             responses={
                 401: {"description": "Not authenticated"},
                 403: {"description": "Inactive user"}
             })
async def create_post(
        post: PostCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Create a new post (requires authentication)"""
    service = PostService(db, current_user)
    new_post = service.create_post(post.title, post.content)
    return new_post


@router.get("/posts/",
            response_model=List[PostOut],
            summary="Get all posts",
            responses={200: {"description": "List of all posts"}})
async def read_posts(
        skip: int = 0,
        limit: int = 10,
        db: Session = Depends(get_db)
):
    """Get paginated list of posts"""
    # Validate limit and skip to avoid extremely large queries
    if limit > 100:
        limit = 100
    if skip < 0:
        skip = 0

    return db.query(Post) \
        .options(joinedload(Post.author)) \
        .offset(skip) \
        .limit(limit) \
        .all()


@router.get("/posts/{post_id}",
            response_model=PostOut,
            summary="Get post by ID",
            responses={404: {"description": "Post not found"}})
async def read_post(
        post_id: int,
        db: Session = Depends(get_db)
):
    """Get a single post by its ID"""
    service = PostService(db)
    post = service.get_post(post_id)

    # Update view count
    post.view_count += 1
    db.commit()

    return post


@router.put("/posts/{post_id}",
            response_model=PostOut,
            summary="Update a post",
            responses={
                403: {"description": "Not authorized to update"},
                404: {"description": "Post not found"}
            })
async def update_post(
        post_id: int,
        post: PostUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Update an existing post (must be post owner)"""
    service = PostService(db, current_user)
    updated_post = service.update_post(post_id, post.title, post.content)
    return updated_post


@router.delete("/posts/{post_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete a post",
               responses={
                   403: {"description": "Not authorized to delete"},
                   404: {"description": "Post not found"}
               })
async def delete_post(
        post_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Delete a post (must be post owner or admin)"""
    service = PostService(db, current_user)
    service.delete_post(post_id)
    return {"message": "Post deleted successfully"}
