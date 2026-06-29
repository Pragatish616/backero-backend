from __future__ import annotations
from models.phase3 import SceneBeat, Camera, Actor, EditMarker, GoldenRulesCheck

SCENE_TEMPLATES = {
    "Step-by-Step": [
        {"name": "THE HOOK", "start": 0, "end": 3, "camera": {"shot": "Close-up", "angle": "Low angle", "movement": "Push in"}, "energy": 9, "pace": "fast"},
        {"name": "AUTHORITY GAP", "start": 3, "end": 8, "camera": {"shot": "Medium", "angle": "Eye level", "movement": "Static"}, "energy": 7, "pace": "medium"},
        {"name": "STEP/HACK", "start": 8, "end": 15, "camera": {"shot": "Close-up", "angle": "Overhead", "movement": "Dolly"}, "energy": 8, "pace": "medium"},
        {"name": "THE PROOF", "start": 15, "end": 25, "camera": {"shot": "Medium", "angle": "Eye level", "movement": "Dolly right"}, "energy": 8, "pace": "medium"},
        {"name": "CTA", "start": 25, "end": 30, "camera": {"shot": "Close-up", "angle": "Eye level", "movement": "Static"}, "energy": 9, "pace": "fast"},
    ],
    "PAS": [
        {"name": "PROBLEM", "start": 0, "end": 4, "camera": {"shot": "Close-up", "angle": "Low angle", "movement": "Handheld shake"}, "energy": 9, "pace": "fast"},
        {"name": "AGITATE", "start": 4, "end": 10, "camera": {"shot": "Medium", "angle": "Dutch angle", "movement": "Slow push"}, "energy": 7, "pace": "slow"},
        {"name": "SOLUTION", "start": 10, "end": 20, "camera": {"shot": "Close-up", "angle": "Eye level", "movement": "Dolly"}, "energy": 8, "pace": "medium"},
        {"name": "PROOF", "start": 20, "end": 27, "camera": {"shot": "Medium wide", "angle": "Eye level", "movement": "Pan right"}, "energy": 8, "pace": "medium"},
        {"name": "CTA", "start": 27, "end": 30, "camera": {"shot": "Close-up", "angle": "Eye level", "movement": "Static"}, "energy": 9, "pace": "fast"},
    ],
    "Story Framework": [
        {"name": "HOOK/INCITING", "start": 0, "end": 3, "camera": {"shot": "Close-up", "angle": "Low angle", "movement": "Push in"}, "energy": 9, "pace": "fast"},
        {"name": "CONFLICT", "start": 3, "end": 10, "camera": {"shot": "Medium", "angle": "Eye level", "movement": "Handheld"}, "energy": 7, "pace": "medium"},
        {"name": "JOURNEY", "start": 10, "end": 20, "camera": {"shot": "Medium wide", "angle": "Various", "movement": "Track"}, "energy": 6, "pace": "slow"},
        {"name": "RESOLUTION", "start": 20, "end": 27, "camera": {"shot": "Medium", "angle": "Eye level", "movement": "Dolly in"}, "energy": 9, "pace": "fast"},
        {"name": "CTA/LESSON", "start": 27, "end": 30, "camera": {"shot": "Close-up", "angle": "Eye level", "movement": "Static"}, "energy": 8, "pace": "medium"},
    ],
    "Smart vs Dumb": [
        {"name": "DUMB WAY HOOK", "start": 0, "end": 3, "camera": {"shot": "Close-up", "angle": "Low angle", "movement": "Whip pan"}, "energy": 9, "pace": "fast"},
        {"name": "SMART CONTRAST", "start": 3, "end": 12, "camera": {"shot": "Medium", "angle": "Eye level", "movement": "Track left"}, "energy": 8, "pace": "medium"},
        {"name": "THE PROOF", "start": 12, "end": 22, "camera": {"shot": "Close-up", "angle": "Overhead", "movement": "Dolly"}, "energy": 8, "pace": "medium"},
        {"name": "CTA", "start": 22, "end": 30, "camera": {"shot": "Close-up", "angle": "Eye level", "movement": "Static"}, "energy": 9, "pace": "fast"},
    ],
    "Comparison A vs B": [
        {"name": "HOOK/THESIS", "start": 0, "end": 3, "camera": {"shot": "Close-up", "angle": "Low angle", "movement": "Push in"}, "energy": 9, "pace": "fast"},
        {"name": "OPTION A", "start": 3, "end": 12, "camera": {"shot": "Medium", "angle": "Eye level", "movement": "Pan left"}, "energy": 7, "pace": "medium"},
        {"name": "OPTION B", "start": 12, "end": 22, "camera": {"shot": "Medium", "angle": "Eye level", "movement": "Pan right"}, "energy": 7, "pace": "medium"},
        {"name": "VERDICT", "start": 22, "end": 27, "camera": {"shot": "Close-up", "angle": "Eye level", "movement": "Dolly in"}, "energy": 9, "pace": "fast"},
        {"name": "CTA", "start": 27, "end": 30, "camera": {"shot": "Close-up", "angle": "Eye level", "movement": "Static"}, "energy": 9, "pace": "fast"},
    ],
}

# Map structure names to template keys
STRUCTURE_ALIASES = {
    "Step-by-Step": "Step-by-Step",
    "PAS": "PAS",
    "Story Framework": "Story Framework",
    "Smart vs Dumb": "Smart vs Dumb",
    "Comparison A vs B": "Comparison A vs B",
    "List Structure": "Step-by-Step",
    "3-Level Structure": "Step-by-Step",
    "Outcome→Pain→Solution": "PAS",
    "Time-Based Experiment": "Step-by-Step",
}

CONTENT_STYLE_ACTIONS = {
    "Demonstration": "Actor demonstrates with props, showing the technique in real-time",
    "Reaction": "Actor reacts with genuine surprise, leaning into camera",
    "Story": "Actor narrates with emotional expression, gesturing naturally",
    "Comparison": "Actor holds up two items side by side, pointing at differences",
    "Reveal": "Actor slowly reveals the result, building suspense with hand placement",
    "Challenge": "Actor attempts the challenge with visible effort and determination",
}


def get_scene_template(structure_name: str) -> list[dict]:
    key = STRUCTURE_ALIASES.get(structure_name, "Step-by-Step")
    return SCENE_TEMPLATES.get(key, SCENE_TEMPLATES["Step-by-Step"])


def scale_templates_to_duration(templates: list[dict], target_seconds: int) -> list[dict]:
    """Scale template timings proportionally to fit the target duration."""
    if not templates:
        return templates
    original_end = max(t["end"] for t in templates)
    if original_end <= 0:
        return templates
    ratio = target_seconds / original_end
    scaled = []
    for t in templates:
        s = dict(t)
        s["start"] = round(t["start"] * ratio, 1)
        s["end"] = round(t["end"] * ratio, 1)
        scaled.append(s)
    return scaled


def generate_edit_markers(start: float, end: float) -> list[EditMarker]:
    markers = []
    t = start
    events = ["B-cam insert", "Cut to product close-up", "Text overlay appears", "Camera angle change", "Visual transition", "Insert shot"]
    i = 0
    while t < end:
        markers.append(EditMarker(time=f"{t:.1f}s", event=events[i % len(events)]))
        t += 1.5
        i += 1
    return markers


def generate_scene_beat(template: dict, phase1: dict, phase2: dict, nuggets: list, idx: int) -> SceneBeat:
    hook = phase1.get("hook_text", "")
    topic = phase1.get("topic", "")
    style = phase1.get("content_style", "Demonstration")
    action_base = CONTENT_STYLE_ACTIONS.get(style, CONTENT_STYLE_ACTIONS["Demonstration"])

    name = template["name"]
    if idx == 0:
        dialogue = hook or f"Wait — did you know this about {topic}?"
        action = f"(Actor snaps to camera, eyes wide) {action_base}"
        visual = f"BOLD TEXT: \"{hook[:30]}...\"" if hook else f"HOOK TEXT: {topic}"
        audio = "Trending audio hit + whoosh SFX at 0.0s"
    elif "CTA" in name:
        dialogue = f"Save this and follow for more {phase1.get('niche', 'tips').lower()} tips!"
        action = "(Actor points at camera, then taps 'follow' gesture)"
        visual = "CTA: FOLLOW + SAVE overlay with arrow animation"
        audio = "Cash register SFX → music fade out"
    elif nuggets and idx - 1 < len(nuggets):
        n = nuggets[idx - 1]
        text = n.get("text", n) if isinstance(n, dict) else str(n)
        dialogue = text
        action = f"(Actor {action_base.split(',')[0].lower().replace('actor ', '')})"
        visual = f"Text overlay: Key fact #{idx}"
        audio = "Background music continues, subtle emphasis SFX"
    else:
        dialogue = f"And here's what most people get wrong about {topic}..."
        action = f"({action_base})"
        visual = f"Supporting visual for scene {idx + 1}"
        audio = "Background music, medium energy"

    start = template["start"]
    end = template["end"]
    markers = generate_edit_markers(start, end)

    if "CTA" in name:
        markers.insert(0, EditMarker(time=f"{start:.1f}s", event="1.0s silence freeze before CTA"))

    return SceneBeat(
        sceneNum=idx + 1,
        name=name,
        timingStart=start,
        timingEnd=end,
        duration=end - start,
        dialogue=dialogue,
        action=action,
        camera=Camera(**template["camera"]),
        actor=Actor(
            expression="intense" if idx == 0 else "confident",
            energy=template.get("energy", 7),
            pace=template.get("pace", "medium"),
        ),
        visual=visual,
        audio=audio,
        editMarkers=markers,
    )


def calculate_metrics(scenes: list[SceneBeat]) -> dict:
    if not scenes:
        return {"total_runtime_sec": 0, "total_words": 0, "cut_count": 0}
    runtime = max(s.timingEnd for s in scenes)
    words = sum(len(s.dialogue.split()) for s in scenes)
    cuts = sum(len(s.editMarkers) for s in scenes)
    return {"total_runtime_sec": runtime, "total_words": words, "cut_count": cuts}


def validate_golden_rules(scenes: list[SceneBeat]) -> list[GoldenRulesCheck]:
    checks = []
    if not scenes:
        return checks

    # GR1: Tri-Modal Convergence in 0-1.5s
    s1 = scenes[0]
    has_visual = any(float(m.time.replace("s", "")) <= 0.5 for m in s1.editMarkers if m.time)
    has_text = bool(s1.visual)
    checks.append(GoldenRulesCheck(
        rule="Tri-Modal Convergence in 0-1.5s",
        passed=has_visual and has_text and bool(s1.audio),
        evidence=f"Scene 1: visual={'yes' if has_visual else 'no'}, audio={'yes' if s1.audio else 'no'}, text={'yes' if has_text else 'no'}"
    ))

    # GR2: No Talking Head >2s
    all_pass = True
    for s in scenes:
        markers_per_2s = len(s.editMarkers) / max(s.duration / 2, 1)
        if markers_per_2s < 1:
            all_pass = False
    checks.append(GoldenRulesCheck(
        rule="No Talking Head >2s",
        passed=all_pass,
        evidence=f"{'All' if all_pass else 'Some'} scenes have sufficient edit markers"
    ))

    # GR3: Hook Parseable Muted
    checks.append(GoldenRulesCheck(
        rule="Hook Parseable Muted",
        passed=bool(s1.visual),
        evidence=f"Scene 1 visual overlay: {'present' if s1.visual else 'missing'}"
    ))

    # GR4: Show Don't Tell
    all_have_action = all(bool(s.action) for s in scenes)
    checks.append(GoldenRulesCheck(
        rule="Show Don't Tell",
        passed=all_have_action,
        evidence=f"{'All' if all_have_action else 'Some'} scenes have action parentheticals"
    ))

    # GR5: Silent Moments
    last = scenes[-1]
    has_freeze = any("freeze" in m.event.lower() or "silence" in m.event.lower() for m in last.editMarkers)
    checks.append(GoldenRulesCheck(
        rule="Silent Moments",
        passed=has_freeze,
        evidence=f"CTA scene freeze: {'present' if has_freeze else 'missing'}"
    ))

    # GR6: Action-to-Dialogue Ratio >= 2.0
    total_action_words = sum(len(s.action.split()) for s in scenes)
    total_dialogue_words = sum(len(s.dialogue.split()) for s in scenes)
    ratio = total_action_words / max(total_dialogue_words, 1)
    checks.append(GoldenRulesCheck(
        rule="Action-to-Dialogue Ratio >= 2.0",
        passed=ratio >= 2.0,
        evidence=f"Ratio: {ratio:.1f} (action: {total_action_words}, dialogue: {total_dialogue_words})"
    ))

    return checks


def generate_screenplay(supabase, brief_id: str) -> dict:
    from services.ai_service import generate_screenplay_ai

    # Fetch phase 1 and 2 data
    p1 = supabase.table("phase1_data").select("*").eq("brief_id", brief_id).execute()
    phase1 = p1.data[0] if p1.data else {}
    p2 = supabase.table("phase2_data").select("*").eq("brief_id", brief_id).execute()
    phase2 = p2.data[0] if p2.data else {}

    structure = phase2.get("selected_structure", "Step-by-Step")
    nuggets = phase1.get("knowledge_nuggets") or []

    # ── CRITICAL FIX: Reconstruct selected_nugget from index ──────
    selected_idx = phase1.get("selected_nugget_index")
    if selected_idx is not None and nuggets and 0 <= selected_idx < len(nuggets):
        phase1["selected_nugget"] = nuggets[selected_idx]
    elif nuggets:
        phase1["selected_nugget"] = nuggets[0]

    # ── Read user-selected duration ───────────────────────────────
    # Frontend saves as "60s", "30s", etc. — strip the 's' suffix safely
    estimated_length = phase1.get("estimated_length", "") or ""
    clean_length = estimated_length.replace("s", "").strip()
    try:
        target_duration = int(clean_length) if clean_length else 30
    except (ValueError, TypeError):
        target_duration = 30

    # ── Read user-selected language ───────────────────────────────
    language = phase1.get("language", "EN") or "EN"

    # ── Try Claude AI (3-call chain) ──────────────────────────────
    ai_result = generate_screenplay_ai(
        phase1, phase2,
        language=language,
        target_duration=target_duration
    )

    # ai_result is a dict like {"title": ..., "total_duration": ..., "scenes": [...]}
    ai_scenes_raw = None
    if ai_result and isinstance(ai_result, dict):
        raw_scenes = ai_result.get("scenes", [])
        if isinstance(raw_scenes, list) and len(raw_scenes) >= 5:
            ai_scenes_raw = raw_scenes
        else:
            print(f"[Phase3] AI returned {len(raw_scenes) if isinstance(raw_scenes, list) else 0} scenes (expected 5) — using template fallback")

    ai_was_used = ai_scenes_raw is not None
    scenes = []

    if ai_scenes_raw:
        # ── Map AI response fields → SceneBeat model fields ──────
        cumulative_time = 0.0
        for raw in ai_scenes_raw:
            try:
                scene_duration = float(raw.get("duration", 5))
                timing_start = cumulative_time
                timing_end = cumulative_time + scene_duration
                cumulative_time = timing_end

                scene_setting = raw.get("scene_setting", "")
                actor_delivery = raw.get("actor_delivery", "")

                beat = SceneBeat(
                    sceneNum=len(scenes) + 1,
                    name=raw.get("title", raw.get("name", f"SCENE {len(scenes)+1}")),
                    timingStart=timing_start,
                    timingEnd=timing_end,
                    duration=scene_duration,
                    dialogue=raw.get("dialogue", ""),
                    action=f"({actor_delivery})" if actor_delivery else "",
                    camera=Camera(
                        shot=raw.get("camera", {}).get("shot", "Medium") if isinstance(raw.get("camera"), dict) else "Medium",
                        angle=raw.get("camera", {}).get("angle", "Eye level") if isinstance(raw.get("camera"), dict) else "Eye level",
                        movement=raw.get("camera", {}).get("movement", "Static") if isinstance(raw.get("camera"), dict) else "Static",
                    ),
                    actor=Actor(
                        expression=raw.get("actor", {}).get("expression", "confident") if isinstance(raw.get("actor"), dict) else "confident",
                        energy=int(raw.get("actor", {}).get("energy", 7)) if isinstance(raw.get("actor"), dict) else 7,
                        pace=raw.get("actor", {}).get("pace", "medium") if isinstance(raw.get("actor"), dict) else "medium",
                    ),
                    visual=scene_setting,
                    audio=raw.get("audio", "Background music"),
                    editMarkers=generate_edit_markers(timing_start, timing_end),
                )
                scenes.append(beat)
            except Exception as e:
                print(f"[Phase3] Scene parse error: {e}")

        if len(scenes) < 5:
            print(f"[Phase3] Only {len(scenes)} scenes parsed — using template fallback")
            scenes = []
            ai_was_used = False

    if not scenes:
        # ── Fallback: template-based generation ─────────────
        print("[Phase3] Claude unavailable or returned invalid data — using template fallback")
        templates = get_scene_template(structure)
        templates = scale_templates_to_duration(templates, target_duration)
        selected_nuggets = [phase1.get("selected_nugget", {})] if phase1.get("selected_nugget") else nuggets
        scenes = [generate_scene_beat(tmpl, phase1, phase2, selected_nuggets, i) for i, tmpl in enumerate(templates)]
        ai_was_used = False

    metrics = calculate_metrics(scenes)
    golden_rules = validate_golden_rules(scenes)
    rules_applied = [g.rule for g in golden_rules if g.passed]

    scenes_json = [s.model_dump() for s in scenes]
    supabase.table("phase3_data").upsert({
        "brief_id": brief_id,
        "total_runtime_sec": metrics["total_runtime_sec"],
        "total_words": metrics["total_words"],
        "cut_count": metrics["cut_count"],
        "scenes": scenes_json,
        "golden_rules_applied": rules_applied,
    }, on_conflict="brief_id").execute()

    return {
        "generated": True,
        "ai_generated": ai_was_used,
        "scenes": scenes_json,
        "total_runtime_sec": metrics["total_runtime_sec"],
        "total_words": metrics["total_words"],
        "cut_count": metrics["cut_count"],
        "golden_rules_check": [g.model_dump() for g in golden_rules],
    }
