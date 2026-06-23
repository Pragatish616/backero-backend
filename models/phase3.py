from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


class Camera(BaseModel):
    shot: str = ""
    angle: str = ""
    movement: str = ""


class Actor(BaseModel):
    expression: str = ""
    energy: int = 5
    pace: str = "medium"


class EditMarker(BaseModel):
    time: str = ""
    event: str = ""


class SceneBeat(BaseModel):
    sceneNum: int
    name: str
    timingStart: float = 0
    timingEnd: float = 0
    duration: float = 0
    dialogue: str = ""
    action: str = ""
    camera: Camera = Camera()
    actor: Actor = Actor()
    visual: str = ""
    audio: str = ""
    editMarkers: list[EditMarker] = []


class Phase3Data(BaseModel):
    id: Optional[str] = None
    brief_id: Optional[str] = None
    total_runtime_sec: float = 0
    total_words: int = 0
    cut_count: int = 0
    scenes: list[SceneBeat] = []
    golden_rules_applied: list[str] = []


class GoldenRulesCheck(BaseModel):
    rule: str
    passed: bool
    evidence: str = ""


class GenerateResponse(BaseModel):
    generated: bool = True
    scenes: list[SceneBeat] = []
    total_runtime_sec: float = 0
    total_words: int = 0
    cut_count: int = 0
    golden_rules_check: list[GoldenRulesCheck] = []
