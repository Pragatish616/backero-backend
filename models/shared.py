from __future__ import annotations
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel
from datetime import datetime


class BriefStatus(str, Enum):
    DRAFT = "Draft"
    IN_PROGRESS = "In Progress"
    PENDING_APPROVAL = "Pending Approval"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    DELETED = "Deleted"


class BriefBase(BaseModel):
    title: str
    current_phase: int = 1
    status: str = "Draft"
    creator_name: Optional[str] = None
    creator_initials: Optional[str] = None
    on_camera_actor: Optional[str] = None
    brand_company: Optional[str] = None


class BriefCreate(BaseModel):
    title: str
    creator_name: str
    creator_initials: str
    on_camera_actor: Optional[str] = None
    brand_company: Optional[str] = None


class BriefUpdate(BaseModel):
    title: Optional[str] = None
    current_phase: Optional[int] = None
    status: Optional[str] = None
    creator_name: Optional[str] = None
    creator_initials: Optional[str] = None
    on_camera_actor: Optional[str] = None
    brand_company: Optional[str] = None


class BriefResponse(BriefBase):
    id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class APIResponse(BaseModel):
    success: bool = True
    data: Any = None
    error: Optional[str] = None
    detail: Optional[str] = None
