from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


class NodeType(BaseModel):
    id: str
    label: str
    category: str
    tool: str
    color: str
    inputs: list[str] = []
    outputs: list[str] = []


class NodePosition(BaseModel):
    x: float = 0
    y: float = 0


class GraphNode(BaseModel):
    id: str
    type: str
    scene_binding: Optional[int] = None
    position: NodePosition = NodePosition()
    parameters: dict = {}
    prompt_template: str = ""
    rendered_prompt: str = ""
    core: bool = True


class GraphEdge(BaseModel):
    id: str
    from_port: str  # "nodeId:portName"
    to_port: str


class Phase6Data(BaseModel):
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []


class GenerateResponse(BaseModel):
    generated: bool = True
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []
    node_count: int = 0
    edge_count: int = 0


class AddNodeRequest(BaseModel):
    type: str
    scene_binding: Optional[int] = None
    position: NodePosition = NodePosition()
    parameters: dict = {}
    prompt_template: str = ""


class UpdateNodeRequest(BaseModel):
    position: Optional[NodePosition] = None
    parameters: Optional[dict] = None
    prompt_template: Optional[str] = None


class AddEdgeRequest(BaseModel):
    from_port: str
    to_port: str


class ExportResponse(BaseModel):
    pipeline_version: str = "1.0"
    brief_id: str
    brief_title: str = ""
    created_at: str = ""
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []
    execution_order: list[str] = []
    estimated_duration_min: int = 45
