"""
Backero Phase 1 Models
Uses the field names the deployed frontend sends.
"""

from pydantic import BaseModel
from typing import Optional, List


class KnowledgeNugget(BaseModel):
    type: str
    text: str
    source: Optional[str] = None       # legacy field
    rationale: Optional[str] = None     # legacy field
    source_hint: Optional[str] = None   # new: where this fact came from
    why_viral: Optional[str] = None     # new: why this hooks viewers
    brain_system: Optional[str] = None  # new: amygdala / tpj_social / prefrontal
    emotional_trigger: Optional[str] = None  # new: Fear + Surprise etc.
    pattern_interrupt_score: Optional[int] = None  # new: 1-10
    color: Optional[str] = None


class Phase1CreateRequest(BaseModel):
    platform: Optional[str] = None
    niche: Optional[str] = None
    sub_niche: Optional[str] = None
    topic: Optional[str] = None
    viral_reference_url: Optional[str] = None
    copy_elements: Optional[list[str]] = None
    time_to_value: Optional[str] = None
    content_style: Optional[str] = None
    hook_text: Optional[str] = None
    knowledge_nuggets: Optional[List[KnowledgeNugget]] = None
    selected_nugget: Optional[dict] = None
    selected_nugget_index: Optional[int] = None
    nugget_rationale: Optional[str] = None
    blacklist_words: Optional[list[str]] = None
    ai_generated: Optional[bool] = None
    batch_id: Optional[str] = None
    production_date: Optional[str] = None
    on_camera_actor: Optional[str] = None
    actor_brief: Optional[str] = None
    brand_company: Optional[str] = None
    reference_description: Optional[str] = None
    language: Optional[str] = None
    content_creator: Optional[str] = None
    number_of_actors: Optional[int] = None
    aspect_ratio: Optional[str] = None
    estimated_length: Optional[str] = None
    sample_hook: Optional[str] = None


class HookValidationRequest(BaseModel):
    hook_text: str


class HookValidationResponse(BaseModel):
    valid: bool
    score: int
    issues: List[str] = []
    suggestions: List[str] = []
    ai_rewrites: Optional[list] = None


class NuggetExtractionRequest(BaseModel):
    topic: str
    research_text: Optional[str] = ""
    language: Optional[str] = None


class NuggetSelectionRequest(BaseModel):
    selected_nugget: dict
