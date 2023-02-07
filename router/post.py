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
    prefix="/post",
    tags=["post"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class NewPost(BaseModel):
    token: str
    title: str
    description: Optional[str] = None
    post_content: object
    technology_ids: Optional[list] = None


@router.get("/create")
async def postInformation(token: str, db: Session = Depends(get_db)):
    await verify_token(token)
    return db.query(Tag).all()



# TODO:
# verify post_content is the right structure 
@router.post("/create")
async def createPost(post: NewPost, db: Session = Depends(get_db)):
    user = await verify_token(post.token)

    postCheck = db.query(Post).filter(Post.title == post.title).first()
    if postCheck != None:
        raise HTTPException(status_code=400, detail="Post with this title already exists")

    slug = post.title.replace(" ", "-").lower()

    tags = db.query(Tag).filter(Tag.id.in_(post.technology_ids)).all()

    db_post = Post(
        title=post.title, 
        post_content=post.post_content, 
        author_id=user.get('id'),
        slug=slug,
        created=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        tags=tags)
    db.add(db_post)
    db.commit()
    return db_post

# TODO:
# write function to get all tags, comments, and up votes for everything related to post with give id

@router.get("/id/{id}")
async def get_post(id: int, db: Session = Depends(get_db)):
    db_post = db.get(Post, id)
    if db_post == None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post

# https://api.stackexchange.com/docs?tab=category#docs


@router.post("/{id}/edit")
async def edit_post(id: int, token: str, db: Session = Depends(get_db)):
    return { "message": "Edit post not implemented yet" }

@router.post("/{id}/delete")
async def delete_post(id: int, token: str, db: Session = Depends(get_db)):
    return { "message": "Delete post not implemented yet" }

async def vote_post(id: int, token: str, db: Session, upVote: bool):
    user = await verify_token(token)
    db_post = db.get(Post, id)
    if db_post == None:
        raise HTTPException(status_code=404, detail="Post not found")
    # fine to change vote
    #db_vote = db.query(VotesPost).filter(VotesPost.user_id == user.get('id'), VotesPost.post_id == id).first()
    #if db_vote != None:
    #    raise HTTPException(status_code=400, detail="Vote already exists")
    print(user)
    newVote = VotesPost(user_id=user.get('id'), post_id=id, vote=upVote)
    db.merge(newVote)
    db.commit()
    return db.query(VotesPost).filter(VotesPost.post_id == id).all()

@router.post("/{id}/upvote")
async def upvote_post(id: int, token: str, db: Session = Depends(get_db)):
    votes = await vote_post(id, token, db, True)
    return votes
@router.post("/{id}/downvote")
async def downvote_post(id: int, token: str, db: Session = Depends(get_db)):
    votes = await vote_post(id, token, db, False)
    return votes

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

@router.post("/{id}/upvote/undo")
async def undo_upvote_post(id: int, token: str, db: Session = Depends(get_db)):
    votes = await undo_vote_post(id, token, db, True)
    return votes

@router.post("/{id}/downvote/undo")
async def undo_downvote_post(id: int, token: str, db: Session = Depends(get_db)):
    votes = await undo_vote_post(id, token, db, False)
    return votes

# VOTING ON COMMENTS
async def vote_comment(id: int, token: str, db: Session, upVote: bool):
    user = await verify_token(token)
    db_comment = db.get(PostComment, id)
    if db_comment == None:
        raise HTTPException(status_code=404, detail="Comment not found")
    # fine to change vote
    #db_vote = db.query(VotesComment).filter(VotesComment.user_id == user.get('id'), VotesComment.post_comment_id == id).first()
    #if db_vote != None:
    #    raise HTTPException(status_code=400, detail="Vote already exists")
    newVote = VotesComment(user_id=user.get('id'), post_comment_id=id, vote=upVote)
    db.merge(newVote)
    db.commit()
    return db.query(VotesComment).filter(VotesComment.post_comment_id == id).all()

@router.post("/comment/{id}/upvote")
async def upvote_comment(id: int, token: str, db: Session = Depends(get_db)):
    votes = await vote_comment(id, token, db, True)
    return votes

@router.post("/comment/{id}/downvote")
async def downvote_comment(id: int, token: str, db: Session = Depends(get_db)):
    votes = await vote_comment(id, token, db, False)
    return votes

async def undo_vote_comment(id: int, token: str, db: Session, undoUpVote: bool):
    user = await verify_token(token)
    db_comment = db.get(PostComment, id)
    if db_comment == None:
        raise HTTPException(status_code=404, detail="Comment not found")
    db_vote = db.query(VotesComment).filter(VotesComment.user_id == user.get('id'), VotesComment.post_comment_id == id).first()
    if db_vote == None:
        raise HTTPException(status_code=404, detail="Vote not found")
    if db_vote.vote != undoUpVote:
        raise HTTPException(status_code=400, detail=  "Vote is down vote" if undoUpVote else "Vote is up vote")
    db.delete(db_vote)
    db.commit()

@router.post("/comment/{id}/upvote/undo")
async def undo_upvote_comment(id: int, token: str, db: Session = Depends(get_db)):
    await undo_vote_comment(id, token, db, True)
    return { "message": "Undo up vote comment" }

@router.post("/comment/{id}/downvote/undo")
async def undo_downvote_comment(id: int, token: str, db: Session = Depends(get_db)):
    await undo_vote_comment(id, token, db, False)
    return { "message": "Undo down vote comment" }

# COMMENTS
@router.post("/comment/{id}/edit")
async def edit_comment(id: int, token: str, newText: str, db: Session = Depends(get_db)):
    user = await verify_token(token)
    db_comment = db.get(PostComment, id)
    if db_comment == None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment.author_id != user.get('id'):
        raise HTTPException(status_code=401, detail="Unauthorized")
    db_comment.updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db_comment.comment = newText
    db.commit()
    return { "message": "Edit comment" }

@router.post("/comment/{id}/delete")
async def delete_comment(id: int, token: str, db: Session = Depends(get_db)):
    user = await verify_token(token)
    db_comment = db.get(PostComment, id)
    if db_comment == None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment.author_id != user.get('id'):
        raise HTTPException(status_code=401, detail="Unauthorized")
    db.delete(db_comment)
    db.commit()
    return { "message": "Delete comment" }

# comments on comment
@router.post("/comment/{id}/comment")
async def create_comment_on_comment(id: int, token: str, comment: str, db: Session = Depends(get_db)):
    user = await verify_token(token)
    db_comment = db.get(PostComment, id)
    if db_comment == None:
        raise HTTPException(status_code=404, detail="Comment not found")
    newComment = PostComment(author_id=user.get('id'), post_id=db_comment.post_id, comment=comment, post_comment_id=id, created=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    db.add(newComment)
    db.commit()
    return { "message": "Created sub comment" }

# comments on post
@router.post("/{id}/comment")
async def create_comment_on_post(id: int, token: str, comment: str, db: Session = Depends(get_db)):
    user = await verify_token(token)
    db_post = db.get(Post, id)
    if db_post == None:
        raise HTTPException(status_code=404, detail="Post not found")
    newComment = PostComment(author_id=user.get('id'), post_id=id, comment=comment, created=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    db.add(newComment)
    db.commit()
    return { "message": "Created comment" }



@router.get("/{slug}")
async def get_post(slug: str, token: str, db: Session = Depends(get_db)):
    await verify_token(token)
    db_post = db.query(Post).filter(Post.slug == slug).first()
    if db_post == None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post

