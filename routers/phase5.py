from fastapi import APIRouter, HTTPException
import traceback
from fastapi.responses import FileResponse
from datetime import datetime, timezone
from db.supabase_client import get_supabase
from services import phase5_service

router = APIRouter(prefix="/api/phase5", tags=["phase5"])


@router.get("/{brief_id}")
def get_phase5(brief_id: str):
    sb = get_supabase()
    try:
        pack = phase5_service.assemble_production_pack(sb, brief_id)
        return pack.model_dump()
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))


@router.get("/{brief_id}/tab/{tab_name}")
def get_tab_view(brief_id: str, tab_name: str):
    sb = get_supabase()
    valid_tabs = ["all", "actor", "camera", "edit", "script", "golden-rules"]
    if tab_name not in valid_tabs:
        raise HTTPException(400, f"Invalid tab. Must be one of: {valid_tabs}")

    if tab_name == "golden-rules":
        pack = phase5_service.assemble_production_pack(sb, brief_id)
        return {"tab": tab_name, "golden_rules": [r.model_dump() for r in pack.golden_rules]}

    p3 = sb.table("phase3_data").select("scenes").eq("brief_id", brief_id).execute()
    scenes = p3.data[0].get("scenes", []) if p3.data else []
    filtered = phase5_service.get_tab_view(scenes, tab_name)
    return {"tab": tab_name, "scenes": filtered}


@router.post("/{brief_id}/export/docx")
def export_docx(brief_id: str):
    sb = get_supabase()
    try:
        pack = phase5_service.assemble_production_pack(sb, brief_id)
        path = phase5_service.generate_docx(pack.meta, pack.scenes, pack.golden_rules, brief_id)

        # Log export
        now = datetime.now(timezone.utc).isoformat()
        existing = sb.table("phase5_data").select("export_history").eq("brief_id", brief_id).execute()
        history = existing.data[0].get("export_history", []) if existing.data else []
        history.append({"exported_at": now, "docx_url": path, "exported_by": pack.meta.actor})
        sb.table("phase5_data").upsert({
            "brief_id": brief_id,
            "meta": pack.meta.model_dump(),
            "golden_rules": [r.model_dump() for r in pack.golden_rules],
            "export_history": history,
            "docx_url": path,
        }, on_conflict="brief_id").execute()

        return FileResponse(
            path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=f"{brief_id}_production_pack.docx",
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))


@router.get("/{brief_id}/export/history")
def export_history(brief_id: str):
    sb = get_supabase()
    result = sb.table("phase5_data").select("export_history").eq("brief_id", brief_id).execute()
    history = result.data[0].get("export_history", []) if result.data else []
    return {"history": history}


@router.post("/{brief_id}/advance")
def advance_phase5(brief_id: str):
    sb = get_supabase()
    sb.table("briefs").update({"current_phase": 6, "status": "Approved"}).eq("id", brief_id).execute()
    return {"success": True, "next_phase": 6}
