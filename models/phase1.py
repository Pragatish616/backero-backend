"""
Backero Phase 1 Models - Complete Implementation
Pydantic models for Phase 1 data structures
"""

from pydantic import BaseModel
from typing import Optional, List


class KnowledgeNugget(BaseModel):
    """Represents a single knowledge nugget option"""
    type: str  # "Shocking Fact", "Practical Hack", or "Story Hook"
    text: str
    source: Optional[str] = None
    rationale: Optional[str] = None
    color: Optional[str] = None  # Hex color for UI display


class Phase1Data(BaseModel):
    """Complete Phase 1 data structure"""
    id: Optional[str] = None
    brief_id: Optional[str] = None

    # Platform & Niche
    platform: Optional[str] = None
    niche: Optional[str] = None
    sub_niche: Optional[str] = None

    # Topic & Content
    topic: Optional[str] = None
    viral_reference: Optional[str] = None
    viral_url: Optional[str] = None

    # Copy Elements
    copy_element: Optional[str] = None
    copy_description: Optional[str] = None

    # Hook
    hook: Optional[str] = None
    hook_text: Optional[str] = None
    hook_score: Optional[int] = None

    # Knowledge Nuggets - ALL 3 OPTIONS
    knowledge_nuggets: Optional[List[KnowledgeNugget]] = None

    # SELECTED NUGGET - THE ONE USER CHOSE
    selected_nugget: Optional[dict] = None

    # Actor Info
    actor_name: Optional[str] = None
    actor_photo_url: Optional[str] = None
    actor_characteristics: Optional[str] = None

    # Production Metadata
    location: Optional[str] = None
    props: Optional[str] = None
    wardrobe: Optional[str] = None

    # Settings
    language: Optional[str] = "EN"
    ai_generated: Optional[bool] = False

    # Timestamps
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class Phase1CreateRequest(BaseModel):
    """Request model for creating/updating Phase 1 data"""
    platform: Optional[str] = None
    niche: Optional[str] = None
    sub_niche: Optional[str] = None

    topic: Optional[str] = None
    viral_reference: Optional[str] = None
    viral_url: Optional[str] = None

    copy_element: Optional[str] = None
    copy_description: Optional[str] = None

    hook: Optional[str] = None
    hook_text: Optional[str] = None
    hook_score: Optional[int] = None

    knowledge_nuggets: Optional[List[KnowledgeNugget]] = None
    selected_nugget: Optional[dict] = None

    actor_name: Optional[str] = None
    actor_photo_url: Optional[str] = None
    actor_characteristics: Optional[str] = None

    location: Optional[str] = None
    props: Optional[str] = None
    wardrobe: Optional[str] = None

    language: Optional[str] = "EN"
    ai_generated: Optional[bool] = False


class HookValidationRequest(BaseModel):
    """Request model for hook validation"""
    hook_text: str


class HookValidationResponse(BaseModel):
    """Response model for hook validation"""
    valid: bool
    score: int
    issues: List[str] = []
    suggestions: List[str] = []
    ai_rewrites: Optional[List[str]] = None


class NuggetExtractionRequest(BaseModel):
    """Request model for extracting nuggets"""
    topic: str
    research_text: Optional[str] = ""


class NuggetSelectionRequest(BaseModel):
    """Request model for selecting a nugget from the 3 options"""
    selected_nugget: dict
