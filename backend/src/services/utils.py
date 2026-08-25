"""Shared utility functions for the AI Content Calendar backend."""

import re


def strip_day_artifacts(caption: str) -> str:
    """
    Remove day-numbering artifacts that LLMs tend to inject when generating
    multi-day content calendars (e.g. 'Day 2 at ...', 'Day 5 vibes!', 'Day 3:').

    Applied post-generation in both strategy_node (Config A) and
    _platform_sub_agent (Config B) so captions read as standalone posts.
    """
    if not caption:
        return caption

    # 1. Strip leading "Day N [connector]" at start of caption
    #    Matches: "Day 2 at", "Day 3 of", "Day 4:", "Day 5 vibes", "Day 6 -", etc.
    caption = re.sub(
        r'^Day\s+\d+\s*(at|of|vibes?|calls?(\s+for)?|[-–:]\s*|\w+\s)?\s*',
        '', caption, flags=re.IGNORECASE
    ).strip()

    # 2. Strip inline "Welcome to Day N of/at" → keeps "Welcome to"
    caption = re.sub(
        r'\bDay\s+\d+\s+(of|at)\s+',
        '', caption, flags=re.IGNORECASE
    ).strip()

    # 3. Remove remaining standalone "Day N" occurrences mid-sentence
    caption = re.sub(
        r'\bDay\s+\d+\b[!.,]?\s*',
        '', caption, flags=re.IGNORECASE
    ).strip()

    # 4. Capitalise first letter if stripping lowercased it
    if caption and caption[0].islower():
        caption = caption[0].upper() + caption[1:]

    # 5. Fix double spaces left behind
    caption = re.sub(r'  +', ' ', caption).strip()

    return caption
