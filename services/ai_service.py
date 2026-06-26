import os
  import re
  import json
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

  BEGIN PHASE {phase_number} OUTPUT NOW:"""


  def _ask(prompt: str, system: str = "", max_tokens: int = 4096) -> Optional[str]:
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
      text = re.sub(r"^```(?:json)?\s*", "", text.strip())
      text = re.sub(r"\s*```$", "", text.strip())
      return json.loads(text.strip())


  def _nugget_fallback(topic: str, niche: str) -> list[dict]:
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


  def extract_nuggets_ai(topic: str, research_text: str = "", niche: str = "", language: str = "EN") -> list[dict]:
      """Phase 1: Extract 3 knowledge nuggets for user to choose from"""

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


  def enhance_hook_validation(hook: str, topic: str, niche: str = "", language: str = "EN") -> dict:
      """Enhance and validate a hook using AI"""

      client = _get_client()
      if not client:
          return {"enhanced_hook": hook, "suggestions": [], "score": 70}

      lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["EN"])

      system_prompt = f"""You are a viral hook specialist. {lang_instruction}

  Analyze the hook and return JSON:
  {{"enhanced_hook": "improved version under 15 words", "suggestions": ["suggestion1", "suggestion2"], "score": 0-100, "issues": ["issue1"]}}"""

      prompt = f"Hook: {hook}\nTopic: {topic}\nNiche: {niche}"

      result = _ask(prompt, system_prompt, max_tokens=1024)
      if not result:
          return {"enhanced_hook": hook, "suggestions": [], "score": 70}

      try:
          return _parse_json(result)
      except:
          return {"enhanced_hook": hook, "suggestions": [], "score": 70}


  def generate_screenplay_ai(phase1: dict, phase2: dict, language: str = "EN") -> dict:
      """Phase 3: Generate screenplay using ONLY the selected nugget"""

      client = _get_client()
      if not client:
          return _screenplay_fallback(phase1, phase2)

      # FIXED: Use only the SELECTED nugget, not all nuggets
      selected_nugget = phase1.get("selected_nugget", {})
      if not selected_nugget:
          # Fallback to first nugget if none selected (shouldn't happen)
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

  Create exactly 5 scenes. Each scene needs:
  1. Scene number and title
  2. Duration in seconds
  3. <scene_setting> tag with visual details
  4. <actor_delivery> tag with performance direction
  5. <dialogue> tag with exact spoken words

  Return as JSON:
  {{
    "title": "video title",
    "total_duration": seconds,
    "scenes": [
      {{
        "scene_number": 1,
        "title": "Hook",
        "duration": 3,
        "scene_setting": "...",
        "actor_delivery": "...",
        "dialogue": "..."
      }}
    ]
  }}"""

      result = _ask(prompt, system_prompt, max_tokens=4096)
      if not result:
          return _screenplay_fallback(phase1, phase2)

      try:
          return _parse_json(result)
      except:
          return _screenplay_fallback(phase1, phase2)


  def _screenplay_fallback(phase1: dict, phase2: dict) -> dict:
      topic = phase1.get("topic", "your topic")
      hook = phase1.get("hook", "Wait, did you know this?")

      return {
          "title": f"The Truth About {topic}",
          "total_duration": 45,
          "scenes": [
              {
                  "scene_number": 1,
                  "title": "Hook",
                  "duration": 3,
                  "scene_setting": "Close-up face shot, eye-level, slight camera push",
                  "actor_delivery": "Conspiratorial whisper, leaning in, wide eyes",
                  "dialogue": hook
              },
              {
                  "scene_number": 2,
                  "title": "Problem",
                  "duration": 8,
                  "scene_setting": "Medium shot, b-roll cuts of relevant imagery",
                  "actor_delivery": "Frustrated energy, hand gestures emphasizing pain points",
                  "dialogue": f"Here's the thing about {topic} that nobody talks about..."
              },
              {
                  "scene_number": 3,
                  "title": "Revelation",
                  "duration": 12,
                  "scene_setting": "Dynamic shot, text overlays appearing with key points",
                  "actor_delivery": "Building excitement, faster pace, confident posture",
                  "dialogue": "But I discovered something that changes everything..."
              },
              {
                  "scene_number": 4,
                  "title": "Proof",
                  "duration": 15,
                  "scene_setting": "Screen recordings, demonstrations, visual evidence",
                  "actor_delivery": "Teacher mode, clear enunciation, pointing at visuals",
                  "dialogue": "Look at this - the numbers don't lie..."
              },
              {
                  "scene_number": 5,
                  "title": "CTA",
                  "duration": 7,
                  "scene_setting": "Back to face, slight zoom out, warm lighting",
                  "actor_delivery": "Friendly, inviting, direct eye contact",
                  "dialogue": "Save this for later. And follow for part 2 where I show you exactly how to do this yourself."
              }
          ]
      }


  def regenerate_scene_ai(existing_scene: dict, phase1: dict, phase2: dict, direction: str, language: str = "EN") -> dict:
      """Regenerate a single scene with director notes"""

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

  Keep the same scene_number and approximate duration. Return JSON with same structure but improved content."""

      result = _ask(prompt, system_prompt, max_tokens=2048)
      if not result:
          return existing_scene

      try:
          return _parse_json(result)
      except:
          return existing_scene


  def analyze_quality_ai(screenplay: dict, phase1: dict, language: str = "EN") -> dict:
      """Phase 4: Quality analysis and scoring"""

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

  Score 0-100 on:
  - Hook strength (first 3 seconds)
  - Retention architecture (keeps viewers watching)
  - Dialogue authenticity (sounds human, not AI)
  - Visual storytelling
  - CTA effectiveness

  Return JSON:
  {{
    "score": 0-100,
    "verdict": "pass" or "needs_work",
    "breakdown": {{"hook": score, "retention": score, "dialogue": score, "visuals": score, "cta": score}},
    "issues": ["critical issues"],
    "suggestions": ["improvement suggestions"]
  }}"""

      result = _ask(prompt, system_prompt, max_tokens=2048)
      if not result:
          return {"score": 75, "verdict": "pass", "issues": [], "suggestions": []}

      try:
          return _parse_json(result)
      except:
          return {"score": 75, "verdict": "pass", "issues": [], "suggestions": []}


  def generate_production_summary_ai(phase1: dict, phase2: dict, phase3: dict, phase4: dict, language: str = "EN") -> dict:
      """Phase 5: Generate production documentation"""

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

  Create a production brief for the video team:

  {json.dumps(previous_data, indent=2)}

  Return JSON:
  {{
    "title": "final video title",
    "duration": "XX seconds",
    "platform": "platform name",
    "equipment_needed": ["list of gear"],
    "location_notes": "shooting location suggestions",
    "wardrobe": "clothing recommendations",
    "props": ["props needed"],
    "post_production": {{
      "editing_style": "description",
      "music_mood": "description",
      "text_overlays": ["key text to add"],
      "transitions": "transition style"
    }},
    "talent_notes": "direction for the actor/creator"
  }}"""

      result = _ask(prompt, system_prompt, max_tokens=2048)
      if not result:
          return _production_fallback(phase1, phase3)

      try:
          return _parse_json(result)
      except:
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
