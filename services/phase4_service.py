from __future__ import annotations
from datetime import datetime, timezone
from models.phase4 import CheckItem, RoleApproval, RevisionItem, ChecksSummary

SEVERITY_DEDUCTIONS = {"Critical": 25, "Major": 10, "Minor": 3, "Info": 0}
EFFORT_MAP = {"Critical": "15 min", "Major": "10 min", "Minor": "5 min", "Info": "2 min"}
CTA_VERBS = {"save", "follow", "comment", "share", "link", "dm", "watch"}
URGENCY_WORDS = {"now", "today", "before", "limited", "only", "last", "hurry", "quick", "fast", "don't miss"}


def check_golden_rules(scenes: list[dict]) -> list[CheckItem]:
    checks = []
    if not scenes:
        return checks

    s1 = scenes[0]
    markers = s1.get("editMarkers", [])

    # GR001: Tri-Modal Convergence
    has_early_visual = any(_time_val(m.get("time", "")) <= 0.5 for m in markers)
    has_audio = bool(s1.get("audio"))
    has_text = bool(s1.get("visual"))
    checks.append(CheckItem(
        id="GR001", name="Tri-Modal Convergence in 0-1.5s", category="Golden Rule",
        severity="Critical", result="PASS" if (has_early_visual and has_audio and has_text) else "FAIL",
        evidence=f"Visual≤0.5s: {has_early_visual}, Audio: {has_audio}, Text: {has_text}",
        scenesAffected=[1], suggestedFix="Add visual motion by 0.5s, audio at 0.0s, and hero text by 0.3s"
    ))

    # GR002: No Talking Head >2s
    fail_scenes = []
    for s in scenes:
        dur = s.get("duration", s.get("timingEnd", 0) - s.get("timingStart", 0))
        needed = max(1, dur / 2)
        if len(s.get("editMarkers", [])) < needed:
            fail_scenes.append(s.get("sceneNum", 0))
    checks.append(CheckItem(
        id="GR002", name="No Talking Head >2s", category="Golden Rule",
        severity="Critical", result="FAIL" if fail_scenes else "PASS",
        evidence=f"Scenes with insufficient markers: {fail_scenes or 'none'}",
        scenesAffected=fail_scenes, suggestedFix="Add edit markers every ≤2s in flagged scenes"
    ))

    # GR003: Hook Parseable Muted
    checks.append(CheckItem(
        id="GR003", name="Hook Parseable Muted", category="Golden Rule",
        severity="Major", result="PASS" if s1.get("visual") else "FAIL",
        evidence=f"Scene 1 visual overlay: {'present' if s1.get('visual') else 'missing'}",
        scenesAffected=[1], suggestedFix="Add text overlay to Scene 1 so hook works on mute"
    ))

    # GR004: Show Don't Tell
    no_action = [s.get("sceneNum", 0) for s in scenes if not s.get("action")]
    checks.append(CheckItem(
        id="GR004", name="Show Don't Tell", category="Golden Rule",
        severity="Major", result="FAIL" if no_action else "PASS",
        evidence=f"Scenes without action: {no_action or 'none'}",
        scenesAffected=no_action, suggestedFix="Add action parenthetical to every dialogue line"
    ))

    # GR005: Silent Moments
    last = scenes[-1]
    has_freeze = any("freeze" in m.get("event", "").lower() or "silence" in m.get("event", "").lower()
                      for m in last.get("editMarkers", []))
    checks.append(CheckItem(
        id="GR005", name="Silent Moments", category="Golden Rule",
        severity="Minor", result="PASS" if has_freeze else "FAIL",
        evidence=f"CTA freeze marker: {'found' if has_freeze else 'missing'}",
        scenesAffected=[last.get("sceneNum", len(scenes))],
        suggestedFix="Add 1.0s silence/freeze marker before CTA"
    ))

    return checks


def check_quality_gates(scenes: list[dict], total_runtime: float, total_words: int, cut_count: int) -> list[CheckItem]:
    checks = []
    if not scenes:
        return checks

    s1 = scenes[0]
    s1_words = len(s1.get("dialogue", "").split())
    checks.append(CheckItem(
        id="QG001", name="Hook Word Count", category="Quality Gate",
        severity="Critical", result="PASS" if s1_words <= 15 else "FAIL",
        evidence=f"Scene 1 dialogue: {s1_words} words",
        scenesAffected=[1], suggestedFix="Trim Scene 1 dialogue to ≤15 words"
    ))

    last_name = scenes[-1].get("name", "")
    checks.append(CheckItem(
        id="QG002", name="CTA Present", category="Quality Gate",
        severity="Critical", result="PASS" if "CTA" in last_name.upper() else "FAIL",
        evidence=f"Last scene name: '{last_name}'",
        scenesAffected=[len(scenes)], suggestedFix="Rename last scene to include 'CTA'"
    ))

    checks.append(CheckItem(
        id="QG003", name="Total Runtime", category="Quality Gate",
        severity="Major", result="PASS" if 15 <= total_runtime <= 60 else "FAIL",
        evidence=f"Runtime: {total_runtime}s (target: 15-60s)",
        suggestedFix="Adjust scene timings to hit 15-60s total"
    ))

    needed_cuts = total_runtime / 2
    checks.append(CheckItem(
        id="QG004", name="Cut Count", category="Quality Gate",
        severity="Major", result="PASS" if cut_count >= needed_cuts else "FAIL",
        evidence=f"Cuts: {cut_count}, needed: ≥{needed_cuts:.0f}",
        suggestedFix="Add more edit markers to increase cut frequency"
    ))

    scene_count = len(scenes)
    checks.append(CheckItem(
        id="QG005", name="Scene Count", category="Quality Gate",
        severity="Minor", result="PASS" if 4 <= scene_count <= 7 else "FAIL",
        evidence=f"Scenes: {scene_count} (target: 4-7)",
        suggestedFix="Adjust to 4-7 scenes"
    ))

    return checks


def check_neuroscience(scenes: list[dict]) -> list[CheckItem]:
    checks = []
    if not scenes:
        return checks

    half = len(scenes) // 2 + 1
    first_half = scenes[:half]
    has_peak = any((s.get("actor", {}).get("energy", 0) if isinstance(s.get("actor"), dict) else 0) >= 8
                   for s in first_half)
    checks.append(CheckItem(
        id="NS001", name="Dopamine Peak Placement", category="Neuroscience",
        severity="Major", result="PASS" if has_peak else "FAIL",
        evidence=f"High-energy scene (≥8) in first half: {'found' if has_peak else 'missing'}",
        suggestedFix="Increase actor energy to ≥8 in one of the first scenes"
    ))

    pattern_words = {"b-cam", "insert", "cut"}
    early_scenes = scenes[:min(3, len(scenes))]
    has_pattern = any(
        any(any(pw in m.get("event", "").lower() for pw in pattern_words)
            for m in s.get("editMarkers", []))
        for s in early_scenes
    )
    checks.append(CheckItem(
        id="NS002", name="Pattern Interrupt", category="Neuroscience",
        severity="Major", result="PASS" if has_pattern else "FAIL",
        evidence=f"B-cam/insert/cut in scenes 1-3: {'found' if has_pattern else 'missing'}",
        suggestedFix="Add a B-cam insert or cut marker in scenes 1-3"
    ))

    return checks


def check_cta(scenes: list[dict]) -> list[CheckItem]:
    checks = []
    if not scenes:
        return checks
    last = scenes[-1]
    dialogue = last.get("dialogue", "").lower()

    has_verb = any(v in dialogue for v in CTA_VERBS)
    checks.append(CheckItem(
        id="CT001", name="CTA Has Action Verb", category="CTA",
        severity="Critical", result="PASS" if has_verb else "FAIL",
        evidence=f"CTA dialogue: '{dialogue[:60]}'",
        scenesAffected=[len(scenes)],
        suggestedFix="Include one of: save, follow, comment, share, link, dm, watch"
    ))

    has_urgency = any(w in dialogue for w in URGENCY_WORDS)
    checks.append(CheckItem(
        id="CT002", name="CTA Urgency", category="CTA",
        severity="Minor", result="PASS" if has_urgency else "FAIL",
        evidence=f"Urgency word in CTA: {'found' if has_urgency else 'missing'}",
        scenesAffected=[len(scenes)],
        suggestedFix="Add urgency: 'before it's too late', 'right now', 'today'"
    ))

    return checks


def run_all_checks(scenes: list[dict], total_runtime: float, total_words: int, cut_count: int) -> list[CheckItem]:
    all_checks = []
    all_checks.extend(check_golden_rules(scenes))
    all_checks.extend(check_quality_gates(scenes, total_runtime, total_words, cut_count))
    all_checks.extend(check_neuroscience(scenes))
    all_checks.extend(check_cta(scenes))
    return all_checks


def calculate_score(checks: list[CheckItem]) -> int:
    score = 100
    for c in checks:
        if c.result == "FAIL":
            ded = SEVERITY_DEDUCTIONS.get(c.severity, 0)
            if c.overridden:
                ded = ded // 2
            score -= ded
    return max(0, min(100, score))


def determine_verdict(checks: list[CheckItem], role_approvals: list[RoleApproval]) -> str:
    critical_fail = any(c.result == "FAIL" and c.severity == "Critical" and not c.overridden for c in checks)
    if critical_fail:
        return "REJECT"
    major_fail = any(c.result == "FAIL" and c.severity == "Major" and not c.overridden for c in checks)
    any_rejected = any(a.status == "Rejected" for a in role_approvals)
    if major_fail or any_rejected:
        return "REVISE"
    return "SHIP"


def build_revision_queue(checks: list[CheckItem]) -> list[RevisionItem]:
    failed = [c for c in checks if c.result == "FAIL" and not c.overridden]
    order = {"Critical": 0, "Major": 1, "Minor": 2, "Info": 3}
    failed.sort(key=lambda c: order.get(c.severity, 9))
    return [
        RevisionItem(
            rank=i + 1, check_id=c.id, severity=c.severity,
            scenes_affected=c.scenesAffected,
            action=c.suggestedFix, estimated_effort=EFFORT_MAP.get(c.severity, "5 min"),
        )
        for i, c in enumerate(failed)
    ]


def get_summary(checks: list[CheckItem]) -> ChecksSummary:
    return ChecksSummary(
        passed=sum(1 for c in checks if c.result == "PASS"),
        fail=sum(1 for c in checks if c.result == "FAIL"),
        na=sum(1 for c in checks if c.result == "N/A"),
        overridden=sum(1 for c in checks if c.overridden),
    )


def _time_val(t: str) -> float:
    try:
        return float(t.replace("s", ""))
    except Exception:
        return 999
