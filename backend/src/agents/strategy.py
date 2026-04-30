import json
import math

from src.services.llm import get_llm
from src.services.state import CampaignState, Post, PostStatus

_PLATFORM_GUIDELINES = {
    "Instagram": "visual-first, 2-4 sentences, 5-8 hashtags in caption, warm and engaging tone",
    "Twitter":   "under 280 chars total including hashtags, punchy hook, 1-2 hashtags",
    "LinkedIn":  "professional thought-leadership, 3-5 sentences, NO hashtags",
    "Facebook":  "friendly and community-focused, 2-3 sentences, 2-3 hashtags",
    "TikTok":    "energetic, trend-aware, short punchy lines, heavy emoji, call-to-action",
}


async def strategy_node(state: CampaignState) -> CampaignState:
    """
    LangGraph-style node: generates the content strategy (posts skeleton).
    Populates state['posts'] and advances current_step to 'content'.
    Retries JSON parsing up to 3 times before writing to state['errors'].
    """
    llm = get_llm(temperature=0.85)
    platforms = state["platforms"]
    num_days = state["num_days"]
    brand_prompt = state["brand_prompt"]

    # Target ~1-2 posts per day, capped by platform count.
    # Distribute evenly across platforms so no platform is skipped entirely.
    posts_per_day = min(2, len(platforms))
    total_posts = num_days * posts_per_day

    guidelines = "\n".join(
        f"  - {p}: {_PLATFORM_GUIDELINES.get(p, 'engaging, on-brand')}"
        for p in platforms
    )

    # Build a rotation schedule hint so the LLM doesn't post to all platforms every day
    rotation: list[str] = []
    for i in range(total_posts):
        rotation.append(platforms[i % len(platforms)])
    rotation_hint = ", ".join(f"Day {(i // posts_per_day) + 1}→{p}" for i, p in enumerate(rotation))

    prompt = f"""You are a senior social media strategist. Create a {num_days}-day content calendar.

Brand / Campaign Brief:
{brand_prompt}

Platforms available: {', '.join(platforms)}
Platform guidelines:
{guidelines}

Distribution rules:
- Generate exactly {total_posts} posts total
- Roughly {posts_per_day} post(s) per day, rotating across platforms (not all platforms every day)
- Suggested rotation: {rotation_hint}
- Each day must have a distinct theme or angle (product feature, behind-the-scenes, social proof, tips, etc.)
- Captions must feel authentic and platform-native — not copy-pasted across platforms
- Hashtags must be a JSON array of strings WITHOUT the # symbol
- image_prompt must be a vivid DALL-E prompt: describe subject, setting, lighting, mood, style. No text in image.
- content_type: one of "image", "carousel", "text"

Return ONLY a valid JSON array — no markdown, no explanation, no code fences:
[
  {{
    "day": 1,
    "platform": "Instagram",
    "content_type": "image",
    "caption": "...",
    "hashtags": ["brand", "marketing"],
    "image_prompt": "..."
  }}
]"""

    last_error: Exception | None = None

    for attempt in range(3):
        try:
            response = await llm.client.chat.completions.create(
                model=llm.model,
                temperature=llm.temperature,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=8192,
            )

            raw = (response.choices[0].message.content or "").strip()
            print(f"[strategy] attempt {attempt + 1} — response {len(raw)} chars")

            # Strip markdown code fences if present
            if raw.startswith("```"):
                parts = raw.split("```")
                raw = parts[1] if len(parts) > 1 else raw
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.strip()

            parsed = json.loads(raw)

            # Unwrap if LLM wrapped the array in a dict
            if isinstance(parsed, dict):
                for v in parsed.values():
                    if isinstance(v, list):
                        parsed = v
                        break

            if not isinstance(parsed, list):
                raise ValueError(f"Expected JSON array, got {type(parsed).__name__}")

            # Map raw dicts → typed Post dicts
            posts: list[Post] = [
                Post(
                    day=int(item["day"]),
                    platform=str(item["platform"]),
                    content_type=str(item.get("content_type", "image")),
                    caption=str(item.get("caption", "")),
                    hashtags=[str(h).lstrip("#") for h in item.get("hashtags", [])],
                    image_prompt=str(item.get("image_prompt", "")),
                    image_url=None,
                    status=PostStatus.DRAFT,
                    scheduled_time=None,
                )
                for item in parsed
            ]

            state["posts"] = posts
            state["current_step"] = "content"
            return state

        except (json.JSONDecodeError, ValueError, KeyError) as exc:
            last_error = exc
            print(f"[strategy] attempt {attempt + 1} failed: {exc}")

    # All 3 attempts exhausted
    state["errors"].append(
        f"strategy_node failed after 3 attempts: {last_error}"
    )
    return state
