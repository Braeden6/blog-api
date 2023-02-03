#main.py

from fastapi import FastAPI, Request, HTTPException, Depends
from typing import Optional
from pydantic import BaseModel
import random
import string
import hashlib
from core.models.database import engine, SessionLocal
from sqlalchemy.orm import Session
import core.models.models as models

SALT_LENGTH = 4

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

savedUsername = "test"
savedPassword =  str(hashlib.sha256((b"test1234")).hexdigest())

# the recent given salt for each ip
salt = {}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def generateRandomString(length: str):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

# https://stackoverflow.com/questions/3715920/is-it-worth-hashing-passwords-on-the-client-side
@app.get("/login")
async def login(request: Request):
    global salt
    salt[request.client.host] = generateRandomString(SALT_LENGTH)
    return { "salt": salt[request.client.host]}

@app.post("/login")
async def login(request: Request, username: str, password: str, clientSalt: str):
    global salt
    if salt.get(request.client.host) == None:
        raise HTTPException(status_code=400, detail="no salt requested from this ip")
    finalPass = str(hashlib.sha256((salt[request.client.host] + savedPassword + clientSalt).encode('utf-8')).hexdigest())
    return { "account found": savedUsername == username, "password correct": password == finalPass}


@app.post("/helper/password")
async def helperPassword(request: Request, password: str, clientSalt: str, serverSalt: str):
    return { "password": str(hashlib.sha256((serverSalt + str(hashlib.sha256((password.encode('utf-8'))).hexdigest()) + clientSalt).encode('utf-8')).hexdigest())}


@app.get("/users")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.User).all()


'''

'''


'''
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None
    interest: float

@app.post("/items/{item_id}")
async def read_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}

# note: put fixed paths first
@app.get("/items/foo")
async def read_item():
    test = 3
    return {"item_id": test, "message": "Hello World %s" %(test)}

@app.get("/items/foo2")
async def read_item():
    test = 4
    return {"item_id": test, "message": f"Hello World {test}"}
'''