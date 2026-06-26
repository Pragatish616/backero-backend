"""
Backero Phase 1 Router - Fixed
Key fixes: prefix /api/phase1, responses wrapped in {success, data}, advance accepts body
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from db.supabase_client import get_supabase
from models.phase1 import (
    Phase1CreateRequest,
    HookValidationRequest,
    HookValidationResponse,
    NuggetExtractionRequest,
    NuggetSelectionRequest,
)
from services import phase1_service

router = APIRouter(prefix="/api/phase1", tags=["phase1"])


# ── CRUD ───────────────────────────────────────────────────────────────────

@router.get("/{brief_id}")
def get_phase1(brief_id: str):
    sb = get_supabase()
    result = sb.table("phase1_data").select("*").eq("brief_id", brief_id).execute()
    if not result.data:
        raise HTTPException(404, "Phase 1 data not found")
    return {"success": True, "data": result.data[0]}


@router.post("/{brief_id}")
def save_phase1(brief_id: str, req: Phase1CreateRequest):
    sb = get_supabase()
    try:
        data = req.model_dump(exclude_none=True)
        saved = phase1_service.upsert_phase1(sb, brief_id, data)
        sb.table("briefs").update({"status": "In Progress"}).eq("id", brief_id).execute()
        return {"success": True, "data": saved}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.patch("/{brief_id}")
def patch_phase1(brief_id: str, req: Phase1CreateRequest):
    sb = get_supabase()
    try:
        data = req.model_dump(exclude_none=True)
        saved = phase1_service.upsert_phase1(sb, brief_id, data)
        return {"success": True, "data": saved}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/{brief_id}/advance")
def advance_phase1(brief_id: str, req: Phase1CreateRequest | None = None):
    sb = get_supabase()
    try:
        if req:
            data = req.model_dump(exclude_none=True)
            phase1_service.upsert_phase1(sb, brief_id, data)
        sb.table("briefs").update({"current_phase": 2, "status": "In Progress"}).eq("id", brief_id).execute()
        return {"success": True, "next_phase": 2}
    except Exception as e:
        raise HTTPException(500, str(e))


# ── Hook Validation ────────────────────────────────────────────────────────

@router.post("/{brief_id}/validate-hook")
def validate_hook(brief_id: str, req: HookValidationRequest):
    sb = get_supabase()
    topic = ""
    niche = ""
    language = "EN"
    try:
        p1 = sb.table("phase1_data").select("topic, niche, language").eq("brief_id", brief_id).execute()
        if p1.data:
            topic = p1.data[0].get("topic", "")
            niche = p1.data[0].get("niche", "")
            language = p1.data[0].get("language", "EN")
    except Exception:
        pass
    result = phase1_service.validate_hook(
        hook_text=req.hook_text, topic=topic, niche=niche, language=language
    )
    return result


# ── Nugget Extraction & Selection ──────────────────────────────────────────

@router.post("/{brief_id}/extract-nuggets")
def extract_nuggets(brief_id: str, req: NuggetExtractionRequest):
    sb = get_supabase()
    niche = ""
    language = "EN"
    try:
        p1 = sb.table("phase1_data").select("niche, language").eq("brief_id", brief_id).execute()
        if p1.data:
            niche = p1.data[0].get("niche", "")
            language = p1.data[0].get("language", "EN")
    except Exception:
        pass
    nuggets = phase1_service.extract_nuggets(
        topic=req.topic, research_text=req.research_text or "", niche=niche, language=language
    )
    # Save nuggets to phase1_data
    try:
        sb.table("phase1_data").update({"knowledge_nuggets": nuggets}).eq("brief_id", brief_id).execute()
    except Exception:
        pass
    return {"success": True, "nuggets": nuggets}


@router.post("/{brief_id}/select-nugget")
def select_nugget(brief_id: str, req: NuggetSelectionRequest):
    sb = get_supabase()
    try:
        result = phase1_service.save_selected_nugget(sb, brief_id, req.selected_nugget)
        return {"success": True, "selected_nugget": req.selected_nugget}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/{brief_id}/selected-nugget")
def get_selected_nugget(brief_id: str):
    sb = get_supabase()
    result = sb.table("phase1_data").select("selected_nugget").eq("brief_id", brief_id).execute()
    if not result.data:
        raise HTTPException(404, "Phase 1 data not found")
    return {"selected_nugget": result.data[0].get("selected_nugget")}


# ── AI Helpers ─────────────────────────────────────────────────────────────

@router.post("/{brief_id}/fluff-examples")
def get_fluff_examples(brief_id: str, body: dict = {}):
    niche = body.get("niche", "")
    topic = body.get("topic", "")
    if not niche:
        try:
            sb = get_supabase()
            p1 = sb.table("phase1_data").select("niche, topic").eq("brief_id", brief_id).execute()
            if p1.data:
                niche = p1.data[0].get("niche", "General")
                topic = topic or p1.data[0].get("topic", "")
        except Exception:
            niche = "General"
    from services.ai_service import generate_fluff_examples_ai
    examples = generate_fluff_examples_ai(topic=topic, niche=niche)
    return {"success": True, "examples": examples}


@router.post("/{brief_id}/suggest-topics")
def suggest_topics_endpoint(brief_id: str, body: dict = {}):
    niche = body.get("niche", "")
    sub_niche = body.get("sub_niche", "")
    if not niche:
        try:
            sb = get_supabase()
            p1 = sb.table("phase1_data").select("niche, sub_niche").eq("brief_id", brief_id).execute()
            if p1.data:
                niche = p1.data[0].get("niche", "General")
                sub_niche = sub_niche or p1.data[0].get("sub_niche", "")
        except Exception:
            niche = "General"
    from services.ai_service import suggest_topics_ai
    topics = suggest_topics_ai(niche=niche, sub_niche=sub_niche)
    return {"success": True, "topics": topics}


# ── Sub-Niches ─────────────────────────────────────────────────────────────

@router.get("/sub-niches/{niche}")
def get_sub_niches(niche: str):
    subs = phase1_service.get_sub_niches(niche)
    if not subs:
        raise HTTPException(404, f"Niche '{niche}' not found")
    return {"niche": niche, "sub_niches": subs}
