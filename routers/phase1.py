from fastapi import APIRouter, HTTPException
from db.supabase_client import get_supabase
from models.phase1 import Phase1CreateRequest, HookValidationRequest, NuggetExtractionRequest
from services import phase1_service

router = APIRouter(prefix="/api/phase1", tags=["phase1"])


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
        data = req.model_dump()
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


@router.post("/{brief_id}/validate-hook")
def validate_hook(brief_id: str, req: HookValidationRequest):
    result = phase1_service.validate_hook(req.hook_text)
    return result


@router.post("/{brief_id}/extract-nuggets")
def extract_nuggets(brief_id: str, req: NuggetExtractionRequest):
    sb = get_supabase()
    # Fetch niche from saved phase1 data for better AI context
    niche = ""
    try:
        p1 = sb.table("phase1_data").select("niche").eq("brief_id", brief_id).execute()
        if p1.data:
            niche = p1.data[0].get("niche", "")
    except Exception:
        pass
    nuggets = phase1_service.extract_nuggets(req.topic, req.research_text, niche=niche)
    return {"success": True, "nuggets": nuggets}


@router.get("/sub-niches/{niche}")
def get_sub_niches(niche: str):
    subs = phase1_service.get_sub_niches(niche)
    if not subs:
        raise HTTPException(404, f"Niche '{niche}' not found")
    return {"niche": niche, "sub_niches": subs}
