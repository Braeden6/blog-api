from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from core.models.database import engine, SessionLocal, Base
from sqlalchemy.orm import Session
from core.models.user import User
from router import login, registration

SALT_LENGTH = 4

app = FastAPI()


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(login.router)
app.include_router(registration.router)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users")
async def read_all(db: Session = Depends(get_db)):
    return db.query(User).all()


'''
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None
    interest: float
    
@app.post("/helper/password")
async def helperPassword(request: Request, password: str, clientSalt: str, serverSalt: str):
    return { "password": str(hashlib.sha256((serverSalt + str(hashlib.sha256((password.encode('utf-8'))).hexdigest()) + clientSalt).encode('utf-8')).hexdigest())}




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