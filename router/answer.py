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
    tags=["answer"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/answer/{answer_id}")
async def get_answer(answer_id: int, token: str, db: Session = Depends(get_db)):
    await verify_token(token)
    db_answer = db.get(PostComment, answer_id)
    if db_answer == None or db_answer.comment_type != "answer":
        raise HTTPException(status_code=404, detail="Answer not found")
    return db_answer

@router.get("/post/{post_id}/answers")
async def get_answers_on_post(post_id: int, token: str, db: Session = Depends(get_db)):
    await verify_token(token)
    db_post = db.get(Post, post_id)
    if db_post == None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post.answers

@router.post("/post/{post_id}/answer/create")
async def create_answer_on_post(token: str, post_id: int, comment: str, db: Session = Depends(get_db)):
    user = await verify_token(token)
    db_post = db.get(Post, post_id)
    if db_post == None:
        raise HTTPException(status_code=404, detail="Post not found")
    newAnswer = PostComment(
        author_id=user.get('id'), 
        post_id=post_id, 
        comment=comment, 
        created=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        comment_type="answer")
    db.add(newAnswer)
    db.commit()
    return newAnswer

@router.post("/answer/{answer_id}/edit")
async def edit_answer(token: str, answer_id: int, comment: str, db: Session = Depends(get_db)):
    user = await verify_token(token)
    db_answer = db.get(PostComment, answer_id)
    if db_answer == None or db_answer.comment_type != "answer":
        raise HTTPException(status_code=404, detail="Answer not found")
    if db_answer.author_id != user.id:
        raise HTTPException(status_code=401, detail="You are not the author of this answer")
    newAnswer = PostComment(
        author_id=user.get('id'), 
        post_id=id, 
        comment=comment, 
        created=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        comment_type="answer")
    db.merge(newAnswer)
    db.commit()
    return newAnswer

@router.delete("/answer/{answer_id}/delete")
async def delete_comment(token: str, answer_id: int, db: Session = Depends(get_db)):
    user = await verify_token(token)
    db_answer = db.get(PostComment, answer_id)
    if db_answer == None or db_answer.comment_type != "answer":
        raise HTTPException(status_code=404, detail="Answer not found")
    if db_answer.author != user.id:
        raise HTTPException(status_code=401, detail="You are not the author of this answer")
    return {"message": "Answer deleted"}




