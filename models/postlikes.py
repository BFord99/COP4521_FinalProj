"""
post likes class deceleration
"""
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import declarative_base


Base = declarative_base()

class PostLikes(Base):
    """
    post likes class deceleration
    """
    __tablename__ = 'post_likes'

    id = Column(String, primary_key=True)
    user_id = Column(String)
    post_id = Column(String)
    is_liked = Column(Boolean)
