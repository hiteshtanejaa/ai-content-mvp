import json
from src.services.llm import get_llm
from src.services.state import CampaignState, Post, PostStatus

_PLATFORM_GUIDELINES = {
    "Instagram": "visual-first, 2-4 sentences, 5-8 hashtags in caption, warm and engaging tone",
    "Twitter":   "under 280 chars total including hashtags, punchy hook, 1-2 hashtags",
    "LinkedIn":  "professional thought-leadership, 3-5 sentences, NO hashtags",
    "Facebook":  "friendly and community-focused, 2-3 sentences, 2-3 hashtags",
    "TikTok":    "energetic, trend-aware, short punchy lines, heavy emoji, call-to-action",
}


async def _build_visual_style_guide(llm, brand_prompt: str) -> str:
    """
    Step 1: Ask the LLM to analyse the brand and produce a concise photography
    style guide. This is used to anchor every image prompt to the brand's
    real-world aesthetic rather than generic AI-art defaults.
    """
    prompt = f"""You are a professional brand photographer and art director.

Analyse this brand and return a concise visual style guide (plain text, no JSON):

Brand brief:
{brand_prompt}

Your guide must include:
1. Photography style (e.g. lifestyle, editorial, product, documentary)
2. Lighting (e.g. soft natural window light, golden-hour, studio softbox)
3. Colour palette (3-5 specific tones, e.g. "warm oak, off-white linen, slate grey")
4. Camera & lens feel (e.g. "35mm full-frame, shallow depth of field, f/2.0")
5. Mood/atmosphere (e.g. "calm, aspirational, Scandinavian minimalism")
6. 6 photography keyword modifiers to append to every prompt
   (e.g. "photorealistic, 8K, award-winning interior photography, no illustration, no CGI")
7. One example hero shot prompt (start the sentence with "Photograph of …")

Keep the guide tight — max 200 words. This will be used verbatim to generate DALL-E prompts."""

    response = await llm.client.chat.completions.create(
        model=llm.model,
        temperature=0.4,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
    )
    return (response.choices[0].message.content or "").strip()


async def strategy_node(state: CampaignState) -> CampaignState:
    """
    LangGraph-style node: generates the content strategy (posts skeleton).
    Step 1 — build a brand visual style guide for realistic image prompts.
    Step 2 — generate the full content calendar using that guide.
    Retries JSON parsing up to 3 times before writing to state['errors'].
    """
    llm = get_llm(temperature=0.85)
    platforms = state["platforms"]
    num_days   = state["num_days"]
    brand_prompt = state["brand_prompt"]

    # ── Step 1: visual style guide ──────────────────────────────────────────
    print("[strategy] building visual style guide…")
    try:
        style_guide = await _build_visual_style_guide(llm, brand_prompt)
        print(f"[strategy] style guide ({len(style_guide)} chars)")
    except Exception as exc:
        style_guide = "Photorealistic, professional photography, natural lighting, 8K quality, no illustration, no CGI."
        print(f"[strategy] style guide failed, using fallback: {exc}")

    # ── Step 2: content calendar ────────────────────────────────────────────
    posts_per_day = min(2, len(platforms))
    total_posts   = num_days * posts_per_day

    guidelines = "\n".join(
        f"  - {p}: {_PLATFORM_GUIDELINES.get(p, 'engaging, on-brand')}"
        for p in platforms
    )

    rotation: list[str] = []
    for i in range(total_posts):
        rotation.append(platforms[i % len(platforms)])
    rotation_hint = ", ".join(f"Day {(i // posts_per_day) + 1}→{p}" for i, p in enumerate(rotation))

    prompt = f"""You are a senior social media strategist and photographer.
Create a {num_days}-day content calendar for this brand.

Brand / Campaign Brief:
{brand_prompt}

━━━ BRAND VISUAL STYLE GUIDE ━━━
{style_guide}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Platforms available: {', '.join(platforms)}
Platform guidelines:
{guidelines}

Distribution rules:
- Generate exactly {total_posts} posts total
- Roughly {posts_per_day} post(s) per day, rotating across platforms
- Suggested rotation: {rotation_hint}
- Each day must have a distinct theme (product feature, behind-the-scenes, social proof, lifestyle, sustainability, etc.)

IMAGE PROMPT RULES (critical):
- Start every image_prompt with "Photograph of …"
- Apply the visual style guide above to every image prompt
- Include specific lighting, camera, mood, and colour details from the guide
- Explicitly include: "photorealistic, hyperrealistic, no illustration, no CGI, no cartoon, no digital art"
- The subject must be a real-looking scene — staged home, real person, physical product, etc.
- image_prompt length: 60–120 words

CAPTION RULES:
- Platform-native tone (see guidelines above)
- Authentic — not copy-pasted across platforms
- Hashtags as a JSON array WITHOUT the # symbol
- content_type: one of "image", "carousel", "text"

Return ONLY a valid JSON array — no markdown, no explanation, no code fences:
[
  {{
    "day": 1,
    "platform": "Instagram",
    "content_type": "image",
    "caption": "...",
    "hashtags": ["brand", "marketing"],
    "image_prompt": "Photograph of ..."
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
            print(f"[strategy] attempt {attempt + 1} — {len(raw)} chars")

            if raw.startswith("```"):
                parts = raw.split("```")
                raw = parts[1] if len(parts) > 1 else raw
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.strip()

            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                for v in parsed.values():
                    if isinstance(v, list):
                        parsed = v
                        break
            if not isinstance(parsed, list):
                raise ValueError(f"Expected JSON array, got {type(parsed).__name__}")

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

    state["errors"].append(f"strategy_node failed after 3 attempts: {last_error}")
    return state
