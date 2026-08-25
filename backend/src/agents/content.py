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


async def _generate_image_pollinations(post: Post) -> str:
    """Generate image via Pollinations.ai — completely free, no API key needed.
    Uses Flux model. Returns a stable URL (no expiry)."""
    import urllib.parse
    import httpx

    enhanced_prompt = (
        f"{post['image_prompt']} "
        "Photorealistic, professional product photography, natural lighting, "
        "clean composition, no text overlay, no watermarks."
    )
    encoded = urllib.parse.quote(enhanced_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&model=flux&nologo=true&seed=42"

    # HEAD request confirms the image was generated; return the URL directly
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.get(url)
        resp.raise_for_status()

    return url


async def _generate_image_dalle(image_client: openai.AsyncOpenAI, image_model: str, post: Post) -> str:
    """Calls gpt-image-1-mini / DALL-E and returns an image URL or base64 data URI.
    Note: DALL-E URLs expire after ~1 hour; gpt-image-1 returns base64."""
    enhanced_prompt = (
        f"{post['image_prompt']} "
        "Ultra-photorealistic, shot on Sony A7R V with 50mm f/1.4 lens, "
        "shallow depth of field, warm cafe ambient lighting, "
        "film-like colour grading, authentic real-world scene, "
        "award-winning food & lifestyle photography, "
        "no illustration, no CGI, no cartoon, no digital art, "
        "no text, no watermarks, no logos."
    )
    # gpt-image-1 / gpt-image-1-mini return base64; dall-e-2/3 return URLs
    is_gpt_image = image_model.startswith("gpt-image")
    response = await image_client.images.generate(
        model=image_model,
        prompt=enhanced_prompt,
        size="1024x1024",
        **({} if is_gpt_image else {"quality": "standard"}),
        n=1,
    )
    item = response.data[0]
    if getattr(item, "b64_json", None):
        return f"data:image/png;base64,{item.b64_json}"
    return item.url


async def _generate_image(image_client: openai.AsyncOpenAI, image_model: str, post: Post) -> str:
    """Image generation with provider selection (in priority order):
    1. Pollinations.ai  — free, no key, Flux model (default)
    2. DALL-E           — if IMAGE_PROVIDER=dalle and OPENAI_API_KEY is set
    """
    provider = os.getenv("IMAGE_PROVIDER", "pollinations").lower()
    if provider == "dalle":
        return await _generate_image_dalle(image_client, image_model, post)
    return await _generate_image_pollinations(post)


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
    image_model = os.getenv("IMAGE_MODEL", "dall-e-2")
    brand_prompt = state["brand_prompt"]

    # Cap concurrent image generation calls to avoid rate-limit errors
    semaphore = asyncio.Semaphore(2)

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
