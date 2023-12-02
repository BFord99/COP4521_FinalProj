"""
news item class deceleration
"""
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class NewsItem(Base):
    """
    news item class deceleration
    """
    __tablename__ = 'news_items_new'

    id = Column(Integer, primary_key=True)
    created_by = Column(String(200))
    title = Column(String(200), nullable=False)
    score = Column(Integer, nullable=False)
    text = Column(Text, nullable=True)
    time = Column(Integer, nullable=True)
