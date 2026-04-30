from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class BrandInput(BaseModel):
    brand_name: str = Field(..., min_length=1)
    brand_description: str = Field(..., min_length=10)
    industry: str = "general"
    tone: str = "professional"
    platforms: List[str] = ["Instagram", "Twitter", "LinkedIn"]
    num_days: int = Field(default=7, ge=1, le=30)


class PostUpdate(BaseModel):
    caption: Optional[str] = None
    status: Optional[str] = None


class PostResponse(BaseModel):
    id: str
    calendar_id: str
    day: int
    platform: str
    caption: Optional[str]
    image_prompt: Optional[str]
    image_url: Optional[str]
    status: str
    created_at: Optional[datetime]

    model_config = {"from_attributes": True}


class CalendarResponse(BaseModel):
    id: str
    brand_name: str
    brand_description: str
    industry: Optional[str]
    tone: Optional[str]
    platforms: Optional[str]
    num_days: int
    status: str
    created_at: Optional[datetime]
    posts: List[PostResponse] = []

    model_config = {"from_attributes": True}
