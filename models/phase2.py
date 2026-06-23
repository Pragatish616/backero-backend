from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


class FormatStructureCombo(BaseModel):
    format: str
    format_tier: str
    structure: str
    structure_num: int
    recommendation: str
    why: str
    data_citation: str = ""
    platform_boosted: bool = False


class ContentTypeConfig(BaseModel):
    label: str
    cta: str
    frequency: str
    combos: list[FormatStructureCombo] = []


class CombosResponse(BaseModel):
    content_type: str
    label: str
    cta: str
    frequency: str
    combos: list[FormatStructureCombo] = []


class Phase2CreateRequest(BaseModel):
    content_type: Optional[str] = None
    selected_format: Optional[str] = None
    selected_structure: Optional[str] = None
    format_tier: Optional[str] = None
    recommendation_level: Optional[str] = None
    platform_boost_applied: bool = False
    data_citations: Optional[list[dict]] = None
    cta_type: Optional[str] = None
    cta_text: Optional[str] = None


class RecommendRequest(BaseModel):
    content_type: str
    platform: str


class ContentTypeItem(BaseModel):
    key: str
    label: str
    cta: str
    frequency: str
