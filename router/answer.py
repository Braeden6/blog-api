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
    tags=["answer"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class AnswerSchema(BaseModel):
    id: int = 1
    comment: str = "This is a comment"
    created: datetime = datetime.now()
    updated: Optional[datetime] = None
    comment_type: str = "comment"
    author_id: int = 1
    post_comment_id: Optional[int] = None
    post_id: int = 1

class AnswersResponse(BaseModel):
    status: str = "success"
    answers: list[AnswerSchema] = [AnswerSchema()]
    code: int = 200
    message: str = "Successfully retrieved answers"

class AnswerResponse(BaseModel):
    status: str = "success"
    answer: AnswerSchema = AnswerSchema()
    code: int = 200
    message: str = "Successfully retrieved answer"

class CreateAnswerSchema(BaseModel):
    token: str
    comment: str


class DeleteAnswerResponse(BaseModel):
    status: str = "success"
    code: int = 200
    message: str = "Successfully deleted answer"


@router.get("/answer/{answer_id}", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def get_answer(answer_id: int, token: str, db: Session = Depends(get_db)) -> AnswerResponse:
    await verify_token(token)
    db_answer = db.get(PostComment, answer_id)
    if db_answer == None or db_answer.comment_type != "answer":
        raise HTTPException(status_code=404, detail="Answer not found")
    return db_answer

@router.get("/post/{post_id}/answers", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def get_answers_on_post(post_id: int, token: str, db: Session = Depends(get_db)) -> AnswersResponse:
    await verify_token(token)
    db_post = db.get(Post, post_id)
    if db_post == None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post.answers

@router.post("/post/{post_id}/answer/create", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def create_answer_on_post(post_id: int, body: CreateAnswerSchema, db: Session = Depends(get_db)) -> AnswerResponse:
    user = await verify_token(body.token)
    db_post = db.get(Post, post_id)
    if db_post == None:
        raise HTTPException(status_code=404, detail="Post not found")
    newAnswer = PostComment(
        author_id=user.get('id'), 
        post_id=post_id, 
        comment=body.comment, 
        created=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        comment_type="answer")
    db.add(newAnswer)
    db.commit()
    return newAnswer

@router.post("/answer/{answer_id}/edit", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def edit_answer(answer_id: int, body: CreateAnswerSchema, db: Session = Depends(get_db)) -> AnswerResponse:
    user = await verify_token(body.token)
    db_answer = db.get(PostComment, answer_id)
    if db_answer == None or db_answer.comment_type != "answer":
        raise HTTPException(status_code=404, detail="Answer not found")
    if db_answer.author_id != user.id:
        raise HTTPException(status_code=401, detail="You are not the author of this answer")
    newAnswer = PostComment(
        author_id=user.get('id'), 
        post_id=id, 
        comment=body.comment, 
        created=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        comment_type="answer")
    db.merge(newAnswer)
    db.commit()
    return newAnswer

@router.delete("/answer/{answer_id}/delete", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def delete_comment(token: str, answer_id: int, db: Session = Depends(get_db)) -> DeleteAnswerResponse:
    user = await verify_token(token)
    db_answer = db.get(PostComment, answer_id)
    if db_answer == None or db_answer.comment_type != "answer":
        raise HTTPException(status_code=404, detail="Answer not found")
    if db_answer.author != user.id:
        raise HTTPException(status_code=401, detail="You are not the author of this answer")
    return {"message": "Answer deleted"}




