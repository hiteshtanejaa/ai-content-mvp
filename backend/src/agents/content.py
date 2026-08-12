import asyncio
import base64
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


async def _generate_image_google(post: Post) -> str:
    """Generate image using Google Imagen 3 via AI Studio (free tier).
    Returns a base64 data URI so no external storage is needed."""
    from google import genai
    from google.genai import types

    api_key = os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key=api_key)

    enhanced_prompt = (
        f"{post['image_prompt']} "
        "Photorealistic, professional product photography, natural lighting, "
        "clean composition, no text overlay, no watermarks."
    )

    response = await asyncio.to_thread(
        client.models.generate_images,
        model="imagen-3.0-generate-002",
        prompt=enhanced_prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="1:1",
        ),
    )

    image_bytes = response.generated_images[0].image.image_bytes
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:image/png;base64,{b64}"


async def _generate_image_dalle(image_client: openai.AsyncOpenAI, image_model: str, post: Post) -> str:
    """Fallback: calls DALL-E and returns the image URL.
    Note: DALL-E URLs expire after ~1 hour."""
    enhanced_prompt = (
        f"{post['image_prompt']} "
        "Photorealistic, hyperrealistic, professional photography, 8K resolution, "
        "shot on Canon EOS R5, natural or studio lighting, no illustration, "
        "no CGI, no cartoon, no digital art, no text overlay, no watermarks."
    )
    response = await image_client.images.generate(
        model=image_model,
        prompt=enhanced_prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    return response.data[0].url


async def _generate_image(image_client: openai.AsyncOpenAI, image_model: str, post: Post) -> str:
    """Image generation with provider selection.
    - If GOOGLE_API_KEY is set → use Google Imagen 3 (free, best quality).
    - Otherwise → fall back to DALL-E via OPENAI_API_KEY.
    """
    if os.getenv("GOOGLE_API_KEY"):
        return await _generate_image_google(post)
    return await _generate_image_dalle(image_client, image_model, post)


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
