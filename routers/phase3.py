from fastapi import APIRouter, HTTPException
from db.supabase_client import get_supabase
from services import phase3_service

router = APIRouter(prefix="/api/phase3", tags=["phase3"])


@router.get("/{brief_id}")
def get_phase3(brief_id: str):
    sb = get_supabase()
    result = sb.table("phase3_data").select("*").eq("brief_id", brief_id).execute()
    if not result.data:
        return {"generated": False}
    data = result.data[0]
    return {"generated": True, **data}


@router.post("/{brief_id}/generate")
def generate_screenplay(brief_id: str):
    sb = get_supabase()
    try:
        return phase3_service.generate_screenplay(sb, brief_id)
    except Exception as e:
        raise HTTPException(500, str(e))


@router.patch("/{brief_id}/scenes/{scene_num}")
def update_scene(brief_id: str, scene_num: int, body: dict):
    sb = get_supabase()
    try:
        result = sb.table("phase3_data").select("scenes").eq("brief_id", brief_id).execute()
        if not result.data:
            raise HTTPException(404, "Phase 3 data not found")
        scenes = result.data[0].get("scenes", [])
        for s in scenes:
            if s.get("sceneNum") == scene_num:
                s.update(body)
                break
        else:
            raise HTTPException(404, f"Scene {scene_num} not found")
        sb.table("phase3_data").update({"scenes": scenes}).eq("brief_id", brief_id).execute()
        return {"success": True, "scene": next(s for s in scenes if s.get("sceneNum") == scene_num)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/{brief_id}/regenerate-scene/{scene_num}")
def regenerate_scene(brief_id: str, scene_num: int, body: dict = {}):
    sb = get_supabase()
    try:
        from services.ai_service import regenerate_scene_ai
        # Load existing scene + phase data
        p3 = sb.table("phase3_data").select("scenes").eq("brief_id", brief_id).execute()
        p1 = sb.table("phase1_data").select("*").eq("brief_id", brief_id).execute()
        p2 = sb.table("phase2_data").select("*").eq("brief_id", brief_id).execute()

        scenes = p3.data[0].get("scenes", []) if p3.data else []
        phase1 = p1.data[0] if p1.data else {}
        phase2 = p2.data[0] if p2.data else {}
        direction = body.get("direction", "")

        existing_scene = next((s for s in scenes if s.get("sceneNum") == scene_num), None)
        if not existing_scene:
            raise HTTPException(404, f"Scene {scene_num} not found")

        # Try targeted AI regeneration first
        new_scene = regenerate_scene_ai(existing_scene, phase1, phase2, direction)

        if new_scene:
            # Update the specific scene in DB
            for i, s in enumerate(scenes):
                if s.get("sceneNum") == scene_num:
                    scenes[i] = new_scene
                    break
            sb.table("phase3_data").update({"scenes": scenes}).eq("brief_id", brief_id).execute()
            return {"success": True, "scene": new_scene, "ai_generated": True}
        else:
            # Fallback: regenerate full screenplay
            result = phase3_service.generate_screenplay(sb, brief_id)
            scenes = result.get("scenes", [])
            scene = next((s for s in scenes if s.get("sceneNum") == scene_num), None)
            if not scene:
                raise HTTPException(404, f"Scene {scene_num} not found")
            return {"success": True, "scene": scene, "ai_generated": False}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/{brief_id}/advance")
def advance_phase3(brief_id: str):
    sb = get_supabase()
    try:
        sb.table("briefs").update({"current_phase": 4, "status": "In Progress"}).eq("id", brief_id).execute()
        return {"success": True, "next_phase": 4}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/{brief_id}/golden-rules-check")
def golden_rules_check(brief_id: str):
    sb = get_supabase()
    result = sb.table("phase3_data").select("scenes").eq("brief_id", brief_id).execute()
    if not result.data:
        raise HTTPException(404, "Phase 3 data not found")
    scenes = result.data[0].get("scenes", [])
    from models.phase3 import SceneBeat
    scene_objs = [SceneBeat(**s) for s in scenes]
    checks = phase3_service.validate_golden_rules(scene_objs)
    return {"checks": [c.model_dump() for c in checks]}
