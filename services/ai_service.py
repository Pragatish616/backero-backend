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
        "You are a neuroscience-trained viral video director who has generated 500M+ cumulative views across "
        "Instagram Reels, TikTok, and YouTube Shorts. You understand dopamine loop scripting, pattern interrupts, "
        "cognitive open loops, and the 1.7-second attention threshold on mobile feeds.\n\n"
        "YOUR CORE BELIEFS:\n"
        "- The first 0.8 seconds decide if the thumb stops scrolling. No warmup. No buildup. Mid-action ONLY.\n"
        "- Every 2-second window needs a NEW visual stimulus or the viewer leaves.\n"
        "- Dialogue must sound like a friend texting you an urgent secret, NOT a script being read.\n"
        "- Action parentheticals are the REAL screenplay — actors need exact body language, prop handling, "
        "eye direction, facial micro-expressions, and blocking down to the centimeter.\n"
        "- Audio design is 50% of retention — every scene needs specific SFX, music energy level (%), and silence beats.\n"
        "- The CTA must create FOMO — 'save before this gets taken down' beats 'follow for more' every time.\n\n"
        "PSYCHOLOGICAL RETENTION TRICKS YOU ALWAYS USE:\n"
        "1. 3-SECOND PATTERN INTERRUPT: Scene 1 opens with a jarring visual or statement that breaks the scroll pattern.\n"
        "2. NARRATIVE OPEN LOOPS: Tease a payoff in Scene 1 that only resolves in Scene 4-5. Viewer can't leave.\n"
        "3. DOPAMINE MICRO-HITS: Every scene delivers a small 'aha' or emotional spike. No dead air. No filler.\n"
        "4. AUTHORITY-VULNERABILITY TOGGLE: Mix confident expertise with personal admission to build trust.\n"
        "5. VISUAL PACING ESCALATION: Cut frequency increases toward the climax. Slow → Medium → Rapid-fire.\n"
        "6. SILENCE AS A WEAPON: 0.5-1s silence before the biggest reveal. Contrast creates impact.\n"
        "7. SPECIFIC NUMBERS: '73%' beats 'most'. '$47' beats 'affordable'. '14 days' beats 'quickly'.\n"
        "8. EMOTIONALLY RESONANT ENDINGS: Final line should be quotable, shareable, and make the viewer feel something.\n\n"
        "ANTI-PATTERNS YOU NEVER DO:\n"
        "- Never start with 'Hey guys', 'So today', 'Welcome back', or any greeting.\n"
        "- Never use generic filler: 'game-changer', 'mind-blowing', 'you won't believe'.\n"
        "- Never write action as just '(Actor talks to camera)' — that's lazy. Specify EVERYTHING.\n"
        "- Never have two consecutive scenes at the same energy level.\n"
        "- Never let dialogue exceed 15 words per scene without a visual interrupt.\n\n"
        "Return ONLY valid JSON arrays. No markdown. No commentary."
    )
    prompt = f"""Write a dopamine-optimized viral video screenplay for {platform} about "{topic}".

═══ VIDEO BRIEF ═══
Topic: {topic}
Hook line: "{hook or topic}"
Niche: {niche}
Content Style: {content_style}
Structure template: {structure}
Format: {fmt}
Platform: {platform} ({aspect_ratio}, target ~{estimated_length})
LANGUAGE: {lang_instruction}{actor_context}
Knowledge Nuggets (weave ALL into the script):
{nugget_text}

═══ SCENE-BY-SCENE REQUIREMENTS ═══

SCENE 1 — "THE HOOK" (0.0s–3.0s)
- Use EXACTLY this line as dialogue: "{hook or topic}"
- Opens MID-ACTION. {actor_name} is already doing something when the video starts.
- Camera: extreme close-up, slightly low angle, handheld micro-shake for energy.
- First visual text overlay appears at 0.3s — big, bold, contrasting color.
- Audio: voice at 0.0s, NO music for first 1.5s (voice-only creates intimacy), beat drop at 2.5s.
- THIS SCENE MUST CREATE AN OPEN LOOP the viewer can only close by watching to Scene 4-5.
- Energy: 10/10. Pace: rapid-fire.

SCENE 2 — "THE TENSION" (3.0s–8.0s)
- Establish the problem/gap/conflict that makes the viewer NEED the answer.
- Use the "authority + vulnerability" toggle — show expertise but admit a personal mistake.
- Camera switches to medium shot — pattern interrupt from Scene 1's close-up.
- Insert a B-cam product/prop close-up at the 5s mark.
- Energy deliberately drops to 7/10 to create contrast for Scene 3.

SCENE 3 — "THE PAYLOAD" (8.0s–18.0s)
- THIS IS THE VALUE BOMB. Deliver the core nugget with maximum specificity.
- Use the most compelling Knowledge Nugget here with exact numbers.
- Camera: push-in dolly, getting physically closer as the value increases.
- Text overlays: key stat appears at the exact moment it's spoken.
- Actor demonstrates (not just says) — if it's a product, SHOW the technique.
- Energy builds from 7 to 9/10.

SCENE 4 — "THE PROOF" (18.0s–25.0s)
- Close the open loop from Scene 1. Pay off the promise.
- Show real/specific results: "I did X for Y days and got Z result."
- Camera: dolly in to product/result close-up.
- Single peak SFX moment (cash register / success chime) — ONE per video, it goes here.
- Energy: 8/10, pace medium — let the proof breathe.

SCENE 5 — "THE FOMO CTA" (25.0s–30.0s)
- 1.0s SILENCE/FREEZE before the CTA begins (this is a deliberate technique).
- CTA must use urgency + specificity: "Save this before [specific consequence]" or "Follow — I'm dropping [specific next topic] tomorrow."
- Camera: static close-up, direct eye contact.
- "SAVE THIS" pulsing text overlay with arrow pointing to save button.
- Music fades out over final 2s. End on a beat, not a fade.
- Energy: 9/10, pace urgent.

═══ OUTPUT FORMAT ═══
Return ONLY a JSON array of exactly 5 scene objects. Each object:
- "sceneNum": int 1-5
- "name": scene name in CAPS
- "timingStart": float seconds
- "timingEnd": float seconds
- "duration": float seconds
- "dialogue": EXACT words {actor_name} says — punchy, conversational, specific numbers, zero filler. Written in {language}.
- "action": "(Actor {actor_name}: [PRECISE physical blocking — hand position, eye direction, prop handling, facial micro-expression, body angle, movement trajectory])"
- "camera": {{"shot": "Close-up/Medium/Wide/etc", "angle": "Low/Eye/High/Dutch", "movement": "Push-in/Static/Dolly/Handheld/etc"}}
- "actor": {{"expression": "specific emotion + physical descriptor", "energy": 1-10, "pace": "fast/medium/slow"}}
- "visual": exact text overlay content, font size, color, animation type, and timestamp
- "audio": music energy level as %, specific SFX names with exact timestamps, silence beats
- "editMarkers": [{{"time": "Xs", "event": "specific edit action"}}] — 3-4 per scene

Return ONLY the JSON array. No markdown fences. No commentary."""
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
