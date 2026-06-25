from __future__ import annotations
import os, json, re
from typing import Optional

LANGUAGE_INSTRUCTIONS = {
    "EN": "Write everything in English.",
    "HI": "Write all dialogue and on-screen text in Hindi (Devanagari script). Use conversational Hindi.",
    "TA": "Write all dialogue and on-screen text in Tamil. Use colloquial Tamil Nadu spoken Tamil.",
    "HIN-EN": "Write dialogue in Hinglish - natural Hindi+English mix as spoken by urban Indian youth. Use Roman script.",
    "TE": "Write all dialogue and on-screen text in Telugu.",
    "KN": "Write all dialogue and on-screen text in Kannada.",
    "ML": "Write all dialogue and on-screen text in Malayalam.",
    "MR": "Write all dialogue and on-screen text in Marathi.",
    "BN": "Write all dialogue and on-screen text in Bengali.",
    "GU": "Write all dialogue and on-screen text in Gujarati.",
}

_client = None

def _get_client():
    global _client
    if _client is None:
        from anthropic import Anthropic
        key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        if not key or key == "your-anthropic-api-key-here":
            return None
        _client = Anthropic(api_key=key)
    return _client

def _ask(prompt: str, system: str = "") -> Optional[str]:
    client = _get_client()
    if not client:
        return None
    try:
        kwargs = {
            "model": "claude-sonnet-4-6",
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system
        response = client.messages.create(**kwargs)
        return response.content[0].text.strip()
    except Exception as e:
        print(f"[AI] Claude call failed: {e}")
        return None

def _parse_json(text: str):
    text = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.MULTILINE)
    text = re.sub(r"\s*```$", "", text.strip(), flags=re.MULTILINE)
    try:
        return json.loads(text.strip())
    except Exception:
        return None

# ── PHASE 1: Nugget Extraction ──────────────────────────────────────────────

def _nugget_fallback(topic: str, niche: str = "") -> list[dict]:
    t = topic.lower()
    n = niche.lower() if niche else "this"
    return [
        {"type": "Shocking Fact", "text": f"Most {n} experts hide this truth about {t}", "source": "Industry Data 2025", "rationale": "Creates us-vs-them tension that drives shares", "color": "#EF4444"},
        {"type": "Practical Hack", "text": f"The 2-minute {t} technique professionals actually use", "source": "Expert Interviews", "rationale": "Immediacy plus exclusivity triggers saves", "color": "#22C55E"},
        {"type": "Story Hook", "text": f"I changed one thing about {t} — got 3x results in 7 days", "source": "Personal Experience", "rationale": "Specific outcome teaser triggers curiosity gap", "color": "#F59E0B"},
    ]

def extract_nuggets_ai(topic: str, research_text: str = "", niche: str = "", language: str = "EN") -> list[dict]:
    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["EN"])
    context = research_text if research_text else f"Topic: {topic}, Niche: {niche}"
    system = (
        "You are a world-class viral short-form video strategist who has helped 500+ creators hit 10M+ views. "
        "Deep expertise in Instagram Reels, YouTube Shorts, TikTok virality. "
        "You ONLY return valid JSON arrays with no extra text."
    )
    prompt = f"""Extract 3 Knowledge Nuggets for a viral video about: "{topic}"
Niche: {niche or "General"}
LANGUAGE: {lang_instruction}

Research/Context:
{context[:3000]}

QUALITY BAR — each nugget must be:
1. SPECIFIC to "{topic}" with real numbers — NO generic filler
2. Emotionally triggering: surprise, FOMO, or burning curiosity
3. Platform-native: sounds like a viral Reel, not Wikipedia
4. Written in the specified language with cultural context

Return ONLY a JSON array of exactly 3 objects, each with:
- "type": "Shocking Fact" | "Practical Hack" | "Story Hook"
- "text": max 15 words, punchy, specific, with numbers where possible
- "source": credible source (e.g. "Journal of Dermatology 2024")
- "rationale": psychological reason this works (1 sentence)
- "color": "#EF4444" for Shocking Fact | "#22C55E" for Practical Hack | "#F59E0B" for Story Hook

Return ONLY the JSON array."""
    raw = _ask(prompt, system=system)
    if not raw:
        return _nugget_fallback(topic, niche)
    parsed = _parse_json(raw)
    if isinstance(parsed, list) and len(parsed) >= 3:
        color_map = {"Shocking Fact": "#EF4444", "Practical Hack": "#22C55E", "Story Hook": "#F59E0B"}
        for n in parsed:
            n["color"] = color_map.get(n.get("type", ""), "#6366F1")
        return parsed[:3]
    return _nugget_fallback(topic, niche)

def enhance_hook_validation(hook_text: str, base_result: dict) -> dict:
    if base_result.get("valid"):
        return base_result
    prompt = f"""Viral video hook expert. Analyse and improve this hook.
HOOK: "{hook_text}"
ISSUES: {', '.join(base_result.get('issues', []))}
Return ONLY JSON: {{"rewrite_primary": "improved hook under 15 words with a specific number", "rewrite_alternative": "different angle rewrite under 15 words", "why_it_works": "one sentence on the psychology"}}"""
    raw = _ask(prompt)
    if raw:
        parsed = _parse_json(raw)
        if isinstance(parsed, dict):
            base_result["ai_rewrites"] = parsed
    return base_result

# ── PHASE 3: Screenplay Generation ─────────────────────────────────────────

def generate_screenplay_ai(phase1: dict, phase2: dict) -> Optional[list[dict]]:
    topic = phase1.get("topic", phase1.get("hook_text", "the topic"))
    hook = phase1.get("hook_text", "")
    niche = phase1.get("niche", "")
    platform = phase1.get("platform", "Instagram")
    content_style = phase1.get("content_style", "Demonstration")
    structure = phase2.get("selected_structure", "Step-by-Step")
    fmt = phase2.get("selected_format", "Talking Head")
    language = phase1.get("language", "EN")
    actor_name = phase1.get("on_camera_actor", "the creator")
    actor_brief = phase1.get("actor_brief", "")
    content_creator = phase1.get("content_creator", "")
    brand = phase1.get("brand_company", "")
    estimated_length = phase1.get("estimated_length", "30-60s")
    aspect_ratio = phase1.get("aspect_ratio", "9:16")
    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["EN"])
    nuggets = phase1.get("knowledge_nuggets", [])
    nugget_text = "\n".join([f"- [{n.get('type','Fact')}] {n.get('text','')}" for n in nuggets]) if nuggets else f"Key insight about {topic}"
    actor_context = ""
    if actor_name and actor_name != "the creator":
        actor_context += f"\nACTOR: {actor_name}"
    if actor_brief:
        actor_context += f"\nACTOR BRIEF: {actor_brief}"
    if content_creator:
        actor_context += f"\nCONTENT CREATOR: {content_creator}"
    if brand:
        actor_context += f"\nBRAND: {brand}"
    system = (
        "You are a top-tier viral video director who has produced content for 100M+ view creators. "
        "You write hyper-specific, emotionally charged screenplays native to the platform. "
        "Your scripts hook in under 2 seconds, use precise actor blocking, and never use generic filler. "
        "Every word earns its place. Return only valid JSON arrays."
    )
    prompt = f"""Write a professional viral video screenplay for a {platform} video about "{topic}".

VIDEO BRIEF:
- Topic: {topic}
- Hook: {hook or topic}
- Niche: {niche}
- Content Style: {content_style}
- Structure: {structure}
- Format: {fmt}
- Platform: {platform} ({aspect_ratio}, ~{estimated_length})
- LANGUAGE: {lang_instruction}{actor_context}
- Knowledge Nuggets to weave in:
{nugget_text}

Generate exactly 5 scenes. NON-NEGOTIABLE rules:

Scene 1 (THE HOOK, 0-3 sec): Use EXACTLY: "{hook or topic}"
- Opens mid-action, energy at 10/10
- First word creates pattern interrupt (NOT "Hey", "So", "Welcome")
- Creates open loop viewer MUST close by watching

Scenes 2-5: Follow the "{structure}" beats.
- Each scene delivers value the previous did not
- Dialogue is conversational, not scripted-sounding
- Scene 5 CTA is specific to {niche.lower() or 'this topic'}

Return ONLY a JSON array of exactly 5 scene objects, each with:
- "sceneNum": int 1-5
- "name": scene name in CAPS (Scene 1 is always "THE HOOK")
- "timingStart": float seconds
- "timingEnd": float seconds (total 28-35 sec)
- "duration": float seconds
- "dialogue": EXACT words {actor_name} says in {language} — specific, punchy, zero filler
- "action": "(Actor {actor_name}: [precise physical blocking])"
- "camera": {{"shot": "...", "angle": "...", "movement": "..."}}
- "actor": {{"expression": "...", "energy": 1-10, "pace": "fast/medium/slow"}}
- "visual": text overlay direction with timing and placement
- "audio": music + SFX with exact timing cues
- "editMarkers": [{{"time": "Xs", "event": "edit action"}}] x2-3

Return ONLY the JSON array."""
    raw = _ask(prompt, system=system)
    if not raw:
        return None
    parsed = _parse_json(raw)
    if isinstance(parsed, list) and len(parsed) >= 5:
        return parsed
    return None

# ── PHASE 3: Single Scene Regeneration ─────────────────────────────────────

def regenerate_scene_ai(scene: dict, phase1: dict, phase2: dict, direction: str = "") -> Optional[dict]:
    topic = phase1.get("topic", "the topic")
    language = phase1.get("language", "EN")
    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["EN"])
    actor_name = phase1.get("on_camera_actor", "the creator")
    actor_brief = phase1.get("actor_brief", "")
    prompt = f"""Viral video director. Rewrite this scene for a video about "{topic}".
Language: {lang_instruction}
Actor: {actor_name}{(' - ' + actor_brief) if actor_brief else ''}

CURRENT SCENE:
{json.dumps(scene, indent=2)}

DIRECTOR NOTE: {direction or 'Make dialogue more specific, punchy, and emotionally charged. Improve actor blocking to be immediately executable.'}

Return ONLY a JSON object — identical structure, same sceneNum/name/timingStart/timingEnd.
Improve: dialogue (more specific/punchy in correct language), action (precise blocking), visual, audio."""
    raw = _ask(prompt)
    if raw:
        parsed = _parse_json(raw)
        if isinstance(parsed, dict) and "sceneNum" in parsed:
            return parsed
    return None

# ── PHASE 4: Quality Fix Suggestions ───────────────────────────────────────

def get_fix_suggestions_ai(failed_checks: list[dict], scenes: list[dict], topic: str) -> dict:
    if not failed_checks:
        return {}
    checks_summary = "\n".join([
        f"- {c['id']} [{c['severity']}] {c['name']}: {c.get('evidence','')}"
        for c in failed_checks[:8]
    ])
    prompt = f"""Video quality consultant reviewing a short-form video about "{topic}".
FAILED CHECKS:
{checks_summary}
For each check ID, provide a specific 1-2 sentence fix specific to "{topic}".
Return ONLY JSON: {{"CHECK_ID": "specific fix instruction"}}"""
    raw = _ask(prompt)
    if raw:
        parsed = _parse_json(raw)
        if isinstance(parsed, dict):
            return parsed
    return {}

# ── PHASE 5: Production Summary ─────────────────────────────────────────────

def generate_production_summary_ai(meta: dict, scenes: list[dict]) -> Optional[str]:
    title = meta.get("title", "Video")
    platform = meta.get("platform", "")
    fmt = meta.get("format", "")
    score = meta.get("score", 0)
    scenes_summary = " -> ".join([s.get("name", "") for s in scenes[:6]])
    prompt = f"""Write a 3-sentence executive production summary for this viral video brief.
Title: {title}
Platform: {platform}
Format: {fmt}
Structure: {scenes_summary}
Quality Score: {score}/100
Tone: confident senior creative director — specific, actionable, no fluff."""
    return _ask(prompt)
