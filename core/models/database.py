from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

#sqlite:///./test.db
#mysql://hbstudent:hbstudent@localhost/dev-portal
SQLALCHEMY_DATABASE_URI =os.environ.get("SQLALCHEMY_DATABASE_URI")


engine = create_engine(SQLALCHEMY_DATABASE_URI)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()