from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


class ProductionMeta(BaseModel):
    title: str = ""
    actor: str = ""
    company: str = ""
    platform: str = ""
    format: str = ""
    contentType: str = ""
    structure: str = ""
    runtime: str = ""
    scenes: int = 0
    cuts: int = 0
    words: int = 0
    verdict: str = ""
    score: int = 0
    aspectRatio: str = "9:16"
    language: str = "English"


class GoldenRule(BaseModel):
    num: int
    name: str
    description: str = ""
    category: str = ""
    passed: bool = False
    evidence: str = ""


class Phase5Response(BaseModel):
    meta: ProductionMeta = ProductionMeta()
    scenes: list[dict] = []
    golden_rules: list[GoldenRule] = []
    tabs_available: list[str] = ["all", "actor", "camera", "edit", "script", "golden-rules"]


class ExportHistoryItem(BaseModel):
    exported_at: str
    docx_url: str = ""
    exported_by: str = ""


class ExportResponse(BaseModel):
    success: bool = True
    docx_url: str = ""
    message: str = ""
