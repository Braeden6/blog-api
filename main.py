from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from core.models.database import engine, SessionLocal, Base
from sqlalchemy.orm import Session
from core.models.user import User
from router import login, registration, post, comment
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info
import strawberry

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

async def notify_new_flavour(name: str):
    print(name)


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello World"


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_flavour(self, name: str, info: Info) -> bool:
        info.context["background_tasks"].add_task(notify_new_flavour, name)
        return True

schema = strawberry.Schema(query=Query)
graphql_router = GraphQLRouter(schema)

Base.metadata.create_all(bind=engine)

app.include_router(login.router)
app.include_router(registration.router)
app.include_router(post.router)
app.include_router(comment.router)
app.include_router(graphql_router, prefix="/graphql")



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users")
async def read_all(db: Session = Depends(get_db)):
    return db.query(User).all()
