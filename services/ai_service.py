"""
Backero AI Service — World-Class Viral Script Engine
=====================================================
7-Upgrade Implementation:
  1. Creator DNA system prompt builder
  2. Role-identity system prompts (persona, not checklist)
  3. Platform algorithm context briefs
  4. Two-call chain: Strategy → Script
  5. Few-shot niche examples
  6. Hard constraint injection
  7. Self-critique reflection pass (Haiku)
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


# ═══════════════════════════════════════════════════════════════════════
#  LANGUAGE MAP
# ═══════════════════════════════════════════════════════════════════════

LANGUAGE_INSTRUCTIONS = {
    "EN": "LANGUAGE: Write ALL output in English only.",
    "HI": "LANGUAGE: Write ALL output — every word, phrase, and sentence — in Hindi using Devanagari script (हिंदी). Do NOT use English except for proper nouns that have no Hindi equivalent.",
    "TA": "LANGUAGE: Write ALL output — every word, phrase, and sentence — in Tamil script (தமிழ்). Do NOT use English except for proper nouns.",
    "TE": "LANGUAGE: Write ALL output — every word, phrase, and sentence — in Telugu script (తెలుగు). Do NOT use English except for proper nouns.",
    "KN": "LANGUAGE: Write ALL output — every word, phrase, and sentence — in Kannada script (ಕನ್ನಡ). Do NOT use English except for proper nouns.",
    "ML": "LANGUAGE: Write ALL output — every word, phrase, and sentence — in Malayalam script (മലയാളം). Do NOT use English except for proper nouns.",
    "BN": "LANGUAGE: Write ALL output — every word, phrase, and sentence — in Bengali script (বাংলা). Do NOT use English except for proper nouns.",
    "MR": "LANGUAGE: Write ALL output — every word, phrase, and sentence — in Marathi using Devanagari script (मराठी). Do NOT use English except for proper nouns.",
    "GU": "LANGUAGE: Write ALL output — every word, phrase, and sentence — in Gujarati script (ગુજરાતી). Do NOT use English except for proper nouns.",
    "PA": "LANGUAGE: Write ALL output — every word, phrase, and sentence — in Punjabi/Gurmukhi script (ਪੰਜਾਬੀ). Do NOT use English except for proper nouns.",
    "HIN-EN": "LANGUAGE: Write ALL output in Hinglish — natural Hindi+English mix as spoken by urban Indian youth. Use Roman script throughout (not Devanagari). Example style: 'Yaar, ye trick try karo — 40% faster results milenge'.",
    "TAM-EN": "LANGUAGE: Write ALL output in Tanglish — natural Tamil+English mix as spoken by urban Tamil youth. Use Roman script throughout (not Tamil script). Example style: 'Bro, indha trick try pannunga — 40% faster results kedaikum'.",
}


# ═══════════════════════════════════════════════════════════════════════
#  UPGRADE 3 — Platform Algorithm Context
# ═══════════════════════════════════════════════════════════════════════

PLATFORM_ALGORITHM_BRIEF = {
    "YouTube Shorts": (
        "Algorithm rewards: watch-through rate above 70%, likes-to-views ratio > 4%, "
        "and shares. Shorts are surfaced in a swipe-feed; the first frame is everything. "
        "Optimal structure: cold-open hook (no intro/greeting), rapid value escalation in "
        "the middle, and an open-loop or question at the end that drives replay or comment. "
        "Viewer psychology: YouTube audiences expect slightly more substance than TikTok — "
        "they tolerate 45-60 sec if there is density. What makes content shareable here: "
        "a 'wait, really?' moment they want to send to a friend, or a stat they can quote. "
        "Avoid: slow intros, asking viewers to 'like and subscribe' before delivering value."
    ),
    "TikTok": (
        "Algorithm rewards: completion rate is king, followed by shares > saves > comments > likes. "
        "Videos that get replayed rank highest. TikTok tests every video with 200-500 viewers first; "
        "if 60%+ finish, it expands. Optimal structure: pattern-interrupt hook in first 0.5 sec, "
        "curiosity gap that builds through middle, payoff that feels both surprising and inevitable. "
        "Viewer psychology: lowest attention threshold of any platform — you have 0.3 sec before "
        "a thumb swipe. Content must feel native, spontaneous, unpolished-on-purpose. "
        "What makes content shareable: humor, shock, 'I literally just learned this', relatable pain. "
        "Avoid: corporate tone, long text overlays, asking viewers to follow before the value."
    ),
    "Instagram": (
        "Algorithm rewards: saves and shares above all else, then comments that are >4 words. "
        "Instagram surfaces Reels in Explore based on early engagement velocity. "
        "Optimal structure: visually striking first frame (thumbnail matters here more than TikTok), "
        "educational or aspirational value in 15-30 sec, CTA that drives save ('screenshot this'). "
        "Viewer psychology: Instagram users curate identity — they share content that makes THEM "
        "look smart, cultured, or in-the-know. Content must be 'save-worthy' reference material. "
        "What makes content shareable: actionable tips, aesthetic reveals, before/after transformations. "
        "Avoid: ugly thumbnails, TikTok watermarks, talking-head without visual variety."
    ),
    "Instagram Reels": (
        "Algorithm rewards: saves and shares above all else, then comments that are >4 words. "
        "Reels are surfaced in Explore and the dedicated Reels tab based on early engagement velocity. "
        "Optimal structure: visually striking first frame, educational or aspirational value in "
        "15-30 sec, CTA that drives save. Viewer psychology: Instagram users curate identity — "
        "they share what makes them look smart or aspirational. "
        "What makes content shareable: actionable tips, aesthetic reveals, transformations. "
        "Avoid: ugly thumbnails, TikTok watermarks, talking-head without visual variety."
    ),
    "LinkedIn": (
        "Algorithm rewards: dwell time (reading/watching duration), comments, and reshares to feed. "
        "LinkedIn heavily favors 'native' content from personal profiles over company pages. "
        "Optimal structure: contrarian or vulnerable opening line, storytelling middle with "
        "professional lesson, specific takeaway framed as career/business advice. "
        "Viewer psychology: professionals scroll LinkedIn to feel productive — content must be "
        "'useful for my career' or 'validates my professional identity'. They share to signal "
        "expertise or thought-leadership to their network. "
        "What makes content shareable: 'I wish someone told me this 10 years ago' moments, "
        "data that challenges conventional business wisdom, honest failure stories with lessons. "
        "Avoid: motivational platitudes, 'agree?' engagement bait, emojis in every line."
    ),
    "Facebook Reels": (
        "Algorithm rewards: shares into Messenger and groups, comments, and watch-through rate. "
        "Facebook pushes Reels heavily in main feed. Optimal structure: relatable hook, "
        "quick value delivery, emotional or funny payoff. Viewer psychology: older demographic "
        "than TikTok, values relatability and practical usefulness. Content must feel approachable. "
        "What makes content shareable: 'tag someone who needs this', practical life hacks. "
        "Avoid: Gen-Z slang, overly trendy formats the audience won't recognize."
    ),
    "Multi-Platform": (
        "When targeting multiple platforms simultaneously, optimize for the lowest common denominator "
        "of attention: TikTok-level hook speed, Instagram-level visual quality, YouTube-level substance. "
        "Keep to 30-45 sec max. Use 9:16 vertical. Avoid platform-specific CTAs ('duet this'). "
        "Focus on the universally shareable: a surprising stat, a useful tip, or an emotional beat "
        "that works regardless of where the viewer encounters it."
    ),
}


# ═══════════════════════════════════════════════════════════════════════
#  UPGRADE 5 — Few-Shot Niche Examples
# ═══════════════════════════════════════════════════════════════════════

NICHE_SCRIPT_EXAMPLES = {
    "Tech": {
        "killer_hook": "Your phone's doing this right now and you have no idea.",
        "dialogue_sample": (
            "ACTOR: So I found this buried setting, right? Three taps. That's it.\n"
            "ACTOR: My battery went from dying at 3pm to lasting till midnight.\n"
            "ACTOR: And the craziest part? Apple doesn't even mention it.\n"
            "ACTOR: I've been telling everyone — you're literally leaving 40% of your battery on the table."
        ),
    },
    "Skincare": {
        "killer_hook": "Your moisturizer's actually making your skin drier.",
        "dialogue_sample": (
            "ACTOR: Okay so I tested this for 28 days — left side, my old routine. Right side, just this.\n"
            "ACTOR: Day seven? Nothing. Day fourteen? My texture completely changed.\n"
            "ACTOR: And it costs less than your Starbucks. I'm talking $4.70.\n"
            "ACTOR: Dermatologists have known this forever — they just don't post about it."
        ),
    },
    "Finance": {
        "killer_hook": "Your savings account is losing you $3,200 a year.",
        "dialogue_sample": (
            "ACTOR: Run this math with me real quick — you've got 10K sitting in savings, yeah?\n"
            "ACTOR: Your bank gives you 0.01%. Inflation's at 3.2%. You're LOSING $319 a year doing nothing.\n"
            "ACTOR: I moved mine here — took 11 minutes — and now it earns 5.1%.\n"
            "ACTOR: That's the difference between retiring at 60 or retiring at 67. Your call."
        ),
    },
    "Fitness": {
        "killer_hook": "The exercise everyone does first is killing their gains.",
        "dialogue_sample": (
            "ACTOR: I spent 3 years starting every workout with cardio. Three years wasted.\n"
            "ACTOR: Then my trainer showed me this study — 22% more muscle when you flip the order.\n"
            "ACTOR: Now I lift first, 20 minutes. Cardio after, 12 minutes. That's it.\n"
            "ACTOR: My arms grew more in 8 weeks than the entire year before."
        ),
    },
    "Food": {
        "killer_hook": "You've been cooking rice wrong your entire life.",
        "dialogue_sample": (
            "ACTOR: Every restaurant does this. Every home cook skips it. One rinse.\n"
            "ACTOR: I'm talking 30 seconds under the tap — watch the water go from cloudy to clear.\n"
            "ACTOR: That starch? That's what makes your rice sticky and clumpy.\n"
            "ACTOR: Do this once and you'll never go back. My wife literally thought I bought new rice."
        ),
    },
    "Travel": {
        "killer_hook": "This $12 trick saved me $900 on my last flight.",
        "dialogue_sample": (
            "ACTOR: So airlines price flights differently based on which COUNTRY you're browsing from.\n"
            "ACTOR: I used a VPN, set my location to India, same exact flight — $340 cheaper.\n"
            "ACTOR: Then I stacked it with a Tuesday 3am booking window. Another $180 off.\n"
            "ACTOR: Total savings: $900 on a round trip. That paid for my entire hotel."
        ),
    },
    "Business": {
        "killer_hook": "We lost $47K before we figured out this one thing.",
        "dialogue_sample": (
            "ACTOR: Our first product launch? Disaster. 2,000 units, 47 sales.\n"
            "ACTOR: The fix wasn't the product — it was the first line of our landing page.\n"
            "ACTOR: We A/B tested one headline change and conversion went from 1.2% to 8.4%.\n"
            "ACTOR: That single sentence turned a failed launch into $280K in 90 days."
        ),
    },
    "Education": {
        "killer_hook": "This study method has a 92% retention rate and nobody teaches it.",
        "dialogue_sample": (
            "ACTOR: Highlighting doesn't work. Re-reading doesn't work. I know, I was shook too.\n"
            "ACTOR: There's this technique from the 1960s called spaced retrieval — here's how it works.\n"
            "ACTOR: You study for 25 minutes, then you CLOSE the book and write down everything you remember.\n"
            "ACTOR: The stuff you forgot? THAT'S what you study next. Your brain literally rewires."
        ),
    },
    "Entertainment": {
        "killer_hook": "This scene almost got cut and it saved the entire movie.",
        "dialogue_sample": (
            "ACTOR: The studio wanted to remove this scene. The director fought for THREE months.\n"
            "ACTOR: Test audiences? Hated it. Focus groups? Said it was confusing.\n"
            "ACTOR: But when the movie came out, critics called it the single best moment of the decade.\n"
            "ACTOR: And now it's been memed 14 million times. Sometimes the audience doesn't know what they want."
        ),
    },
    "Lifestyle": {
        "killer_hook": "I stopped waking up at 5am and my productivity doubled.",
        "dialogue_sample": (
            "ACTOR: Every productivity guru says wake up at 5. I did it for a year. I was miserable.\n"
            "ACTOR: Then I read this sleep study — your chronotype is genetic. You can't hack it.\n"
            "ACTOR: I switched to my natural rhythm, 8am wake, and my deep work hours went from 3 to 6.\n"
            "ACTOR: Stop fighting your biology. Start working WITH it."
        ),
    },
}


# ═══════════════════════════════════════════════════════════════════════
#  UPGRADE 1 — Creator DNA Voice Block
# ═══════════════════════════════════════════════════════════════════════

def build_creator_voice_block(phase1: dict) -> str:
    """Build a rich creator-voice context string from Phase 1 data."""
    creator = phase1.get("content_creator", "").strip() or "an independent content creator"
    actor_brief = phase1.get("actor_brief", "").strip()
    num_actors = phase1.get("number_of_actors", 1) or 1
    platform = phase1.get("platform", "YouTube Shorts")
    aspect = phase1.get("aspect_ratio", "9:16")
    language = phase1.get("language", "EN")
    niche = phase1.get("niche", "General")
    sample_hook = phase1.get("sample_hook", "").strip()

    # Delivery style mapping from actor_brief dropdown values
    delivery_map = {
        "Storyteller / Narrative": "speaks in stories — every point has a beginning, middle, and payoff. Conversational pacing with dramatic pauses.",
        "Teacher / Explainer": "breaks complex ideas into simple steps. Patient but energetic. Uses analogies and 'here, let me show you' energy.",
        "Hype / Energetic": "high-octane delivery. Fast cuts match fast speech. Every sentence lands like a punchline. Exclamation energy without being annoying.",
        "Deadpan / Dry Humor": "delivers wild facts with a completely straight face. The contrast between insane content and calm delivery IS the hook.",
        "Conversational / Friend": "sounds like a friend sharing a secret over coffee. Relaxed, authentic, uses filler words naturally. Zero performance energy.",
        "Confrontational / Debate": "challenges the viewer directly. 'You think X? Wrong. Here's why.' Confident, slightly provocative, backed by data.",
    }

    style_desc = delivery_map.get(actor_brief, "")
    if not style_desc and actor_brief:
        style_desc = f"Delivery personality: {actor_brief}"
    if not style_desc:
        # Infer from platform
        platform_defaults = {
            "TikTok": "fast, punchy, trend-aware. Feels native to the For You Page.",
            "YouTube Shorts": "slightly more substantive than TikTok but still rapid-fire hook energy.",
            "Instagram": "polished, aesthetic, save-worthy. Every frame could be a screenshot.",
            "Instagram Reels": "polished, aesthetic, save-worthy. Every frame could be a screenshot.",
            "LinkedIn": "professional but human. Data-backed contrarian takes delivered with calm authority.",
        }
        style_desc = platform_defaults.get(platform, "conversational, authentic, punchy.")

    lang_label = {
        "EN": "English", "HI": "Hindi", "TA": "Tamil", "TE": "Telugu",
        "KN": "Kannada", "ML": "Malayalam", "BN": "Bengali", "MR": "Marathi",
        "GU": "Gujarati", "PA": "Punjabi", "HIN-EN": "Hinglish",
        "TAM-EN": "Tanglish",
    }.get(language, "English")

    block = f"""<creator_voice>
CREATOR: {creator}
PLATFORM: {platform} ({aspect})
NICHE: {niche}
LANGUAGE: {lang_label}
ACTORS ON SCREEN: {num_actors}
DELIVERY STYLE: {style_desc}"""

    if sample_hook:
        block += f"\nSAMPLE HOOK FROM CREATOR (match this voice): \"{sample_hook}\""

    block += "\n</creator_voice>"
    return block


# ═══════════════════════════════════════════════════════════════════════
#  Core API helpers
# ═══════════════════════════════════════════════════════════════════════

def _ask(prompt: str, system: str = "", max_tokens: int = 4096,
         model: str = "claude-sonnet-4-6") -> Optional[str]:
    """Execute a Claude API call with error handling"""
    client = _get_client()
    if not client:
        return None
    try:
        kwargs = {
            "model": model,
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


# ═══════════════════════════════════════════════════════════════════════
#  UPGRADE 2 — Role-Identity System Prompts
# ═══════════════════════════════════════════════════════════════════════

def _get_phase_system_prompt(phase_number: int, previous_phase_data: dict) -> str:
    """
    Generate the master system prompt with phase isolation enforcement.
    Uses role-identity framing (UPGRADE 2).
    """
    previous_data_str = json.dumps(previous_phase_data, indent=2, default=str)

    return f"""You are AXIS-7, an elite viral video scriptwriter with 847M cumulative views across TikTok, YouTube Shorts, and Instagram Reels. You execute ONE phase at a time with surgical precision.

CURRENT PHASE: {phase_number}
PREVIOUS DATA: {previous_data_str}

Before generating ANY content:
- Execute ONLY Phase {phase_number}
- Previous phase data is READ-ONLY historical context
- Do NOT regenerate, modify, or loop back to previous phases
- Your output advances the narrative FORWARD from where Phase {phase_number - 1} ended

PHASE DEFINITIONS (Reference Only):
Phase 1 - TOPIC EXTRACTION: Generate 3 knowledge nuggets. User selects ONE.
Phase 2 - HOOK ENGINEERING: Craft the opening thumb-stop moment.
Phase 3 - STRUCTURAL OUTLINE: Build the 5-beat retention architecture.
Phase 4 - FULL SCRIPT: Write scene-by-scene production-ready dialogue.
Phase 5 - DELIVERY DIRECTION: Actor cues, pacing, emotional beats.

WRITING MANDATES:
- Dialogue sounds like a friend texting an urgent secret at 2AM
- Zero corporate speak: ban "game-changer", "revolutionary", "unlock your potential"
- Every sentence earns its existence or gets cut
- Numbers and specifics over vague claims ("47% faster" not "much faster")
- Conflict, tension, or curiosity in every beat
- Write for a 14-second attention span viewer
- NEVER use markdown formatting (no **bold**, no # headers, no * bullets)
- Return plain conversational text only in all dialogue fields

BEGIN PHASE {phase_number} OUTPUT NOW:"""


# ═══════════════════════════════════════════════════════════════════════
#  Phase 1: Nugget Extraction
# ═══════════════════════════════════════════════════════════════════════

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
    Phase 1: Extract 3 knowledge nuggets — UPGRADE 2 role-identity prompt.
    """
    client = _get_client()
    if not client:
        return _nugget_fallback(topic, niche)

    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["EN"])

    # UPGRADE 2: Role-identity, not instruction list
    system_prompt = f"""You are the viral content strategist who identified the single core insight behind 500+ short-form videos that each crossed 10M views. You do not brainstorm — you extract. You read raw research the way a diamond cutter reads rough stone: you find the ONE fracture line where a single tap releases a gem that makes millions of people stop scrolling.

{lang_instruction}
IMPORTANT: The "text" field of every nugget MUST be written in the language specified above. The "type", "source", "rationale" fields may stay in English for technical compatibility.

Your task: Extract exactly 3 DIFFERENT knowledge nuggets that could each be the SINGLE CORE MESSAGE of a viral video.

EXTRACTION RULES:
- If research text is provided, your nuggets MUST come directly FROM that research. Do NOT invent facts.
- Each nugget is a COMPLETE video premise — specific enough that a scriptwriter could build an entire 30-60 second video around just this one point.
- Avoid vague nuggets like "most people get X wrong" — instead say WHAT they get wrong and include the real stat.
- No markdown formatting. Plain text only.

Return ONLY valid JSON array, no markdown:
[
  {{"type": "Shocking Fact", "text": "...", "source": "where this fact came from", "rationale": "why this hooks viewers", "color": "#EF4444"}},
  {{"type": "Practical Hack", "text": "...", "source": "where this technique comes from", "rationale": "why this hooks viewers", "color": "#22C55E"}},
  {{"type": "Story Hook", "text": "...", "source": "the real scenario this is based on", "rationale": "why this hooks viewers", "color": "#F59E0B"}}
]"""

    research_section = ""
    if research_text and len(research_text.strip()) > 50:
        research_section = f"""
RESEARCH TEXT (extract nuggets FROM this — do not ignore it):
---
{research_text[:4000]}
---
"""

    prompt = f"""Topic: {topic}
Niche: {niche or 'General'}
{research_section}
Generate 3 unique knowledge nuggets{' based on the research text above' if research_section else ' for this viral video'}. Each must be specific enough to build an entire video around. Return ONLY the JSON array."""

    result = _ask(prompt, system_prompt)
    if not result:
        return _nugget_fallback(topic, niche)

    try:
        nuggets = _parse_json(result)
        if isinstance(nuggets, list) and len(nuggets) >= 3:
            return nuggets[:3]
        return _nugget_fallback(topic, niche)
    except Exception:
        return _nugget_fallback(topic, niche)


# ═══════════════════════════════════════════════════════════════════════
#  Phase 1: Fluff Examples
# ═══════════════════════════════════════════════════════════════════════

def generate_fluff_examples_ai(topic: str, niche: str = "", language: str = "EN") -> list[dict]:
    """
    Generate 3 niche+topic specific fluff vs specific example pairs.
    UPGRADE 2: Role-identity prompt for fluff checker.
    """
    client = _get_client()
    if not client:
        return _fluff_fallback(topic, niche)

    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["EN"])
    lang_name = {
        "EN": "English", "HI": "Hindi", "TA": "Tamil", "TE": "Telugu",
        "KN": "Kannada", "ML": "Malayalam", "BN": "Bengali",
        "MR": "Marathi", "GU": "Gujarati", "PA": "Punjabi",
        "HIN-EN": "Hinglish", "TAM-EN": "Tanglish",
    }.get(language, "English")

    # UPGRADE 2: Role-identity
    prompt = f"""You are the script doctor who can read a single line and tell whether it stops a scroll or loses a viewer. You have rewritten 10,000+ lines of dialogue for the top short-form agencies in the world. Your superpower: turning vague, generic sentences into specific, data-laden punches that make people screenshot your content.

CRITICAL LANGUAGE RULE: {lang_instruction}
Every single word in your output MUST be in {lang_name}. No exceptions.

TASK: Generate 3 "Fluff vs Specific" example pairs for a creator making content about:
- Topic: "{topic}"
- Niche: "{niche or 'General'}"

The FLUFF example: vague, could apply to anything, sounds AI-generated.
The SPECIFIC rewrite: contains a real number/percentage/timeframe, clearly about "{topic}", sounds like a real person.

Return ONLY a valid JSON array of exactly 3 objects. No markdown, no explanation:
[
  {{"fluff": "vague bad line in {lang_name}", "specific": "specific good rewrite in {lang_name}"}},
  {{"fluff": "vague bad line in {lang_name}", "specific": "specific good rewrite in {lang_name}"}},
  {{"fluff": "vague bad line in {lang_name}", "specific": "specific good rewrite in {lang_name}"}}
]"""

    result = _ask(prompt, "", max_tokens=1024)
    if not result:
        return _fluff_fallback(topic, niche)

    try:
        parsed = _parse_json(result)
        if isinstance(parsed, list) and len(parsed) >= 3:
            validated = []
            for item in parsed[:3]:
                if isinstance(item, dict) and "fluff" in item and "specific" in item:
                    validated.append({"fluff": str(item["fluff"]), "specific": str(item["specific"])})
            if len(validated) == 3:
                return validated
        return _fluff_fallback(topic, niche)
    except Exception:
        return _fluff_fallback(topic, niche)


def _fluff_fallback(topic: str, niche: str) -> list[dict]:
    t = topic or niche or "this topic"
    return [
        {"fluff": f"This {t} tip is amazing", "specific": f"This {t} method cut my time by 40% in 7 days"},
        {"fluff": f"You should really try this", "specific": f"I tested 11 {t} methods — only this one actually worked"},
        {"fluff": f"Everyone is talking about this", "specific": f"This {t} trick got 2.1M views because it saves $180/month"},
    ]


# ═══════════════════════════════════════════════════════════════════════
#  Hook Validation (existing — preserved)
# ═══════════════════════════════════════════════════════════════════════

def enhance_hook_validation(hook_text: str, validation_result: dict,
                            topic: str = "", niche: str = "",
                            language: str = "EN") -> dict:
    client = _get_client()
    if not client:
        return validation_result

    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["EN"])

    system_prompt = f"""You are a viral hook specialist. {lang_instruction}

Take a hook with issues and provide 3 improved rewrites (each under 15 words, punchy, with specific data/numbers).
Rules: include a number/stat, create curiosity gap, sound natural, no banned words.

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
        validation_result["ai_rewrites"] = enhanced.get("ai_rewrites", [])
        return validation_result
    except Exception:
        return validation_result


# ═══════════════════════════════════════════════════════════════════════
#  UPGRADE 4 — Strategy → Script → Critique  (3-call chain)
# ═══════════════════════════════════════════════════════════════════════

def _generate_video_strategy(phase1: dict, phase2: dict, language: str = "EN",
                             target_duration: int = 30) -> Optional[dict]:
    """
    Call 1: Fast strategy generation (~500 tokens).
    Returns emotional arc, share trigger, scene strategies, banned phrases.
    """
    selected_nugget = phase1.get("selected_nugget", {})
    nugget_text = f"[{selected_nugget.get('type', 'Fact')}] {selected_nugget.get('text', '')}"
    platform = phase1.get("platform", "YouTube Shorts")
    niche = phase1.get("niche", "General")
    creator_voice = build_creator_voice_block(phase1)
    platform_brief = PLATFORM_ALGORITHM_BRIEF.get(platform, PLATFORM_ALGORITHM_BRIEF.get("Multi-Platform", ""))

    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["EN"])

    system_prompt = f"""You are the head strategist at a viral video agency that has generated 2.1B cumulative views. You do not write scripts — you architect them. You see the emotional blueprint beneath every viral hit: why it hooked, why they stayed, why they shared. You design that blueprint for others to execute.

{creator_voice}

<platform_context>
{platform_brief}
</platform_context>

{lang_instruction}"""

    prompt = f"""Design the viral strategy for a {target_duration}-second {platform} video.

CORE NUGGET (the entire video serves this ONE idea): {nugget_text}
NICHE: {niche}
CONTENT TYPE: {phase2.get('content_type', 'educational')}
FORMAT: {phase2.get('selected_format', 'talking_head')}

Return ONLY JSON, no markdown:
{{
  "emotional_arc": "one sentence describing the emotional journey from start to finish",
  "share_trigger": "the specific moment or revelation that makes someone send this to a friend",
  "hook_angle": "the exact psychological lever the first 2 seconds pull (curiosity gap / pattern interrupt / identity challenge / shocking stat)",
  "scene_strategy": [
    {{"beat": "HOOK", "seconds": X, "job": "what this beat must accomplish emotionally"}},
    {{"beat": "SETUP", "seconds": X, "job": "..."}},
    {{"beat": "REVELATION", "seconds": X, "job": "..."}},
    {{"beat": "PROOF", "seconds": X, "job": "..."}},
    {{"beat": "CTA", "seconds": X, "job": "..."}}
  ],
  "banned_phrases": ["list", "of", "generic", "phrases", "to", "avoid"]
}}

All 5 beat seconds must sum to exactly {target_duration}."""

    result = _ask(prompt, system_prompt, max_tokens=600)
    if not result:
        return None
    try:
        return _parse_json(result)
    except Exception:
        return None


def _generate_screenplay_from_strategy(strategy: dict, phase1: dict, phase2: dict,
                                       language: str = "EN",
                                       target_duration: int = 30) -> Optional[dict]:
    """
    Call 2: Full screenplay generation from strategy blueprint.
    """
    selected_nugget = phase1.get("selected_nugget", {})
    nugget_text = f"[{selected_nugget.get('type', 'Fact')}] {selected_nugget.get('text', '')}"
    platform = phase1.get("platform", "YouTube Shorts")
    niche = phase1.get("niche", "General")
    hook = phase1.get("hook_text", "") or phase1.get("hook", "")
    creator_voice = build_creator_voice_block(phase1)
    platform_brief = PLATFORM_ALGORITHM_BRIEF.get(platform, PLATFORM_ALGORITHM_BRIEF.get("Multi-Platform", ""))

    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["EN"])

    # UPGRADE 5: Get niche example
    niche_example = NICHE_SCRIPT_EXAMPLES.get(niche, NICHE_SCRIPT_EXAMPLES.get("Tech", {}))
    example_block = ""
    if niche_example:
        example_block = f"""
<example_for_reference>
NICHE: {niche}
KILLER HOOK: "{niche_example.get('killer_hook', '')}"
DIALOGUE STYLE:
{niche_example.get('dialogue_sample', '')}
</example_for_reference>

Write dialogue that matches this ENERGY and SPECIFICITY level. Do not copy — match the vibe."""

    # UPGRADE 6: Hard constraints
    blacklist_words = phase1.get("blacklist_words", [])
    if isinstance(blacklist_words, str):
        try:
            blacklist_words = json.loads(blacklist_words)
        except Exception:
            blacklist_words = [w.strip() for w in blacklist_words.split(",") if w.strip()]

    banned_from_strategy = strategy.get("banned_phrases", []) if strategy else []
    all_banned = list(set(
        ["important", "crucial", "key", "essential", "vital", "amazing", "incredible",
         "game-changer", "revolutionary", "unlock", "secret", "mind-blowing", "insane"]
        + (blacklist_words or [])
        + (banned_from_strategy or [])
    ))

    constraint_block = f"""
<hard_constraints>
THESE ARE NON-NEGOTIABLE. VIOLATING ANY ONE MEANS THE SCRIPT FAILS:
1. Hook (Scene 1 dialogue) must be 8 WORDS OR FEWER. Count them.
2. BANNED WORDS — do NOT use any of these anywhere in dialogue: {', '.join(all_banned)}
3. ALL dialogue must use contractions (you're, it's, they're, don't, can't — NEVER "you are", "it is", "do not", "can not")
4. Scene 3 MUST contain at least one specific number with %, $, or a specific timeframe
5. The FINAL line of Scene 5 must be either a QUESTION or an incomplete sentence that creates an open loop (ends with "..." or a question mark)
6. NEVER use markdown formatting. No **bold**, no # headers, no * bullets. Plain conversational text only.
7. Dialogue must sound like a real human said it to a friend. Not like a blog post, article, or AI output.
</hard_constraints>"""

    strategy_block = ""
    if strategy:
        strategy_block = f"""
<video_strategy>
EMOTIONAL ARC: {strategy.get('emotional_arc', '')}
SHARE TRIGGER: {strategy.get('share_trigger', '')}
HOOK ANGLE: {strategy.get('hook_angle', '')}
SCENE BLUEPRINT:
{json.dumps(strategy.get('scene_strategy', []), indent=2)}
</video_strategy>

Follow this strategy exactly. Each scene's "job" must be fulfilled."""

    # UPGRADE 2: Role-identity for screenplay writer
    system_prompt = f"""You are the head writer at the world's top short-form video agency. Your obsession: dialogue that sounds like something a real person said to their friend at 2am, never like an article or a LinkedIn post. You have written 3,000+ scripts. The ones that hit 10M+ views all had one thing in common — every single line earned its place or got cut.

{creator_voice}

<platform_context>
{platform_brief}
</platform_context>

{lang_instruction}

{example_block}

{constraint_block}"""

    # Build language-specific example for the JSON template
    lang_name_map = {
        "EN": "English", "HI": "Hindi", "TA": "Tamil", "TE": "Telugu",
        "KN": "Kannada", "ML": "Malayalam", "BN": "Bengali",
        "MR": "Marathi", "GU": "Gujarati", "PA": "Punjabi",
        "HIN-EN": "Hinglish", "TAM-EN": "Tanglish",
    }
    target_lang_name = lang_name_map.get(language, "English")
    is_non_english = language != "EN"

    lang_dialogue_note = ""
    if is_non_english:
        lang_dialogue_note = f"""

⚠️ LANGUAGE OVERRIDE — READ THIS CAREFULLY:
The "dialogue" field in EVERY scene MUST be written in {target_lang_name}.
The "title" field MUST also be in {target_lang_name}.
ONLY the JSON keys (scene_number, title, duration, scene_setting, actor_delivery, dialogue) stay in English.
The VALUES of "dialogue" and "title" MUST be in {target_lang_name}. Do NOT write dialogue in English.
The "scene_setting" and "actor_delivery" fields may remain in English (they are technical stage directions)."""

    prompt = f"""{strategy_block}

CRITICAL LANGUAGE REQUIREMENT: {lang_instruction}
ALL dialogue lines MUST be written in {target_lang_name}. This is non-negotiable.{lang_dialogue_note}

Write a 5-scene viral video screenplay for:
- Platform: {platform}
- Niche: {niche}
- Selected Nugget (THE CORE MESSAGE): {nugget_text}
- Opening Hook Text: {hook}
- Content Type: {phase2.get('content_type', 'educational')}
- Format: {phase2.get('selected_format', 'talking_head')}
- TOTAL DURATION: {target_duration} seconds

The ENTIRE screenplay is about the selected nugget. Do NOT introduce other facts or points.

Return ONLY JSON, no markdown wrapping:
{{
  "title": "video title in {target_lang_name}",
  "total_duration": {target_duration},
  "scenes": [
    {{
      "scene_number": 1,
      "title": "Hook",
      "duration": <seconds>,
      "scene_setting": "camera shot, framing, movement, text overlays — plain text (English OK)",
      "actor_delivery": "tone, energy, physical cues — plain text (English OK)",
      "dialogue": "exact spoken words IN {target_lang_name.upper()} — the actor speaks {target_lang_name}, NOT English"
    }},
    ...5 scenes total...
  ]
}}

All scene durations must sum to exactly {target_duration}."""

    result = _ask(prompt, system_prompt, max_tokens=3000)
    if not result:
        return None
    try:
        screenplay = _parse_json(result)
        if isinstance(screenplay.get("scenes"), list) and len(screenplay["scenes"]) >= 5:
            return screenplay
        return None
    except Exception:
        return None


def _critique_and_improve(screenplay: dict, language: str = "EN") -> dict:
    """
    UPGRADE 7 — Call 3: Self-critique via claude-haiku.
    Finds the weakest line and rewrites it. Returns improved screenplay.
    """
    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["EN"])

    system_prompt = f"""You are a ruthless script editor. You read a screenplay and instantly spot the single weakest line — the one that would make a viewer swipe away. You fix it in one surgical rewrite that doubles its scroll-stopping power.

{lang_instruction}
Do NOT use markdown formatting in any dialogue. Plain text only."""

    prompt = f"""Here is a 5-scene viral video screenplay:

{json.dumps(screenplay, indent=2)}

TASKS:
1. Rate each scene's "hook power" from 1-10 (how likely is it to prevent a scroll-away?)
2. Identify the single WEAKEST dialogue line across all 5 scenes
3. Rewrite ONLY that one line to be 2x more scroll-stopping (keep same meaning, make it punchier)
4. Return the FULL improved screenplay with that one line replaced

CRITICAL: The rewritten line and ALL dialogue MUST remain in the same language as the original screenplay. {lang_instruction}

Return ONLY JSON:
{{
  "scene_ratings": [
    {{"scene": 1, "hook_power": 8, "note": "why this score"}},
    ...
  ],
  "weakest_line_scene": <scene_number>,
  "original_line": "the weak line",
  "improved_line": "the 2x better version",
  "improved_screenplay": {{
    "title": "...",
    "total_duration": ...,
    "scenes": [ ...full 5 scenes with the one fix applied... ]
  }}
}}"""

    result = _ask(prompt, system_prompt, max_tokens=800,
                  model="claude-haiku-4-5-20251001")
    if not result:
        return screenplay

    try:
        critique = _parse_json(result)
        improved = critique.get("improved_screenplay")
        if improved and isinstance(improved.get("scenes"), list) and len(improved["scenes"]) >= 5:
            return improved
        return screenplay
    except Exception:
        return screenplay


# ═══════════════════════════════════════════════════════════════════════
#  Main Screenplay Orchestrator (3-call chain)
# ═══════════════════════════════════════════════════════════════════════

def generate_screenplay_ai(phase1: dict, phase2: dict, language: str = "EN",
                           target_duration: int = 30) -> dict:
    """
    Phase 3: Generate screenplay using the 3-call chain:
      1. Strategy (fast, ~500 tokens)
      2. Screenplay from strategy (full script)
      3. Critique & improve (Haiku, cheap)
    Falls back gracefully at each step.
    """
    client = _get_client()
    if not client:
        return _screenplay_fallback(phase1, phase2, target_duration)

    # Ensure selected_nugget exists
    selected_nugget = phase1.get("selected_nugget", {})
    if not selected_nugget:
        nuggets = phase1.get("knowledge_nuggets", [])
        selected_nugget = nuggets[0] if nuggets else {"type": "Fact", "text": phase1.get("topic", "")}
        phase1["selected_nugget"] = selected_nugget

    duration = target_duration or 30

    # ── Call 1: Strategy ──────────────────────────────────────────
    try:
        strategy = _generate_video_strategy(phase1, phase2, language, duration)
    except Exception as e:
        print(f"[AI] Strategy call failed: {e}")
        strategy = None

    # ── Call 2: Screenplay ────────────────────────────────────────
    try:
        screenplay = _generate_screenplay_from_strategy(strategy, phase1, phase2, language, duration)
    except Exception as e:
        print(f"[AI] Screenplay call failed: {e}")
        screenplay = None

    if not screenplay:
        return _screenplay_fallback(phase1, phase2, duration)

    # ── Call 3: Critique & Improve ────────────────────────────────
    # Skip critique for non-English languages — Haiku tends to rewrite
    # dialogue back to English, defeating the language instruction.
    if language == "EN":
        try:
            improved = _critique_and_improve(screenplay, language)
            return improved
        except Exception as e:
            print(f"[AI] Critique call failed (using unimproved screenplay): {e}")
            return screenplay
    else:
        print(f"[AI] Skipping critique pass for non-English language ({language}) to preserve dialogue language")
        return screenplay


def _screenplay_fallback(phase1: dict, phase2: dict, duration: int = 30) -> dict:
    """Fallback screenplay when API fails — respects target duration"""
    topic = phase1.get("topic", "your topic")
    hook = phase1.get("hook_text", "") or phase1.get("hook", "Wait, did you know this?")
    selected_nugget = phase1.get("selected_nugget", {})
    nugget_text = selected_nugget.get("text", f"the truth about {topic}")

    d = duration
    hook_d = max(2, round(d * 0.1))
    prob_d = round(d * 0.2)
    rev_d = round(d * 0.28)
    proof_d = round(d * 0.28)
    cta_d = d - hook_d - prob_d - rev_d - proof_d

    return {
        "title": f"The Truth About {topic}",
        "total_duration": d,
        "scenes": [
            {
                "scene_number": 1,
                "title": "Hook",
                "duration": hook_d,
                "scene_setting": "Close-up face shot, eye-level, slight camera push-in. Clean background.",
                "actor_delivery": "Conspiratorial whisper, leaning in, wide eyes, slight head shake",
                "dialogue": hook if hook else "Okay so... nobody's talking about this."
            },
            {
                "scene_number": 2,
                "title": "Problem",
                "duration": prob_d,
                "scene_setting": "Medium shot, cut to b-roll of relevant imagery. Text overlay: key stat.",
                "actor_delivery": "Frustrated energy, hand gestures emphasizing pain points, building tension",
                "dialogue": f"Here's the thing about {topic} that nobody tells you... and it's actually kind of wild when you think about it."
            },
            {
                "scene_number": 3,
                "title": "Revelation",
                "duration": rev_d,
                "scene_setting": "Dynamic shot, text overlays appearing with key points. Quick cuts.",
                "actor_delivery": "Building excitement, faster pace, confident posture, finger pointing",
                "dialogue": f"But here's what I found out: {nugget_text}. Like... that changes everything, right?"
            },
            {
                "scene_number": 4,
                "title": "Proof",
                "duration": proof_d,
                "scene_setting": "Screen share or demonstration footage. Numbered list overlay.",
                "actor_delivery": "Teacher mode, clear enunciation, pointing at visuals, nodding",
                "dialogue": "Look - I'll show you exactly what I mean. Step one... step two... and boom. See that? The numbers don't lie."
            },
            {
                "scene_number": 5,
                "title": "CTA",
                "duration": cta_d,
                "scene_setting": "Back to face, slight zoom out, warm lighting. Follow button animation.",
                "actor_delivery": "Friendly, inviting, direct eye contact, genuine smile",
                "dialogue": "Save this for later. And follow because part 2 is where it gets really interesting..."
            }
        ]
    }


# ═══════════════════════════════════════════════════════════════════════
#  Scene Regeneration (existing — preserved)
# ═══════════════════════════════════════════════════════════════════════

def regenerate_scene_ai(existing_scene: dict, phase1: dict, phase2: dict,
                        direction: str, language: str = "EN") -> dict:
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
Make the dialogue more punchy and conversational. No markdown formatting.
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
    except Exception:
        return existing_scene


# ═══════════════════════════════════════════════════════════════════════
#  Quality Analysis (existing — preserved)
# ═══════════════════════════════════════════════════════════════════════

def analyze_quality_ai(screenplay: dict, phase1: dict, language: str = "EN") -> dict:
    client = _get_client()
    if not client:
        return {"score": 75, "verdict": "pass", "issues": [], "suggestions": []}

    previous_data = {"phase1": phase1, "screenplay": screenplay}
    system_prompt = _get_phase_system_prompt(4, previous_data)
    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["EN"])

    prompt = f"""{lang_instruction}

Analyze this screenplay for viral potential:

{json.dumps(screenplay, indent=2)}

Score 0-100 on: hook strength, retention architecture, dialogue authenticity, visual storytelling, CTA effectiveness.

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
  "issues": ["issue 1", "issue 2"],
  "suggestions": ["improvement 1", "improvement 2"]
}}"""

    result = _ask(prompt, system_prompt, max_tokens=2048)
    if not result:
        return {"score": 75, "verdict": "pass", "issues": [], "suggestions": []}

    try:
        return _parse_json(result)
    except Exception:
        return {"score": 75, "verdict": "pass", "issues": [], "suggestions": []}


# ═══════════════════════════════════════════════════════════════════════
#  Production Summary (existing — preserved)
# ═══════════════════════════════════════════════════════════════════════

def generate_production_summary_ai(phase1: dict, phase2: dict, phase3: dict,
                                   phase4: dict, language: str = "EN") -> dict:
    client = _get_client()
    if not client:
        return _production_fallback(phase1, phase3)

    previous_data = {"phase1": phase1, "phase2": phase2, "phase3": phase3, "phase4": phase4}
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
    except Exception:
        return _production_fallback(phase1, phase3)


def _production_fallback(phase1: dict, phase3: dict) -> dict:
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


# ═══════════════════════════════════════════════════════════════════════
#  Topic Suggestions (existing — preserved)
# ═══════════════════════════════════════════════════════════════════════

def suggest_topics_ai(niche: str, sub_niche: str = "", language: str = "EN") -> list[dict]:
    client = _get_client()
    if not client:
        return [{"topic": f"Top 5 {niche} tips", "hook_angle": "List format"},
                {"topic": f"Common {niche} mistakes", "hook_angle": "Problem-solution"}]

    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["EN"])

    prompt = f"""{lang_instruction}

Niche: {niche}
Sub-niche: {sub_niche or 'General'}

Generate 5 viral video topic ideas for short-form platforms.

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
    except Exception:
        return [{"topic": f"Top 5 {niche} tips", "hook_angle": "List format", "difficulty": "easy"}]
