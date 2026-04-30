import asyncio
import traceback
from typing import List

from fastapi import BackgroundTasks, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session

from src.agents.content_agent import ContentAgent
from src.services.database import SessionLocal, get_db
from src.services import models, schemas

router = APIRouter(prefix="/api")
agent = ContentAgent()


# ---------------------------------------------------------------------------
# Background generation task
# ---------------------------------------------------------------------------

async def _generate_calendar_posts(calendar_id: str, brand_input: schemas.BrandInput):
    db = SessionLocal()
    try:
        calendar = db.query(models.Calendar).filter(models.Calendar.id == calendar_id).first()
        if not calendar:
            return

        content_plan = await agent.generate_content_plan(
            brand_name=brand_input.brand_name,
            brand_description=brand_input.brand_description,
            industry=brand_input.industry,
            tone=brand_input.tone,
            platforms=brand_input.platforms,
            num_days=brand_input.num_days,
        )

        post_ids_and_prompts: list[tuple[str, str]] = []
        for item in content_plan:
            post = models.Post(
                calendar_id=calendar_id,
                day=item["day"],
                platform=item["platform"],
                caption=item["caption"],
                image_prompt=item["image_prompt"],
                status="pending",
            )
            db.add(post)
            db.flush()
            post_ids_and_prompts.append((post.id, item["image_prompt"]))

        db.commit()

        semaphore = asyncio.Semaphore(3)

        async def _save_image(post_id: str, image_prompt: str):
            async with semaphore:
                url = await agent.generate_image(image_prompt, brand_input.brand_name)
            if url:
                inner_db = SessionLocal()
                try:
                    p = inner_db.query(models.Post).filter(models.Post.id == post_id).first()
                    if p:
                        p.image_url = url
                        inner_db.commit()
                finally:
                    inner_db.close()

        await asyncio.gather(*[_save_image(pid, prompt) for pid, prompt in post_ids_and_prompts])

        calendar.status = "ready"
        db.commit()

    except Exception as exc:
        print(f"[routes] calendar generation error: {exc}")
        traceback.print_exc()
        cal = db.query(models.Calendar).filter(models.Calendar.id == calendar_id).first()
        if cal:
            cal.status = "error"
            db.commit()
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Calendar routes
# ---------------------------------------------------------------------------

@router.post("/calendars", response_model=schemas.CalendarResponse, status_code=201)
async def create_calendar(
    brand_input: schemas.BrandInput,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    calendar = models.Calendar(
        brand_name=brand_input.brand_name,
        brand_description=brand_input.brand_description,
        industry=brand_input.industry,
        tone=brand_input.tone,
        platforms=",".join(brand_input.platforms),
        num_days=brand_input.num_days,
        status="generating",
    )
    db.add(calendar)
    db.commit()
    db.refresh(calendar)
    background_tasks.add_task(_generate_calendar_posts, calendar.id, brand_input)
    return calendar


@router.get("/calendars", response_model=List[schemas.CalendarResponse])
def list_calendars(db: Session = Depends(get_db)):
    return db.query(models.Calendar).order_by(models.Calendar.created_at.desc()).all()


@router.get("/calendars/{calendar_id}", response_model=schemas.CalendarResponse)
def get_calendar(calendar_id: str, db: Session = Depends(get_db)):
    cal = db.query(models.Calendar).filter(models.Calendar.id == calendar_id).first()
    if not cal:
        raise HTTPException(404, "Calendar not found")
    return cal


@router.delete("/calendars/{calendar_id}", status_code=204)
def delete_calendar(calendar_id: str, db: Session = Depends(get_db)):
    cal = db.query(models.Calendar).filter(models.Calendar.id == calendar_id).first()
    if not cal:
        raise HTTPException(404, "Calendar not found")
    db.delete(cal)
    db.commit()


# ---------------------------------------------------------------------------
# Post routes
# ---------------------------------------------------------------------------

@router.put("/posts/{post_id}", response_model=schemas.PostResponse)
def update_post(post_id: str, update: schemas.PostUpdate, db: Session = Depends(get_db)):
    post = _get_post_or_404(post_id, db)
    if update.caption is not None:
        post.caption = update.caption
    if update.status is not None:
        post.status = update.status
    db.commit()
    db.refresh(post)
    return post


@router.post("/posts/{post_id}/approve", response_model=schemas.PostResponse)
def approve_post(post_id: str, db: Session = Depends(get_db)):
    post = _get_post_or_404(post_id, db)
    post.status = "approved"
    db.commit()
    db.refresh(post)
    return post


@router.post("/posts/{post_id}/reject", response_model=schemas.PostResponse)
def reject_post(post_id: str, db: Session = Depends(get_db)):
    post = _get_post_or_404(post_id, db)
    post.status = "rejected"
    db.commit()
    db.refresh(post)
    return post


@router.post("/posts/{post_id}/regenerate-caption", response_model=schemas.PostResponse)
async def regenerate_caption(post_id: str, db: Session = Depends(get_db)):
    post = _get_post_or_404(post_id, db)
    cal = post.calendar
    new_caption = await agent.regenerate_caption(
        brand_name=cal.brand_name,
        brand_description=cal.brand_description,
        platform=post.platform,
        tone=cal.tone or "professional",
        day=post.day,
        current_caption=post.caption,
    )
    post.caption = new_caption
    post.status = "pending"
    db.commit()
    db.refresh(post)
    return post


@router.post("/posts/{post_id}/regenerate-image", response_model=schemas.PostResponse)
async def regenerate_image(post_id: str, db: Session = Depends(get_db)):
    post = _get_post_or_404(post_id, db)
    cal = post.calendar
    new_prompt = await agent.regenerate_image_prompt(
        brand_name=cal.brand_name,
        brand_description=cal.brand_description,
        platform=post.platform,
        day=post.day,
    )
    post.image_prompt = new_prompt
    url = await agent.generate_image(new_prompt, cal.brand_name)
    if url:
        post.image_url = url
    post.status = "pending"
    db.commit()
    db.refresh(post)
    return post


@router.post("/posts/{post_id}/schedule", response_model=schemas.PostResponse)
def schedule_post(post_id: str, db: Session = Depends(get_db)):
    post = _get_post_or_404(post_id, db)
    if post.status != "approved":
        raise HTTPException(400, "Post must be approved before scheduling")
    post.status = "scheduled"
    db.commit()
    db.refresh(post)
    return post


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_post_or_404(post_id: str, db: Session) -> models.Post:
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(404, "Post not found")
    return post
