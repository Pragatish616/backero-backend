"""
Backero Phase 1 Service - Complete Implementation
Handles hook validation, nugget extraction, and phase 1 data operations
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

NUGGET_COLORS = {
    "Shocking Fact": "#EF4444",
    "Practical Hack": "#22C55E",
    "Story Hook": "#F59E0B",
}


def get_sub_niches(niche: str) -> list[str]:
    """Get sub-niches for a given niche"""
    return SUB_NICHES.get(niche, [])


def validate_hook(hook_text: str, topic: str = "", niche: str = "",
                  blacklist: list[str] | None = None, language: str = "EN") -> dict:
    """
    Validate a hook text against viral content best practices.
    Returns validation result with score, issues, and AI-enhanced suggestions.
    """
    bl = blacklist or DEFAULT_BLACKLIST
    issues = []
    suggestions = []
    words = hook_text.split()
    score = 100

    # Length check
    if len(words) > 15:
        issues.append("Hook exceeds 15 words")
        score -= 20
        suggestions.append("Shorten to under 15 words for maximum impact")
    if len(words) < 3:
        issues.append("Hook is too short (under 3 words)")
        score -= 15

    # Blacklist check
    lower = hook_text.lower()
    for bw in bl:
        if bw.lower() in lower:
            issues.append(f"Contains overused word: '{bw}'")
            score -= 15
            suggestions.append(f"Replace '{bw}' with a specific claim or data point")

    # Specificity check - look for numbers/data
    has_specific = bool(re.search(r'\d+%?|\$\d+|#\d+|\d+ out of \d+', hook_text))
    if not has_specific:
        issues.append("No specific claim (number, percentage, or data point)")
        score -= 10
        suggestions.append("Add a number or percentage to increase credibility")

    # Curiosity gap check
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

    # Enhance with AI rewrites if there are issues
    if issues:
        from services.ai_service import enhance_hook_validation
        result = enhance_hook_validation(hook_text, result, topic, niche, language)

    return result


def extract_nuggets(topic: str, research_text: str = "", niche: str = "",
                    language: str = "EN") -> list[dict]:
    """
    Extract knowledge nuggets using Claude AI, with template fallback.
    Returns exactly 3 nuggets for user to choose from.
    """
    from services.ai_service import extract_nuggets_ai
    return extract_nuggets_ai(topic=topic, research_text=research_text,
                              niche=niche, language=language)


def generate_fluff_examples(topic: str, niche: str = "", language: str = "EN") -> list[str]:
    """Generate examples of fluff phrases to avoid for this topic/niche"""
    from services.ai_service import generate_fluff_examples_ai
    return generate_fluff_examples_ai(topic=topic, niche=niche, language=language)


def suggest_topics(niche: str, sub_niche: str = "", language: str = "EN") -> list[dict]:
    """Suggest viral video topics based on niche"""
    from services.ai_service import suggest_topics_ai
    return suggest_topics_ai(niche=niche, sub_niche=sub_niche, language=language)


def upsert_phase1(supabase, brief_id: str, data: dict) -> dict:
    """
    Upsert phase 1 data to database.
    Handles serialization of complex objects.
    """
    data["brief_id"] = brief_id

    # Remove None values
    clean = {k: v for k, v in data.items() if v is not None}

    # Convert knowledge_nuggets to serializable format
    if "knowledge_nuggets" in clean and clean["knowledge_nuggets"]:
        clean["knowledge_nuggets"] = [
            n if isinstance(n, dict) else n.model_dump()
            for n in clean["knowledge_nuggets"]
        ]

    # Convert selected_nugget to serializable format
    if "selected_nugget" in clean and clean["selected_nugget"]:
        if hasattr(clean["selected_nugget"], "model_dump"):
            clean["selected_nugget"] = clean["selected_nugget"].model_dump()

    result = supabase.table("phase1_data").upsert(clean, on_conflict="brief_id").execute()
    return result.data[0] if result.data else {}


def save_selected_nugget(supabase, brief_id: str, selected_nugget: dict) -> dict:
    """
    Save the user's selected nugget.
    This is called when user clicks on one of the 3 nugget options.
    """
    result = supabase.table("phase1_data").update({
        "selected_nugget": selected_nugget
    }).eq("brief_id", brief_id).execute()

    return result.data[0] if result.data else {}
