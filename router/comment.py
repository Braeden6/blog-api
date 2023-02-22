from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel
from core.models.database import SessionLocal, Base, engine
from core.models.post import Post, Tag, PostComment, VotesComment, VotesPost
from sqlalchemy.orm import Session
from router.login import verify_token


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

@router.get("/comment/{id}")
async def get_comment(id: int, token: str, db: Session = Depends(get_db)):
    await verify_token(token)
    comment = db.query(PostComment).filter(PostComment.id == id).first()
    return comment

@router.get("/post/{post_id}/comments")
async def get_comments_on_post(post_id: int, token: str, db: Session = Depends(get_db)):
    await verify_token(token)
    comment = db.query(Post).filter(Post.id == post_id).first()
    return comment.comments

@router.get("/answer/{answer_id}/comments")
async def get_comments_on_answer(answer_id: int, token: str, db: Session = Depends(get_db)):
    await verify_token(token)
    comment = db.query(PostComment).filter(PostComment.id == answer_id).first()
    return comment.comments

@router.post("/post/{post_id}/comment/create")
async def create_comment_on_post(post_id: int, comment: str, token: str, db: Session = Depends(get_db)):
    user = await verify_token(token)
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post == None:
        raise HTTPException(status_code=404, detail="Post not found")
    db_comment = PostComment(
        post_id=post_id,
        comment=comment,
        author_id=user.get('id'),
        created=datetime.now(),#.strftime('%Y-%m-%d %H:%M:%S')
        comment_type="comment"
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.post("/answer/{answer_id}/comment/create")
async def create_comment_on_answer(answer_id: int, comment: str, token: str, db: Session = Depends(get_db)):
    user = await verify_token(token)
    db_answer = db.query(PostComment).filter(PostComment.id == answer_id).first()
    if db_answer == None or db_answer.comment_type != "answer":
        raise HTTPException(status_code=404, detail="Answer not found")
    db_comment = PostComment(
        post_id=db_answer.post_id,
        comment=comment,
        author_id=user.get('id'),
        post_comment_id=answer_id,
        created=datetime.now(),#.strftime('%Y-%m-%d %H:%M:%S')
        comment_type="comment"
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.delete("/comment/{id}/delete")
async def delete_comment(id: int, token: str, db: Session = Depends(get_db)):
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
@router.post("/comment/{id}/edit")
async def edit_comment(id: int, token: str, newText: str, db: Session = Depends(get_db)):
    user = await verify_token(token)
    db_comment = db.get(PostComment, id)
    if db_comment == None or db_comment.comment_type != "comment":
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment.author_id != user.get('id'):
        raise HTTPException(status_code=401, detail="Unauthorized")
    db_comment.updated = datetime.now()#.strftime('%Y-%m-%d %H:%M:%S')
    db_comment.comment = newText
    db.commit()
    return { "message": "Edit comment" }




