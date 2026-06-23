from __future__ import annotations
import re
import time
from collections import defaultdict, deque
from models.phase6 import GraphNode, GraphEdge, NodePosition

NODE_TYPES = [
    {"id": "reference.actor", "label": "Actor Ref", "category": "input", "tool": "midjourney-cref", "color": "#F59E0B", "inputs": [], "outputs": ["lookbook"]},
    {"id": "t2i.keyframe", "label": "Keyframe", "category": "generate", "tool": "midjourney", "color": "#8B5CF6", "inputs": ["actor_lock"], "outputs": ["keyframe"]},
    {"id": "i2v.scene", "label": "Image→Video", "category": "generate", "tool": "kling-2.0-master", "color": "#06D6A0", "inputs": ["first_frame"], "outputs": ["clip"]},
    {"id": "t2v.scene", "label": "Text→Video", "category": "generate", "tool": "kling-2.0-master", "color": "#0EA5E9", "inputs": ["prompt"], "outputs": ["clip"]},
    {"id": "tts.voiceover", "label": "Voiceover", "category": "audio", "tool": "elevenlabs", "color": "#EC4899", "inputs": ["script"], "outputs": ["audio"]},
    {"id": "audio.lipsync", "label": "Lip Sync", "category": "audio", "tool": "sync.so", "color": "#F97316", "inputs": ["video", "audio"], "outputs": ["synced_video"]},
    {"id": "audio.sfx", "label": "SFX", "category": "audio", "tool": "elevenlabs-sfx", "color": "#EF4444", "inputs": [], "outputs": ["audio"]},
    {"id": "audio.music", "label": "Music", "category": "audio", "tool": "epidemic-load", "color": "#D946EF", "inputs": [], "outputs": ["audio"]},
    {"id": "overlay.text", "label": "Text Overlay", "category": "composite", "tool": "compositor-capcut", "color": "#3B82F6", "inputs": [], "outputs": ["card"]},
    {"id": "transition.cut", "label": "Cut", "category": "composite", "tool": "compositor-capcut", "color": "#6366F1", "inputs": [], "outputs": ["transition"]},
    {"id": "compositor.scene", "label": "Scene Comp", "category": "composite", "tool": "compositor-capcut", "color": "#22C55E", "inputs": ["video_layer", "audio_layer", "overlay_layer", "sfx_layer"], "outputs": ["scene_comp"]},
    {"id": "compositor.master", "label": "Master Comp", "category": "composite", "tool": "compositor-capcut", "color": "#14B8A6", "inputs": ["scene_comps", "music", "transitions"], "outputs": ["master_comp"]},
    {"id": "render.output", "label": "Render", "category": "output", "tool": "compositor-capcut", "color": "#64748B", "inputs": ["master_comp"], "outputs": ["final_video"]},
]


def render_prompt_template(template: str, scene: dict, brief: dict) -> str:
    if not template:
        return ""
    replacements = {
        "{{scene.dialogue}}": scene.get("dialogue", ""),
        "{{scene.action}}": scene.get("action", ""),
        "{{scene.camera.shot}}": (scene.get("camera", {}) or {}).get("shot", ""),
        "{{scene.camera.angle}}": (scene.get("camera", {}) or {}).get("angle", ""),
        "{{scene.camera.movement}}": (scene.get("camera", {}) or {}).get("movement", ""),
        "{{scene.actor.expression}}": (scene.get("actor", {}) or {}).get("expression", ""),
        "{{scene.visual}}": scene.get("visual", ""),
        "{{scene.audio}}": scene.get("audio", ""),
        "{{brief.title}}": brief.get("title", ""),
        "{{brief.platform}}": brief.get("platform", ""),
    }
    result = template
    for k, v in replacements.items():
        result = result.replace(k, str(v))
    return result


def generate_node_graph(supabase, brief_id: str) -> dict:
    p3 = supabase.table("phase3_data").select("*").eq("brief_id", brief_id).execute()
    p3d = p3.data[0] if p3.data else {}
    scenes = p3d.get("scenes", [])

    p1 = supabase.table("phase1_data").select("*").eq("brief_id", brief_id).execute()
    p1d = p1.data[0] if p1.data else {}

    brief = supabase.table("briefs").select("*").eq("id", brief_id).execute()
    brief_data = brief.data[0] if brief.data else {}
    brief_ctx = {**brief_data, **p1d}

    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []
    scene_comp_ids = []

    x_base = 100
    for idx, scene in enumerate(scenes):
        sn = scene.get("sceneNum", idx + 1)
        x = x_base + idx * 300
        y_base = 50

        # Keyframe
        kf_id = f"s{sn}.keyframe"
        kf_template = "{{scene.camera.shot}} of {{scene.action}}, cinematic lighting, 9:16"
        nodes.append(GraphNode(
            id=kf_id, type="t2i.keyframe", scene_binding=sn,
            position=NodePosition(x=x, y=y_base),
            parameters={"aspect_ratio": "9:16", "stylize": 250},
            prompt_template=kf_template,
            rendered_prompt=render_prompt_template(kf_template, scene, brief_ctx),
        ))

        # I2V
        i2v_id = f"s{sn}.i2v"
        nodes.append(GraphNode(
            id=i2v_id, type="i2v.scene", scene_binding=sn,
            position=NodePosition(x=x, y=y_base + 100),
            parameters={"duration": scene.get("duration", 5), "cfg_scale": 0.5},
            prompt_template="{{scene.action}}", rendered_prompt=render_prompt_template("{{scene.action}}", scene, brief_ctx),
        ))
        edges.append(GraphEdge(id=f"e.{kf_id}-{i2v_id}", from_port=f"{kf_id}:keyframe", to_port=f"{i2v_id}:first_frame"))

        # TTS
        tts_id = f"s{sn}.tts"
        nodes.append(GraphNode(
            id=tts_id, type="tts.voiceover", scene_binding=sn,
            position=NodePosition(x=x, y=y_base + 200),
            parameters={"voice": "default", "speed": 1.0},
            prompt_template="{{scene.dialogue}}", rendered_prompt=render_prompt_template("{{scene.dialogue}}", scene, brief_ctx),
        ))

        # Overlay
        ov_id = f"s{sn}.overlay"
        nodes.append(GraphNode(
            id=ov_id, type="overlay.text", scene_binding=sn,
            position=NodePosition(x=x, y=y_base + 300),
            parameters={"font": "Montserrat Bold", "size": 48},
            prompt_template="{{scene.visual}}", rendered_prompt=render_prompt_template("{{scene.visual}}", scene, brief_ctx),
        ))

        # Scene compositor
        comp_id = f"s{sn}.comp"
        nodes.append(GraphNode(
            id=comp_id, type="compositor.scene", scene_binding=sn,
            position=NodePosition(x=x, y=y_base + 400),
            parameters={},
        ))
        scene_comp_ids.append(comp_id)

        edges.append(GraphEdge(id=f"e.{i2v_id}-{comp_id}", from_port=f"{i2v_id}:clip", to_port=f"{comp_id}:video_layer"))
        edges.append(GraphEdge(id=f"e.{tts_id}-{comp_id}", from_port=f"{tts_id}:audio", to_port=f"{comp_id}:audio_layer"))
        edges.append(GraphEdge(id=f"e.{ov_id}-{comp_id}", from_port=f"{ov_id}:card", to_port=f"{comp_id}:overlay_layer"))

    # Master compositor
    master_x = x_base + len(scenes) * 300
    master_id = "master.comp"
    nodes.append(GraphNode(
        id=master_id, type="compositor.master", scene_binding=None,
        position=NodePosition(x=master_x, y=250),
        parameters={},
    ))
    for comp_id in scene_comp_ids:
        edges.append(GraphEdge(id=f"e.{comp_id}-{master_id}", from_port=f"{comp_id}:scene_comp", to_port=f"{master_id}:scene_comps"))

    # Render output
    render_id = "render.output"
    nodes.append(GraphNode(
        id=render_id, type="render.output", scene_binding=None,
        position=NodePosition(x=master_x + 200, y=250),
        parameters={"resolution": "1080x1920", "fps": 30, "codec": "h264"},
    ))
    edges.append(GraphEdge(id=f"e.{master_id}-{render_id}", from_port=f"{master_id}:master_comp", to_port=f"{render_id}:master_comp"))

    # Save
    nodes_json = [n.model_dump() for n in nodes]
    edges_json = [e.model_dump() for e in edges]
    supabase.table("phase6_data").upsert({
        "brief_id": brief_id, "nodes": nodes_json, "edges": edges_json,
    }, on_conflict="brief_id").execute()

    return {
        "generated": True,
        "nodes": nodes_json,
        "edges": edges_json,
        "node_count": len(nodes),
        "edge_count": len(edges),
    }


def topological_sort(nodes: list[dict], edges: list[dict]) -> list[str]:
    node_ids = {n["id"] for n in nodes}
    in_degree: dict[str, int] = {nid: 0 for nid in node_ids}
    adj: dict[str, list[str]] = defaultdict(list)

    for e in edges:
        from_id = e.get("from_port", "").split(":")[0]
        to_id = e.get("to_port", "").split(":")[0]
        if from_id in node_ids and to_id in node_ids:
            adj[from_id].append(to_id)
            in_degree[to_id] = in_degree.get(to_id, 0) + 1

    queue = deque(nid for nid, deg in in_degree.items() if deg == 0)
    order = []
    while queue:
        nid = queue.popleft()
        order.append(nid)
        for neighbor in adj[nid]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    return order


def validate_edge(nodes: list[dict], from_ref: str, to_ref: str) -> tuple[bool, str]:
    type_map = {nt["id"]: nt for nt in NODE_TYPES}
    node_map = {n["id"]: n for n in nodes}

    from_parts = from_ref.split(":")
    to_parts = to_ref.split(":")
    if len(from_parts) != 2 or len(to_parts) != 2:
        return False, "Edge refs must be 'nodeId:portName'"

    from_node = node_map.get(from_parts[0])
    to_node = node_map.get(to_parts[0])
    if not from_node:
        return False, f"Source node '{from_parts[0]}' not found"
    if not to_node:
        return False, f"Target node '{to_parts[0]}' not found"

    from_type = type_map.get(from_node.get("type", ""))
    to_type = type_map.get(to_node.get("type", ""))
    if from_type and from_parts[1] not in from_type.get("outputs", []):
        return False, f"Output port '{from_parts[1]}' not found on node type '{from_node.get('type')}'"
    if to_type and to_parts[1] not in to_type.get("inputs", []):
        return False, f"Input port '{to_parts[1]}' not found on node type '{to_node.get('type')}'"

    return True, ""
