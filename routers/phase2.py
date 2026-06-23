from fastapi import APIRouter, HTTPException, Query
from db.supabase_client import get_supabase
from models.phase2 import Phase2CreateRequest, RecommendRequest
from services import phase2_service

router = APIRouter(prefix="/api/phase2", tags=["phase2"])


@router.get("/content-types")
def get_content_types():
    return {"content_types": phase2_service.get_content_types()}


@router.get("/combos/{content_type}")
def get_combos(content_type: str, platform: str = Query("")):
    result = phase2_service.get_combos(content_type, platform)
    if not result:
        raise HTTPException(404, f"Content type '{content_type}' not found")
    return result


@router.get("/{brief_id}")
def get_phase2(brief_id: str):
    sb = get_supabase()
    result = sb.table("phase2_data").select("*").eq("brief_id", brief_id).execute()
    p1 = sb.table("phase1_data").select("platform").eq("brief_id", brief_id).execute()
    platform = p1.data[0]["platform"] if p1.data else None
    data = result.data[0] if result.data else None
    if not data:
        raise HTTPException(404, "Phase 2 data not found")
    return {"success": True, "data": data, "platform": platform}


@router.post("/{brief_id}")
def save_phase2(brief_id: str, req: Phase2CreateRequest):
    sb = get_supabase()
    try:
        data = req.model_dump(exclude_none=True)
        saved = phase2_service.upsert_phase2(sb, brief_id, data)
        return {"success": True, "data": saved}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/{brief_id}/advance")
def advance_phase2(brief_id: str):
    sb = get_supabase()
    try:
        sb.table("briefs").update({"current_phase": 3, "status": "In Progress"}).eq("id", brief_id).execute()
        return {"success": True, "next_phase": 3}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/{brief_id}/recommend")
def recommend(brief_id: str, req: RecommendRequest):
    result = phase2_service.get_recommendation(req.content_type, req.platform)
    if not result:
        raise HTTPException(404, "No recommendation available")
    return {"success": True, **result}
