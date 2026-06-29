"""
Backero AI Service — Maximum Performance Build
Scalerock Viral Video Production Pipeline
All 5 phases fully implemented with brand context, platform intelligence,
TRIBE v2 scoring, 4-document Phase 5 output, and quality enforcement.
"""

import os
import re
import json
import time
from typing import Optional
from anthropic import Anthropic

_client = None


def _get_client():
    global _client
    if _client:
        return _client
    key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not key or key == "your-anthropic-api-key-here":
        return None
    _client = Anthropic(api_key=key)
    return _client


# ============================================================
# LANGUAGE INSTRUCTIONS
# ============================================================

LANGUAGE_INSTRUCTIONS = {
    "EN": "LANGUAGE: Write ALL output in English only.",
    "HI": "LANGUAGE: Write ALL output in Hindi using Devanagari script (हिंदी). Do NOT use English except for proper nouns with no Hindi equivalent.",
    "TA": "LANGUAGE: Write ALL output in Tamil script (தமிழ்). Do NOT use English except for proper nouns.",
    "TE": "LANGUAGE: Write ALL output in Telugu script (తెలుగు). Do NOT use English except for proper nouns.",
    "KN": "LANGUAGE: Write ALL output in Kannada script (ಕನ್ನಡ). Do NOT use English except for proper nouns.",
    "ML": "LANGUAGE: Write ALL output in Malayalam script (മലയാളം). Do NOT use English except for proper nouns.",
    "BN": "LANGUAGE: Write ALL output in Bengali script (বাংলা). Do NOT use English except for proper nouns.",
    "MR": "LANGUAGE: Write ALL output in Marathi using Devanagari script (मराठी). Do NOT use English except for proper nouns.",
    "GU": "LANGUAGE: Write ALL output in Gujarati script (ગુજરાતી). Do NOT use English except for proper nouns.",
    "PA": "LANGUAGE: Write ALL output in Punjabi/Gurmukhi script (ਪੰਜਾਬੀ). Do NOT use English except for proper nouns.",
    "HIN-EN": (
        "LANGUAGE: Write ALL output in Hinglish — natural Hindi+English mix as spoken by urban Indian youth aged 18-28. "
        "Use Roman script throughout (NOT Devanagari). "
        "English nouns for products, brands, tech. Hindi verbs, connectors, emotions. "
        "Example: 'Yaar, ye serum try karo — 40% glow 7 din mein milega, I swear.'"
    ),
    "TAN-EN": (
        "LANGUAGE: Write ALL output in Tanglish — natural Tamil+English mix as spoken by urban Tamil youth aged 18-28. "
        "Use Roman script throughout (NOT Tamil script). "
        "English nouns for products, brands, tech. Tamil verbs, connectors, emotions. "
        "Example: 'Da, ipdi oru trick iruku — weekly oru time use pannu, face glow aagum guaranteed.'"
    ),
}

LANGUAGE_NAMES = {
    "EN": "English", "HI": "Hindi", "TA": "Tamil", "TE": "Telugu",
    "KN": "Kannada", "ML": "Malayalam", "BN": "Bengali", "MR": "Marathi",
    "GU": "Gujarati", "PA": "Punjabi", "HIN-EN": "Hinglish", "TAN-EN": "Tanglish",
}


# ============================================================
# PLATFORM INTELLIGENCE
# ============================================================

PLATFORM_RULES = {
    "Instagram Reels": (
        "PLATFORM — Instagram Reels:\n"
        "- Hook must land in first 0.8 seconds before scroll decision\n"
        "- Optimal duration: 15–30s (max 90s, sweet spot 25–35s)\n"
        "- Drop-off cliff at 7 seconds — must re-hook here\n"
        "- Captions drive saves and shares — add bold text overlays\n"
        "- Vertical 9:16 full-screen only, face fills top 60% of frame\n"
        "- Trending audio = algorithmic boost — mention audio mood\n"
        "- Loop-able endings increase rewatch rate\n"
        "- End CTA: 'Save this' performs 3x better than 'Follow me'"
    ),
    "YouTube Shorts": (
        "PLATFORM — YouTube Shorts:\n"
        "- First frame IS your thumbnail — must be visually striking\n"
        "- Max 60 seconds — viewer knows this, so pacing can breathe slightly\n"
        "- End screen CTA works: 'Subscribe' and 'Watch next' both drive action\n"
        "- Sound-off less common than TikTok — dialogue quality matters more\n"
        "- Chapters/timestamps not relevant — linear watch expected\n"
        "- Hook in title carries weight — bake curiosity into opening line\n"
        "- Drop-off cliff at 15s — second hook required here"
    ),
    "TikTok": (
        "PLATFORM — TikTok:\n"
        "- Sound-ON by default — audio is a creative tool, not background\n"
        "- Hook must work in 0.5 seconds (faster scroll than other platforms)\n"
        "- Loop endings strongly rewarded by algorithm (rewatch = signal)\n"
        "- Trending audio boosts reach even on educational content\n"
        "- Authenticity over production value — raw works if content is good\n"
        "- Duet/Stitch potential: design content others can react to\n"
        "- Comment bait: end with a debatable statement or open question"
    ),
    "YouTube Shorts / Instagram Reels": (
        "PLATFORM — Multi-platform (YouTube Shorts + Instagram Reels):\n"
        "- Hook must land in 0.8s for Reels, 0.5s for TikTok\n"
        "- Design for vertical 9:16, 30–60s duration\n"
        "- Caption strategy: bold overlays for Reels saves, verbal hooks for YT\n"
        "- Loop ending works across both platforms\n"
        "- CTA: 'Save this' for Reels, 'Subscribe' tag for YT"
    ),
}

DEFAULT_PLATFORM_RULE = (
    "PLATFORM — Short-form vertical video:\n"
    "- Hook in first 1 second, vertical 9:16, 30–60s duration\n"
    "- Loop-able ending, bold text overlays, clear CTA at close"
)


# ============================================================
# TRIBE v2 — EMOTIONAL TRIGGER FRAMEWORK
# ============================================================

TRIBE_EMOTIONS = {
    "Trust":        "Builds credibility through specificity, data, and lived experience. Viewer thinks: 'This person knows what they're talking about.'",
    "Relatability": "Creates 'that's me' moments. Viewer thinks: 'Finally someone said it.'",
    "Inspiration":  "Shows possibility. Viewer thinks: 'If they can, I can.'",
    "Belonging":    "Creates in-group identity. Viewer thinks: 'People like me do this.'",
    "Envy":         "Triggers FOMO through aspiration. Viewer thinks: 'I want that life.'",
}

# NeuralSet hook patterns mapped to psychological triggers
NEURAL_HOOKS = {
    "Curiosity Gap":    "Opens a question the viewer physically cannot leave unanswered. 'The one thing dermatologists won't say in ads...'",
    "Pattern Break":    "Contradicts what viewer expected to hear in frame 1. Stops scroll through cognitive dissonance.",
    "Social Proof":     "Uses numbers and authority. '2.3M people got this wrong — including me.'",
    "Fear of Loss":     "Activates loss aversion. 'You're losing X every time you do Y.'",
    "Identity Threat":  "Challenges viewer's self-image. 'If you do this, you're not actually skincare-conscious.'",
    "Instant Payoff":   "Promises value in seconds. 'In the next 30 seconds you'll know exactly why...'",
}


# ============================================================
# BRAND CONTEXT BUILDER
# ============================================================

def _build_brand_context(phase1: dict) -> str:
    """Extract and format brand context for injection into all prompts."""
    brand = phase1.get("brand_name", "")
    product = phase1.get("product_name", "")
    category = phase1.get("product_category", "")
    description = phase1.get("product_description", "")
    usp = phase1.get("product_usp", "")
    audience = phase1.get("target_audience", "Indian consumers")
    niche = phase1.get("niche", "")

    lines = ["BRAND & PRODUCT CONTEXT (inject naturally, never sound like an ad):"]
    if brand:
        lines.append(f"- Brand: {brand}")
    if product:
        lines.append(f"- Product: {product}")
    if category:
        lines.append(f"- Category: {category}")
    if description:
        lines.append(f"- What it does: {description}")
    if usp:
        lines.append(f"- Key differentiator: {usp}")
    if audience:
        lines.append(f"- Target viewer: {audience}")
    if niche:
        lines.append(f"- Content niche: {niche}")

    lines.append("- Market: Indian consumers — use Indian relatability, not Western references")
    lines.append("- Voice: Real person speaking to a friend, NOT a brand speaking to a customer")

    return "\n".join(lines)


def _build_tribe_context(phase1: dict) -> str:
    """Build TRIBE v2 + NeuralSet emotional framework for prompt injection."""
    tribe_emotion = phase1.get("tribe_emotion", "")
    neural_hook = phase1.get("neural_hook_type", "")
    content_pillar = phase1.get("content_pillar", "")

    lines = ["EMOTIONAL ARCHITECTURE (TRIBE v2 + NeuralSet):"]

    if tribe_emotion and tribe_emotion in TRIBE_EMOTIONS:
        lines.append(f"- Primary TRIBE emotion: {tribe_emotion}")
        lines.append(f"  → {TRIBE_EMOTIONS[tribe_emotion]}")
    else:
        lines.append("- TRIBE emotion: Relatability (default) — create 'finally someone said it' moments")

    if neural_hook and neural_hook in NEURAL_HOOKS:
        lines.append(f"- NeuralSet hook type: {neural_hook}")
        lines.append(f"  → {NEURAL_HOOKS[neural_hook]}")
    else:
        lines.append("- NeuralSet hook: Curiosity Gap (default) — open a question viewer can't leave unanswered")

    if content_pillar:
        lines.append(f"- Content pillar: {content_pillar}")

    return "\n".join(lines)


# ============================================================
# PHASE SYSTEM PROMPT — UPGRADED WITH PLATFORM + BRAND AWARENESS
# ============================================================

def _get_phase_system_prompt(phase_number: int, previous_phase_data: dict,
                              platform: str = "", brand_context: str = "",
                              tribe_context: str = "") -> str:
    previous_data_str = json.dumps(previous_phase_data, indent=2, default=str)
    platform_rules = PLATFORM_RULES.get(platform, DEFAULT_PLATFORM_RULE)

    return f"""You are AXIS-7, an elite viral short-form video scriptwriter. You have written scripts that generated 847M+ cumulative views across Indian Instagram Reels, YouTube Shorts, and TikTok. You specialize in Indian beauty, wellness, and lifestyle content for brands like Mamaearth, The Derma Co., and emerging D2C brands.

You execute ONE phase at a time with surgical precision. No exceptions.

═══════════════════════════════════════════════════════════════════════════
                     CURRENT EXECUTION CONTEXT
═══════════════════════════════════════════════════════════════════════════

CURRENT PHASE: {phase_number}
PREVIOUS DATA (READ-ONLY — do NOT modify or regenerate):
{previous_data_str}

═══════════════════════════════════════════════════════════════════════════
                     PLATFORM INTELLIGENCE
═══════════════════════════════════════════════════════════════════════════

{platform_rules}

═══════════════════════════════════════════════════════════════════════════
                     BRAND & EMOTIONAL CONTEXT
═══════════════════════════════════════════════════════════════════════════

{brand_context}

{tribe_context}

═══════════════════════════════════════════════════════════════════════════
                     PHASE BOUNDARY ENFORCEMENT
═══════════════════════════════════════════════════════════════════════════

<phase_boundary_check>
Before generating ANY content, confirm:
□ I am executing ONLY Phase {phase_number}
□ Previous phase data is READ-ONLY context — I will not regenerate it
□ I will NOT output content belonging to any other phase
□ My output ADVANCES the narrative forward from Phase {phase_number - 1}
□ I am aware of the platform, brand, and emotional targets above
</phase_boundary_check>

PHASE REFERENCE (locked — do not execute):
Phase 1 — NUGGET EXTRACTION: 3 knowledge angles for user selection
Phase 2 — HOOK ENGINEERING: 3 thumb-stop opening lines from selected nugget
Phase 3 — SCREENPLAY: 5-beat production-ready scene-by-scene script
Phase 4 — QUALITY SCORING: viral potential analysis with enforcement
Phase 5 — PRODUCTION DOCS: Actor Brief, Camera Sheet, Edit Timeline, Clean Script

═══════════════════════════════════════════════════════════════════════════
                     UNIVERSAL WRITING RULES
═══════════════════════════════════════════════════════════════════════════

MANDATORY:
- Every sentence earns its place or gets cut
- Numbers over vague claims: "37% more hydration in 6 days" not "more hydrated"
- Tension or curiosity in every single beat
- Indian cultural context: use desi references, not Western analogies
- Write for a viewer who has their thumb hovering to scroll RIGHT NOW

BANNED WORDS/PHRASES (auto-fail if used):
game-changer, revolutionary, unlock, secret sauce, mind-blowing, insane results,
transform your life, you won't believe, amazing, incredible, must-have, powerful

FORBIDDEN ACTIONS:
✗ Regenerate content from completed phases
✗ Use placeholder text like "[insert X here]"
✗ Output corporate marketing language
✗ Write content for phases other than Phase {phase_number}
✗ Summarize previous phases as new content

═══════════════════════════════════════════════════════════════════════════
                     BEGIN PHASE {phase_number} OUTPUT NOW
═══════════════════════════════════════════════════════════════════════════"""


# ============================================================
# CORE API CALLER
# ============================================================

def _ask(prompt: str, system: str = "", max_tokens: int = 4096,
         retries: int = 2) -> Optional[str]:
    """Claude API call with retry logic and error handling."""
    client = _get_client()
    if not client:
        return None
    for attempt in range(retries + 1):
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
            print(f"Anthropic API error (attempt {attempt + 1}): {e}")
            if attempt < retries:
                time.sleep(2 ** attempt)
    return None


def _parse_json(text: str):
    """Parse JSON from Claude response — strips markdown fences."""
    text = re.sub(r"^```(?:json)?\s*", "", text.strip())
    text = re.sub(r"\s*```$", "", text.strip())
    return json.loads(text.strip())


# ============================================================
# PHASE 1 — NUGGET EXTRACTION (upgraded with brand + TRIBE context)
# ============================================================

def extract_nuggets_ai(topic: str, research_text: str = "", niche: str = "",
                       language: str = "EN", phase1_data: dict = None) -> list[dict]:
    """
    Phase 1: Extract 3 knowledge nuggets for user to choose from.
    Each nugget is a different psychological angle on the same topic.
    """
    client = _get_client()
    phase1_data = phase1_data or {}

    if not client:
        return _nugget_fallback(topic, niche)

    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["EN"])
    lang_name = LANGUAGE_NAMES.get(language, "English")
    brand_context = _build_brand_context({**phase1_data, "niche": niche})
    tribe_context = _build_tribe_context(phase1_data)
    platform = phase1_data.get("platform", "Instagram Reels")
    platform_rules = PLATFORM_RULES.get(platform, DEFAULT_PLATFORM_RULE)

    system_prompt = f"""You are a world-class viral short-form video strategist. You have helped 500+ Indian creators hit 10M+ views on Instagram Reels and YouTube Shorts. You specialize in Indian beauty, skincare, wellness, and D2C product content.

{lang_instruction}
LANGUAGE RULE: The "text" field of every nugget MUST be in {lang_name}. "type", "source", "rationale" may stay in English for technical compatibility.

{brand_context}

{tribe_context}

{platform_rules}

NUGGET RULES:
- Each nugget: maximum 15 words in {lang_name}
- Must be specific — include a number, timeframe, or comparison where possible
- Must be genuinely surprising or counterintuitive for the target audience
- Must be directly tied to the brand/product context above
- Three completely different psychological angles (no overlap)

ANGLE TYPES:
1. "Shocking Fact" — Counterintuitive data that stops the scroll cold
2. "Practical Hack" — One actionable step they can use today
3. "Story Hook" — Personal/emotional angle that builds instant connection

Return ONLY valid JSON array, no markdown, no explanation:
[
  {{"type": "Shocking Fact", "text": "...", "source": "...", "rationale": "why this stops the scroll", "tribe_emotion": "Trust", "color": "#EF4444"}},
  {{"type": "Practical Hack", "text": "...", "source": "...", "rationale": "why this hooks viewers", "tribe_emotion": "Relatability", "color": "#22C55E"}},
  {{"type": "Story Hook", "text": "...", "source": "...", "rationale": "why this creates connection", "tribe_emotion": "Belonging", "color": "#F59E0B"}}
]"""

    prompt = f"""Topic: {topic}
Niche: {niche or 'General'}
Brand: {phase1_data.get('brand_name', '')}
Product: {phase1_data.get('product_name', '')}
Research Context: {research_text or 'No additional research provided'}
Target Audience: {phase1_data.get('target_audience', 'Urban Indian consumers')}

Generate 3 unique knowledge nuggets. Each must be tied to the product/brand context. Return ONLY the JSON array."""

    result = _ask(prompt, system_prompt, max_tokens=1024)
    if not result:
        return _nugget_fallback(topic, niche)

    try:
        nuggets = _parse_json(result)
        if isinstance(nuggets, list) and len(nuggets) >= 3:
            return nuggets[:3]
        return _nugget_fallback(topic, niche)
    except Exception:
        return _nugget_fallback(topic, niche)


def _nugget_fallback(topic: str, niche: str) -> list[dict]:
    return [
        {"type": "Shocking Fact", "text": f"Most people use {topic} wrong — here's what the data shows", "source": "Industry research", "rationale": "Creates immediate curiosity gap", "tribe_emotion": "Trust", "color": "#EF4444"},
        {"type": "Practical Hack", "text": f"The 2-minute {topic} method that dermatologists use daily", "source": "Expert interviews", "rationale": "Promises quick actionable value", "tribe_emotion": "Relatability", "color": "#22C55E"},
        {"type": "Story Hook", "text": f"I used {topic} every day for 30 days — my skin didn't expect this", "source": "Personal experiment", "rationale": "Personal narrative builds trust", "tribe_emotion": "Belonging", "color": "#F59E0B"},
    ]


# ============================================================
# PHASE 2 — HOOK ENGINEERING (NEW — was missing entirely)
# ============================================================

def generate_hook_ai(selected_nugget: dict, topic: str, platform: str = "Instagram Reels",
                     niche: str = "", language: str = "EN",
                     phase1_data: dict = None) -> dict:
    """
    Phase 2: Generate 3 distinct thumb-stop hook options from the selected nugget.
    User picks one. This was missing from the original implementation.
    Returns: {hooks: [{text, type, neural_trigger, psychology, estimated_ctr}], selected_hook: None}
    """
    client = _get_client()
    phase1_data = phase1_data or {}

    if not client:
        return _hook_fallback(selected_nugget, topic)

    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["EN"])
    lang_name = LANGUAGE_NAMES.get(language, "English")
    brand_context = _build_brand_context({**phase1_data, "niche": niche})
    tribe_context = _build_tribe_context(phase1_data)
    platform_rules = PLATFORM_RULES.get(platform, DEFAULT_PLATFORM_RULE)
    previous_data = {"selected_nugget": selected_nugget, "topic": topic, "platform": platform}

    system_prompt = _get_phase_system_prompt(2, previous_data, platform, brand_context, tribe_context)

    nugget_text = f"[{selected_nugget.get('type', 'Fact')}] {selected_nugget.get('text', topic)}"

    prompt = f"""{lang_instruction}

You are engineering the FIRST FRAME of this video — the 0.8-second thumb-stop moment.
The viewer's thumb is already moving. This hook must physically stop it.

SELECTED NUGGET (your raw material): {nugget_text}
Topic: {topic}
Platform: {platform}
Brand: {phase1_data.get('brand_name', '')}
Product: {phase1_data.get('product_name', '')}
Target Viewer: {phase1_data.get('target_audience', 'Urban Indian consumers aged 18-35')}

{platform_rules}

HOOK ENGINEERING RULES:
- Maximum 12 words spoken aloud (tested for 0.8s delivery)
- Must weaponize ONE of these NeuralSet triggers (each hook uses a DIFFERENT one):
  1. Curiosity Gap — question the viewer CANNOT leave unanswered
  2. Pattern Break — say the OPPOSITE of what they expect to hear
  3. Identity Threat — challenge their self-perception as a smart consumer
- Absolutely NO: "Have you ever...", "Are you struggling with...", "In this video I'll show you..."
- Must be in {lang_name}
- Must sound like something a real person says to a friend, not a brand talking to a customer
- Include the product/brand angle naturally — not as a promo, as a revelation

Generate exactly 3 hook options, each using a DIFFERENT NeuralSet trigger.

Return ONLY valid JSON:
{{
  "hooks": [
    {{
      "text": "exact spoken words in {lang_name}",
      "type": "Curiosity Gap",
      "neural_trigger": "what psychological mechanism this pulls",
      "delivery_note": "how to say this — speed, emphasis, pause placement",
      "estimated_ctr": "High/Very High/Exceptional",
      "why_it_works": "one sentence on the psychology"
    }},
    {{
      "text": "exact spoken words in {lang_name}",
      "type": "Pattern Break",
      "neural_trigger": "...",
      "delivery_note": "...",
      "estimated_ctr": "...",
      "why_it_works": "..."
    }},
    {{
      "text": "exact spoken words in {lang_name}",
      "type": "Identity Threat",
      "neural_trigger": "...",
      "delivery_note": "...",
      "estimated_ctr": "...",
      "why_it_works": "..."
    }}
  ],
  "selected_hook": null
}}"""

    result = _ask(prompt, system_prompt, max_tokens=2048)
    if not result:
        return _hook_fallback(selected_nugget, topic)

    try:
        parsed = _parse_json(result)
        if isinstance(parsed.get("hooks"), list) and len(parsed["hooks"]) >= 3:
            return parsed
        return _hook_fallback(selected_nugget, topic)
    except Exception:
        return _hook_fallback(selected_nugget, topic)


def _hook_fallback(selected_nugget: dict, topic: str) -> dict:
    t = topic or "this"
    return {
        "hooks": [
            {"text": f"Okay wait — nobody actually tells you the truth about {t}", "type": "Curiosity Gap", "neural_trigger": "Opens an unanswerable question", "delivery_note": "Pause after 'wait', conspiratorial lean", "estimated_ctr": "High", "why_it_works": "Brain can't tolerate an open loop"},
            {"text": f"Stop. You've been using {t} backwards this whole time.", "type": "Pattern Break", "neural_trigger": "Contradicts learned behavior", "delivery_note": "Hard stop, then slower second sentence", "estimated_ctr": "Very High", "why_it_works": "Cognitive dissonance freezes the scroll"},
            {"text": f"If you think you know {t} — you actually don't. Not yet.", "type": "Identity Threat", "neural_trigger": "Challenges self-image as informed consumer", "delivery_note": "Confident, not aggressive, direct eye contact", "estimated_ctr": "High", "why_it_works": "Ego protection drives completion"},
        ],
        "selected_hook": None,
    }


def enhance_hook_validation(hook_text: str, validation_result: dict,
                            topic: str = "", niche: str = "",
                            language: str = "EN") -> dict:
    """Enhance hook validation with AI-powered suggestions and rewrites."""
    client = _get_client()
    if not client:
        return validation_result

    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["EN"])

    system_prompt = f"""You are a viral hook specialist. {lang_instruction}

Take a hook with issues and provide 3 improved rewrites:
- Each under 12 words
- Each uses a different NeuralSet trigger (Curiosity Gap / Pattern Break / Identity Threat)
- Must include a specific claim, number, or timeframe
- Must sound like real human speech, not marketing copy
- Banned: game-changer, revolutionary, unlock, amazing, insane

Return JSON:
{{
  "valid": false,
  "score": {validation_result.get('score', 50)},
  "issues": {json.dumps(validation_result.get('issues', []))},
  "suggestions": {json.dumps(validation_result.get('suggestions', []))},
  "ai_rewrites": [
    {{"text": "rewrite 1", "type": "Curiosity Gap"}},
    {{"text": "rewrite 2", "type": "Pattern Break"}},
    {{"text": "rewrite 3", "type": "Identity Threat"}}
  ]
}}"""

    prompt = f"""Original Hook: {hook_text}
Topic: {topic}
Niche: {niche}
Current Issues: {json.dumps(validation_result.get('issues', []))}

Generate 3 improved hook alternatives in the target language."""

    result = _ask(prompt, system_prompt, max_tokens=1024)
    if not result:
        return validation_result

    try:
        enhanced = _parse_json(result)
        validation_result["ai_rewrites"] = enhanced.get("ai_rewrites", [])
        return validation_result
    except Exception:
        return validation_result


# ============================================================
# PHASE 3 — SCREENPLAY GENERATION (upgraded with all context)
# ============================================================

def generate_screenplay_ai(phase1: dict, phase2: dict, language: str = "EN") -> dict:
    """
    Phase 3: Generate 5-beat production-ready screenplay.
    Uses selected nugget + selected hook + full brand/platform/TRIBE context.
    """
    client = _get_client()
    if not client:
        return _screenplay_fallback(phase1, phase2)

    selected_nugget = phase1.get("selected_nugget", {})
    if not selected_nugget:
        nuggets = phase1.get("knowledge_nuggets", [])
        selected_nugget = nuggets[0] if nuggets else {"type": "Fact", "text": phase1.get("topic", "")}

    # Get selected hook from Phase 2
    selected_hook = phase2.get("selected_hook") or ""
    if not selected_hook and isinstance(phase2.get("hooks"), list) and phase2["hooks"]:
        selected_hook = phase2["hooks"][0].get("text", "")

    topic = phase1.get("topic", "")
    platform = phase1.get("platform", "Instagram Reels")
    brand_context = _build_brand_context(phase1)
    tribe_context = _build_tribe_context(phase1)
    platform_rules = PLATFORM_RULES.get(platform, DEFAULT_PLATFORM_RULE)

    content_type = phase2.get("content_type", "educational")
    format_style = phase2.get("format", "talking_head")

    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["EN"])
    lang_name = LANGUAGE_NAMES.get(language, "English")

    # Platform-specific duration targets
    duration_map = {
        "Instagram Reels": 30,
        "YouTube Shorts": 55,
        "TikTok": 28,
    }
    target_duration = duration_map.get(platform, 40)
    scene_durations = _calculate_scene_durations(target_duration)

    previous_data = {
        "phase1": {
            "topic": topic,
            "selected_nugget": selected_nugget,
            "platform": platform,
            "brand": phase1.get("brand_name", ""),
            "product": phase1.get("product_name", ""),
        },
        "phase2": {"selected_hook": selected_hook, "content_type": content_type}
    }

    system_prompt = _get_phase_system_prompt(3, previous_data, platform, brand_context, tribe_context)

    prompt = f"""{lang_instruction}

Write a 5-scene viral video screenplay. Every word of dialogue must be in {lang_name}.

LOCKED INPUTS — use exactly as written:
- Opening Hook (SCENE 1 DIALOGUE — do not change): "{selected_hook}"
- Core Message (SCENE 3 revelation): [{selected_nugget.get('type')}] {selected_nugget.get('text')}
- Platform: {platform}
- Content Type: {content_type}
- Format: {format_style}

{brand_context}

{tribe_context}

{platform_rules}

5-BEAT STRUCTURE WITH PLATFORM-OPTIMIZED TIMING:
Scene 1 — HOOK ({scene_durations[0]}s): Use the locked hook above. EXACTLY as written. Do not modify it.
Scene 2 — TENSION ({scene_durations[1]}s): Deepen the problem/curiosity. Create the second hook (drop-off cliff re-engagement).
Scene 3 — REVELATION ({scene_durations[2]}s): Deliver the core nugget. This is the payoff. Make it feel earned.
Scene 4 — PROOF ({scene_durations[3]}s): Evidence, demonstration, or social proof. Numbers required.
Scene 5 — CTA ({scene_durations[4]}s): One clear action. No multiple CTAs. "Save this" > "Follow me" for Reels.

DIALOGUE RULES:
- Every line sounds like a real person talking to a friend, not a creator talking to an audience
- Contractions mandatory (don't, won't, it's — not "do not", "will not", "it is")
- One idea per sentence maximum
- Verbal rhythm: short-SHORT-longer. Short-SHORT-longer.
- The brand/product name appears ONCE maximum — and only when it's the natural revelation, not a promo

Return ONLY valid JSON:
{{
  "title": "video title (not a promo — make it sound like organic content)",
  "total_duration": {target_duration},
  "platform": "{platform}",
  "language": "{language}",
  "scenes": [
    {{
      "scene_number": 1,
      "title": "Hook",
      "duration": {scene_durations[0]},
      "scene_setting": "Exact camera direction: shot type, framing, movement, text overlay if any",
      "actor_delivery": "Tone, energy level, physical cues, eye contact, pace",
      "dialogue": "Exact spoken words in {lang_name}. Natural. Punchy. Human."
    }}
  ]
}}"""

    result = _ask(prompt, system_prompt, max_tokens=4096)
    if not result:
        return _screenplay_fallback(phase1, phase2)

    try:
        screenplay = _parse_json(result)
        scenes = screenplay.get("scenes", [])

        # Validation: need exactly 5 scenes
        if not isinstance(scenes, list) or len(scenes) < 5:
            return _screenplay_fallback(phase1, phase2)

        # Validation: duration math sanity check
        total = sum(s.get("duration", 0) for s in scenes)
        if total < 20 or total > 120:
            # Rebalance durations to target
            for i, scene in enumerate(scenes):
                scene["duration"] = scene_durations[i]
            screenplay["total_duration"] = target_duration

        # Validation: hook scene must use selected hook
        if selected_hook and scenes[0].get("dialogue"):
            hook_words = set(selected_hook.lower().split())
            scene_words = set(scenes[0]["dialogue"].lower().split())
            overlap = len(hook_words & scene_words) / max(len(hook_words), 1)
            if overlap < 0.4:
                # Hook was rewritten — restore it
                scenes[0]["dialogue"] = selected_hook

        return screenplay

    except Exception:
        return _screenplay_fallback(phase1, phase2)


def _calculate_scene_durations(total: int) -> list[int]:
    """Calculate 5 scene durations from total video length."""
    # Distribution: Hook 8%, Tension 22%, Revelation 30%, Proof 28%, CTA 12%
    ratios = [0.08, 0.22, 0.30, 0.28, 0.12]
    durations = [max(2, round(total * r)) for r in ratios]
    # Adjust to hit exact total
    diff = total - sum(durations)
    durations[2] += diff  # Add/subtract from revelation scene
    return durations


def _screenplay_fallback(phase1: dict, phase2: dict) -> dict:
    topic = phase1.get("topic", "your topic")
    selected_hook = phase2.get("selected_hook") or "Okay wait — nobody actually talks about this."
    selected_nugget = phase1.get("selected_nugget", {})
    nugget_text = selected_nugget.get("text", f"the truth about {topic}")
    product = phase1.get("product_name", topic)
    platform = phase1.get("platform", "Instagram Reels")
    target_duration = 30

    return {
        "title": f"The truth about {topic} nobody tells you",
        "total_duration": target_duration,
        "platform": platform,
        "scenes": [
            {"scene_number": 1, "title": "Hook", "duration": 3, "scene_setting": "Extreme close-up, eye-level, slight push-in. No text overlay. Clean background.", "actor_delivery": "Conspiratorial whisper, leaning in, eyebrows raised, pause after first clause", "dialogue": selected_hook},
            {"scene_number": 2, "title": "Tension", "duration": 7, "scene_setting": "Medium shot, cut to b-roll of problem. Text overlay: '87% of people do this wrong'", "actor_delivery": "Building frustration, hands gesturing, faster pace, head shake", "dialogue": f"Here's the thing — I was doing the exact same thing with {topic}. For two years. And nobody corrected me."},
            {"scene_number": 3, "title": "Revelation", "duration": 9, "scene_setting": "Back to face, slight zoom-in on reveal word. Text overlay appears with key stat.", "actor_delivery": "Controlled excitement, slower pace on the key fact, finger point", "dialogue": f"And then I found out: {nugget_text}. That's not a small thing. That changes the entire routine."},
            {"scene_number": 4, "title": "Proof", "duration": 8, "scene_setting": "Product demonstration or screen share. Numbered text overlays. Fast cuts.", "actor_delivery": "Teacher energy, clear enunciation, pointing at visual elements", "dialogue": f"I switched to {product}. Week one — nothing. Week two — I noticed it. Week three — three different people asked what I changed."},
            {"scene_number": 5, "title": "CTA", "duration": 3, "scene_setting": "Back to face, slight zoom out, direct address. Save animation in corner.", "actor_delivery": "Genuine, warm, direct eye contact, real smile — not a performer smile", "dialogue": "Save this. You'll want it later when you're actually shopping."},
        ]
    }


def regenerate_scene_ai(existing_scene: dict, phase1: dict, phase2: dict,
                        direction: str, language: str = "EN") -> dict:
    """Regenerate a single scene based on director feedback."""
    client = _get_client()
    if not client:
        return existing_scene

    selected_nugget = phase1.get("selected_nugget", {})
    brand_context = _build_brand_context(phase1)
    tribe_context = _build_tribe_context(phase1)
    platform = phase1.get("platform", "Instagram Reels")

    previous_data = {
        "phase1": {"topic": phase1.get("topic"), "selected_nugget": selected_nugget},
        "phase2": phase2,
        "existing_scene": existing_scene
    }

    system_prompt = _get_phase_system_prompt(4, previous_data, platform, brand_context, tribe_context)
    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["EN"])

    prompt = f"""{lang_instruction}

Rewrite this scene based on director feedback. Keep scene_number and approximate duration. Improve everything else.

CURRENT SCENE:
{json.dumps(existing_scene, indent=2)}

DIRECTOR NOTES: {direction}

RULES:
- Dialogue must be punchier and more conversational than the original
- Apply the director notes exactly
- Keep the same emotional beat/purpose of the scene
- No placeholder text

Return JSON with same structure:
{{
  "scene_number": {existing_scene.get('scene_number', 1)},
  "title": "...",
  "duration": {existing_scene.get('duration', 8)},
  "scene_setting": "...",
  "actor_delivery": "...",
  "dialogue": "..."
}}"""

    result = _ask(prompt, system_prompt, max_tokens=2048)
    if not result:
        return existing_scene

    try:
        return _parse_json(result)
    except Exception:
        return existing_scene


# ============================================================
# PHASE 4 — QUALITY SCORING WITH ENFORCEMENT
# ============================================================

# Minimum score to pass to Phase 5 without auto-regen
QUALITY_PASS_THRESHOLD = 65
# Score below this triggers auto-regen of weakest scene
AUTO_REGEN_THRESHOLD = 50

def analyze_quality_ai(screenplay: dict, phase1: dict, language: str = "EN") -> dict:
    """
    Phase 4: Quality scoring with enforcement.
    Score < 65: returns needs_work with specific scene to fix.
    Score < 50: auto-regenerates the weakest scene before returning.
    """
    client = _get_client()
    if not client:
        return {"score": 75, "verdict": "pass", "issues": [], "suggestions": []}

    brand_context = _build_brand_context(phase1)
    tribe_context = _build_tribe_context(phase1)
    platform = phase1.get("platform", "Instagram Reels")
    previous_data = {"phase1": phase1, "screenplay": screenplay}
    system_prompt = _get_phase_system_prompt(4, previous_data, platform, brand_context, tribe_context)
    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["EN"])

    prompt = f"""{lang_instruction}

Score this screenplay for viral potential on {platform}. Be harsh. Viral content must be exceptional, not good.

SCREENPLAY:
{json.dumps(screenplay, indent=2)}

BRAND CONTEXT:
{phase1.get('brand_name', '')} — {phase1.get('product_name', '')}
Target: {phase1.get('target_audience', 'Urban Indian consumers')}

SCORING CRITERIA (0-100 each):
- hook_strength: Does Scene 1 physically stop a scrolling thumb in 0.8 seconds?
- retention_architecture: Does each scene make the next one impossible to skip?
- dialogue_authenticity: Does it sound like a real Indian person talking, not an AI or a brand?
- visual_storytelling: Are scene_setting instructions specific enough for a camera operator to execute?
- cta_effectiveness: Is the final action clear, singular, and motivated?
- brand_integration: Is the product/brand woven in naturally, not pushed as a promo?
- language_quality: Is the {language} natural and authentic for the target demographic?

SCORING RULES:
- 80+ = Exceptional — ready to film
- 65-79 = Good — minor tweaks needed
- 50-64 = Needs work — specific scenes require rewrite
- Below 50 = Major issues — structural problems

Return JSON:
{{
  "score": 0-100,
  "verdict": "pass" or "needs_work" or "major_revision",
  "breakdown": {{
    "hook_strength": 0-100,
    "retention_architecture": 0-100,
    "dialogue_authenticity": 0-100,
    "visual_storytelling": 0-100,
    "cta_effectiveness": 0-100,
    "brand_integration": 0-100,
    "language_quality": 0-100
  }},
  "weakest_scene_number": 1-5,
  "weakest_scene_reason": "specific explanation of what's wrong",
  "issues": ["specific issue 1", "specific issue 2"],
  "suggestions": ["specific fix 1", "specific fix 2"],
  "director_note_for_regen": "exact instruction to pass to regenerate_scene_ai if needed"
}}"""

    result = _ask(prompt, system_prompt, max_tokens=2048)
    if not result:
        return {"score": 75, "verdict": "pass", "issues": [], "suggestions": []}

    try:
        quality = _parse_json(result)
        score = quality.get("score", 75)

        # ENFORCEMENT: Auto-regen weakest scene if score < AUTO_REGEN_THRESHOLD
        if score < AUTO_REGEN_THRESHOLD:
            weakest_num = quality.get("weakest_scene_number", 1)
            direction = quality.get("director_note_for_regen", "Make dialogue punchier and more specific")
            scenes = screenplay.get("scenes", [])
            weakest_scene = next((s for s in scenes if s.get("scene_number") == weakest_num), None)
            if weakest_scene:
                improved = regenerate_scene_ai(weakest_scene, phase1, {}, direction, language)
                for i, scene in enumerate(scenes):
                    if scene.get("scene_number") == weakest_num:
                        scenes[i] = improved
                        break
                screenplay["scenes"] = scenes
                quality["auto_regenerated_scene"] = weakest_num
                quality["note"] = f"Scene {weakest_num} was auto-improved due to low score ({score})"

        # ENFORCEMENT: Set verdict based on score thresholds
        if score >= QUALITY_PASS_THRESHOLD:
            quality["verdict"] = "pass"
        elif score >= AUTO_REGEN_THRESHOLD:
            quality["verdict"] = "needs_work"
        else:
            quality["verdict"] = "major_revision"

        quality["updated_screenplay"] = screenplay
        return quality

    except Exception:
        return {"score": 75, "verdict": "pass", "issues": [], "suggestions": []}


# ============================================================
# PHASE 5 — PRODUCTION DOCS (4 separate documents)
# ============================================================

def generate_production_summary_ai(phase1: dict, phase2: dict, phase3: dict,
                                   phase4: dict, language: str = "EN") -> dict:
    """
    Phase 5: Generate all 4 Scalerock production documents.
    - Actor Brief
    - Camera Sheet
    - Edit Timeline
    - Clean Script
    Returns all 4 as separate fields ready for docx generation.
    """
    client = _get_client()
    if not client:
        return _production_fallback(phase1, phase3)

    brand_context = _build_brand_context(phase1)
    tribe_context = _build_tribe_context(phase1)
    platform = phase1.get("platform", "Instagram Reels")
    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["EN"])
    lang_name = LANGUAGE_NAMES.get(language, "English")

    screenplay = phase3
    scenes = screenplay.get("scenes", [])
    previous_data = {"phase1": phase1, "phase2": phase2, "phase3": phase3, "phase4_score": phase4.get("score")}
    system_prompt = _get_phase_system_prompt(5, previous_data, platform, brand_context, tribe_context)

    # Generate all 4 docs in parallel prompt calls
    actor_brief = _generate_actor_brief(scenes, phase1, language, system_prompt)
    camera_sheet = _generate_camera_sheet(scenes, phase1, platform, system_prompt)
    edit_timeline = _generate_edit_timeline(scenes, screenplay, phase1, system_prompt)
    clean_script = _generate_clean_script(scenes, phase1, language, lang_instruction, lang_name, system_prompt)

    return {
        "title": screenplay.get("title", ""),
        "total_duration": screenplay.get("total_duration", 45),
        "platform": platform,
        "quality_score": phase4.get("score", 0),
        "actor_brief": actor_brief,
        "camera_sheet": camera_sheet,
        "edit_timeline": edit_timeline,
        "clean_script": clean_script,
    }


def _generate_actor_brief(scenes: list, phase1: dict, language: str,
                          system_prompt: str) -> dict:
    """Actor Brief: emotional arc, delivery notes, physical direction per scene."""
    prompt = f"""Generate a professional Actor Brief for this viral video.

Brand: {phase1.get('brand_name', '')} | Product: {phase1.get('product_name', '')}
Target Viewer: {phase1.get('target_audience', 'Urban Indian consumers')}
Language to perform in: {LANGUAGE_NAMES.get(language, 'English')}

SCENES:
{json.dumps(scenes, indent=2)}

The actor brief is a psychological and physical guide for the person on camera.
Not a script — they need the emotional TRUTH behind each line, not the lines themselves.

Return JSON:
{{
  "character_brief": "Who is this person? Background, personality, relationship to product — 3 sentences",
  "overall_energy": "The emotional arc of the entire video in one word + explanation",
  "wardrobe": "Specific clothing description — color, style, why it works for this content",
  "hair_makeup": "Natural/styled/specific look — what signals credibility for this audience",
  "scene_directions": [
    {{
      "scene_number": 1,
      "emotional_state": "exact internal feeling, not 'happy' or 'excited' — be specific",
      "subtext": "what are they NOT saying that the viewer should sense",
      "physical_notes": "specific micro-expressions, gestures, posture, eye behavior",
      "common_mistake": "the wrong way to play this beat and why it fails",
      "delivery_example": "one example sentence from the dialogue with phonetic emphasis markers"
    }}
  ],
  "pro_tips": ["tip 1 specific to this content", "tip 2", "tip 3"]
}}"""

    result = _ask(prompt, system_prompt, max_tokens=2048)
    if not result:
        return _actor_brief_fallback(scenes, phase1)
    try:
        return _parse_json(result)
    except Exception:
        return _actor_brief_fallback(scenes, phase1)


def _actor_brief_fallback(scenes: list, phase1: dict) -> dict:
    return {
        "character_brief": f"A real person who has genuinely used {phase1.get('product_name', 'this product')} and is sharing what they found — not a creator, not an influencer, a friend.",
        "overall_energy": "Conspiratorial → Frustrated → Revelatory → Confident → Inviting",
        "wardrobe": "Casual, solid color (not white, not black). Looks like a real person on a Sunday, not a photoshoot.",
        "hair_makeup": "Natural. The kind of face that looks like they're not wearing makeup even if they are.",
        "scene_directions": [{"scene_number": s.get("scene_number"), "emotional_state": s.get("actor_delivery", ""), "subtext": "I know something you don't yet", "physical_notes": "Lean slightly toward camera. Speak to one person, not an audience.", "common_mistake": "Don't perform. Just talk.", "delivery_example": s.get("dialogue", "")[:60] + "..."} for s in scenes],
        "pro_tips": ["Rehearse once. Record ten times. Use take 6-8.", "Look at the lens, not the screen.", "If you smile before the word, cut it."]
    }


def _generate_camera_sheet(scenes: list, phase1: dict, platform: str,
                            system_prompt: str) -> dict:
    """Camera Sheet: technical shot-by-shot production guide."""
    prompt = f"""Generate a professional Camera Sheet for a {platform} short-form video.

Platform specs: Vertical 9:16, minimum 1080x1920px
Brand: {phase1.get('brand_name', '')} | Product: {phase1.get('product_name', '')}

SCENES:
{json.dumps(scenes, indent=2)}

Return JSON:
{{
  "equipment": {{
    "primary_camera": "specific recommendation (phone model or camera)",
    "lens_equivalent": "focal length suggestion for this content",
    "stabilization": "tripod/gimbal/handheld — specific to this content",
    "lighting": "specific lighting setup with positioning",
    "microphone": "specific mic type and placement",
    "backdrop": "background direction"
  }},
  "shots": [
    {{
      "scene_number": 1,
      "shot_type": "ECU/CU/MCU/MS/WS",
      "framing": "exact framing description — where face sits in frame",
      "camera_movement": "static/push-in/pull-out/pan — when and how fast",
      "focal_length_feel": "tight/normal/wide",
      "text_overlay_zone": "where NOT to have face so text can appear",
      "lighting_note": "specific light direction for this scene",
      "cut_trigger": "what action on screen triggers the cut to next scene"
    }}
  ],
  "b_roll_list": ["shot 1 description", "shot 2 description"],
  "post_notes": "color grade direction, LUT mood, overall visual treatment"
}}"""

    result = _ask(prompt, system_prompt, max_tokens=2048)
    if not result:
        return _camera_sheet_fallback(scenes, platform)
    try:
        return _parse_json(result)
    except Exception:
        return _camera_sheet_fallback(scenes, platform)


def _camera_sheet_fallback(scenes: list, platform: str) -> dict:
    return {
        "equipment": {"primary_camera": "iPhone 15 Pro or Samsung S24 Ultra — 4K 60fps", "lens_equivalent": "24mm equivalent (standard wide)", "stabilization": "Tripod with phone mount — no handheld", "lighting": "Ring light at 45° angle, 5600K daylight balanced", "microphone": "Rode Wireless GO II lavalier or DJI Mic 2", "backdrop": "Plain wall, 1-2 meters behind subject, no objects"},
        "shots": [{"scene_number": s.get("scene_number"), "shot_type": "CU" if s.get("scene_number") in [1, 5] else "MCU", "framing": "Eyes at upper third, chin at center, shoulders visible", "camera_movement": "Static" if s.get("scene_number") != 3 else "Slow push-in during revelation", "focal_length_feel": "Normal", "text_overlay_zone": "Bottom 30% of frame", "lighting_note": "Key light camera-left, fill camera-right", "cut_trigger": "End of dialogue line"} for s in scenes],
        "b_roll_list": ["Product on clean surface, macro shot", "Hands applying product, overhead angle", "Before/after split screen of skin"],
        "post_notes": "Warm grade, slightly desaturated greens, skin tones punchy. Think Mamaearth aesthetic."
    }


def _generate_edit_timeline(scenes: list, screenplay: dict, phase1: dict,
                            system_prompt: str) -> dict:
    """Edit Timeline: frame-by-frame post-production instruction."""
    total_duration = screenplay.get("total_duration", 40)
    prompt = f"""Generate a professional Edit Timeline for a {total_duration}-second viral video.

Brand: {phase1.get('brand_name', '')}
Platform: {phase1.get('platform', 'Instagram Reels')}

SCENES:
{json.dumps(scenes, indent=2)}

Return JSON:
{{
  "software_recommendation": "CapCut / Premiere Pro / DaVinci Resolve — with reason",
  "total_duration_seconds": {total_duration},
  "music": {{
    "mood": "specific music mood",
    "tempo": "BPM range",
    "drop_point": "which second the music hits hardest",
    "volume_levels": "dialogue vs music ratio per section"
  }},
  "timeline": [
    {{
      "scene_number": 1,
      "start_sec": 0,
      "end_sec": 3,
      "cut_type": "hard cut / J-cut / L-cut / dissolve",
      "text_overlays": [
        {{
          "text": "exact text on screen",
          "appears_at_sec": 0.5,
          "disappears_at_sec": 2.5,
          "style": "bold white / outlined / kinetic",
          "position": "top / bottom / center"
        }}
      ],
      "audio_note": "music fade in / SFX / dialogue only",
      "color_note": "grade change if any for this scene",
      "pacing_note": "jump cut here / let it breathe / speed ramp"
    }}
  ],
  "caption_strategy": "caption style recommendation for this platform",
  "thumbnail_frame": "which exact second makes the best thumbnail and why"
}}"""

    result = _ask(prompt, system_prompt, max_tokens=2048)
    if not result:
        return _edit_timeline_fallback(scenes, total_duration)
    try:
        return _parse_json(result)
    except Exception:
        return _edit_timeline_fallback(scenes, total_duration)


def _edit_timeline_fallback(scenes: list, total_duration: int) -> dict:
    cursor = 0
    timeline = []
    for scene in scenes:
        dur = scene.get("duration", 8)
        timeline.append({"scene_number": scene.get("scene_number"), "start_sec": cursor, "end_sec": cursor + dur, "cut_type": "hard cut", "text_overlays": [], "audio_note": "dialogue primary, music -18dB under", "color_note": "standard grade", "pacing_note": "match cut to next scene"})
        cursor += dur
    return {"software_recommendation": "CapCut — fastest for mobile-first creators with trending audio integration", "total_duration_seconds": total_duration, "music": {"mood": "Upbeat, slightly tense — builds to revelation", "tempo": "120-130 BPM", "drop_point": "Scene 3 revelation moment", "volume_levels": "Dialogue scenes: music at -20dB. B-roll: music at -10dB."}, "timeline": timeline, "caption_strategy": "Auto-caption with manual correction. Bold white text, centered, bottom 25% of frame.", "thumbnail_frame": "Use Scene 3 revelation face — expression of genuine surprise works best for CTR"}


def _generate_clean_script(scenes: list, phase1: dict, language: str,
                           lang_instruction: str, lang_name: str,
                           system_prompt: str) -> dict:
    """Clean Script: the final read-aloud version with no production notes."""
    prompt = f"""{lang_instruction}

Generate a clean read-aloud script from these scenes.
The clean script is ONLY dialogue — no stage directions, no production notes.
Format it for the actor to hold in their hand and read once before filming.

{json.dumps(scenes, indent=2)}

Rules:
- Dialogue only — exact words as written in the scenes
- Add [PAUSE] markers where natural silence helps
- Add [EMPHASIS] markers on the most important word per line
- Add scene beat labels as headers
- Total word count approximate for {language}

Return JSON:
{{
  "language": "{language}",
  "estimated_speaking_time_seconds": {sum(s.get('duration', 8) for s in scenes)},
  "word_count": 0,
  "script_text": "Full formatted script as a single string with newlines. Scene headers, dialogue, pause markers.",
  "scenes": [
    {{
      "scene_number": 1,
      "beat": "Hook",
      "dialogue": "exact words only",
      "key_word_to_emphasize": "the single most important word"
    }}
  ],
  "performance_note": "one sentence summary of how to read this entire script"
}}"""

    result = _ask(prompt, system_prompt, max_tokens=2048)
    if not result:
        return _clean_script_fallback(scenes, language)
    try:
        return _parse_json(result)
    except Exception:
        return _clean_script_fallback(scenes, language)


def _clean_script_fallback(scenes: list, language: str) -> dict:
    script_lines = []
    scene_scripts = []
    for scene in scenes:
        beat = scene.get("title", f"Scene {scene.get('scene_number')}")
        dialogue = scene.get("dialogue", "")
        script_lines.append(f"[{beat.upper()}]\n{dialogue}\n")
        scene_scripts.append({"scene_number": scene.get("scene_number"), "beat": beat, "dialogue": dialogue, "key_word_to_emphasize": dialogue.split()[0] if dialogue else ""})

    return {"language": language, "estimated_speaking_time_seconds": sum(s.get("duration", 8) for s in scenes), "word_count": sum(len(s.get("dialogue", "").split()) for s in scenes), "script_text": "\n".join(script_lines), "scenes": scene_scripts, "performance_note": "Read it once. Then put it down and film it from memory. The best takes are never the ones reading from notes."}


def _production_fallback(phase1: dict, phase3: dict) -> dict:
    scenes = phase3.get("scenes", [])
    return {
        "title": phase3.get("title", f"Video about {phase1.get('topic', 'topic')}"),
        "total_duration": phase3.get("total_duration", 40),
        "platform": phase1.get("platform", "Instagram Reels"),
        "quality_score": 0,
        "actor_brief": _actor_brief_fallback(scenes, phase1),
        "camera_sheet": _camera_sheet_fallback(scenes, phase1.get("platform", "Instagram Reels")),
        "edit_timeline": _edit_timeline_fallback(scenes, phase3.get("total_duration", 40)),
        "clean_script": _clean_script_fallback(scenes, "EN"),
    }


# ============================================================
# SUPPORTING FUNCTIONS — Fluff Examples, Topic Suggestions
# ============================================================

def generate_fluff_examples_ai(topic: str, niche: str = "", language: str = "EN",
                                phase1_data: dict = None) -> list[dict]:
    """Generate 3 niche+topic specific fluff vs specific example pairs."""
    client = _get_client()
    phase1_data = phase1_data or {}
    if not client:
        return _fluff_fallback(topic, niche)

    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["EN"])
    lang_name = LANGUAGE_NAMES.get(language, "English")
    brand_context = _build_brand_context({**phase1_data, "niche": niche})

    prompt = f"""You are a viral content editor who rewrites generic copy into scroll-stopping specifics.

{lang_instruction}
Both the fluff AND specific must be in {lang_name}. No exceptions.

{brand_context}

Generate 3 "Fluff vs Specific" pairs for content about:
- Topic: "{topic}"
- Niche: "{niche or 'General'}"

FLUFF = vague, generic, could be about anything
SPECIFIC = tied to this exact topic+brand, includes a number/timeframe/comparison, sounds like a real person

Return ONLY valid JSON:
[
  {{"fluff": "vague line in {lang_name}", "specific": "specific rewrite in {lang_name}"}},
  {{"fluff": "vague line in {lang_name}", "specific": "specific rewrite in {lang_name}"}},
  {{"fluff": "vague line in {lang_name}", "specific": "specific rewrite in {lang_name}"}}
]"""

    result = _ask(prompt, "", max_tokens=1024)
    if not result:
        return _fluff_fallback(topic, niche)

    try:
        parsed = _parse_json(result)
        if isinstance(parsed, list) and len(parsed) >= 3:
            validated = [{"fluff": str(i["fluff"]), "specific": str(i["specific"])} for i in parsed[:3] if "fluff" in i and "specific" in i]
            if len(validated) == 3:
                return validated
        return _fluff_fallback(topic, niche)
    except Exception:
        return _fluff_fallback(topic, niche)


def _fluff_fallback(topic: str, niche: str) -> list[dict]:
    t = topic or niche or "this topic"
    return [
        {"fluff": f"This {t} tip is amazing", "specific": f"This {t} method cut my time by 40% in 7 days"},
        {"fluff": "You should really try this", "specific": f"I tested 11 {t} methods — only this one actually worked"},
        {"fluff": "Everyone is talking about this", "specific": f"This {t} trick got 2.1M views because it saves ₹180/month"},
    ]


def suggest_topics_ai(niche: str, sub_niche: str = "", language: str = "EN",
                      phase1_data: dict = None) -> list[dict]:
    """Generate viral topic suggestions based on niche with brand context."""
    client = _get_client()
    phase1_data = phase1_data or {}
    if not client:
        return [{"topic": f"Top 5 {niche} tips", "hook_angle": "List format", "difficulty": "easy"}]

    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["EN"])
    brand_context = _build_brand_context({**phase1_data, "niche": niche})
    platform = phase1_data.get("platform", "Instagram Reels")
    platform_rules = PLATFORM_RULES.get(platform, DEFAULT_PLATFORM_RULE)

    prompt = f"""{lang_instruction}

{brand_context}

{platform_rules}

Niche: {niche}
Sub-niche: {sub_niche or 'General'}

Generate 5 viral video topic ideas for {platform} that:
- Are specific to the brand/product context above
- Have a clear hook angle
- Would perform well with Indian audiences
- Could rank on trending for this niche

Return JSON:
[
  {{
    "topic": "specific topic title",
    "hook_angle": "why it hooks viewers — the psychological pull",
    "tribe_emotion": "which TRIBE emotion this targets",
    "difficulty": "easy/medium/hard",
    "estimated_virality": "Low/Medium/High/Exceptional"
  }}
]"""

    result = _ask(prompt, "", max_tokens=1024)
    if not result:
        return [{"topic": f"Top 5 {niche} tips", "hook_angle": "List format", "difficulty": "easy", "tribe_emotion": "Trust", "estimated_virality": "Medium"}]

    try:
        return _parse_json(result)
    except Exception:
        return [{"topic": f"Top 5 {niche} tips", "hook_angle": "List format", "difficulty": "easy", "tribe_emotion": "Trust", "estimated_virality": "Medium"}]
