import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.agents.content import content_node
from src.agents.graph import get_graph
from src.services.database import Base, engine, get_db
from src.services.models import InteractionLog
from src.services.state import CampaignState, PostStatus

app = FastAPI(title="AI Content Calendar API", version="2.0.0")


@app.on_event("startup")
def create_tables():
    """Create all DB tables (interaction_logs etc.) on first startup."""
    Base.metadata.create_all(bind=engine)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# In-memory store — MVP data layer
# Each entry: CampaignState fields + "status" + "agent_logs"
# ---------------------------------------------------------------------------
campaigns: dict[str, dict] = {}


# ---------------------------------------------------------------------------
# Interaction logging helper
# ---------------------------------------------------------------------------

def _log_interaction(
    db: Session,
    campaign_id: str,
    post_day: int,
    post_platform: str,
    action: str,
    caption_before: Optional[str] = None,
    caption_after: Optional[str] = None,
) -> None:
    """Persist a HITL interaction to PostgreSQL for RQ2 analysis."""
    mode = (campaigns.get(campaign_id) or {}).get("orchestration_mode", "sequential")
    log = InteractionLog(
        campaign_id=campaign_id,
        post_day=post_day,
        post_platform=post_platform,
        action=action,
        orchestration_mode=mode,
        caption_before=caption_before,
        caption_after=caption_after,
    )
    db.add(log)
    db.commit()


def _log_agent(campaign_id: str, agent: str, status: str, message: str) -> None:
    """Append a timestamped status entry for an agent."""
    if campaign_id not in campaigns:
        return
    campaigns[campaign_id].setdefault("agent_logs", []).append({
        "agent":   agent,
        "status":  status,   # running | done | error | waiting
        "message": message,
        "ts":      datetime.now(timezone.utc).isoformat(),
    })


# ---------------------------------------------------------------------------
# Pydantic request / response models
# ---------------------------------------------------------------------------

class CampaignRequest(BaseModel):
    brand_prompt: str
    platforms: list[str]
    num_days: int = 7
    orchestration_mode: str = "sequential"   # "sequential" | "hierarchical"


class PostUpdate(BaseModel):
    status: Optional[str] = None
    caption: Optional[str] = None


# ---------------------------------------------------------------------------
# Background helpers
# ---------------------------------------------------------------------------

async def _run_graph(campaign_id: str, state: CampaignState) -> None:
    try:
        mode = state.get("orchestration_mode", "sequential")
        if mode == "hierarchical":
            _log_agent(campaign_id, "orchestrator", "running",
                       "Orchestrator dispatching parallel platform sub-agents…")
            _log_agent(campaign_id, "sub-agents",   "waiting",
                       "Platform sub-agents queued — will run in parallel")
        else:
            _log_agent(campaign_id, "strategy", "running",
                       "Analysing brand and building visual style guide…")
        _log_agent(campaign_id, "content",   "waiting", "Waiting for strategy/orchestrator to complete")
        _log_agent(campaign_id, "scheduler", "waiting", "Waiting for posts to be approved")

        graph  = get_graph(mode)
        result = await graph.ainvoke(state)

        post_count = len(result.get("posts", []))
        if mode == "hierarchical":
            _log_agent(campaign_id, "orchestrator", "done",
                       f"Sub-agents produced {post_count} posts across {len(state['platforms'])} platforms")
        else:
            _log_agent(campaign_id, "strategy", "done",
                       f"Generated {post_count} posts across {state['num_days']} days")
        _log_agent(campaign_id, "content", "done",
                   f"Captions and images generated for {post_count} posts")

        campaigns[campaign_id].update({**result, "status": "ready"})
    except Exception as exc:
        _log_agent(campaign_id, "strategy", "error", str(exc))
        campaigns[campaign_id]["status"] = "error"
        campaigns[campaign_id]["errors"].append(str(exc))


async def _run_regenerate(campaign_id: str) -> None:
    """Re-runs content_node for a single campaign. Only REGENERATE posts are processed."""
    _log_agent(campaign_id, "content", "running", "Regenerating post — building new caption and image…")
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
    _log_agent(campaign_id, "content", "done", "Post regenerated successfully")


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
        orchestration_mode=req.orchestration_mode,
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
        {
            "campaign_id": cid,
            "status": c["status"],
            "brand_prompt": (c.get("brand_prompt") or "")[:80],
            "platforms": c.get("platforms", []),
            "num_days": c.get("num_days", 0),
        }
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
def update_post(campaign_id: str, day: int, update: PostUpdate, db: Session = Depends(get_db)):
    """Updates a post by day number (first match).
    Updates status and/or caption if provided.
    Logs approve / reject / edit_caption interactions to the database."""
    if campaign_id not in campaigns:
        raise HTTPException(404, "Campaign not found")

    post = next((p for p in campaigns[campaign_id]["posts"] if p["day"] == day), None)
    if post is None:
        raise HTTPException(404, f"No post found for day {day}")

    caption_before = post.get("caption")

    if update.status is not None:
        post["status"] = PostStatus(update.status)
        # Log approve / reject
        if update.status in ("approved", "rejected"):
            _log_interaction(
                db, campaign_id, day, post["platform"],
                action=update.status,
                caption_before=caption_before,
            )

    if update.caption is not None:
        post["caption"] = update.caption
        # Log caption edit
        _log_interaction(
            db, campaign_id, day, post["platform"],
            action="edit_caption",
            caption_before=caption_before,
            caption_after=update.caption,
        )

    return post


# ---------------------------------------------------------------------------
# POST /campaigns/{id}/posts/{day}/regenerate
# ---------------------------------------------------------------------------

@app.post("/campaigns/{campaign_id}/posts/{day}/regenerate")
async def regenerate_post(
    campaign_id: str, day: int, background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
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

    _log_interaction(
        db, campaign_id, day, post["platform"],
        action="regenerate",
        caption_before=post.get("caption"),
    )

    post["status"] = PostStatus.REGENERATE
    campaigns[campaign_id]["status"] = "generating"

    background_tasks.add_task(_run_regenerate, campaign_id)
    return {"status": "regenerating"}


# ---------------------------------------------------------------------------
# POST /campaigns/{id}/schedule
# ---------------------------------------------------------------------------

@app.post("/campaigns/{campaign_id}/schedule")
def schedule_campaign(campaign_id: str, db: Session = Depends(get_db)):
    """Sets all APPROVED posts to SCHEDULED.
    Logs one 'schedule' interaction per post.
    TODO Phase 3: post to Meta Graph API and LinkedIn API for real scheduling."""
    if campaign_id not in campaigns:
        raise HTTPException(404, "Campaign not found")

    count = 0
    for post in campaigns[campaign_id]["posts"]:
        if post["status"] == PostStatus.APPROVED:
            _log_interaction(
                db, campaign_id, post["day"], post["platform"],
                action="schedule",
                caption_before=post.get("caption"),
            )
            post["status"] = PostStatus.SCHEDULED
            count += 1

    _log_agent(campaign_id, "scheduler", "done", f"Scheduled {count} approved post(s)")
    return {"scheduled": count}


# ---------------------------------------------------------------------------
# GET /campaigns/{id}/interactions
# ---------------------------------------------------------------------------

@app.get("/campaigns/{campaign_id}/interactions")
def get_interactions(campaign_id: str, db: Session = Depends(get_db)):
    """Returns all logged HITL interactions for a campaign.
    Used for RQ2 evaluation: analyse approve/reject/edit rates by orchestration mode."""
    if campaign_id not in campaigns:
        raise HTTPException(404, "Campaign not found")

    rows = (
        db.query(InteractionLog)
        .filter(InteractionLog.campaign_id == campaign_id)
        .order_by(InteractionLog.timestamp)
        .all()
    )
    return [
        {
            "id":                 r.id,
            "campaign_id":        r.campaign_id,
            "post_day":           r.post_day,
            "post_platform":      r.post_platform,
            "action":             r.action,
            "orchestration_mode": r.orchestration_mode,
            "caption_before":     r.caption_before,
            "caption_after":      r.caption_after,
            "timestamp":          r.timestamp.isoformat() if r.timestamp else None,
        }
        for r in rows
    ]
