"""
Backero AI Service - Complete Implementation
Handles all Anthropic Claude API interactions with phase isolation
"""

import os
import re
import json
from typing import Optional
from anthropic import Anthropic

_client = None


def _get_client():
    """Get or create singleton Anthropic client"""
    global _client
    if _client:
        return _client
    key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not key or key == "your-anthropic-api-key-here":
        return None
    _client = Anthropic(api_key=key)
    return _client


LANGUAGE_INSTRUCTIONS = {
    "EN": "Respond in English.",
    "HI": "Respond in Hindi (Devanagari script).",
    "TA": "Respond in Tamil.",
    "TE": "Respond in Telugu.",
    "KN": "Respond in Kannada.",
    "ML": "Respond in Malayalam.",
    "BN": "Respond in Bengali.",
    "MR": "Respond in Marathi.",
    "GU": "Respond in Gujarati.",
    "PA": "Respond in Punjabi.",
}


def _get_phase_system_prompt(phase_number: int, previous_phase_data: dict) -> str:
    """
    Generate the master system prompt with phase isolation enforcement.
    This is the core prompt that prevents looping and ensures linear progression.
    """
    previous_data_str = json.dumps(previous_phase_data, indent=2, default=str)

    return f"""You are AXIS-7, an elite viral video scriptwriter with 847M cumulative views across TikTok, YouTube Shorts, and Instagram Reels. You execute ONE phase at a time with surgical precision.

═══════════════════════════════════════════════════════════════════════════════
                         PHASE EXECUTION PROTOCOL
═══════════════════════════════════════════════════════════════════════════════

CURRENT PHASE: {phase_number}
PREVIOUS DATA: {previous_data_str}

<phase_boundary_check>
Before generating ANY content, execute this checklist:
□ I am executing ONLY Phase {phase_number}
□ Previous phase data is READ-ONLY historical context
□ I will NOT regenerate, modify, or loop back to previous phases
□ I will NOT output content belonging to other phases
□ My output advances the narrative FORWARD from where Phase {phase_number - 1} ended
</phase_boundary_check>

═══════════════════════════════════════════════════════════════════════════════
                         PHASE DEFINITIONS (Reference Only)
═══════════════════════════════════════════════════════════════════════════════

PHASE 1 - TOPIC EXTRACTION: Generate 3 knowledge nuggets. User selects ONE.
PHASE 2 - HOOK ENGINEERING: Craft the opening 0.8-second thumb-stop moment.
PHASE 3 - STRUCTURAL OUTLINE: Build the 5-beat retention architecture.
PHASE 4 - FULL SCRIPT: Write scene-by-scene production-ready dialogue.
PHASE 5 - DELIVERY DIRECTION: Actor cues, pacing, emotional beats.

You execute ONLY the phase number specified. Other phases are locked.

═══════════════════════════════════════════════════════════════════════════════
                         CONTENT GENERATION RULES
═══════════════════════════════════════════════════════════════════════════════

<narrative_arc_progression>
Verify before writing:
1. What specific content did Phase {phase_number - 1} produce?
2. What NEW element does Phase {phase_number} add that didn't exist?
3. Does my output build ON TOP of previous work, not replace it?
4. Am I generating fresh creative material, not summarizing inputs?
</narrative_arc_progression>

WRITING MANDATES:
- Dialogue sounds like a friend texting an urgent secret at 2AM
- Zero corporate speak: ban "game-changer", "revolutionary", "unlock your potential"
- Every sentence earns its existence or gets cut
- Numbers and specifics over vague claims ("47% faster" not "much faster")
- Conflict, tension, or curiosity in every beat
- Write for a 14-second attention span viewer

═══════════════════════════════════════════════════════════════════════════════
                         MANDATORY OUTPUT FORMAT
═══════════════════════════════════════════════════════════════════════════════

Structure your Phase {phase_number} output using EXACTLY these tags:

<scene_setting>
[VISUAL FRAME]: Describe exactly what the camera sees - shot type, framing, movement
[TEXT OVERLAY]: Any on-screen text, font style, animation timing
[PACING]: Speed of cuts, visual rhythm, transition style
[DURATION]: Precise timing in seconds for this beat
</scene_setting>

<actor_delivery>
[TONE]: Emotional register (conspiratorial whisper, excited friend, deadpan expert)
[SUBTEXT]: What the actor is FEELING beneath the words
[PAUSE CUES]: Exact moments of silence and their duration
[PHYSICAL]: Micro-expressions, hand gestures, eye contact with camera
</actor_delivery>

<dialogue>
[Write the exact spoken words here. Punchy. Conversational. Real human speech patterns. Include verbal fillers and natural rhythm. No AI clichés. No corporate polish.]
</dialogue>

═══════════════════════════════════════════════════════════════════════════════
                         ANTI-LOOP ENFORCEMENT
═══════════════════════════════════════════════════════════════════════════════

FORBIDDEN ACTIONS:
✗ Regenerating nuggets if Phase 1 is complete
✗ Rewriting hooks if Phase 2 is complete
✗ Restructuring outline if Phase 3 is complete
✗ Outputting content for phases other than {phase_number}
✗ Summarizing or restating previous phase outputs as new content
✗ Using placeholder text like "[insert X here]"

If you detect yourself about to violate these rules, STOP and output only Phase {phase_number} content.

═══════════════════════════════════════════════════════════════════════════════
                         EXECUTION
═══════════════════════════════════════════════════════════════════════════════

Read previous data as immutable context.
Generate NEW content for Phase {phase_number} ONLY.
Format output using the three required XML tags where applicable.
Make it scroll-stopping, tension-filled, and unmistakably human.

BEGIN PHASE {phase_number} OUTPUT NOW:"""


def _ask(prompt: str, system: str = "", max_tokens: int = 4096) -> Optional[str]:
    """Execute a Claude API call with error handling"""
    client = _get_client()
    if not client:
        return None
    try:
        kwargs = {
            "model": "claude-sonnet-4-6",
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system
        response = client.messages.create(**kwargs)
        return response.content[0].text.strip()
    except Exception as e:
        print(f"Anthropic API error: {e}")
        return None


def _parse_json(text: str):
    """Parse JSON from Claude response, handling markdown code blocks"""
    text = re.sub(r"^```(?:json)?\s*", "", text.strip())
    text = re.sub(r"\s*```$", "", text.strip())
    return json.loads(text.strip())


def _nugget_fallback(topic: str, niche: str) -> list[dict]:
    """Fallback nuggets when API fails"""
    return [
        {
            "type": "Shocking Fact",
            "text": f"Most people get {topic} completely wrong - here's the data",
            "source": "Industry research",
            "rationale": "Creates immediate curiosity gap",
            "color": "#EF4444"
        },
        {
            "type": "Practical Hack",
            "text": f"The 2-minute {topic} trick that experts use daily",
            "source": "Expert interviews",
            "rationale": "Promises quick actionable value",
            "color": "#22C55E"
        },
        {
            "type": "Story Hook",
            "text": f"I tested {topic} for 30 days - the results shocked me",
            "source": "Personal experiment",
            "rationale": "Personal narrative builds trust",
            "color": "#F59E0B"
        }
    ]


def extract_nuggets_ai(topic: str, research_text: str = "", niche: str = "",
                       language: str = "EN") -> list[dict]:
    """
    Phase 1: Extract 3 knowledge nuggets for user to choose from.
    Returns exactly 3 nuggets with different angles.
    """
    client = _get_client()
    if not client:
        return _nugget_fallback(topic, niche)

    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["EN"])

    system_prompt = f"""You are a world-class viral short-form video strategist who has helped 500+ creators hit 10M+ views on Instagram Reels, YouTube Shorts, and TikTok.

{lang_instruction}

Your task: Extract exactly 3 DIFFERENT knowledge nuggets from the given topic/research. Each nugget must be:
- Maximum 15 words
- Punchy and scroll-stopping
- Specific with numbers where possible
- Unique angle (no overlap between the 3)

CRITICAL: Generate exactly 3 nuggets of these types:
1. "Shocking Fact" - Counterintuitive data that makes people stop scrolling
2. "Practical Hack" - Actionable tip they can use immediately
3. "Story Hook" - Personal/emotional angle that builds connection

Return ONLY valid JSON array, no markdown:
[
  {{"type": "Shocking Fact", "text": "...", "source": "...", "rationale": "why this hooks viewers", "color": "#EF4444"}},
  {{"type": "Practical Hack", "text": "...", "source": "...", "rationale": "why this hooks viewers", "color": "#22C55E"}},
  {{"type": "Story Hook", "text": "...", "source": "...", "rationale": "why this hooks viewers", "color": "#F59E0B"}}
]"""

    prompt = f"""Topic: {topic}
Niche: {niche or 'General'}
Research Context: {research_text or 'No additional research provided'}

Generate 3 unique knowledge nuggets for this viral video. Return ONLY the JSON array."""

    result = _ask(prompt, system_prompt)
    if not result:
        return _nugget_fallback(topic, niche)

    try:
        nuggets = _parse_json(result)
        if isinstance(nuggets, list) and len(nuggets) >= 3:
            return nuggets[:3]
        return _nugget_fallback(topic, niche)
    except:
        return _nugget_fallback(topic, niche)


def enhance_hook_validation(hook_text: str, validation_result: dict,
                            topic: str = "", niche: str = "",
                            language: str = "EN") -> dict:
    """
    Enhance hook validation with AI-powered suggestions and rewrites.
    Takes existing validation result and adds AI improvements.
    """
    client = _get_client()
    if not client:
        return validation_result

    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["EN"])

    system_prompt = f"""You are a viral hook specialist with expertise in short-form video. {lang_instruction}

Your job: Take a hook that has issues and provide:
1. 3 improved rewrites (each under 15 words, punchy, with specific data/numbers)
2. Keep the core message but make it irresistible

Rules for rewrites:
- Must include a number, stat, or specific claim
- Must create a curiosity gap
- Must sound like natural speech, not marketing copy
- No banned words: game-changer, revolutionary, unlock, secret, mind-blowing, insane

Return JSON:
{{
  "valid": false,
  "score": {validation_result.get('score', 50)},
  "issues": {json.dumps(validation_result.get('issues', []))},
  "suggestions": {json.dumps(validation_result.get('suggestions', []))},
  "ai_rewrites": ["rewrite1", "rewrite2", "rewrite3"]
}}"""

    prompt = f"""Original Hook: {hook_text}
Topic: {topic}
Niche: {niche}
Current Issues: {json.dumps(validation_result.get('issues', []))}

Generate 3 improved hook alternatives."""

    result = _ask(prompt, system_prompt, max_tokens=1024)
    if not result:
        return validation_result

    try:
        enhanced = _parse_json(result)
        # Merge with original validation result
        validation_result["ai_rewrites"] = enhanced.get("ai_rewrites", [])
        return validation_result
    except:
        return validation_result


def generate_screenplay_ai(phase1: dict, phase2: dict, language: str = "EN") -> dict:
    """
    Phase 3: Generate screenplay using ONLY the selected nugget.
    CRITICAL: Uses selected_nugget, not all knowledge_nuggets.
    """
    client = _get_client()
    if not client:
        return _screenplay_fallback(phase1, phase2)

    # FIXED: Use only the SELECTED nugget, not all nuggets
    selected_nugget = phase1.get("selected_nugget", {})
    if not selected_nugget:
        # Fallback to first nugget if none selected (shouldn't happen with proper frontend)
        nuggets = phase1.get("knowledge_nuggets", [])
        selected_nugget = nuggets[0] if nuggets else {"type": "Fact", "text": phase1.get("topic", "")}

    nugget_text = f"[{selected_nugget.get('type', 'Fact')}] {selected_nugget.get('text', '')}"

    topic = phase1.get("topic", "")
    platform = phase1.get("platform", "YouTube Shorts")
    niche = phase1.get("niche", "")
    hook = phase1.get("hook", "")

    content_type = phase2.get("content_type", "educational")
    format_style = phase2.get("format", "talking_head")

    previous_data = {
        "phase1": {
            "topic": topic,
            "selected_nugget": selected_nugget,
            "hook": hook,
            "platform": platform,
            "niche": niche
        },
        "phase2": phase2
    }

    system_prompt = _get_phase_system_prompt(3, previous_data)

    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["EN"])

    prompt = f"""{lang_instruction}

Generate a 5-scene viral video screenplay for:
- Platform: {platform}
- Topic: {topic}
- Selected Nugget (USE THIS AS CORE MESSAGE): {nugget_text}
- Opening Hook: {hook}
- Content Type: {content_type}
- Format: {format_style}

Create exactly 5 scenes with these beats:
1. HOOK (0-3 sec): Thumb-stopping opener
2. PROBLEM/SETUP (3-12 sec): Create tension or curiosity
3. REVELATION (12-25 sec): Deliver the core insight
4. PROOF/DEMO (25-38 sec): Show evidence or how-to
5. CTA (38-45 sec): Clear next action

Each scene needs:
- scene_number (1-5)
- title (beat name)
- duration (seconds)
- scene_setting (camera, visuals, text overlays)
- actor_delivery (tone, energy, physical cues)
- dialogue (exact words - punchy, conversational, NO corporate speak)

Return as JSON:
{{
  "title": "video title",
  "total_duration": 45,
  "scenes": [
    {{
      "scene_number": 1,
      "title": "Hook",
      "duration": 3,
      "scene_setting": "Close-up, eye-level, slight push-in. No text overlay yet.",
      "actor_delivery": "Conspiratorial whisper, eyebrows raised, leaning toward camera",
      "dialogue": "Okay wait... nobody talks about this but..."
    }}
  ]
}}"""

    result = _ask(prompt, system_prompt, max_tokens=4096)
    if not result:
        return _screenplay_fallback(phase1, phase2)

    try:
        screenplay = _parse_json(result)
        # Validate we got 5 scenes
        if isinstance(screenplay.get("scenes"), list) and len(screenplay["scenes"]) >= 5:
            return screenplay
        return _screenplay_fallback(phase1, phase2)
    except:
        return _screenplay_fallback(phase1, phase2)


def _screenplay_fallback(phase1: dict, phase2: dict) -> dict:
    """Fallback screenplay when API fails"""
    topic = phase1.get("topic", "your topic")
    hook = phase1.get("hook", "Wait, did you know this?")
    selected_nugget = phase1.get("selected_nugget", {})
    nugget_text = selected_nugget.get("text", f"the truth about {topic}")

    return {
        "title": f"The Truth About {topic}",
        "total_duration": 45,
        "scenes": [
            {
                "scene_number": 1,
                "title": "Hook",
                "duration": 3,
                "scene_setting": "Close-up face shot, eye-level, slight camera push-in. Clean background.",
                "actor_delivery": "Conspiratorial whisper, leaning in, wide eyes, slight head shake",
                "dialogue": hook if hook else "Okay so... nobody's talking about this."
            },
            {
                "scene_number": 2,
                "title": "Problem",
                "duration": 9,
                "scene_setting": "Medium shot, cut to b-roll of relevant imagery. Text overlay: key stat.",
                "actor_delivery": "Frustrated energy, hand gestures emphasizing pain points, building tension",
                "dialogue": f"Here's the thing about {topic} that nobody tells you... and it's actually kind of wild when you think about it."
            },
            {
                "scene_number": 3,
                "title": "Revelation",
                "duration": 13,
                "scene_setting": "Dynamic shot, text overlays appearing with key points. Quick cuts.",
                "actor_delivery": "Building excitement, faster pace, confident posture, finger pointing",
                "dialogue": f"But here's what I found out: {nugget_text}. Like... that changes everything, right?"
            },
            {
                "scene_number": 4,
                "title": "Proof",
                "duration": 13,
                "scene_setting": "Screen share or demonstration footage. Numbered list overlay.",
                "actor_delivery": "Teacher mode, clear enunciation, pointing at visuals, nodding",
                "dialogue": "Look - I'll show you exactly what I mean. Step one... step two... and boom. See that? The numbers don't lie."
            },
            {
                "scene_number": 5,
                "title": "CTA",
                "duration": 7,
                "scene_setting": "Back to face, slight zoom out, warm lighting. Follow button animation.",
                "actor_delivery": "Friendly, inviting, direct eye contact, genuine smile",
                "dialogue": "Save this for later. And follow because part 2 is where it gets really interesting."
            }
        ]
    }


def regenerate_scene_ai(existing_scene: dict, phase1: dict, phase2: dict,
                        direction: str, language: str = "EN") -> dict:
    """
    Regenerate a single scene based on director feedback.
    Keeps scene number and approximate timing, improves content.
    """
    client = _get_client()
    if not client:
        return existing_scene

    selected_nugget = phase1.get("selected_nugget", {})

    previous_data = {
        "phase1": {"topic": phase1.get("topic"), "selected_nugget": selected_nugget},
        "phase2": phase2,
        "existing_scene": existing_scene
    }

    system_prompt = _get_phase_system_prompt(4, previous_data)
    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["EN"])

    prompt = f"""{lang_instruction}

Rewrite this scene based on director feedback:

CURRENT SCENE:
{json.dumps(existing_scene, indent=2)}

DIRECTOR NOTES: {direction}

Keep the same scene_number and approximate duration.
Make the dialogue more punchy and conversational.
Return JSON with same structure but improved content:
{{
  "scene_number": {existing_scene.get('scene_number', 1)},
  "title": "...",
  "duration": ...,
  "scene_setting": "...",
  "actor_delivery": "...",
  "dialogue": "..."
}}"""

    result = _ask(prompt, system_prompt, max_tokens=2048)
    if not result:
        return existing_scene

    try:
        return _parse_json(result)
    except:
        return existing_scene


def analyze_quality_ai(screenplay: dict, phase1: dict, language: str = "EN") -> dict:
    """
    Phase 4: Quality analysis and scoring.
    Evaluates screenplay for viral potential.
    """
    client = _get_client()
    if not client:
        return {"score": 75, "verdict": "pass", "issues": [], "suggestions": []}

    previous_data = {
        "phase1": phase1,
        "screenplay": screenplay
    }

    system_prompt = _get_phase_system_prompt(4, previous_data)
    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["EN"])

    prompt = f"""{lang_instruction}

Analyze this screenplay for viral potential:

{json.dumps(screenplay, indent=2)}

Score 0-100 on these criteria:
- Hook strength (first 3 seconds - does it stop the scroll?)
- Retention architecture (does each scene compel the next?)
- Dialogue authenticity (sounds human, not AI-generated?)
- Visual storytelling (clear, compelling visuals?)
- CTA effectiveness (clear, motivating action?)

Be harsh but fair. Viral content needs to be exceptional.

Return JSON:
{{
  "score": 0-100,
  "verdict": "pass" or "needs_work",
  "breakdown": {{
    "hook": 0-100,
    "retention": 0-100,
    "dialogue": 0-100,
    "visuals": 0-100,
    "cta": 0-100
  }},
  "issues": ["critical issue 1", "critical issue 2"],
  "suggestions": ["specific improvement 1", "specific improvement 2"]
}}"""

    result = _ask(prompt, system_prompt, max_tokens=2048)
    if not result:
        return {"score": 75, "verdict": "pass", "issues": [], "suggestions": []}

    try:
        return _parse_json(result)
    except:
        return {"score": 75, "verdict": "pass", "issues": [], "suggestions": []}


def generate_production_summary_ai(phase1: dict, phase2: dict, phase3: dict,
                                   phase4: dict, language: str = "EN") -> dict:
    """
    Phase 5: Generate production documentation.
    Creates a complete brief for the video production team.
    """
    client = _get_client()
    if not client:
        return _production_fallback(phase1, phase3)

    previous_data = {
        "phase1": phase1,
        "phase2": phase2,
        "phase3": phase3,
        "phase4": phase4
    }

    system_prompt = _get_phase_system_prompt(5, previous_data)
    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["EN"])

    prompt = f"""{lang_instruction}

Create a production brief for the video team based on this approved screenplay:

{json.dumps(previous_data, indent=2)}

Return JSON:
{{
  "title": "final video title",
  "duration": "XX seconds",
  "platform": "platform name",
  "equipment_needed": ["smartphone with 4K", "ring light", "lapel mic"],
  "location_notes": "specific shooting location suggestions",
  "wardrobe": "specific clothing recommendations",
  "props": ["prop 1", "prop 2"],
  "post_production": {{
    "editing_style": "fast cuts, jump cuts, etc",
    "music_mood": "upbeat, dramatic, chill",
    "text_overlays": ["key text 1", "key text 2"],
    "transitions": "transition style description"
  }},
  "talent_notes": "specific direction for the actor/creator"
}}"""

    result = _ask(prompt, system_prompt, max_tokens=2048)
    if not result:
        return _production_fallback(phase1, phase3)

    try:
        return _parse_json(result)
    except:
        return _production_fallback(phase1, phase3)


def _production_fallback(phase1: dict, phase3: dict) -> dict:
    """Fallback production summary when API fails"""
    return {
        "title": phase3.get("title", f"Video about {phase1.get('topic', 'topic')}"),
        "duration": f"{phase3.get('total_duration', 45)} seconds",
        "platform": phase1.get("platform", "YouTube Shorts"),
        "equipment_needed": ["Smartphone with good camera", "Ring light", "Lapel mic"],
        "location_notes": "Clean, uncluttered background with good lighting",
        "wardrobe": "Casual but put-together, solid colors work best",
        "props": [],
        "post_production": {
            "editing_style": "Fast cuts, high energy",
            "music_mood": "Upbeat, trending audio",
            "text_overlays": ["Key stats", "CTA"],
            "transitions": "Quick cuts, occasional zoom"
        },
        "talent_notes": "Energy high from first frame. Talk TO the viewer, not AT them."
    }


def generate_fluff_examples_ai(topic: str, niche: str = "", language: str = "EN") -> list[str]:
    """Generate examples of fluff/filler words to avoid"""
    client = _get_client()
    if not client:
        return ["basically", "actually", "you know", "like", "so yeah"]

    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["EN"])

    prompt = f"""{lang_instruction}

Topic: {topic}
Niche: {niche}

Generate 5 specific fluff phrases that creators in this niche overuse and should avoid.
These should be clichés or filler words specific to the topic.

Return ONLY a JSON array of 5 strings:
["fluff phrase 1", "fluff phrase 2", "fluff phrase 3", "fluff phrase 4", "fluff phrase 5"]"""

    result = _ask(prompt, "", max_tokens=512)
    if not result:
        return ["basically", "actually", "you know", "like", "so yeah"]

    try:
        return _parse_json(result)
    except:
        return ["basically", "actually", "you know", "like", "so yeah"]


def suggest_topics_ai(niche: str, sub_niche: str = "", language: str = "EN") -> list[dict]:
    """Generate topic suggestions based on niche"""
    client = _get_client()
    if not client:
        return [{"topic": f"Top 5 {niche} tips", "hook_angle": "List format"},
                {"topic": f"Common {niche} mistakes", "hook_angle": "Problem-solution"}]

    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["EN"])

    prompt = f"""{lang_instruction}

Niche: {niche}
Sub-niche: {sub_niche or 'General'}

Generate 5 viral video topic ideas that would perform well on short-form platforms.
Each topic should have a clear hook angle.

Return JSON array:
[
  {{"topic": "specific topic title", "hook_angle": "why it hooks viewers", "difficulty": "easy/medium/hard"}},
  ...
]"""

    result = _ask(prompt, "", max_tokens=1024)
    if not result:
        return [{"topic": f"Top 5 {niche} tips", "hook_angle": "List format", "difficulty": "easy"}]

    try:
        return _parse_json(result)
    except:
        return [{"topic": f"Top 5 {niche} tips", "hook_angle": "List format", "difficulty": "easy"}]
