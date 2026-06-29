"""
Backero Phase 1 Service
"""

from __future__ import annotations
import re

VALID_PLATFORMS = ["Instagram", "TikTok", "YouTube Shorts", "Facebook Reels", "Multi-Platform"]
VALID_NICHES = ["Skincare", "Fitness", "Finance", "Food", "Tech", "Lifestyle"]

SUB_NICHES = {
    "Skincare": ["Anti-aging", "Acne", "Routines", "Product Reviews", "Ingredients", "SPF"],
    "Fitness": ["Weight Loss", "Muscle Building", "Home Workouts", "Yoga", "Running", "Nutrition"],
    "Finance": ["Investing", "Budgeting", "Crypto", "Side Hustles", "Tax Tips", "Credit"],
    "Food": ["Recipes", "Restaurant Reviews", "Meal Prep", "Baking", "Healthy Eating", "Street Food"],
    "Tech": ["Gadgets", "Apps", "AI Tools", "Coding", "Gaming", "Smart Home"],
    "Lifestyle": ["Productivity", "Travel", "Fashion", "Minimalism", "Self-Care", "Relationships"],
}

DEFAULT_BLACKLIST = ["game-changer", "revolutionary", "unlock", "secret", "mind-blowing", "insane"]


def get_sub_niches(niche: str) -> list[str]:
    return SUB_NICHES.get(niche, [])


def validate_hook(hook_text: str, topic: str = "", niche: str = "",
                  blacklist: list[str] | None = None, language: str = "EN") -> dict:
    bl = blacklist or DEFAULT_BLACKLIST
    issues = []
    suggestions = []
    words = hook_text.split()
    score = 100

    if len(words) > 15:
        issues.append("Hook exceeds 15 words")
        score -= 20
        suggestions.append("Shorten to under 15 words for maximum impact")
    if len(words) < 3:
        issues.append("Hook is too short (under 3 words)")
        score -= 15

    lower = hook_text.lower()
    for bw in bl:
        if bw.lower() in lower:
            issues.append(f"Contains overused word: '{bw}'")
            score -= 15
            suggestions.append(f"Replace '{bw}' with a specific claim or data point")

    has_specific = bool(re.search(r'\d+%?|\$\d+|#\d+|\d+ out of \d+', hook_text))
    if not has_specific:
        issues.append("No specific claim (number, percentage, or data point)")
        score -= 10
        suggestions.append("Add a number or percentage to increase credibility")

    curiosity_words = ["but", "actually", "nobody", "don't", "stop", "wrong",
                       "mistake", "truth", "really", "think", "?", "wait",
                       "okay so", "here's the thing"]
    has_curiosity = any(w in lower for w in curiosity_words)
    if not has_curiosity:
        issues.append("Weak curiosity gap — no tension word detected")
        score -= 10
        suggestions.append("Add a curiosity trigger: 'but', 'nobody talks about', 'the mistake'")

    score = max(0, min(100, score))
    result = {
        "valid": len(issues) == 0,
        "score": score,
        "issues": issues,
        "suggestions": suggestions,
    }

    if issues:
        try:
            from services.ai_service import enhance_hook_validation
            result = enhance_hook_validation(hook_text, result, topic, niche, language)
        except Exception:
            pass

    return result


def extract_nuggets(topic: str, research_text: str = "", niche: str = "",
                    language: str = "EN") -> list[dict]:
    from services.ai_service import extract_nuggets_ai
    return extract_nuggets_ai(topic=topic, research_text=research_text,
                              niche=niche, language=language)


def generate_fluff_examples(topic: str, niche: str = "", language: str = "EN") -> list[str]:
    from services.ai_service import generate_fluff_examples_ai
    return generate_fluff_examples_ai(topic=topic, niche=niche, language=language)


def suggest_topics(niche: str, sub_niche: str = "", language: str = "EN") -> list[dict]:
    from services.ai_service import suggest_topics_ai
    return suggest_topics_ai(niche=niche, sub_niche=sub_niche, language=language)


def upsert_phase1(supabase, brief_id: str, data: dict) -> dict:
    data["brief_id"] = brief_id
    clean = {k: v for k, v in data.items() if v is not None}

    if "knowledge_nuggets" in clean and clean["knowledge_nuggets"]:
        clean["knowledge_nuggets"] = [
            n if isinstance(n, dict) else n.model_dump()
            for n in clean["knowledge_nuggets"]
        ]

    if "selected_nugget" in clean and clean["selected_nugget"]:
        if hasattr(clean["selected_nugget"], "model_dump"):
            clean["selected_nugget"] = clean["selected_nugget"].model_dump()

    # Keep selected_nugget JSONB in sync with selected_nugget_index
    idx = clean.get("selected_nugget_index")
    nuggets = clean.get("knowledge_nuggets", [])
    if idx is not None and nuggets and 0 <= idx < len(nuggets):
        clean["selected_nugget"] = nuggets[idx]

    result = supabase.table("phase1_data").upsert(clean, on_conflict="brief_id").execute()
    return result.data[0] if result.data else {}


def save_selected_nugget(supabase, brief_id: str, selected_nugget: dict) -> dict:
    result = supabase.table("phase1_data").update({
        "selected_nugget": selected_nugget
    }).eq("brief_id", brief_id).execute()
    return result.data[0] if result.data else {}
