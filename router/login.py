from datetime import datetime, timedelta
from fastapi import Request, HTTPException, Depends, APIRouter
import hashlib
from core.models.database import engine, SessionLocal, Base
from sqlalchemy.orm import Session
from core.models.user import User
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt

SECRET = "asdjsdvhb2qjkb4e32jkfbasbkn324"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

Base.metadata.create_all(bind=engine)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")


router = APIRouter(
    prefix="/login",
    tags=["login"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_token(id: int, full_name: str):
    encode = {"sub": full_name, "id": id,
              "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)}
    return jwt.encode(encode, SECRET, algorithm=ALGORITHM)


async def verify_token(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login"))):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        if payload.get("id") == None or payload.get("sub") == None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"id" : payload.get("id"), "name" : payload.get("sub")}
    except:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(),  db: Session = Depends(get_db),):
    user = db.query(User).filter(User.email == form_data.username).first()
    if user == None:
        raise HTTPException(status_code=404, detail="user not found")

    hashedPass = str(hashlib.sha256((form_data.password + user.salt).encode()).hexdigest())
    if hashedPass != user.password:
        raise HTTPException(status_code=401, detail="password incorrect")

    # update last login
    timestamp = datetime.now()#.strftime('%Y-%m-%d %H:%M:%S')
    user.last_login = timestamp
    db.commit()

    return {
        "token": create_token(user.id, user.first_name + " " + user.last_name),
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "role": user.role_id
    }
