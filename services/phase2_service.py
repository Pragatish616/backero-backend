from __future__ import annotations
from copy import deepcopy

CORRELATION_MAP = {
    "educational": {
        "label": "Educational",
        "cta": "Follow / Save",
        "frequency": "3-5x/week",
        "combos": [
            {"format": "Whiteboard", "format_tier": "A", "structure": "Step-by-Step", "structure_num": 2, "recommendation": "best", "why": "Visual explanation + clear steps = highest retention (42.1%)", "data_citation": "2026 Short-Form Study: Whiteboard educational = 42.1% retention"},
            {"format": "Voiceover + Visuals", "format_tier": "A", "structure": "PAS", "structure_num": 9, "recommendation": "best", "why": "Emotional arc drives engagement for pain-point topics", "data_citation": ""},
            {"format": "Visual Prop Explainer", "format_tier": "S", "structure": "List Structure", "structure_num": 7, "recommendation": "good", "why": "Physical props make abstract concepts tangible", "data_citation": ""},
            {"format": "Carousel / Slide Deck", "format_tier": "S", "structure": "3-Level Structure", "structure_num": 8, "recommendation": "good", "why": "Carousel saves highest on Instagram for educational", "data_citation": ""},
            {"format": "Voiceover + Visuals", "format_tier": "A", "structure": "Outcome→Pain→Solution", "structure_num": 10, "recommendation": "good", "why": "Aspirational hook pulls viewers into educational content", "data_citation": ""},
            {"format": "Whiteboard", "format_tier": "A", "structure": "Time-Based Experiment", "structure_num": 12, "recommendation": "available", "why": "Proof-based for data-heavy educational topics", "data_citation": ""},
        ],
    },
    "entertaining_education": {
        "label": "Entertaining Education",
        "cta": "Share / Save",
        "frequency": "3-5x/week",
        "combos": [
            {"format": "Clone (Smart vs Dumb)", "format_tier": "S", "structure": "Smart vs Dumb", "structure_num": 4, "recommendation": "best", "why": "Comedy contrast maximizes shares and watch time", "data_citation": ""},
            {"format": "Trending Audio + B-roll", "format_tier": "A", "structure": "Comparison A vs B", "structure_num": 1, "recommendation": "best", "why": "Trending audio + comparison = algorithmic boost", "data_citation": ""},
            {"format": "Talking Back & Forth", "format_tier": "A", "structure": "PAS", "structure_num": 9, "recommendation": "good", "why": "Dialogue format increases watch time on educational topics", "data_citation": ""},
            {"format": "Visual Prop Explainer", "format_tier": "S", "structure": "Step-by-Step", "structure_num": 2, "recommendation": "good", "why": "Props add entertainment value to educational steps", "data_citation": ""},
            {"format": "B-roll Only", "format_tier": "B", "structure": "List Structure", "structure_num": 7, "recommendation": "available", "why": "B-roll lists work for simple entertaining facts", "data_citation": ""},
        ],
    },
    "storytelling": {
        "label": "Storytelling",
        "cta": "Comment / Share",
        "frequency": "2-3x/week",
        "combos": [
            {"format": "Talking Head + ABR", "format_tier": "S", "structure": "Story Framework", "structure_num": 3, "recommendation": "best", "why": "Personal narration + action B-roll = highest emotional engagement", "data_citation": ""},
            {"format": "Voiceover + Visuals", "format_tier": "A", "structure": "Story Framework", "structure_num": 3, "recommendation": "best", "why": "Cinematic voiceover storytelling creates movie-like experience", "data_citation": ""},
            {"format": "Talking Back & Forth", "format_tier": "A", "structure": "PAS", "structure_num": 9, "recommendation": "good", "why": "Dialogue-driven stories feel more authentic", "data_citation": ""},
            {"format": "B-roll Only", "format_tier": "B", "structure": "Outcome→Pain→Solution", "structure_num": 10, "recommendation": "available", "why": "B-roll stories require strong voiceover to carry narrative", "data_citation": ""},
        ],
    },
    "authority": {
        "label": "Authority",
        "cta": "Follow / DM",
        "frequency": "2-3x/week",
        "combos": [
            {"format": "Whiteboard", "format_tier": "A", "structure": "Step-by-Step", "structure_num": 2, "recommendation": "best", "why": "Whiteboard + structured steps = maximum credibility", "data_citation": ""},
            {"format": "Talking Head + ABR", "format_tier": "S", "structure": "3-Level Structure", "structure_num": 8, "recommendation": "best", "why": "Face-on-camera with layered expertise builds trust", "data_citation": ""},
            {"format": "Visual Prop Explainer", "format_tier": "S", "structure": "Comparison A vs B", "structure_num": 1, "recommendation": "good", "why": "Props as evidence in comparisons strengthen authority", "data_citation": ""},
            {"format": "Carousel / Slide Deck", "format_tier": "S", "structure": "List Structure", "structure_num": 7, "recommendation": "good", "why": "Data-heavy carousels position creator as expert", "data_citation": ""},
        ],
    },
    "personal": {
        "label": "Personal",
        "cta": "Comment / Follow",
        "frequency": "1-2x/week",
        "combos": [
            {"format": "Talking Head + ABR", "format_tier": "S", "structure": "Story Framework", "structure_num": 3, "recommendation": "best", "why": "Personal stories need face + supporting visuals", "data_citation": ""},
            {"format": "Voiceover + Visuals", "format_tier": "A", "structure": "Outcome→Pain→Solution", "structure_num": 10, "recommendation": "good", "why": "Aspirational personal journey with cinematic feel", "data_citation": ""},
            {"format": "Talking Back & Forth", "format_tier": "A", "structure": "PAS", "structure_num": 9, "recommendation": "good", "why": "Internal dialogue format for personal reflection", "data_citation": ""},
        ],
    },
    "trending": {
        "label": "Trending",
        "cta": "Share / Duet",
        "frequency": "Daily",
        "combos": [
            {"format": "Trending Audio + B-roll", "format_tier": "A", "structure": "Smart vs Dumb", "structure_num": 4, "recommendation": "best", "why": "Trending audio + comedy format = maximum algorithmic push", "data_citation": ""},
            {"format": "Clone (Smart vs Dumb)", "format_tier": "S", "structure": "Comparison A vs B", "structure_num": 1, "recommendation": "best", "why": "Clone format on trending topics maximizes shares", "data_citation": ""},
            {"format": "B-roll Only", "format_tier": "B", "structure": "List Structure", "structure_num": 7, "recommendation": "good", "why": "Quick B-roll lists ride trend waves effectively", "data_citation": ""},
            {"format": "Talking Back & Forth", "format_tier": "A", "structure": "PAS", "structure_num": 9, "recommendation": "available", "why": "Dialogue reacting to trends creates engagement", "data_citation": ""},
        ],
    },
}

PLATFORM_BOOSTS = {
    "Instagram": {"Carousel / Slide Deck": 1, "Visual Prop Explainer": 1},
    "TikTok": {"Trending Audio + B-roll": 1, "Clone (Smart vs Dumb)": 1},
    "YouTube Shorts": {"Whiteboard": 1, "Voiceover + Visuals": 1},
    "Facebook Reels": {"Talking Back & Forth": 1, "B-roll Only": 1},
}

RECOMMENDATION_ORDER = {"best": 0, "good": 1, "available": 2, "avoid": 3}


def get_combos(content_type: str, platform: str | None = None) -> dict | None:
    config = CORRELATION_MAP.get(content_type)
    if not config:
        return None
    combos = deepcopy(config["combos"])
    boosts = PLATFORM_BOOSTS.get(platform or "", {})
    for c in combos:
        c["platform_boosted"] = c["format"] in boosts
    # Sort: boosted items get priority within same recommendation level
    combos.sort(key=lambda c: (
        RECOMMENDATION_ORDER.get(c["recommendation"], 9),
        0 if c["platform_boosted"] else 1,
    ))
    return {
        "content_type": content_type,
        "label": config["label"],
        "cta": config["cta"],
        "frequency": config["frequency"],
        "combos": combos,
    }


def get_content_types() -> list[dict]:
    return [
        {"key": k, "label": v["label"], "cta": v["cta"], "frequency": v["frequency"]}
        for k, v in CORRELATION_MAP.items()
    ]


def get_recommendation(content_type: str, platform: str) -> dict | None:
    result = get_combos(content_type, platform)
    if not result or not result["combos"]:
        return None
    best = result["combos"][0]
    return {
        "recommended": best,
        "justification": f"For {result['label']} content on {platform}, '{best['format']}' with '{best['structure']}' is the strongest combination. {best['why']}",
        "platform_boosted": best.get("platform_boosted", False),
    }


def upsert_phase2(supabase, brief_id: str, data: dict) -> dict:
    data["brief_id"] = brief_id
    clean = {k: v for k, v in data.items() if v is not None}
    result = supabase.table("phase2_data").upsert(clean, on_conflict="brief_id").execute()
    return result.data[0] if result.data else {}
