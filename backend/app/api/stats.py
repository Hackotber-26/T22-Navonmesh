import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case

from backend.app.core.database import get_db
from backend.app.models.incident import Incident

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/stats", tags=["stats"])

FLAGGED_LEVELS = ["medium", "high", "critical"]


@router.get("/summary", status_code=status.HTTP_200_OK)
async def get_stats_summary(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Get high-level summary of total scans and flagged incidents.
    Low-risk scans are tracked separately so 'scams caught' is never inflated.
    """
    # Group by risk_level
    stmt = select(Incident.risk_level, func.count(Incident.id)).group_by(Incident.risk_level)
    result = await db.execute(stmt)
    rows = result.all()

    by_risk: Dict[str, int] = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0
    }
    total_scans = 0

    for level, count in rows:
        total_scans += count
        if level in by_risk:
            by_risk[level] = count

    total_flagged = by_risk["critical"] + by_risk["high"] + by_risk["medium"]

    return {
        "total_scans": total_scans,
        "total_flagged": total_flagged,
        "total_safe": by_risk["low"],
        "flagged_percentage": round((total_flagged / total_scans * 100), 1) if total_scans > 0 else 0.0,
        "by_risk_level": by_risk
    }


@router.get("/categories", status_code=status.HTTP_200_OK)
async def get_stats_categories(db: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    """Return counts of confirmed threats per category (medium risk or higher only)."""
    stmt = (
        select(Incident.category, func.count(Incident.id))
        .where(Incident.risk_level.in_(FLAGGED_LEVELS))
        .group_by(Incident.category)
        .order_by(func.count(Incident.id).desc())
    )
    result = await db.execute(stmt)
    rows = result.all()

    return [{"category": cat, "count": count} for cat, count in rows]


@router.get("/timeline", status_code=status.HTTP_200_OK)
async def get_stats_timeline(
    days: int = Query(default=7, ge=1, le=30, description="Number of days for trend timeline"),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Return daily timeline of threats caught vs safe scans over the past N days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    stmt = select(
        Incident.created_at,
        Incident.risk_level
    ).where(Incident.created_at >= cutoff)

    result = await db.execute(stmt)
    rows = result.all()

    # Aggregate by YYYY-MM-DD
    daily_map: Dict[str, Dict[str, int]] = {}
    for i in range(days):
        day_date = (datetime.now(timezone.utc) - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
        daily_map[day_date] = {"flagged": 0, "safe": 0, "total": 0}

    for created_at, risk_level in rows:
        if created_at:
            day_str = created_at.strftime("%Y-%m-%d")
            if day_str in daily_map:
                daily_map[day_str]["total"] += 1
                if risk_level in FLAGGED_LEVELS:
                    daily_map[day_str]["flagged"] += 1
                else:
                    daily_map[day_str]["safe"] += 1

    timeline_data = [
        {"date": date_str, "flagged": data["flagged"], "safe": data["safe"], "total": data["total"]}
        for date_str, data in daily_map.items()
    ]

    return timeline_data


@router.get("/by-language", status_code=status.HTTP_200_OK)
async def get_stats_by_language(db: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    """Return distribution of scans across supported languages."""
    stmt = (
        select(Incident.language, func.count(Incident.id))
        .group_by(Incident.language)
        .order_by(func.count(Incident.id).desc())
    )
    result = await db.execute(stmt)
    rows = result.all()

    return [{"language": lang, "count": count} for lang, count in rows]


@router.get("/actions", status_code=status.HTTP_200_OK)
async def get_stats_actions(db: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    """Return self-reported user action state distribution by category."""
    stmt = (
        select(
            Incident.category,
            func.count(case((Incident.user_action_state == "not_acted", 1))).label("not_acted"),
            func.count(case((Incident.user_action_state == "clicked", 1))).label("clicked"),
            func.count(case((Incident.user_action_state == "paid", 1))).label("paid"),
            func.count(Incident.id).label("total")
        )
        .where(Incident.risk_level.in_(FLAGGED_LEVELS))
        .group_by(Incident.category)
        .order_by(func.count(Incident.id).desc())
    )
    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "category": row[0],
            "not_acted": row[1],
            "clicked": row[2],
            "paid": row[3],
            "total": row[4]
        }
        for row in rows
    ]

