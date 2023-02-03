from datetime import datetime
from fastapi import Request, HTTPException, Depends, APIRouter
import random
import string
import hashlib
from core.models.database import engine, SessionLocal, Base
from sqlalchemy.orm import Session
from core.models.user import User


SALT_LENGTH = 4

# the recent given salt for each ip
salt = {}

Base.metadata.create_all(bind=engine)

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


def generateRandomString(length: str):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))


# https://stackoverflow.com/questions/3715920/is-it-worth-hashing-passwords-on-the-client-side
@router.get("/")
async def login(request: Request):
    global salt
    salt[request.client.host] = generateRandomString(SALT_LENGTH)
    return { "salt": salt[request.client.host]}

@router.post("/")
async def login(request: Request, username: str, password: str, clientSalt: str, db: Session = Depends(get_db)):
    global salt
    if salt.get(request.client.host) == None:
        raise HTTPException(status_code=400, detail="no salt requested from this ip")
    
    user = db.query(User).filter(User.email == username).first()
    if user == None:
        raise HTTPException(status_code=404, detail="user not found")

    finalPass = str(hashlib.sha256((salt[request.client.host] + user.password + clientSalt).encode('utf-8')).hexdigest())
    if finalPass != password:
        raise HTTPException(status_code=401, detail="password incorrect")


    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user.last_login = timestamp
    db.commit()

    return { "first_name": user.first_name, "last_name": user.last_name, "email": user.email, "role": user.role_id}

