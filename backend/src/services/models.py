from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from src.services.database import Base


class Calendar(Base):
    __tablename__ = "calendars"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    brand_name = Column(String, nullable=False)
    brand_description = Column(Text, nullable=False)
    industry = Column(String)
    tone = Column(String)
    platforms = Column(String)
    num_days = Column(Integer, default=7)
    created_at = Column(DateTime, server_default=func.now())
    status = Column(String, default="generating")  # generating | ready | error

    posts = relationship("Post", back_populates="calendar", cascade="all, delete-orphan")


class Post(Base):
    __tablename__ = "posts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    calendar_id = Column(String, ForeignKey("calendars.id"), nullable=False)
    day = Column(Integer, nullable=False)
    platform = Column(String, nullable=False)
    caption = Column(Text)
    image_prompt = Column(Text)
    image_url = Column(String)
    status = Column(String, default="pending")  # pending | approved | rejected | scheduled
    created_at = Column(DateTime, server_default=func.now())

    calendar = relationship("Calendar", back_populates="posts")
