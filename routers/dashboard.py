from fastapi import APIRouter, HTTPException, Query
from db.supabase_client import get_supabase
from models.dashboard import CreateBriefRequest, UpdateBriefRequest
from services import dashboard_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/metrics")
def get_metrics(date_range: int = Query(30)):
    sb = get_supabase()
    return dashboard_service.get_metrics(sb, date_range)


@router.get("/briefs")
def list_briefs(
    date_range: int = Query(30),
    page: int = Query(1),
    limit: int = Query(10),
    status: str | None = Query(None),
    phase: int | None = Query(None),
):
    sb = get_supabase()
    return dashboard_service.get_briefs_list(sb, date_range, page, limit, status, phase)


@router.get("/pipeline")
def get_pipeline():
    sb = get_supabase()
    return dashboard_service.get_pipeline(sb)


@router.post("/briefs")
def create_brief(req: CreateBriefRequest):
    sb = get_supabase()
    try:
        data = {
            "title": req.title,
            "creator_name": req.creator_name,
            "creator_initials": req.creator_initials,
            "status": "Draft",
            "current_phase": 1,
        }
        if req.on_camera_actor:
            data["on_camera_actor"] = req.on_camera_actor
        if req.brand_company:
            data["brand_company"] = req.brand_company
        result = sb.table("briefs").insert(data).execute()
        if result.data:
            return {"success": True, "brief_id": result.data[0]["id"], "brief": result.data[0]}
        raise HTTPException(500, "Failed to create brief")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


@router.patch("/briefs/{brief_id}")
def update_brief(brief_id: str, req: UpdateBriefRequest):
    sb = get_supabase()
    data = req.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(400, "No fields to update")
    try:
        result = sb.table("briefs").update(data).eq("id", brief_id).execute()
        if result.data:
            return {"success": True, "brief": result.data[0]}
        raise HTTPException(404, "Brief not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


@router.delete("/briefs/{brief_id}")
def delete_brief(brief_id: str, hard: bool = Query(False)):
    sb = get_supabase()
    try:
        if hard:
            sb.table("briefs").delete().eq("id", brief_id).execute()
        else:
            sb.table("briefs").update({"status": "Deleted"}).eq("id", brief_id).execute()
        return {"success": True}
    except Exception as e:
        raise HTTPException(500, str(e))
