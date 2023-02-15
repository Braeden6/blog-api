from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from core.models.database import SessionLocal, Base, engine
from sqlalchemy.orm import Session
from core.models.requests import Requests
from core.models.user import User
from router.login import verify_token
import io
import pandas as pd
import matplotlib.pyplot as plt
from fastapi.responses import JSONResponse
import base64


Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/blog",
    tags=["admin"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/admin/chart")
async def get_chart_data(token: str, db: Session = Depends(get_db)):
    user = await verify_token(token)
    db_user = db.get(User, user.get('id'))
    if db_user == None or  db_user.role_id != "admin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db_requests = db.query(Requests).all()
    times = {
        "timestamp": [],
        "method": []
    }
    for request in db_requests:
        times.get("timestamp").append(request.requested)
        times.get("method").append(request.request_method)

    df = pd.DataFrame(times)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df.set_index("timestamp", inplace=True)

    resampled = df.resample("1min").method.value_counts().unstack().fillna(0)
    resampled.plot(kind="bar", stacked=True, figsize=(12, 10))
    
    plt.title("Requests over time")
    plt.xlabel("Time")
    plt.ylabel("Number of requests")
    plt.legend(title="Method")

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    encoded_string = base64.b64encode(buf.read()).decode("utf-8")

    return JSONResponse(content={"image": encoded_string})