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


async def vote_answer(id: int, token: str, db: Session, upVote: bool):
    user = await verify_token(token)
    db_answer = db.get(PostComment, id)
    if db_answer == None or db_answer.comment_type != "answer":
        raise HTTPException(status_code=404, detail="Answer not found")
    newVote = VotesComment(user_id=user.get('id'), post_comment_id=id, vote=upVote)
    db.merge(newVote)
    db.commit()
    return db.query(VotesComment).filter(VotesComment.post_comment_id == id).all()



async def undo_vote_answer(id: int, token: str, db: Session, undoUpVote: bool):
    user = await verify_token(token)
    db_answer = db.get(PostComment, id)
    if db_answer == None or db_answer.comment_type != "answer":
        raise HTTPException(status_code=404, detail="Answer not found")
    db_vote = db.query(VotesComment).filter(VotesComment.user_id == user.get('id'), VotesComment.post_comment_id == id).first()
    if db_vote == None:
        raise HTTPException(status_code=404, detail="Vote not found")
    if db_vote.vote != undoUpVote:
        raise HTTPException(status_code=400, detail=  "Vote is down vote" if undoUpVote else "Vote is up vote")
    db.delete(db_vote)
    db.commit()


@router.post("/answer/{answer_id}/upvote")
async def upvote_answer(token: str, answer_id: int, db: Session = Depends(get_db)):  
    votes = await vote_answer(answer_id, token, db, True)
    return votes

@router.post("/answer/{answer_id}/downvote")
async def upvote_answer(token: str, answer_id: int, db: Session = Depends(get_db)):  
    votes = await vote_answer(answer_id, token, db, False)
    return votes

@router.delete("/answer/{answer_id}/upvote/undo")
async def undo_upvote_answer(token: str, answer_id: int, db: Session = Depends(get_db)):  
    undo_vote_answer(answer_id, token, db, True)
    return {"message": "Vote undone"}

@router.delete("/answer/{answer_id}/downvote/undo")
async def undo_downvote_answer(token: str, answer_id: int, db: Session = Depends(get_db)):
    undo_vote_answer(answer_id, token, db, False)
    return {"message": "Vote undone"}

