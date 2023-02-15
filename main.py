from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from core.models.database import engine, SessionLocal, Base
from sqlalchemy.orm import Session
from core.models.user import User
from router import login, registration, post, answer, comment, votes,admin
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info
import strawberry
from datetime import datetime
from core.models.requests import Requests
from starlette.types import Message
from urllib.parse import parse_qs
from starlette.concurrency import iterate_in_threadpool

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


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def set_body(request: Request, body: bytes):
    async def receive() -> Message:
        return {"type": "http.request", "body": body}
    request._receive = receive
 
async def get_body(request: Request) -> bytes:
    body = await request.body()
    await set_body(request, body)
    return body

async def get_user_id(query):
    try:
        token = parse_qs(query)['token'][0]
        
        user = await login.verify_token(token)
        return user.get('id')
    except:
        print("no user id")
        return None


# https://github.com/tiangolo/fastapi/issues/394
@app.middleware("http")
async def log_requests(request: Request, call_next, ):
    # disable logging for graphql and admin
    if request.url.path.startswith("/graphql") or request.url.path.startswith("/blog/admin/"):
        return await call_next(request)

    db = SessionLocal()
    time = datetime.now()

    body = await get_body(request)

    user_id = await get_user_id(request.url.query)
    request_body = body.decode("utf-8")

    response = await call_next(request)

    response_body =""
    response_body_chunks = [chunk async for chunk in response.body_iterator]
    if len(response_body_chunks) > 0:
        response.body_iterator = iterate_in_threadpool(iter(response_body_chunks))
        response_body = response_body_chunks[0].decode()

    request = Requests(user_id = user_id, requested=time, request_method=request.method, request_query=request.url.query,
                        request_path=request.url.path, request_header=str(request.headers), 
                        request_body=request_body, client_ip=request.client.host, 
                        response_status_code=response.status_code, response_header=str(response.headers), 
                        response_body=response_body, latency=int((datetime.now() - time).microseconds/1000))
    db.add(request)
    db.commit()
    return response

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
app.include_router(answer.router)
app.include_router(votes.router)
app.include_router(admin.router)
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
