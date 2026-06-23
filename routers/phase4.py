from fastapi import APIRouter, HTTPException
import traceback
from datetime import datetime, timezone
from db.supabase_client import get_supabase
from models.phase4 import CheckItem, RoleApproval, ApprovalSubmitRequest
from services import phase4_service

router = APIRouter(prefix="/api/phase4", tags=["phase4"])

DEFAULT_APPROVALS = [
    {"name": "Content Lead", "status": "Pending Approval", "feedback": "", "timestamp": None},
    {"name": "Actor", "status": "Pending Approval", "feedback": "", "timestamp": None},
    {"name": "Editor", "status": "Pending Approval", "feedback": "", "timestamp": None},
]


@router.get("/{brief_id}")
def get_phase4(brief_id: str):
    sb = get_supabase()
    result = sb.table("phase4_data").select("*").eq("brief_id", brief_id).execute()
    if not result.data:
        return {
            "checks": [], "role_approvals": DEFAULT_APPROVALS,
            "revision_queue": [], "overall_verdict": None, "quality_score": None,
        }
    return result.data[0]


@router.post("/{brief_id}/run-checks")
def run_checks(brief_id: str):
    sb = get_supabase()
    try:
        p3 = sb.table("phase3_data").select("*").eq("brief_id", brief_id).execute()
        if not p3.data:
            raise HTTPException(404, "Phase 3 data not found — generate screenplay first")
        p3d = p3.data[0]
        scenes = p3d.get("scenes", [])
        runtime = float(p3d.get("total_runtime_sec", 0))
        words = int(p3d.get("total_words", 0))
        cuts = int(p3d.get("cut_count", 0))

        checks = phase4_service.run_all_checks(scenes, runtime, words, cuts)
        score = phase4_service.calculate_score(checks)

        # Get existing approvals or default
        existing = sb.table("phase4_data").select("role_approvals").eq("brief_id", brief_id).execute()
        approvals_raw = existing.data[0].get("role_approvals", DEFAULT_APPROVALS) if existing.data else DEFAULT_APPROVALS
        approvals = [RoleApproval(**a) for a in approvals_raw]

        verdict = phase4_service.determine_verdict(checks, approvals)
        revision_queue = phase4_service.build_revision_queue(checks)
        summary = phase4_service.get_summary(checks)

        # Save
        checks_json = [c.model_dump() for c in checks]
        revisions_json = [r.model_dump() for r in revision_queue]
        sb.table("phase4_data").upsert({
            "brief_id": brief_id,
            "checks": checks_json,
            "role_approvals": approvals_raw,
            "revision_queue": revisions_json,
            "overall_verdict": verdict,
            "quality_score": score,
        }, on_conflict="brief_id").execute()

        if verdict == "REJECT":
            sb.table("briefs").update({"status": "Rejected"}).eq("id", brief_id).execute()
        elif verdict == "REVISE":
            sb.table("briefs").update({"status": "Pending Approval"}).eq("id", brief_id).execute()

        return {
            "checks": checks_json,
            "quality_score": score,
            "overall_verdict": verdict,
            "revision_queue": revisions_json,
            "summary": summary.model_dump(),
        }
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))


@router.patch("/{brief_id}/checks/{check_id}/override")
def override_check(brief_id: str, check_id: str):
    sb = get_supabase()
    try:
        result = sb.table("phase4_data").select("*").eq("brief_id", brief_id).execute()
        if not result.data:
            raise HTTPException(404, "Phase 4 data not found")
        data = result.data[0]
        checks = data.get("checks", [])
        for c in checks:
            if c["id"] == check_id:
                c["overridden"] = not c["overridden"]
                break
        else:
            raise HTTPException(404, f"Check '{check_id}' not found")

        check_objs = [CheckItem(**c) for c in checks]
        score = phase4_service.calculate_score(check_objs)
        approvals = [RoleApproval(**a) for a in data.get("role_approvals", DEFAULT_APPROVALS)]
        verdict = phase4_service.determine_verdict(check_objs, approvals)
        revision_queue = [r.model_dump() for r in phase4_service.build_revision_queue(check_objs)]

        sb.table("phase4_data").update({
            "checks": checks, "quality_score": score,
            "overall_verdict": verdict, "revision_queue": revision_queue,
        }).eq("brief_id", brief_id).execute()

        return {"success": True, "quality_score": score, "overall_verdict": verdict}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))


@router.post("/{brief_id}/approvals/{role}/submit")
def submit_approval(brief_id: str, role: str, req: ApprovalSubmitRequest):
    sb = get_supabase()
    try:
        result = sb.table("phase4_data").select("*").eq("brief_id", brief_id).execute()
        if not result.data:
            raise HTTPException(404, "Phase 4 data not found — run checks first")
        data = result.data[0]
        approvals = data.get("role_approvals", DEFAULT_APPROVALS)

        found = False
        for a in approvals:
            if a["name"] == role:
                a["status"] = req.status
                a["feedback"] = req.feedback
                a["timestamp"] = datetime.now(timezone.utc).isoformat()
                found = True
                break
        if not found:
            raise HTTPException(404, f"Role '{role}' not found")

        checks = [CheckItem(**c) for c in data.get("checks", [])]
        approval_objs = [RoleApproval(**a) for a in approvals]
        verdict = phase4_service.determine_verdict(checks, approval_objs)

        sb.table("phase4_data").update({
            "role_approvals": approvals, "overall_verdict": verdict,
        }).eq("brief_id", brief_id).execute()

        if verdict == "SHIP":
            sb.table("briefs").update({"status": "Approved"}).eq("id", brief_id).execute()

        return {"success": True, "overall_verdict": verdict, "role_approvals": approvals}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))


@router.get("/{brief_id}/approvals")
def get_approvals(brief_id: str):
    sb = get_supabase()
    result = sb.table("phase4_data").select("role_approvals").eq("brief_id", brief_id).execute()
    if not result.data:
        return {"role_approvals": DEFAULT_APPROVALS}
    return {"role_approvals": result.data[0].get("role_approvals", DEFAULT_APPROVALS)}


@router.post("/{brief_id}/advance")
def advance_phase4(brief_id: str):
    sb = get_supabase()
    result = sb.table("phase4_data").select("overall_verdict").eq("brief_id", brief_id).execute()
    if not result.data or result.data[0].get("overall_verdict") != "SHIP":
        raise HTTPException(400, "Cannot advance — verdict must be SHIP")
    sb.table("briefs").update({"current_phase": 5}).eq("id", brief_id).execute()
    return {"success": True, "next_phase": 5}


@router.post("/{brief_id}/revise")
def revise(brief_id: str):
    sb = get_supabase()
    sb.table("briefs").update({"current_phase": 3, "status": "In Progress"}).eq("id", brief_id).execute()
    return {"success": True, "next_phase": 3}
