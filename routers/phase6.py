from fastapi import APIRouter, HTTPException, Query
import traceback
from datetime import datetime, timezone
from db.supabase_client import get_supabase
from models.phase6 import AddNodeRequest, UpdateNodeRequest, AddEdgeRequest, GraphNode, GraphEdge, NodePosition
from services import phase6_service
import time

router = APIRouter(prefix="/api/phase6", tags=["phase6"])


@router.get("/node-types")
def get_node_types():
    return {"node_types": phase6_service.NODE_TYPES}


@router.get("/{brief_id}")
def get_phase6(brief_id: str):
    sb = get_supabase()
    result = sb.table("phase6_data").select("*").eq("brief_id", brief_id).execute()
    if not result.data:
        return {"generated": False}
    data = result.data[0]
    return {"generated": True, **data}


@router.post("/{brief_id}/generate")
def generate_graph(brief_id: str):
    sb = get_supabase()
    try:
        return phase6_service.generate_node_graph(sb, brief_id)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))


@router.patch("/{brief_id}/nodes/{node_id}")
def update_node(brief_id: str, node_id: str, req: UpdateNodeRequest):
    sb = get_supabase()
    try:
        result = sb.table("phase6_data").select("nodes").eq("brief_id", brief_id).execute()
        if not result.data:
            raise HTTPException(404, "Phase 6 data not found")
        nodes = result.data[0].get("nodes", [])
        found = False
        for n in nodes:
            if n["id"] == node_id:
                if req.position is not None:
                    n["position"] = req.position.model_dump()
                if req.parameters is not None:
                    n["parameters"] = req.parameters
                if req.prompt_template is not None:
                    n["prompt_template"] = req.prompt_template
                found = True
                break
        if not found:
            raise HTTPException(404, f"Node '{node_id}' not found")
        sb.table("phase6_data").update({"nodes": nodes}).eq("brief_id", brief_id).execute()
        return {"success": True, "node": next(n for n in nodes if n["id"] == node_id)}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))


@router.post("/{brief_id}/nodes")
def add_node(brief_id: str, req: AddNodeRequest):
    sb = get_supabase()
    try:
        result = sb.table("phase6_data").select("nodes").eq("brief_id", brief_id).execute()
        if not result.data:
            raise HTTPException(404, "Phase 6 data not found")
        nodes = result.data[0].get("nodes", [])
        new_id = f"{req.type}.{int(time.time())}"
        node = GraphNode(
            id=new_id, type=req.type, scene_binding=req.scene_binding,
            position=req.position, parameters=req.parameters,
            prompt_template=req.prompt_template, core=False,
        )
        nodes.append(node.model_dump())
        sb.table("phase6_data").update({"nodes": nodes}).eq("brief_id", brief_id).execute()
        return {"success": True, "node": node.model_dump()}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))


@router.delete("/{brief_id}/nodes/{node_id}")
def delete_node(brief_id: str, node_id: str, force: bool = Query(False)):
    sb = get_supabase()
    try:
        result = sb.table("phase6_data").select("*").eq("brief_id", brief_id).execute()
        if not result.data:
            raise HTTPException(404, "Phase 6 data not found")
        data = result.data[0]
        nodes = data.get("nodes", [])
        node = next((n for n in nodes if n["id"] == node_id), None)
        if not node:
            raise HTTPException(404, f"Node '{node_id}' not found")
        if node.get("core") and not force:
            raise HTTPException(400, "Cannot delete core node without ?force=true")

        edges = data.get("edges", [])
        removed_edges = [e for e in edges if node_id in e.get("from_port", "") or node_id in e.get("to_port", "")]
        remaining_edges = [e for e in edges if e not in removed_edges]
        remaining_nodes = [n for n in nodes if n["id"] != node_id]

        sb.table("phase6_data").update({"nodes": remaining_nodes, "edges": remaining_edges}).eq("brief_id", brief_id).execute()
        return {"deleted": True, "edges_removed": len(removed_edges)}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))


@router.post("/{brief_id}/edges")
def add_edge(brief_id: str, req: AddEdgeRequest):
    sb = get_supabase()
    try:
        result = sb.table("phase6_data").select("*").eq("brief_id", brief_id).execute()
        if not result.data:
            raise HTTPException(404, "Phase 6 data not found")
        data = result.data[0]
        nodes = data.get("nodes", [])
        valid, err = phase6_service.validate_edge(nodes, req.from_port, req.to_port)
        if not valid:
            raise HTTPException(400, err)
        edges = data.get("edges", [])
        edge_id = f"e.{req.from_port.split(':')[0]}-{req.to_port.split(':')[0]}"
        edge = GraphEdge(id=edge_id, from_port=req.from_port, to_port=req.to_port)
        edges.append(edge.model_dump())
        sb.table("phase6_data").update({"edges": edges}).eq("brief_id", brief_id).execute()
        return {"success": True, "edge": edge.model_dump()}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))


@router.delete("/{brief_id}/edges/{edge_id}")
def delete_edge(brief_id: str, edge_id: str):
    sb = get_supabase()
    try:
        result = sb.table("phase6_data").select("edges").eq("brief_id", brief_id).execute()
        if not result.data:
            raise HTTPException(404, "Phase 6 data not found")
        edges = result.data[0].get("edges", [])
        remaining = [e for e in edges if e.get("id") != edge_id]
        if len(remaining) == len(edges):
            raise HTTPException(404, f"Edge '{edge_id}' not found")
        sb.table("phase6_data").update({"edges": remaining}).eq("brief_id", brief_id).execute()
        return {"deleted": True}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))


@router.post("/{brief_id}/render-prompts")
def render_prompts(brief_id: str):
    sb = get_supabase()
    try:
        p6 = sb.table("phase6_data").select("nodes").eq("brief_id", brief_id).execute()
        if not p6.data:
            raise HTTPException(404, "Phase 6 data not found")
        nodes = p6.data[0].get("nodes", [])

        p3 = sb.table("phase3_data").select("scenes").eq("brief_id", brief_id).execute()
        scenes = p3.data[0].get("scenes", []) if p3.data else []
        scene_map = {s.get("sceneNum"): s for s in scenes}

        p1 = sb.table("phase1_data").select("*").eq("brief_id", brief_id).execute()
        brief_data = sb.table("briefs").select("*").eq("id", brief_id).execute()
        brief_ctx = {**(brief_data.data[0] if brief_data.data else {}), **(p1.data[0] if p1.data else {})}

        for n in nodes:
            if n.get("prompt_template") and n.get("scene_binding"):
                scene = scene_map.get(n["scene_binding"], {})
                n["rendered_prompt"] = phase6_service.render_prompt_template(n["prompt_template"], scene, brief_ctx)

        sb.table("phase6_data").update({"nodes": nodes}).eq("brief_id", brief_id).execute()
        return {"success": True, "nodes": nodes}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))


@router.get("/{brief_id}/export")
def export_pipeline(brief_id: str):
    sb = get_supabase()
    result = sb.table("phase6_data").select("*").eq("brief_id", brief_id).execute()
    if not result.data:
        raise HTTPException(404, "Phase 6 data not found")
    data = result.data[0]
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    brief = sb.table("briefs").select("title, created_at").eq("id", brief_id).execute()
    brief_data = brief.data[0] if brief.data else {}

    order = phase6_service.topological_sort(nodes, edges)

    return {
        "pipeline_version": "1.0",
        "brief_id": brief_id,
        "brief_title": brief_data.get("title", ""),
        "created_at": brief_data.get("created_at", ""),
        "nodes": nodes,
        "edges": edges,
        "execution_order": order,
        "estimated_duration_min": max(15, len(nodes) * 3),
    }
