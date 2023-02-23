from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel
from core.models.database import SessionLocal, Base, engine
from core.models.post import Post, Tag, PostComment, VotesComment, VotesPost
from sqlalchemy.orm import Session
from router.login import verify_token
from router.post import Error400, Error401, Error404, Error500


Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/blog",
    tags=["comment"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Comment(BaseModel):
    id: int = 1
    comment: str = "This is a comment"
    created: datetime = datetime.now()
    comment_type: str = "comment"
    author_id: int = 1
    post_comment_id: Optional[int] = 1
    post_id: int = 1

class NewCommentSchema(BaseModel):
    comment: str
    token: str

class CommentSchema(BaseModel):
    id: int = 1
    comment: str = "This is a comment"
    created: datetime = datetime.now()
    updated: Optional[datetime] = None
    comment_type: str = "comment"
    author_id: int = 1
    post_comment_id: Optional[int] = None
    post_id: int = 1

class CommentResponse(BaseModel):
    status: str = "success"
    comment: CommentSchema = CommentSchema()
    code: int = 200
    message: str = "Successfully retrieved comment"

class CommentsResponse(BaseModel):
    status: str = "success"
    comments: list[CommentSchema] = [CommentSchema()]
    code: int = 200
    message: str = "Successfully retrieved comments"

class ChangeCommentResponse(BaseModel):
    status: str = "success"
    code: int = 200
    message: str = "Successfully deleted/edited comment"

class MergeCommentSchema(BaseModel):
    comment: str
    token: str


@router.get("/comment/{id}", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def get_comment(id: int, token: str, db: Session = Depends(get_db)) -> CommentResponse:
    await verify_token(token)
    comment = db.query(PostComment).filter(PostComment.id == id).first()
    return comment

@router.get("/post/{post_id}/comments", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def get_comments_on_post(post_id: int, token: str, db: Session = Depends(get_db)) -> CommentsResponse:
    await verify_token(token)
    comment = db.query(Post).filter(Post.id == post_id).first()
    return comment.comments

@router.get("/answer/{answer_id}/comments", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def get_comments_on_answer(answer_id: int, token: str, db: Session = Depends(get_db)) -> CommentsResponse:
    await verify_token(token)
    comment = db.query(PostComment).filter(PostComment.id == answer_id).first()
    return comment.comments

@router.post("/post/{post_id}/comment/create", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def create_comment_on_post(post_id: int, newComment: NewCommentSchema, db: Session = Depends(get_db)) -> CommentResponse:
    user = await verify_token(newComment.token)
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post == None:
        raise HTTPException(status_code=404, detail="Post not found")
    db_comment = PostComment(
        post_id=post_id,
        comment=newComment.comment,
        author_id=user.get('id'),
        created=datetime.now(),#.strftime('%Y-%m-%d %H:%M:%S')
        comment_type="comment"
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.post("/answer/{answer_id}/comment/create", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def create_comment_on_answer(answer_id: int, body: MergeCommentSchema, db: Session = Depends(get_db))  -> CommentResponse:
    user = await verify_token(body.token)
    db_answer = db.query(PostComment).filter(PostComment.id == answer_id).first()
    if db_answer == None or db_answer.comment_type != "answer":
        raise HTTPException(status_code=404, detail="Answer not found")
    db_comment = PostComment(
        post_id=db_answer.post_id,
        comment=body.comment,
        author_id=user.get('id'),
        post_comment_id=answer_id,
        created=datetime.now(),#.strftime('%Y-%m-%d %H:%M:%S')
        comment_type="comment"
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.delete("/comment/{id}/delete", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def delete_comment(id: int, token: str, db: Session = Depends(get_db)) -> ChangeCommentResponse:
    user = await verify_token(token)
    db_comment = db.get(PostComment, id)
    if db_comment == None or db_comment.comment_type != "comment":
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment.author_id != user.get('id'):
        raise HTTPException(status_code=401, detail="Unauthorized")
    db.delete(db_comment)
    db.commit()
    return { "message": "Deleted comment" }

# COMMENTS
@router.post("/comment/{id}/edit", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def edit_comment(id: int, body: MergeCommentSchema, db: Session = Depends(get_db)) -> ChangeCommentResponse:
    user = await verify_token(body.token)
    db_comment = db.get(PostComment, id)
    if db_comment == None or db_comment.comment_type != "comment":
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment.author_id != user.get('id'):
        raise HTTPException(status_code=401, detail="Unauthorized")
    db_comment.updated = datetime.now()#.strftime('%Y-%m-%d %H:%M:%S')
    db_comment.comment = body.newText
    db.commit()
    return { "message": "Edit comment" }




