import json
import os
from typing import List, Optional

import openai
from dotenv import load_dotenv

from src.services.llm import get_llm

load_dotenv()


class ContentAgent:
    """Autonomous agent responsible for generating social media content and images."""

    def __init__(self):
        self.llm = get_llm(temperature=0.8)
        # Image generation always uses OpenAI (DALL-E); uses its own client
        self.image_client = openai.AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.image_model = os.getenv("IMAGE_MODEL", "dall-e-3")

    async def generate_content_plan(
        self,
        brand_name: str,
        brand_description: str,
        industry: str,
        tone: str,
        platforms: List[str],
        num_days: int,
    ) -> List[dict]:
        platform_guidelines = {
            "Instagram": "visual-first, 3-5 sentences, 5-10 relevant hashtags, emoji-friendly, warm and engaging",
            "Twitter":   "concise under 280 chars, punchy hook, 1-2 hashtags max, conversational",
            "LinkedIn":  "professional thought-leadership tone, 3-5 sentences, no hashtags, industry insight angle",
            "Facebook":  "friendly and community-focused, 2-4 sentences, 2-3 hashtags, storytelling angle",
            "TikTok":    "energetic and trend-aware, short punchy text, heavy emoji use, call-to-action",
        }

        selected_guidelines = "\n".join(
            f"- {p}: {platform_guidelines.get(p, 'engaging, on-brand')}"
            for p in platforms
        )

        prompt = f"""You are an expert social media content strategist. Create a {num_days}-day content calendar for this brand.

Brand Name: {brand_name}
Brand Description: {brand_description}
Industry: {industry}
Tone: {tone}
Platforms: {', '.join(platforms)}

Platform-specific guidelines:
{selected_guidelines}

For EACH combination of day x platform, generate:
1. A compelling caption (follow platform guidelines strictly)
2. A vivid DALL-E image generation prompt (photorealistic or artistic, brand-consistent, describe lighting, mood, composition)

Rules:
- Each day must have a unique theme or angle (e.g. Day 1: product feature, Day 2: behind the scenes, Day 3: customer story)
- Captions must feel authentic, not generic
- Image prompts must be specific and visual (avoid text in images)
- Total entries = {num_days} days x {len(platforms)} platforms = {num_days * len(platforms)} items

Return ONLY a valid JSON array, no markdown, no explanation:
[
  {{
    "day": 1,
    "platform": "Instagram",
    "caption": "...",
    "image_prompt": "..."
  }}
]"""

        response = await self.llm.client.chat.completions.create(
            model=self.llm.model,
            temperature=self.llm.temperature,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=8192,
        )

        raw = (response.choices[0].message.content or "").strip()
        print(f"[content-agent] response length: {len(raw)} chars")

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
            raise ValueError(f"Expected a JSON array, got: {type(parsed)}")
        return parsed

    async def generate_image(self, prompt: str, brand_name: str) -> Optional[str]:
        try:
            enhanced = (
                f"{prompt}. High-quality professional photography or illustration, "
                "suitable for social media marketing, vibrant and eye-catching."
            )
            response = await self.image_client.images.generate(
                model=self.image_model,
                prompt=enhanced,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            return response.data[0].url
        except Exception as e:
            print(f"[content-agent] image generation failed: {e}")
            return None

    async def regenerate_caption(
        self,
        brand_name: str,
        brand_description: str,
        platform: str,
        tone: str,
        day: int,
        current_caption: Optional[str] = None,
    ) -> str:
        avoid = (
            f"\n\nDo NOT repeat or closely resemble this previous caption:\n{current_caption}"
            if current_caption
            else ""
        )

        prompt = f"""Generate a fresh social media caption for {platform}.

Brand: {brand_name}
Description: {brand_description}
Tone: {tone}
Day theme index: {day}{avoid}

Platform rules:
- Instagram: 3-5 sentences, 5-10 hashtags, emojis, warm tone
- Twitter: under 280 chars, punchy, 1-2 hashtags
- LinkedIn: professional, 3-5 sentences, no hashtags
- Facebook: friendly, 2-4 sentences, storytelling
- TikTok: energetic, short, heavy emoji

Return ONLY the caption text."""

        response = await self.llm.client.chat.completions.create(
            model=self.llm.model,
            temperature=self.llm.temperature,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
        )
        return (response.choices[0].message.content or "").strip()

    async def regenerate_image_prompt(
        self,
        brand_name: str,
        brand_description: str,
        platform: str,
        day: int,
    ) -> str:
        prompt = f"""Generate a detailed DALL-E image prompt for a social media post.

Brand: {brand_name}
Description: {brand_description}
Platform: {platform}
Day: {day}

The prompt must describe: subject, setting, lighting, mood, composition, style.
Avoid text or words in the image.
Return ONLY the image prompt."""

        response = await self.llm.client.chat.completions.create(
            model=self.llm.model,
            temperature=self.llm.temperature,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=256,
        )
        return (response.choices[0].message.content or "").strip()
