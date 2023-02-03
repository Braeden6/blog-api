from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from core.models.database import Base

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String)
    password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    middle_name = Column(String)
    phone_number = Column(String)
    created = Column(String)
    last_login = Column(String)
    role_id = Column(Integer)
    active = Column(Boolean)