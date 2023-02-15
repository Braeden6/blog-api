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

# TODO:
# verify post_content is the right structure 
@router.post("/post/create")
async def create_post(post: NewPost, db: Session = Depends(get_db)):
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
        tags=tags,
        version=0)
    db.add(db_post)
    db.commit()
    return db_post

@router.get("/post/create")
async def get_tags(token: str, db: Session = Depends(get_db)):
    await verify_token(token)
    return db.query(Tag).all()

# https://api.stackexchange.com/docs?tab=category#docs
@router.post("/post/{id}/edit")
async def edit_post(id: int, token: str, db: Session = Depends(get_db)):
    return { "message": "Edit post not implemented yet" }

@router.delete("/post/{id}/delete")
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
    newVote = VotesPost(user_id=user.get('id'), post_id=id, vote=upVote)
    db.merge(newVote)
    db.commit()
    return db.query(VotesPost).filter(VotesPost.post_id == id).all()

@router.post("/post/{id}/upvote")
async def upvote_post(id: int, token: str, db: Session = Depends(get_db)):
    votes = await vote_post(id, token, db, True)
    return votes
    
@router.post("/post/{id}/downvote")
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

@router.delete("/post/{id}/upvote/undo")
async def undo_upvote_post(id: int, token: str, db: Session = Depends(get_db)):
    votes = await undo_vote_post(id, token, db, True)
    return votes

@router.delete("/post/{id}/downvote/undo")
async def undo_downvote_post(id: int, token: str, db: Session = Depends(get_db)):
    votes = await undo_vote_post(id, token, db, False)
    return votes



@router.get("/posts")
async def get_all_posts(token: str, db: Session = Depends(get_db)):
    await verify_token(token)
    return db.query(Post).all()

@router.get("/post/{slug}")
async def get_post(slug: str, token: str, db: Session = Depends(get_db)):
    await verify_token(token)
    db_post = db.query(Post).filter(Post.slug == slug).first()
    if db_post == None:
        raise HTTPException(status_code=404, detail="Post not found") 
    return db_post

@router.get("/post/id/{id}")
async def get_post(id: int, token: str, db: Session = Depends(get_db)):
    await verify_token(token)
    print(id)
    db_post = db.query(Post).filter(Post.id == id).first()
    if db_post == None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post