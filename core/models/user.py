from sqlalchemy import Boolean, Column, Integer, String, BigInteger, VARCHAR, TIMESTAMP, Enum
from core.models.database import Base
from sqlalchemy.orm import deferred

class User(Base):
    __tablename__ = "user"
    id = Column(BigInteger, primary_key=True, index=True)
    email = Column(VARCHAR(45), nullable=False, unique=True)
    password = deferred(Column(VARCHAR(70), nullable=False))
    first_name = Column(VARCHAR(45), nullable=False)
    last_name = Column(VARCHAR(45), nullable=False)
    middle_name = Column(VARCHAR(45), nullable=True)
    phone_number = Column(VARCHAR(45), nullable=False)
    created = Column(TIMESTAMP, nullable=False)
    updated = Column(TIMESTAMP, nullable=True)
    last_login = Column(TIMESTAMP, nullable=False)
    role_id = Column(Enum('user', 'admin'), nullable=False)
    active = Column(Boolean, nullable=False)
    version = Column(Integer, nullable=False)
    salt = Column(VARCHAR(32), nullable=False)