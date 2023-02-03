from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# mysql+mysqlconnector://root@localhost:3306/serversiderendering
#SQLALCHEMY_DATABASE_URI = 'sqlite:///bank.db'
SQLALCHEMY_DATABASE_URI = 'mysql://hbstudent:hbstudent@localhost/dev-portal'


engine = create_engine(SQLALCHEMY_DATABASE_URI) # , connect_args={"check_same_thread" : False}

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()