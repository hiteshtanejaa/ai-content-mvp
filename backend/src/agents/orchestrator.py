"""
Config B — Hierarchical Orchestration Node
==========================================
Architecture (contrast with Config A sequential):

  Config A:  strategy_node ──────────────────────────────► content_node ► END
             (one LLM call plans ALL platforms together)

  Config B:  orchestrator_node ──► [Instagram sub-agent ║ LinkedIn sub-agent ║ ...]
                                    (parallel, isolated)
                                         │
                                   synthesiser_node ──────► content_node ► END
                                   (merge + consistency check)

Key academic differences:
  - Sub-agents are platform-specialists; they never see each other's output during generation
  - Parallel execution: each sub-agent runs concurrently via asyncio.gather
  - Synthesiser resolves any cross-platform inconsistency after the fact
  - Overhead: one extra LLM call (orchestrator briefs) vs Config A
"""

import asyncio
import json

from src.services.llm import get_llm
from src.services.state import CampaignState, Post, PostStatus
from src.agents.strategy import _build_visual_style_guide

_PLATFORM_GUIDELINES = {
    "Instagram": "visual-first, 2-4 sentences, 5-8 hashtags in caption, warm engaging tone",
    "Twitter":   "under 280 chars total including hashtags, punchy hook, 1-2 hashtags",
    "LinkedIn":  "professional thought-leadership, 3-5 sentences, NO hashtags",
    "Facebook":  "friendly and community-focused, 2-3 sentences, 2-3 hashtags",
    "TikTok":    "energetic, trend-aware, short punchy lines, heavy emoji, call-to-action",
}


async def _platform_sub_agent(
    llm,
    platform: str,
    brand_prompt: str,
    style_guide: str,
    num_days: int,
    platform_brief: str,
) -> list[Post]:
    """
    Dedicated sub-agent for a single platform.
    Generates num_days posts independently without knowledge of other platforms.
    """
    guidelines = _PLATFORM_GUIDELINES.get(platform, "engaging, on-brand")

    prompt = f"""You are a specialist {platform} content creator. You work independently.

Brand Brief:
{brand_prompt}

Visual Style Guide (apply to every image prompt):
{style_guide}

Your strategic brief from the campaign orchestrator:
{platform_brief}

Platform rules for {platform}: {guidelines}

Generate exactly {num_days} posts — one per day — each with a distinct theme.

IMAGE PROMPT RULES:
- Start every image_prompt with "Photograph of …"
- Apply all details from the visual style guide (lighting, lens, colour palette, mood)
- Append: "photorealistic, hyperrealistic, no illustration, no CGI, no cartoon, no digital art"
- Length: 60–120 words

Return ONLY a valid JSON array, no markdown, no explanation:
[
  {{
    "day": 1,
    "platform": "{platform}",
    "content_type": "image",
    "caption": "...",
    "hashtags": ["tag1", "tag2"],
    "image_prompt": "Photograph of ..."
  }}
]"""

    response = await llm.client.chat.completions.create(
        model=llm.model,
        temperature=0.85,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4096,
    )

    raw = (response.choices[0].message.content or "").strip()
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
        raise ValueError(f"Sub-agent for {platform} returned non-list: {type(parsed)}")

    return [
        Post(
            day=int(item["day"]),
            platform=str(item.get("platform", platform)),
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


async def orchestrator_node(state: CampaignState) -> CampaignState:
    """
    Hierarchical orchestrator (Config B) — LangGraph node.

    Step 1 — Orchestrator:
        Builds a brand visual style guide (shared across all sub-agents).
        Generates a short strategic brief for each platform, giving each
        sub-agent its own angle without cross-contamination.

    Step 2 — Parallel sub-agents:
        Each platform sub-agent runs concurrently via asyncio.gather.
        They share the style guide but NOT each other's content output.

    Step 3 — Synthesiser:
        Merges all platform outputs, sorts by day, and validates completeness.
        Appends errors for any platform that failed rather than crashing.
    """
    llm = get_llm(temperature=0.7)
    brand_prompt  = state["brand_prompt"]
    platforms     = state["platforms"]
    num_days      = state["num_days"]

    # ── Step 1a: Shared visual style guide ────────────────────────────────────
    print("[orchestrator] building visual style guide…")
    try:
        style_guide = await _build_visual_style_guide(llm, brand_prompt)
        print(f"[orchestrator] style guide ({len(style_guide)} chars)")
    except Exception as exc:
        style_guide = (
            "Photorealistic, professional photography, natural lighting, "
            "8K quality, no illustration, no CGI."
        )
        print(f"[orchestrator] style guide fallback: {exc}")

    # ── Step 1b: Per-platform strategic briefs ────────────────────────────────
    print(f"[orchestrator] generating platform briefs for {platforms}…")
    platform_list = "\n".join(f"- {p}" for p in platforms)

    brief_prompt = f"""You are a senior campaign orchestrator managing specialist content creators.

Brand Brief:
{brand_prompt}

You are directing a {num_days}-day campaign across:
{platform_list}

For EACH platform write a 2–3 sentence brief instructing that platform's specialist on:
1. The day-by-day theme progression across {num_days} days
2. The unique tone/angle that differentiates this platform from others
3. One content tactic specific to that platform's algorithm or audience

Return ONLY valid JSON — keys are platform names, values are brief strings:
{{{{"Instagram": "brief...", "LinkedIn": "brief..."}}}}"""

    try:
        brief_resp = await llm.client.chat.completions.create(
            model=llm.model,
            temperature=0.6,
            messages=[{"role": "user", "content": brief_prompt}],
            max_tokens=1024,
        )
        raw = (brief_resp.choices[0].message.content or "").strip()
        if raw.startswith("```"):
            parts = raw.split("```")
            raw = parts[1] if len(parts) > 1 else raw
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        platform_briefs: dict[str, str] = json.loads(raw)
        print(f"[orchestrator] briefs ready for: {list(platform_briefs.keys())}")
    except Exception as exc:
        platform_briefs = {
            p: f"Create {num_days} days of high-quality, platform-native content for {p}."
            for p in platforms
        }
        print(f"[orchestrator] brief fallback: {exc}")

    # ── Step 2: Parallel platform sub-agents ─────────────────────────────────
    print(f"[orchestrator] launching {len(platforms)} parallel sub-agents…")

    async def run_sub_agent(platform: str) -> list[Post]:
        brief = platform_briefs.get(platform, f"Create {num_days} days of {platform} content.")
        print(f"[sub-agent:{platform}] starting…")
        for attempt in range(3):
            try:
                posts = await _platform_sub_agent(
                    llm, platform, brand_prompt, style_guide, num_days, brief
                )
                print(f"[sub-agent:{platform}] ✓ {len(posts)} posts generated")
                return posts
            except Exception as exc:
                print(f"[sub-agent:{platform}] attempt {attempt + 1} failed: {exc}")
        state["errors"].append(f"sub-agent failed for {platform} after 3 attempts")
        return []

    results: list[list[Post]] = await asyncio.gather(
        *[run_sub_agent(p) for p in platforms]
    )

    # ── Step 3: Synthesiser — merge + sort ───────────────────────────────────
    all_posts: list[Post] = []
    for platform_posts in results:
        all_posts.extend(platform_posts)

    # Sort by day first, then platform name for deterministic ordering
    all_posts.sort(key=lambda p: (p["day"], p["platform"]))

    print(f"[orchestrator] synthesiser merged {len(all_posts)} posts across {len(platforms)} platforms")

    state["posts"] = all_posts
    state["current_step"] = "content"
    return state
