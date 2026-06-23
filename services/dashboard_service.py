from __future__ import annotations
from datetime import datetime, timezone, timedelta
from models.dashboard import (
    MetricsResponse, InProgressBreakdown, PendingApprovals, ActivityItem,
    BriefListResponse, BriefListItem, PipelineResponse, PipelinePhase, PipelineBrief,
)


def format_time_ago(dt_str: str | None) -> str:
    if not dt_str:
        return "just now"
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except Exception:
        return "recently"
    now = datetime.now(timezone.utc)
    diff = now - dt
    seconds = diff.total_seconds()
    if seconds < 60:
        return "just now"
    if seconds < 3600:
        return f"{int(seconds // 60)}m ago"
    if seconds < 86400:
        return f"{int(seconds // 3600)}h ago"
    return f"{int(seconds // 86400)}d ago"


def get_metrics(supabase, date_range_days: int) -> MetricsResponse:
    try:
        query = supabase.table("briefs").select("*").neq("status", "Deleted")
        if date_range_days > 0:
            cutoff = (datetime.now(timezone.utc) - timedelta(days=date_range_days)).isoformat()
            query = query.gte("updated_at", cutoff)
        result = query.execute()
        briefs = result.data or []

        total = len(briefs)
        in_progress_briefs = [b for b in briefs if b.get("status") == "In Progress"]
        by_phase: dict[str, int] = {}
        for b in in_progress_briefs:
            p = str(b.get("current_phase", 1))
            by_phase[p] = by_phase.get(p, 0) + 1

        # Pending approvals from phase4_data
        pending_total = 0
        by_role: dict[str, int] = {}
        pending_briefs = [b for b in briefs if b.get("status") == "Pending Approval"]
        for b in pending_briefs:
            try:
                p4 = supabase.table("phase4_data").select("role_approvals").eq("brief_id", b["id"]).execute()
                if p4.data:
                    approvals = p4.data[0].get("role_approvals") or []
                    for a in approvals:
                        if a.get("status") == "Pending Approval":
                            pending_total += 1
                            role = a.get("name", "Unknown")
                            by_role[role] = by_role.get(role, 0) + 1
            except Exception:
                pass

        recent = sorted(briefs, key=lambda b: b.get("updated_at", ""), reverse=True)[:5]
        activity = [
            ActivityItem(
                id=b["id"], name=b.get("title", "Untitled"),
                phase=b.get("current_phase", 1),
                updated_at=format_time_ago(b.get("updated_at"))
            ) for b in recent
        ]

        return MetricsResponse(
            total_videos=total,
            in_progress=InProgressBreakdown(total=len(in_progress_briefs), by_phase=by_phase),
            pending_approvals=PendingApprovals(total=pending_total, by_role=by_role),
            recent_activity=activity,
        )
    except Exception as e:
        return MetricsResponse()


def get_briefs_list(supabase, date_range: int, page: int, limit: int, status: str | None, phase: int | None) -> BriefListResponse:
    try:
        query = supabase.table("briefs").select("*", count="exact").neq("status", "Deleted")
        if date_range > 0:
            cutoff = (datetime.now(timezone.utc) - timedelta(days=date_range)).isoformat()
            query = query.gte("updated_at", cutoff)
        if status:
            query = query.eq("status", status)
        if phase:
            query = query.eq("current_phase", phase)
        query = query.order("updated_at", desc=True)
        offset = (page - 1) * limit
        query = query.range(offset, offset + limit - 1)
        result = query.execute()
        total = result.count or len(result.data or [])
        items = [BriefListItem(**b) for b in (result.data or [])]
        return BriefListResponse(briefs=items, total=total, page=page, limit=limit)
    except Exception:
        return BriefListResponse()


def get_pipeline(supabase) -> PipelineResponse:
    try:
        result = supabase.table("briefs").select("*").neq("status", "Deleted").execute()
        briefs = result.data or []
        phase_map: dict[int, list] = {i: [] for i in range(1, 7)}
        for b in briefs:
            p = b.get("current_phase", 1)
            if p in phase_map:
                phase_map[p].append(b)
        phases = []
        for i in range(1, 7):
            bs = phase_map[i]
            preview = [PipelineBrief(id=b["id"], name=b.get("title", ""), creator_initials=b.get("creator_initials")) for b in bs[:5]]
            phases.append(PipelinePhase(phase=i, count=len(bs), briefs=preview))
        return PipelineResponse(phases=phases)
    except Exception:
        return PipelineResponse(phases=[PipelinePhase(phase=i) for i in range(1, 7)])
