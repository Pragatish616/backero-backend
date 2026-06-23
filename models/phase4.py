from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


class CheckItem(BaseModel):
    id: str
    name: str
    category: str
    severity: str  # Critical | Major | Minor | Info
    result: str = "PASS"  # PASS | FAIL | N/A
    evidence: str = ""
    overridden: bool = False
    scenesAffected: list[int] = []
    suggestedFix: str = ""


class RoleApproval(BaseModel):
    name: str
    status: str = "Pending Approval"
    feedback: str = ""
    timestamp: Optional[str] = None


class RevisionItem(BaseModel):
    rank: int
    check_id: str
    severity: str
    scenes_affected: list[int] = []
    action: str = ""
    estimated_effort: str = ""


class ChecksSummary(BaseModel):
    passed: int = 0
    fail: int = 0
    na: int = 0
    overridden: int = 0


class ChecksRunResponse(BaseModel):
    checks: list[CheckItem] = []
    quality_score: int = 100
    overall_verdict: str = "REVISE"
    revision_queue: list[RevisionItem] = []
    summary: ChecksSummary = ChecksSummary()


class ApprovalSubmitRequest(BaseModel):
    status: str  # Approved | Rejected
    feedback: str = ""
