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
from router.post import Error400, Error401, Error404, Error500, VoteSchema


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


class VoteResponse(BaseModel):
    status: str = "success"
    code: int = 200
    message: str = "Successfully added vote"

class UndoVoteResponse(BaseModel):
    status: str = "success"
    code: int = 200
    message: str = "Successfully removed vote"

class VotesResponse(BaseModel):
    status: str = "success"
    votes: list[VoteSchema] = [VoteSchema()]
    code: int = 200
    message: str = "Successfully retrieved votes"

# class VoteSchema(BaseModel):
#     vote: int = 1
#     post_id: int = 1
#     user_id: int = 1



@router.get("/post/{post_id}/votes", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def get_votes_on_post(post_id: int, token: str, db: Session = Depends(get_db)) -> VotesResponse:
    await verify_token(token)
    db_post = db.get(Post, post_id)
    if db_post == None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post.votes

@router.get("/answer/{answer_id}/votes", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def get_votes_on_answer(answer_id: int, token: str, db: Session = Depends(get_db)) -> VotesResponse:
    await verify_token(token)
    db_answer = db.get(PostComment, answer_id)
    if db_answer == None or db_answer.comment_type != "answer":
        raise HTTPException(status_code=404, detail="Answer not found")
    return db_answer.votes

@router.get("/comment/{comment_id}/votes", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def get_votes_on_comment(comment_id: int, token: str, db: Session = Depends(get_db)) -> VotesResponse:
    await verify_token(token)
    db_comment = db.get(PostComment, comment_id)
    if db_comment == None or db_comment.comment_type != "comment":
        raise HTTPException(status_code=404, detail="Comment not found")
    return db_comment.votes

# VOTING HELPERS
async def upvote(id: int, token: str, db: Session, upVote: bool, type: str):
    user = await verify_token(token)
    db_answer = db.get(PostComment, id)
    if db_answer == None or db_answer.comment_type != type:
        raise HTTPException(status_code=404, detail= type + " not found")
    newVote = VotesComment(user_id=user.get('id'), post_comment_id=id, vote=upVote)
    db.merge(newVote)
    db.commit()
    return db.query(VotesComment).filter(VotesComment.post_comment_id == id).all()

async def undo_vote(id: int, token: str, db: Session, undoUpVote: bool, type : str):
    user = await verify_token(token)
    db_answer = db.get(PostComment, id)
    if db_answer == None or db_answer.comment_type != type:
        raise HTTPException(status_code=404, detail=type + " not found")
    db_vote = db.query(VotesComment).filter(VotesComment.user_id == user.get('id'), VotesComment.post_comment_id == id).first()
    if db_vote == None:
        raise HTTPException(status_code=404, detail="Vote not found")
    if db_vote.vote != undoUpVote:
        raise HTTPException(status_code=400, detail=  "Vote is down vote" if undoUpVote else "Vote is up vote")
    db.delete(db_vote)
    db.commit()

# VOTING ON ANSWERS
@router.post("/answer/{answer_id}/upvote", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def upvote_answer(token: str, answer_id: int, db: Session = Depends(get_db)) -> VoteResponse:  
    votes = await upvote(answer_id, token, db, True, 'answer')
    return votes

@router.post("/answer/{answer_id}/downvote", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def upvote_answer(token: str, answer_id: int, db: Session = Depends(get_db)) -> VoteResponse:  
    votes = await upvote(answer_id, token, db, False, 'answer')
    return votes

@router.delete("/answer/{answer_id}/upvote/undo", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def undo_upvote_answer(token: str, answer_id: int, db: Session = Depends(get_db)) -> UndoVoteResponse:  
    undo_vote(answer_id, token, db, True, 'answer')
    return {"message": "Vote undone"}

@router.delete("/answer/{answer_id}/downvote/undo", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def undo_downvote_answer(token: str, answer_id: int, db: Session = Depends(get_db)) -> UndoVoteResponse:
    undo_vote(answer_id, token, db, False, 'answer')
    return {"message": "Vote undone"}

# VOTING ON COMMENTS
@router.post("/comment/{id}/upvote", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def upvote_comment(id: int, token: str, db: Session = Depends(get_db)) -> VoteResponse:
    votes = await upvote(id, token, db, True, 'comment')
    return votes

@router.post("/comment/{id}/downvote", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def downvote_comment(id: int, token: str, db: Session = Depends(get_db)) -> VoteResponse:
    votes = await upvote(id, token, db, False, 'comment')
    return votes

@router.delete("/comment/{id}/upvote/undo", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def undo_upvote_comment(id: int, token: str, db: Session = Depends(get_db)) -> UndoVoteResponse:
    await undo_vote(id, token, db, True, 'comment')
    return { "message": "Undo up vote comment" }

@router.delete("/comment/{id}/downvote/undo", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def undo_downvote_comment(id: int, token: str, db: Session = Depends(get_db)) -> UndoVoteResponse:
    await undo_vote(id, token, db, False, 'comment')
    return { "message": "Undo down vote comment" }

# VOTING ON POSTS
async def vote_post(id: int, token: str, db: Session, upVote: bool):
    user = await verify_token(token)
    db_post = db.get(Post, id)
    if db_post == None:
        raise HTTPException(status_code=404, detail="Post not found")
    newVote = VotesPost(user_id=user.get('id'), post_id=id, vote=upVote)
    db.merge(newVote)
    db.commit()
    return db.query(VotesPost).filter(VotesPost.post_id == id).all()

async def undo_vote_post(id: int, token: str, db: Session, undoUpVote: bool):
    user = await verify_token(token)
    db_post = db.get(Post, id)
    if db_post == None:
        raise HTTPException(status_code=404, detail="Post not found")
    db_vote = db.query(VotesPost).filter(VotesPost.user_id == user.get('id'), VotesPost.post_id == id).first()
    if db_vote == None:
        raise HTTPException(status_code=404, detail="Vote not found")
    if db_vote.vote != undoUpVote:
        raise HTTPException(status_code=400, detail= "Vote is down vote" if undoUpVote else "Vote is up vote")
    db.delete(db_vote)
    db.commit()
    return db.query(VotesPost).filter(VotesPost.post_id == id).all()

@router.post("/post/{id}/upvote", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def upvote_post(id: int, token: str, db: Session = Depends(get_db)) -> VoteResponse:
    votes = await vote_post(id, token, db, True)
    return votes
    
@router.post("/post/{id}/downvote", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def downvote_post(id: int, token: str, db: Session = Depends(get_db)) -> VoteResponse:
    votes = await vote_post(id, token, db, False)
    return votes

@router.delete("/post/{id}/upvote/undo", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def undo_upvote_post(id: int, token: str, db: Session = Depends(get_db)) -> UndoVoteResponse:
    votes = await undo_vote_post(id, token, db, True)
    return votes

@router.delete("/post/{id}/downvote/undo", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def undo_downvote_post(id: int, token: str, db: Session = Depends(get_db)) -> UndoVoteResponse:
    votes = await undo_vote_post(id, token, db, False)
    return votes




