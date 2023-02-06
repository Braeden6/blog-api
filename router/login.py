from datetime import datetime, timedelta
from fastapi import Request, HTTPException, Depends, APIRouter
import random
import string
import hashlib
from core.models.database import engine, SessionLocal, Base
from sqlalchemy.orm import Session
from core.models.user import User
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt

SECRET = "asdjsdvhb2qjkb4e32jkfbasbkn324"
ALGORITHM = "HS256"


SALT_LENGTH = 4

# the recent given salt for each ip
salt = {}

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
              "exp": datetime.utcnow() + timedelta(minutes=15)}
    return jwt.encode(encode, SECRET, algorithm=ALGORITHM)


def generateRandomString(length: str):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

async def verify_token(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login"))):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        if payload.get("id") == None or payload.get("sub") == None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"id" : payload.get("id"), "name" : payload.get("sub")}
    except:
        raise HTTPException(status_code=401, detail="Invalid token")


# https://stackoverflow.com/questions/3715920/is-it-worth-hashing-passwords-on-the-client-side
@router.get("/")
async def login(request: Request):
    global salt
    salt[request.client.host] = generateRandomString(SALT_LENGTH)
    return {"salt": salt[request.client.host]}


@router.post("/")
async def login(request: Request, clientSalt: str, form_data: OAuth2PasswordRequestForm = Depends(),  db: Session = Depends(get_db),):
    global salt
    if salt.get(request.client.host) == None:
        raise HTTPException(
            status_code=400, detail="no salt requested from this ip")

    user = db.query(User).filter(User.email == form_data.username).first()
    if user == None:
        raise HTTPException(status_code=404, detail="user not found")

    finalPass = str(hashlib.sha256(
        (salt[request.client.host] + user.password + clientSalt).encode('utf-8')).hexdigest())
    if finalPass != form_data.password:
        raise HTTPException(status_code=401, detail="password incorrect")

    # update last login
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user.last_login = timestamp
    db.commit()

    return {
        "token": create_token(user.id, user.first_name + " " + user.last_name),
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "role": user.role_id
    }
