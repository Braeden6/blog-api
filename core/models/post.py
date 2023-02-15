from sqlalchemy import Column, JSON, BIGINT, VARCHAR, TIMESTAMP, ForeignKey, TEXT, Boolean, Enum, Integer
from core.models.database import Base
from sqlalchemy.orm import relationship, mapped_column, backref

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
    comments = relationship('PostComment', lazy="subquery", primaryjoin="and_(Post.id==PostComment.post_id," "PostComment.post_comment_id==null()," "PostComment.comment_type=='comment')")
    answers = relationship('PostComment', lazy="subquery", primaryjoin="and_(Post.id==PostComment.post_id," "PostComment.post_comment_id==null()," "PostComment.comment_type=='answer')")
    votes = relationship('VotesPost', lazy="subquery")
    author_id = Column(BIGINT, ForeignKey("user.id"))
    author = relationship("User", lazy="subquery")
    version = Column(Integer, default=0)

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


class PostComment(Base):
    __tablename__ = "post_comment"
    id = Column(BIGINT, primary_key=True)
    post_id = Column(BIGINT, ForeignKey("post.id"))
    post_comment_id = Column(BIGINT, ForeignKey("post_comment.id"))
    # can only comment on answer
    comments = relationship('PostComment', lazy="joined")
    author_id = Column(BIGINT, ForeignKey("user.id"))
    author = relationship("User", lazy="subquery")
    comment = Column(TEXT)
    created = Column(TIMESTAMP)
    updated = Column(TIMESTAMP)
    votes = relationship('VotesComment', lazy="subquery")
    comment_type = Column(Enum('comment', 'answer'))
    version = Column(Integer, default=0)

class VotesPost(Base):
    __tablename__ = "votes_post"
    post_id = Column(BIGINT, ForeignKey("post.id"), primary_key=True)
    user_id = Column(BIGINT, ForeignKey("user.id"), primary_key=True)
    vote = Column(Boolean)

class VotesComment(Base):
    __tablename__ = "votes_comment"
    post_comment_id = Column(BIGINT, ForeignKey("post_comment.id"), primary_key=True)
    user_id = Column(BIGINT, ForeignKey("user.id"), primary_key=True)
    vote = Column(Boolean)
