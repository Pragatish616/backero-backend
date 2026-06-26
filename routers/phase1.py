"""
Backero Phase 1 Router - Complete Implementation
All API endpoints for Phase 1 operations
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from db.supabase_client import get_supabase
from services import phase1_service
from models.phase1 import (
    Phase1CreateRequest,
    HookValidationRequest,
    HookValidationResponse,
    NuggetExtractionRequest,
    NuggetSelectionRequest,
)
router = APIRouter(prefix="/phase1", tags=["Phase 1"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class FluffExamplesRequest(BaseModel):
    topic: str
    niche: Optional[str] = ""


class TopicSuggestRequest(BaseModel):
    niche: str
    sub_niche: Optional[str] = ""


# ============================================================================
# CRUD ENDPOINTS
# ============================================================================

@router.get("/{brief_id}")
async def get_phase1(brief_id: str):
    """Retrieve phase 1 data for a brief"""
    sb = get_supabase()
    result = sb.table("phase1_data").select("*").eq("brief_id", brief_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Phase 1 data not found")
    return result.data[0]


@router.post("/{brief_id}")
async def save_phase1(brief_id: str, req: Phase1CreateRequest):
    """Save phase 1 data and update brief status"""
    sb = get_supabase()
    try:
        data = req.model_dump(exclude_none=True)
        saved = phase1_service.upsert_phase1(sb, brief_id, data)

        # Update brief status
        sb.table("briefs").update({"status": "phase1_complete"}).eq("id", brief_id).execute()

        return saved
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{brief_id}")
async def update_phase1(brief_id: str, req: Phase1CreateRequest):
    """Partial update of phase 1 data"""
    sb = get_supabase()
    try:
        data = req.model_dump(exclude_none=True)
        saved = phase1_service.upsert_phase1(sb, brief_id, data)
        return saved
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{brief_id}/advance")
async def advance_to_phase2(brief_id: str):
    """Advance brief to phase 2"""
    sb = get_supabase()
    try:
        sb.table("briefs").update({"status": "phase2"}).eq("id", brief_id).execute()
        return {"status": "advanced", "next_phase": 2}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# HOOK VALIDATION
# ============================================================================

@router.post("/{brief_id}/validate-hook", response_model=HookValidationResponse)
async def validate_hook(brief_id: str, req: HookValidationRequest):
    """
    Validate a hook for viral potential.
    Returns score, issues, suggestions, and AI-powered rewrites.
    """
    sb = get_supabase()

    # Get existing phase1 data for context
    p1 = sb.table("phase1_data").select("topic, niche, language").eq("brief_id", brief_id).execute()
    topic = ""
    niche = ""
    language = "EN"
    if p1.data:
        topic = p1.data[0].get("topic", "")
        niche = p1.data[0].get("niche", "")
        language = p1.data[0].get("language", "EN")

    result = phase1_service.validate_hook(
        hook_text=req.hook_text,
        topic=topic,
        niche=niche,
        language=language
    )

    return HookValidationResponse(**result)


# ============================================================================
# NUGGET EXTRACTION & SELECTION
# ============================================================================

@router.post("/{brief_id}/extract-nuggets")
async def extract_nuggets(brief_id: str, req: NuggetExtractionRequest):
    """
    Extract 3 knowledge nuggets for the user to choose from.
    User must select ONE nugget before proceeding to screenplay generation.
    """
    sb = get_supabase()

    # Get niche from saved phase1 data if not provided
    p1 = sb.table("phase1_data").select("niche, language").eq("brief_id", brief_id).execute()
    niche = ""
    language = "EN"
    if p1.data:
        niche = p1.data[0].get("niche", "")
        language = p1.data[0].get("language", "EN")

    nuggets = phase1_service.extract_nuggets(
        topic=req.topic,
        research_text=req.research_text or "",
        niche=niche,
        language=language
    )

    # Save nuggets to phase1_data
    sb.table("phase1_data").update({
        "knowledge_nuggets": nuggets
    }).eq("brief_id", brief_id).execute()

    return {"nuggets": nuggets, "message": "Select ONE nugget to proceed"}


@router.post("/{brief_id}/select-nugget")
async def select_nugget(brief_id: str, req: NuggetSelectionRequest):
    """
    Save the user's selected nugget.
    This MUST be called before generating screenplay.
    The selected nugget becomes the core message for the video.
    """
    sb = get_supabase()

    try:
        result = phase1_service.save_selected_nugget(
            sb, brief_id, req.selected_nugget
        )

        if not result:
            raise HTTPException(status_code=404, detail="Brief not found")

        return {
            "status": "ok",
            "message": "Nugget selected successfully",
            "selected_nugget": req.selected_nugget
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{brief_id}/selected-nugget")
async def get_selected_nugget(brief_id: str):
    """Get the currently selected nugget for a brief"""
    sb = get_supabase()

    result = sb.table("phase1_data").select("selected_nugget").eq("brief_id", brief_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Phase 1 data not found")

    selected = result.data[0].get("selected_nugget")
    if not selected:
        return {"selected_nugget": None, "message": "No nugget selected yet"}

    return {"selected_nugget": selected}


# ============================================================================
# AI HELPERS
# ============================================================================

@router.post("/{brief_id}/fluff-examples")
async def get_fluff_examples(brief_id: str, req: FluffExamplesRequest):
    """Generate niche+topic specific fluff vs specific pairs in the user's language."""
    sb = get_supabase()
    language = "EN"
    saved_topic = req.topic
    saved_niche = req.niche or ""
    try:
        p1 = sb.table("phase1_data").select("language, topic, niche").eq("brief_id", brief_id).execute()
        if p1.data:
            language = p1.data[0].get("language", "EN") or "EN"
            if not saved_topic:
                saved_topic = p1.data[0].get("topic", "") or ""
            if not saved_niche:
                saved_niche = p1.data[0].get("niche", "") or ""
    except Exception:
        pass

    from services.ai_service import generate_fluff_examples_ai
    examples = generate_fluff_examples_ai(
        topic=saved_topic,
        niche=saved_niche,
        language=language,
    )
    # Always return {examples: [...]} so frontend can read res.examples
    return {"success": True, "examples": examples}


@router.post("/{brief_id}/suggest-topics")
async def suggest_topics(brief_id: str, req: TopicSuggestRequest):
    """Suggest viral video topics based on niche"""
    sb = get_supabase()

    # Get language preference
    p1 = sb.table("phase1_data").select("language").eq("brief_id", brief_id).execute()
    language = "EN"
    if p1.data:
        language = p1.data[0].get("language", "EN")

    topics = phase1_service.suggest_topics(
        niche=req.niche,
        sub_niche=req.sub_niche or "",
        language=language
    )

    return {"suggested_topics": topics}


# ============================================================================
# SUB-NICHES
# ============================================================================

@router.get("/sub-niches/{niche}")
async def get_sub_niches(niche: str):
    """Get sub-niches for a given niche"""
    sub_niches = phase1_service.get_sub_niches(niche)
    return {"niche": niche, "sub_niches": sub_niches}
