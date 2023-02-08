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
    prefix="/comment",
    tags=["comment"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/post/{post_id}")
async def getComments(post_id: int, token: str, db: Session = Depends(get_db)):
    await verify_token(token)
    comments = db.query(PostComment).filter(PostComment.post_id == post_id).all()
    return comments

@router.get("/comment/{id}")
async def getComment(id: int, token: str, db: Session = Depends(get_db)):
    await verify_token(token)
    comment = db.query(PostComment).filter(PostComment.id == id).first()
    return comment

@router.get("/subcomments/{id}}")
async def getComments(id: int, token: str, db: Session = Depends(get_db)):
    await verify_token(token)
    comment = db.query(PostComment).filter(PostComment.id == id).first()
    return comment.sub_comments

class NewPostComment(BaseModel):
    post_id: int
    comment: str
    post_comment_id: Optional[int] = None

@router.post("/comment/")
async def createComment(comment: NewPostComment, token: str, db: Session = Depends(get_db)):
    user = await verify_token(token)
    db_comment = PostComment(
        post_id=comment.post_id,
        comment=comment.comment,
        post_comment_id=comment.post_comment_id,
        author_id=user.get('id'),
        created=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

# !!! figure out cascade delete
@router.delete("/comment/{id}")
async def deleteComment(id: int, token: str, db: Session = Depends(get_db)):
    user = await verify_token(token)
    db_comment = db.query(PostComment).filter(PostComment.id == id).first()
    if db_comment.author_id != user.get('id'):
        raise HTTPException(status_code=401, detail="You are not the author of this comment")
    db.delete(db_comment)
    db.commit()
    return db_comment

