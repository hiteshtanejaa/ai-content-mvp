from enum import Enum
from typing import Optional
from typing_extensions import TypedDict, NotRequired


class PostStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    REGENERATE = "regenerate"
    SCHEDULED = "scheduled"


class Post(TypedDict):
    day: int
    platform: str
    content_type: str                  # e.g. "image", "text", "carousel"
    caption: str
    hashtags: list[str]
    image_prompt: str
    image_url: NotRequired[Optional[str]]
    status: PostStatus
    scheduled_time: NotRequired[Optional[str]]  # ISO-8601 datetime string


class CampaignState(TypedDict):
    campaign_id: str
    brand_prompt: str
    platforms: list[str]
    num_days: int
    posts: list[Post]
    current_step: str
    errors: list[str]
