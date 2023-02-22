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
    tags=["notifications"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/notifications/{user_id}")
async def get_user_notifications(user_id: int, token: str, db: Session = Depends(get_db)):
    # await verify_token(token)
    # comment = db.query(PostComment).filter(PostComment.id == id).first()
    return { "all" : []}

class NewNotification(BaseModel):
    user_id: int
    from_id: int
    post_id: int
    url: Optional[str]
    type: str
    note: Optional[str]
    #created: datetime


@router.post("/notifications/{notifications_id}/edit")
async def edit_user_notification(notifications_id: int, token: str, newNote : NewNotification, db: Session = Depends(get_db)):
    # await verify_token(token)
    return { "new notification": {}}



# @router.get("/post/{post_id}/comments")
# async def get_comments_on_post(post_id: int, token: str, db: Session = Depends(get_db)):
#     await verify_token(token)
#     comment = db.query(Post).filter(Post.id == post_id).first()
#     return comment.comments

# @router.get("/answer/{answer_id}/comments")
# async def get_comments_on_answer(answer_id: int, token: str, db: Session = Depends(get_db)):
#     await verify_token(token)
#     comment = db.query(PostComment).filter(PostComment.id == answer_id).first()
#     return comment.comments

# @router.post("/post/{post_id}/comment/create")
# async def create_comment_on_post(post_id: int, comment: str, token: str, db: Session = Depends(get_db)):
#     user = await verify_token(token)
#     db_post = db.query(Post).filter(Post.id == post_id).first()
#     if db_post == None:
#         raise HTTPException(status_code=404, detail="Post not found")
#     db_comment = PostComment(
#         post_id=post_id,
#         comment=comment,
#         author_id=user.get('id'),
#         created=datetime.now(),#.strftime('%Y-%m-%d %H:%M:%S')
#         comment_type="comment"
#     )
#     db.add(db_comment)
#     db.commit()
#     db.refresh(db_comment)
#     return db_comment

# @router.post("/answer/{answer_id}/comment/create")
# async def create_comment_on_answer(answer_id: int, comment: str, token: str, db: Session = Depends(get_db)):
#     user = await verify_token(token)
#     db_answer = db.query(PostComment).filter(PostComment.id == answer_id).first()
#     if db_answer == None or db_answer.comment_type != "answer":
#         raise HTTPException(status_code=404, detail="Answer not found")
#     db_comment = PostComment(
#         post_id=db_answer.post_id,
#         comment=comment,
#         author_id=user.get('id'),
#         post_comment_id=answer_id,
#         created=datetime.now(),#.strftime('%Y-%m-%d %H:%M:%S')
#         comment_type="comment"
#     )
#     db.add(db_comment)
#     db.commit()
#     db.refresh(db_comment)
#     return db_comment

# @router.delete("/comment/{id}/delete")
# async def delete_comment(id: int, token: str, db: Session = Depends(get_db)):
#     user = await verify_token(token)
#     db_comment = db.get(PostComment, id)
#     if db_comment == None or db_comment.comment_type != "comment":
#         raise HTTPException(status_code=404, detail="Comment not found")
#     if db_comment.author_id != user.get('id'):
#         raise HTTPException(status_code=401, detail="Unauthorized")
#     db.delete(db_comment)
#     db.commit()
#     return { "message": "Deleted comment" }

# # COMMENTS
# @router.post("/comment/{id}/edit")
# async def edit_comment(id: int, token: str, newText: str, db: Session = Depends(get_db)):
#     user = await verify_token(token)
#     db_comment = db.get(PostComment, id)
#     if db_comment == None or db_comment.comment_type != "comment":
#         raise HTTPException(status_code=404, detail="Comment not found")
#     if db_comment.author_id != user.get('id'):
#         raise HTTPException(status_code=401, detail="Unauthorized")
#     db_comment.updated = datetime.now()#.strftime('%Y-%m-%d %H:%M:%S')
#     db_comment.comment = newText
#     db.commit()
#     return { "message": "Edit comment" }

# # VOTING ON COMMENTS
# async def vote_comment(id: int, token: str, db: Session, upVote: bool):
#     user = await verify_token(token)
#     db_comment = db.get(PostComment, id)
#     if db_comment == None or db_comment.comment_type != "comment":
#         raise HTTPException(status_code=404, detail="Comment not found")
#     # fine to change vote
#     #db_vote = db.query(VotesComment).filter(VotesComment.user_id == user.get('id'), VotesComment.post_comment_id == id).first()
#     #if db_vote != None:
#     #    raise HTTPException(status_code=400, detail="Vote already exists")
#     newVote = VotesComment(user_id=user.get('id'), post_comment_id=id, vote=upVote)
#     db.merge(newVote)
#     db.commit()
#     return db.query(VotesComment).filter(VotesComment.post_comment_id == id).all()

# @router.post("/comment/{id}/upvote")
# async def upvote_comment(id: int, token: str, db: Session = Depends(get_db)):
#     votes = await vote_comment(id, token, db, True)
#     return votes

# @router.post("/comment/{id}/downvote")
# async def downvote_comment(id: int, token: str, db: Session = Depends(get_db)):
#     votes = await vote_comment(id, token, db, False)
#     return votes

# async def undo_vote_comment(id: int, token: str, db: Session, undoUpVote: bool):
#     user = await verify_token(token)
#     db_comment = db.get(PostComment, id)
#     if db_comment == None:
#         raise HTTPException(status_code=404, detail="Comment not found")
#     db_vote = db.query(VotesComment).filter(VotesComment.user_id == user.get('id'), VotesComment.post_comment_id == id).first()
#     if db_vote == None:
#         raise HTTPException(status_code=404, detail="Vote not found")
#     if db_vote.vote != undoUpVote:
#         raise HTTPException(status_code=400, detail=  "Vote is down vote" if undoUpVote else "Vote is up vote")
#     db.delete(db_vote)
#     db.commit()

# @router.delete("/comment/{id}/upvote/undo")
# async def undo_upvote_comment(id: int, token: str, db: Session = Depends(get_db)):
#     await undo_vote_comment(id, token, db, True)
#     return { "message": "Undo up vote comment" }

# @router.delete("/comment/{id}/downvote/undo")
# async def undo_downvote_comment(id: int, token: str, db: Session = Depends(get_db)):
#     await undo_vote_comment(id, token, db, False)
#     return { "message": "Undo down vote comment" }



