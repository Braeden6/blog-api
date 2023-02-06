from sqlalchemy import Column, JSON, BIGINT, VARCHAR, TIMESTAMP, ForeignKey
from core.models.database import Base
from sqlalchemy.orm import relationship, mapped_column

class Post(Base):
    __tablename__ = "post"
    id = Column(BIGINT, primary_key=True, index=True)
    solution_id = Column(BIGINT)
    title = Column(VARCHAR(45))
    description = Column(VARCHAR(70))
    slug = Column(VARCHAR(45))
    created = Column(TIMESTAMP)
    updated = Column(TIMESTAMP)
    post_content = Column(JSON)
    tags = relationship('Tag', secondary="post_tag", lazy="subquery")
    author_id = Column(BIGINT, ForeignKey("user.id"))
    author = relationship("User", lazy="subquery")

class Tag(Base):
    __tablename__ = "technology"
    id = Column(BIGINT, primary_key=True)
    name = Column(VARCHAR(45))
    parent_id =  Column(BIGINT, ForeignKey("technology.id"))
    #post = relationship("Post", secondary="post_tag", lazy="subquery")


class PostTag(Base):
    __tablename__ = "post_tag"
    post_id = Column(BIGINT, ForeignKey("post.id"), primary_key=True)
    technology_id = Column(BIGINT, ForeignKey("technology.id"), primary_key=True)
