from datetime import datetime
from fastapi import HTTPException, Request, Depends, APIRouter
from pydantic import BaseModel
from typing import Optional
from core.models.database import engine, SessionLocal, Base
from sqlalchemy.orm import Session
import bcrypt
import hashlib
import re

from core.models.user import User

PASSWORD_MIN_LENGTH = 8
NAME_MIN_LENGTH = 2

Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/registration",
    tags=["registration"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class NewUser(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    phone_number: str

email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$" 


# TODO: check phone number is valid
@router.post("/")
async def registration(request: Request, newUser: NewUser, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == newUser.email).first()

    if not re.fullmatch(email_regex, newUser.email):
        raise HTTPException(status_code=400, detail="Invalid email")
    if len(newUser.password) < PASSWORD_MIN_LENGTH:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    if len(newUser.first_name) < NAME_MIN_LENGTH or len(newUser.last_name) < NAME_MIN_LENGTH:
        raise HTTPException(status_code=400, detail="Name must be at least 2 characters long")

    if user != None:
        raise HTTPException(status_code=400, detail="User already exists with that email")

    user = db.query(User).filter(User.phone_number == newUser.phone_number).first()
    if user != None:
        raise HTTPException(status_code=400, detail="User already exists with that phone number")

    salt = bcrypt.gensalt().hex()
    timestamp = datetime.now()#.strftime('%Y-%m-%d %H:%M:%S')

    hashedPass = str(hashlib.sha256((newUser.password + salt).encode()).hexdigest())
    user = User(email=newUser.email, password= hashedPass, first_name=newUser.first_name,
           last_name=newUser.last_name, middle_name=newUser.middle_name, phone_number=newUser.phone_number, 
           created= timestamp, last_login=timestamp, role_id='user', active=True, version = 0, salt = salt)
    db.add(user)
    db.commit()
    return  {"first_name": user.first_name, "last_name": user.last_name, "email": user.email, "role": user.role_id}