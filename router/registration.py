from datetime import datetime
from fastapi import HTTPException, Request, Depends, APIRouter
from pydantic import BaseModel
from typing import Optional
from core.models.database import engine, SessionLocal, Base
from sqlalchemy.orm import Session

from core.models.user import User

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


@router.post("/")
async def registration(request: Request, newUser: NewUser, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == newUser.email).first()
    if user != None:
        raise HTTPException(status_code=400, detail="User already exists with that email")

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user = User(email=newUser.email, password=newUser.password, first_name=newUser.first_name,
           last_name=newUser.last_name, middle_name=newUser.middle_name, phone_number=newUser.phone_number, created= timestamp, last_login=timestamp, role_id='user', active=True)
    db.add(user)
    db.commit()
    
    return  {"first_name": user.first_name, "last_name": user.last_name, "email": user.email, "role": user.role_id}
