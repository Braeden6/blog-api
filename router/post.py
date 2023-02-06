from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel
from core.models.database import SessionLocal, Base, engine
from core.models.post import Post, Tag
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





@router.get("/{slug}")
async def get_post(slug: str, token: str, db: Session = Depends(get_db)):
    #await verify_token(token)

    db_post = db.query(Post).filter(Post.slug == slug).first()
    if db_post == None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post