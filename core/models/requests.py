from sqlalchemy import Column, JSON, BIGINT, VARCHAR, TIMESTAMP, ForeignKey, TEXT, Boolean, Enum, Integer
from core.models.database import Base
from sqlalchemy.orm import relationship, mapped_column, backref


class Requests(Base):
    __tablename__ = "requests"
    id = Column(BIGINT, primary_key=True)
    user_id = Column(BIGINT, ForeignKey("user.id"), nullable=True)
    #user = relationship("User", lazy="subquery")
    requested = Column(TIMESTAMP, nullable=False)
    request_path = Column(VARCHAR(255), nullable=False)
    request_query = Column(VARCHAR(255), nullable=False)
    request_method = Column(VARCHAR(10), nullable=False)
    request_header = Column(TEXT, nullable=True)
    request_body = Column(TEXT, nullable=True)
    client_ip = Column(VARCHAR(45), nullable=False)
    response_status_code = Column(Integer, nullable=False)
    response_header = Column(TEXT, nullable=False)
    response_body = Column(TEXT, nullable=False)
    latency = Column(Integer, nullable=False)
