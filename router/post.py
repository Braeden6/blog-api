from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel
from core.models.database import SessionLocal, Base, engine
from core.models.post import Post, Tag, PostComment, VotesComment, VotesPost
from sqlalchemy.orm import Session
from core.schemas.error import Error400, Error401, Error404, Error500
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
    token: str = "ebc.edf.123"
    title: str = "My new post"
    description: Optional[str] = None
    post_content: object = [ { "type": "image" , "url" : "https://example.com/image.png"}, { "type": "text" , "text" : "This is a text"}]
    technology_ids: Optional[list] = ["Python", "VScode"]

class NewPostResponse(BaseModel):
    status: str = "success"
    post_id: int = 1
    code: int = 200
    message: str = "Successfully created post"

class SkillTag(BaseModel):
    id: int = 1
    name: str = "Python"
    parent_id: Optional[int] = None

class NewPostInformationResponse(BaseModel):
    status: str = "success"
    tags: list[SkillTag] = [ SkillTag()]
    code: int = 200
    message: str = "Successfully retrieved post information"

class DeletePost(BaseModel):
    token : str = "ebc.edf.123"

class DeletePostResponse(BaseModel):
    status: str = "success"
    code: int = 200
    message: str = "Successfully deleted post"

# TODO:
# verify post_content is the right structure 
@router.post("/post/create", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def create_post(post: NewPost, db: Session = Depends(get_db)) -> NewPostResponse:
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
        created=datetime.now(),
        tags=tags,
        version=0)
    db.add(db_post)
    db.commit()
    return NewPostResponse(post_id=db_post.id)

@router.get("/post/create", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def get_post_create_information(token: str, db: Session = Depends(get_db)) -> NewPostInformationResponse:
    await verify_token(token)
    tags = db.query(Tag).all()
    result: SkillTag = []
    for tag in tags:
        result.append(SkillTag(id=tag.id, name=tag.name, parent_id=tag.parent_id))
    return NewPostInformationResponse(tags=result)

# https://api.stackexchange.com/docs?tab=category#docs
@router.post("/post/{id}/edit", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def edit_post(id: int, newPost: NewPost, db: Session = Depends(get_db)) -> NewPostResponse:
    user = await verify_token(newPost.token)
    db_post = db.query(Post).filter(Post.id == id).first()
    if db_post == None:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.author_id != user.get('id'):
        raise HTTPException(status_code=401, detail="You are not the author of this post")

    db_post.title = newPost.title
    db_post.post_content = newPost.post_content
    db_post.slug = newPost.title.replace(" ", "-").lower()
    db_post.tags =  db.query(Tag).filter(Tag.id.in_(newPost.technology_ids)).all()
    db_post.updated = datetime.now()
    db_post.version += 1
    db.commit()
    return NewPostResponse(post_id=id)

@router.delete("/post/{id}/delete", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def delete_post(id: int, deletePost: DeletePost, db: Session = Depends(get_db)) -> DeletePostResponse:
    user = await verify_token(deletePost.token)
    db_post = db.query(Post).filter(Post.id == id).first()
    if db_post == None:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.author_id != user.get('id'):
        raise HTTPException(status_code=401, detail="You are not the author of this post")
    db.delete(db_post)
    db.commit()
    return DeletePostResponse()

@router.get("/posts", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def get_all_posts(token: str, db: Session = Depends(get_db)):
    await verify_token(token)
    return db.query(Post).all()

@router.get("/post/{slug}", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def get_post(slug: str, token: str, db: Session = Depends(get_db)):
    await verify_token(token)
    db_post = db.query(Post).filter(Post.slug == slug).first()
    if db_post == None:
        raise HTTPException(status_code=404, detail="Post not found") 
    return db_post

@router.get("/post/id/{id}", responses={400: { "model" : Error400 }, 401: { "model" : Error401 }, 404: { "model" : Error404 }, 422: {"model": Error400}, 500: { "model" : Error500 }})
async def get_post(id: int, token: str, db: Session = Depends(get_db)):
    await verify_token(token)
    db_post = db.query(Post).filter(Post.id == id).first()
    if db_post == None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post