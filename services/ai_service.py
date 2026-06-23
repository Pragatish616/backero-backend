"""
ai_service.py — All AI calls using Google Gemini.

Model: gemini-2.0-flash (fast, free-tier friendly, great at JSON)
Falls back to hardcoded templates gracefully if GEMINI_API_KEY is missing.
"""
from __future__ import annotations
import os, json, re
from typing import Optional

_client = None


def _get_client():
    global _client
    if _client is None:
        import google.generativeai as genai
        key = os.getenv("GEMINI_API_KEY", "").strip()
        if not key or key == "your-gemini-api-key-here":
            return None
        genai.configure(api_key=key)
        _client = genai.GenerativeModel("gemini-1.5-flash")
    return _client


def _ask(prompt: str, system: str = "") -> Optional[str]:
    """Single Gemini call — returns text or None on failure."""
    client = _get_client()
    if not client:
        return None
    try:
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        response = client.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"[AI] Gemini call failed: {e}")
        return None


def _parse_json(text: str) -> Optional[dict | list]:
    """Strip markdown fences and parse JSON."""
    text = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.MULTILINE)
    text = re.sub(r"\s*```$", "", text.strip(), flags=re.MULTILINE)
    try:
        return json.loads(text.strip())
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────
#  PHASE 1 — Nugget Extraction
# ─────────────────────────────────────────────────────────────

def extract_nuggets_ai(topic: str, research_text: str = "", niche: str = "") -> list[dict]:
    context = research_text if research_text else f"Topic: {topic}, Niche: {niche}"

    prompt = f"""You are a viral video content strategist specialising in short-form content.

Given this topic and research, extract exactly 3 Knowledge Nuggets for a viral video hook.

TOPIC: {topic}
NICHE: {niche or 'General'}
RESEARCH / CONTEXT:
{context[:3000]}

Return ONLY a JSON array with exactly 3 objects. Each object must have:
- "type": one of "Shocking Fact", "Practical Hack", "Story Hook"
- "text": nugget text as it would appear on screen (max 15 words, punchy, specific, include real numbers)
- "source": where this insight comes from (e.g. "Dermatology Research 2026")
- "rationale": why this nugget works psychologically (1 sentence)
- "color": "#EF4444" for Shocking Fact, "#22C55E" for Practical Hack, "#F59E0B" for Story Hook

Rules:
- Include specific numbers or percentages where possible
- Each nugget must be specific to "{topic}" — no generic filler
- Shocking Fact: counterintuitive or surprising stat
- Practical Hack: immediately actionable in under 60 seconds
- Story Hook: creates curiosity about a personal result

Return ONLY the JSON array, no other text."""

    raw = _ask(prompt, system="You are a viral content expert. Return only valid JSON arrays.")
    if not raw:
        return [
            {"type": "Shocking Fact", "text": f"73% of people get {topic.lower()} completely wrong", "source": "Industry Research 2026", "rationale": "Shocking percentage creates immediate credibility", "color": "#EF4444"},
            {"type": "Practical Hack", "text": f"The 30-second {topic.lower()} trick that experts actually use", "source": "Expert Interviews", "rationale": "Actionable tip drives saves and shares", "color": "#22C55E"},
            {"type": "Story Hook", "text": f"I tried {topic.lower()} for 30 days and this happened", "source": "Personal Experience", "rationale": "Personal story builds emotional connection", "color": "#F59E0B"},
        ]

    parsed = _parse_json(raw)
    if isinstance(parsed, list) and len(parsed) >= 3:
        color_map = {"Shocking Fact": "#EF4444", "Practical Hack": "#22C55E", "Story Hook": "#F59E0B"}
        for n in parsed:
            n["color"] = color_map.get(n.get("type", ""), "#6366F1")
        return parsed[:3]

    return [
        {"type": "Shocking Fact", "text": f"73% of people get {topic.lower()} completely wrong", "source": "Industry Research 2026", "rationale": "Shocking percentage creates immediate credibility", "color": "#EF4444"},
        {"type": "Practical Hack", "text": f"The 30-second {topic.lower()} trick that experts actually use", "source": "Expert Interviews", "rationale": "Actionable tip drives saves and shares", "color": "#22C55E"},
        {"type": "Story Hook", "text": f"I tried {topic.lower()} for 30 days and this happened", "source": "Personal Experience", "rationale": "Personal story builds emotional connection", "color": "#F59E0B"},
    ]


# ─────────────────────────────────────────────────────────────
#  PHASE 1 — Hook Validation AI Enhancement
# ─────────────────────────────────────────────────────────────

def enhance_hook_validation(hook_text: str, base_result: dict) -> dict:
    if base_result.get("valid"):
        return base_result

    prompt = f"""You are a viral video hook expert. Analyse this hook and suggest improvements.

HOOK: "{hook_text}"
ISSUES FOUND: {', '.join(base_result.get('issues', []))}

Return ONLY JSON:
{{
  "rewrite_primary": "improved version under 15 words with a specific number",
  "rewrite_alternative": "different angle rewrite under 15 words",
  "why_it_works": "one sentence explaining the psychology"
}}"""

    raw = _ask(prompt)
    if raw:
        parsed = _parse_json(raw)
        if isinstance(parsed, dict):
            base_result["ai_rewrites"] = parsed
    return base_result


# ─────────────────────────────────────────────────────────────
#  PHASE 3 — Screenplay Generation
# ─────────────────────────────────────────────────────────────

def generate_screenplay_ai(phase1: dict, phase2: dict) -> Optional[list[dict]]:
    topic = phase1.get("topic", phase1.get("hook_text", "the topic"))
    hook = phase1.get("hook_text", "")
    niche = phase1.get("niche", "")
    platform = phase1.get("platform", "Instagram")
    content_style = phase1.get("content_style", "Demonstration")
    structure = phase2.get("selected_structure", "Step-by-Step")
    fmt = phase2.get("selected_format", "Talking Head")
    nuggets = phase1.get("knowledge_nuggets", [])
    nugget_text = "\n".join([f"- [{n.get('type','Fact')}] {n.get('text','')}" for n in nuggets]) if nuggets else f"Key insight about {topic}"

    prompt = f"""You are an expert viral short-form video director and screenplay writer.

Write a complete scene-by-scene screenplay for a viral {platform} video.

VIDEO BRIEF:
- Topic: {topic}
- Hook: {hook or topic}
- Niche: {niche}
- Content Style: {content_style}
- Structure: {structure}
- Format: {fmt}
- Knowledge Nuggets:
{nugget_text}

Generate exactly 5 scenes following the "{structure}" structure.

Return ONLY a JSON array of 5 scene objects. Each scene must have:
- "sceneNum": integer (1-5)
- "name": scene name in CAPS (e.g. "THE HOOK", "AUTHORITY GAP", "THE HACK", "THE PROOF", "CTA")
- "timingStart": float seconds
- "timingEnd": float seconds
- "duration": float (timingEnd - timingStart)
- "dialogue": exact words the actor says — specific to {topic}, punchy, under 20 words per scene
- "action": parenthetical director note — what the actor does physically (start with "(Actor ")
- "camera": object with "shot" (e.g. "Close-up"), "angle" (e.g. "Low angle"), "movement" (e.g. "Push in")
- "actor": object with "expression" (string), "energy" (integer 1-10), "pace" ("fast"/"medium"/"slow")
- "visual": text overlay or editor direction (e.g. "BOLD TEXT: '73%' appears at 0.3s")
- "audio": music/SFX direction (e.g. "Trending audio hit + whoosh SFX at 0.0s")
- "editMarkers": array of 2-3 objects each with "time" (e.g. "1.5s") and "event" (edit action)

Rules:
- Total runtime 28-32 seconds across all 5 scenes
- Scene 1 THE HOOK must be 0-3 seconds using the hook text: "{hook or topic}"
- Scene 5 CTA must end with "Follow for more {niche.lower() or 'tips'}" style call to action
- All dialogue must be specific to "{topic}" — absolutely no generic filler
- Make it native to {platform} platform

Return ONLY the JSON array, nothing else."""

    raw = _ask(prompt, system="You are a viral video director. Return only valid JSON arrays with no markdown.")
    if not raw:
        return None

    parsed = _parse_json(raw)
    if isinstance(parsed, list) and len(parsed) >= 3:
        return parsed
    return None


# ─────────────────────────────────────────────────────────────
#  PHASE 3 — Single Scene Regeneration
# ─────────────────────────────────────────────────────────────

def regenerate_scene_ai(scene: dict, phase1: dict, phase2: dict, direction: str = "") -> Optional[dict]:
    topic = phase1.get("topic", "the topic")

    prompt = f"""You are a viral video director. Rewrite this single scene for a video about "{topic}".

CURRENT SCENE:
{json.dumps(scene, indent=2)}

DIRECTOR'S NOTE: {direction or 'Make the dialogue more specific and punchy. Improve the action description.'}

Return ONLY a JSON object with the exact same structure and same sceneNum, name, timingStart, timingEnd.
Improve the dialogue, action, visual and audio directions. Keep timing identical."""

    raw = _ask(prompt)
    if raw:
        parsed = _parse_json(raw)
        if isinstance(parsed, dict) and "sceneNum" in parsed:
            return parsed
    return None


# ─────────────────────────────────────────────────────────────
#  PHASE 4 — Quality Fix Suggestions
# ─────────────────────────────────────────────────────────────

def get_fix_suggestions_ai(failed_checks: list[dict], scenes: list[dict], topic: str) -> dict:
    if not failed_checks:
        return {}

    checks_summary = "\n".join([
        f"- {c['id']} [{c['severity']}] {c['name']}: {c.get('evidence','')}"
        for c in failed_checks[:8]
    ])

    prompt = f"""You are a video quality consultant reviewing a short-form video about "{topic}".

FAILED CHECKS:
{checks_summary}

For each check ID, provide a specific actionable fix (1-2 sentences, specific to "{topic}").

Return ONLY JSON:
{{"CHECK_ID": "specific fix instruction"}}"""

    raw = _ask(prompt)
    if raw:
        parsed = _parse_json(raw)
        if isinstance(parsed, dict):
            return parsed
    return {}


# ─────────────────────────────────────────────────────────────
#  PHASE 5 — Production Summary
# ─────────────────────────────────────────────────────────────

def generate_production_summary_ai(meta: dict, scenes: list[dict]) -> Optional[str]:
    title = meta.get("title", "Video")
    platform = meta.get("platform", "")
    fmt = meta.get("format", "")
    score = meta.get("score", 0)
    scenes_summary = " → ".join([s.get("name", "") for s in scenes[:6]])

    prompt = f"""Write a 3-sentence executive production summary for this viral video brief.

Title: {title}
Platform: {platform}
Format: {fmt}
Structure: {scenes_summary}
Quality Score: {score}/100

Make it sound like a professional production brief — confident, specific, actionable. No bullet points."""

    return _ask(prompt)
