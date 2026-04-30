import uuid
from typing import Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.agents.content import content_node
from src.agents.graph import campaign_graph
from src.services.state import CampaignState, PostStatus

app = FastAPI(title="AI Content Calendar API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# In-memory store — MVP data layer
# Each entry: CampaignState fields + "status" (generating | ready | error)
# ---------------------------------------------------------------------------
campaigns: dict[str, dict] = {}


# ---------------------------------------------------------------------------
# Pydantic request / response models
# ---------------------------------------------------------------------------

class CampaignRequest(BaseModel):
    brand_prompt: str
    platforms: list[str]
    num_days: int = 7


class PostUpdate(BaseModel):
    status: Optional[str] = None
    caption: Optional[str] = None


# ---------------------------------------------------------------------------
# Background helpers
# ---------------------------------------------------------------------------

async def _run_graph(campaign_id: str, state: CampaignState) -> None:
    try:
        result = await campaign_graph.ainvoke(state)
        campaigns[campaign_id].update({**result, "status": "ready"})
    except Exception as exc:
        campaigns[campaign_id]["status"] = "error"
        campaigns[campaign_id]["errors"].append(str(exc))


async def _run_regenerate(campaign_id: str) -> None:
    """Re-runs content_node for a single campaign. Only REGENERATE posts are processed."""
    data = campaigns[campaign_id]
    state = CampaignState(
        campaign_id=data["campaign_id"],
        brand_prompt=data["brand_prompt"],
        platforms=data["platforms"],
        num_days=data["num_days"],
        posts=data["posts"],
        current_step=data["current_step"],
        errors=data["errors"],
    )
    result = await content_node(state)
    campaigns[campaign_id]["posts"] = result["posts"]
    campaigns[campaign_id]["errors"] = result["errors"]
    campaigns[campaign_id]["status"] = "ready"


# ---------------------------------------------------------------------------
# POST /campaigns
# ---------------------------------------------------------------------------

@app.post("/campaigns", status_code=201)
async def create_campaign(req: CampaignRequest, background_tasks: BackgroundTasks):
    """Creates a campaign and immediately returns campaign_id.
    LangGraph graph runs in the background — poll GET /campaigns/{id} for status."""
    campaign_id = str(uuid.uuid4())
    state = CampaignState(
        campaign_id=campaign_id,
        brand_prompt=req.brand_prompt,
        platforms=req.platforms,
        num_days=req.num_days,
        posts=[],
        current_step="init",
        errors=[],
    )
    campaigns[campaign_id] = {**state, "status": "generating"}
    background_tasks.add_task(_run_graph, campaign_id, state)
    return {"campaign_id": campaign_id, "status": "generating"}


# ---------------------------------------------------------------------------
# GET /campaigns  and  GET /campaigns/{id}
# ---------------------------------------------------------------------------

@app.get("/campaigns")
def list_campaigns():
    """Returns all campaigns with campaign_id and status only."""
    return [
        {"campaign_id": cid, "status": c["status"]}
        for cid, c in campaigns.items()
    ]


@app.get("/campaigns/{campaign_id}")
def get_campaign(campaign_id: str):
    """Returns full campaign dict including posts and errors.
    While generating: status='generating', posts=[].
    After done:       status='ready',      posts=full array."""
    if campaign_id not in campaigns:
        raise HTTPException(404, "Campaign not found")
    return campaigns[campaign_id]


# ---------------------------------------------------------------------------
# PATCH /campaigns/{id}/posts/{day}
# ---------------------------------------------------------------------------

@app.patch("/campaigns/{campaign_id}/posts/{day}")
def update_post(campaign_id: str, day: int, update: PostUpdate):
    """Updates a post by day number (first match).
    Updates status and/or caption if provided."""
    if campaign_id not in campaigns:
        raise HTTPException(404, "Campaign not found")

    # Find first post matching this day
    post = next((p for p in campaigns[campaign_id]["posts"] if p["day"] == day), None)
    if post is None:
        raise HTTPException(404, f"No post found for day {day}")

    if update.status is not None:
        post["status"] = PostStatus(update.status)
    if update.caption is not None:
        post["caption"] = update.caption

    return post


# ---------------------------------------------------------------------------
# POST /campaigns/{id}/posts/{day}/regenerate
# ---------------------------------------------------------------------------

@app.post("/campaigns/{campaign_id}/posts/{day}/regenerate")
async def regenerate_post(
    campaign_id: str, day: int, background_tasks: BackgroundTasks
):
    """Marks target post as REGENERATE, runs content_node in background.
    All other posts keep their current status — APPROVED posts are untouched."""
    if campaign_id not in campaigns:
        raise HTTPException(404, "Campaign not found")

    post = next(
        (p for p in campaigns[campaign_id]["posts"] if p["day"] == day), None
    )
    if post is None:
        raise HTTPException(404, f"No post found for day {day}")

    post["status"] = PostStatus.REGENERATE
    campaigns[campaign_id]["status"] = "generating"

    background_tasks.add_task(_run_regenerate, campaign_id)
    return {"status": "regenerating"}


# ---------------------------------------------------------------------------
# POST /campaigns/{id}/schedule
# ---------------------------------------------------------------------------

@app.post("/campaigns/{campaign_id}/schedule")
def schedule_campaign(campaign_id: str):
    """Sets all APPROVED posts to SCHEDULED.
    TODO Phase 3: post to Meta Graph API and LinkedIn API for real scheduling."""
    if campaign_id not in campaigns:
        raise HTTPException(404, "Campaign not found")

    count = 0
    for post in campaigns[campaign_id]["posts"]:
        if post["status"] == PostStatus.APPROVED:
            post["status"] = PostStatus.SCHEDULED
            count += 1

    return {"scheduled": count}
