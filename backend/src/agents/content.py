import asyncio
import json
import os

import openai
from dotenv import load_dotenv

from src.services.llm import get_llm
from src.services.state import CampaignState, Post, PostStatus

load_dotenv()

_PLATFORM_RULES = {
    "Instagram": "Max 2200 chars. Warm, visual-first tone. 5-8 hashtags. Emoji-friendly.",
    "LinkedIn":  "Max 1300 chars. Professional thought-leadership tone. NO hashtags.",
    "Facebook":  "Max 500 chars. Friendly, community-focused. 2-3 hashtags.",
    "Twitter":   "Max 280 chars total including hashtags. Punchy, 1-2 hashtags only.",
    "TikTok":    "Max 300 chars. Energetic, trend-aware, heavy emoji, call-to-action.",
}


async def _generate_caption(llm, post: Post, brand_prompt: str) -> dict:
    """Returns {caption: str, hashtags: list[str]} parsed from LLM JSON response."""
    rules = _PLATFORM_RULES.get(post["platform"], "Engaging, on-brand.")

    prompt = f"""Generate a social media caption for the following post.

Brand context: {brand_prompt}
Platform: {post["platform"]}
Platform rules: {rules}
Content type: {post["content_type"]}
Day theme / angle: Day {post["day"]}

Return ONLY a JSON object — no markdown, no explanation:
{{"caption": "...", "hashtags": ["tag1", "tag2"]}}

Hashtags must NOT include the # symbol."""

    response = await llm.client.chat.completions.create(
        model=llm.model,
        temperature=llm.temperature,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
    )

    raw = (response.choices[0].message.content or "").strip()

    # Strip markdown fences
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    data = json.loads(raw)
    return {
        "caption": str(data.get("caption", "")),
        "hashtags": [str(h).lstrip("#") for h in data.get("hashtags", [])],
    }


async def _generate_image(image_client: openai.AsyncOpenAI, image_model: str, post: Post) -> str:
    """Calls DALL-E and returns the image URL."""
    # TODO: save image to cloud storage (S3 / Cloudinary) — DALL-E URLs expire after ~1 hour
    enhanced_prompt = (
        f"{post['image_prompt']}. "
        "Clean, professional, no text overlay, no watermarks."
    )
    response = await image_client.images.generate(
        model=image_model,
        prompt=enhanced_prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    return response.data[0].url


async def content_node(state: CampaignState) -> CampaignState:
    """
    LangGraph-style node: generates captions and images for each post.
    - Skips posts with status APPROVED.
    - Caption generation and image generation each have independent try/except.
    - A single post failure never crashes the pipeline.
    - Errors are appended to state['errors'].
    """
    llm = get_llm(temperature=0.75)
    image_client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    image_model = os.getenv("IMAGE_MODEL", "dall-e-3")
    brand_prompt = state["brand_prompt"]

    # Cap concurrent DALL-E calls to avoid rate-limit errors
    semaphore = asyncio.Semaphore(3)

    async def process_post(post: Post) -> Post:
        if post["status"] == PostStatus.APPROVED:
            return post

        # --- Caption ---
        try:
            result = await _generate_caption(llm, post, brand_prompt)
            post = {**post, "caption": result["caption"], "hashtags": result["hashtags"]}
        except Exception as exc:
            state["errors"].append(
                f"caption failed — day={post['day']} platform={post['platform']}: {exc}"
            )

        # --- Image ---
        try:
            async with semaphore:
                url = await _generate_image(image_client, image_model, post)
            post = {**post, "image_url": url}
        except Exception as exc:
            state["errors"].append(
                f"image failed — day={post['day']} platform={post['platform']}: {exc}"
            )

        return post

    updated = await asyncio.gather(*[process_post(p) for p in state["posts"]])
    state["posts"] = list(updated)
    state["current_step"] = "review"
    return state
