from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel


class InProgressBreakdown(BaseModel):
    total: int = 0
    by_phase: dict[str, int] = {}


class PendingApprovals(BaseModel):
    total: int = 0
    by_role: dict[str, int] = {}


class ActivityItem(BaseModel):
    id: str
    name: str
    phase: int
    updated_at: str


class MetricsResponse(BaseModel):
    total_videos: int = 0
    in_progress: InProgressBreakdown = InProgressBreakdown()
    pending_approvals: PendingApprovals = PendingApprovals()
    recent_activity: list[ActivityItem] = []


class BriefListItem(BaseModel):
    id: str
    title: str
    current_phase: int
    status: str
    creator_name: Optional[str] = None
    creator_initials: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class BriefListResponse(BaseModel):
    briefs: list[BriefListItem] = []
    total: int = 0
    page: int = 1
    limit: int = 10


class PipelineBrief(BaseModel):
    id: str
    name: str
    creator_initials: Optional[str] = None


class PipelinePhase(BaseModel):
    phase: int
    count: int = 0
    briefs: list[PipelineBrief] = []


class PipelineResponse(BaseModel):
    phases: list[PipelinePhase] = []


class CreateBriefRequest(BaseModel):
    title: str
    creator_name: str
    creator_initials: str
    on_camera_actor: Optional[str] = None
    brand_company: Optional[str] = None


class UpdateBriefRequest(BaseModel):
    title: Optional[str] = None
    current_phase: Optional[int] = None
    status: Optional[str] = None
    creator_name: Optional[str] = None
    creator_initials: Optional[str] = None
    on_camera_actor: Optional[str] = None
    brand_company: Optional[str] = None
