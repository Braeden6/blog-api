from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel
from core.models.database import SessionLocal, Base, engine
from core.models.post import Post, Tag, PostComment, VotesComment, VotesPost
from sqlalchemy.orm import Session
from router.login import verify_token
import router.answer as answer
import router.comment as comment


Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/blog",
    tags=["vote"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/post/{post_id}/votes")
async def get_votes_on_post(post_id: int, token: str, db: Session = Depends(get_db)):
    await verify_token(token)
    db_post = db.get(Post, post_id)
    if db_post == None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post.votes

@router.get("/answer/{answer_id}/votes")
async def get_votes_on_answer(answer_id: int, token: str, db: Session = Depends(get_db)):
    await verify_token(token)
    db_answer = db.get(PostComment, answer_id)
    if db_answer == None or db_answer.comment_type != "answer":
        raise HTTPException(status_code=404, detail="Answer not found")
    return db_answer.votes

@router.get("/comment/{comment_id}/votes")
async def get_votes_on_comment(comment_id: int, token: str, db: Session = Depends(get_db)):
    await verify_token(token)
    db_comment = db.get(PostComment, comment_id)
    if db_comment == None or db_comment.comment_type != "comment":
        raise HTTPException(status_code=404, detail="Comment not found")
    return db_comment.votes
