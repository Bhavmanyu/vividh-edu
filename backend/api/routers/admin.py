"""
/api/admin — Admin panel endpoints (protected by API key)
- GET  /admin/anomalies            — list pending anomalies
- POST /admin/anomalies/{id}/review — accept or reject
- GET  /admin/feedback             — educator feedback queue
- POST /admin/feedback             — submit educator correction
- GET  /admin/scrapes              — scrape run history
- POST /admin/scrapes/trigger      — manually trigger a scrape
- GET  /admin/models               — model version history
- POST /admin/stats                — dashboard summary stats
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional
from datetime import datetime

from ..db.database import get_db
from ..schemas import AnomalyReviewRequest, FeedbackCreateRequest
from ..config import settings

router = APIRouter()


def _require_admin(x_api_key: Optional[str] = Header(None)):
    if not x_api_key or x_api_key != settings.api_key_admin:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@router.get("/anomalies")
async def list_anomalies(
    db: AsyncSession = Depends(get_db),
    status: str = "pending",
    _: None = Depends(_require_admin),
):
    try:
        result = await db.execute(text("""
            SELECT
                a.id, a.program_id, a.field_name, a.prior_value, a.new_value,
                a.delta_pct, a.status, a.created_at,
                c.short_name AS college_name,
                d.short_name AS degree_name
            FROM anomalies a
            JOIN programs p ON p.id = a.program_id
            JOIN colleges c ON c.id = p.college_id
            JOIN degrees d ON d.id = p.degree_id
            WHERE a.status = :status
            ORDER BY a.created_at DESC
            LIMIT 100
        """), {"status": status})

        rows = [dict(r._mapping) for r in result]
        return {"data": rows, "total": len(rows)}
    except Exception:
        # Return empty if DB unavailable
        return {"data": [], "total": 0, "_source": "error"}


@router.post("/anomalies/{anomaly_id}/review")
async def review_anomaly(
    anomaly_id: str,
    body: AnomalyReviewRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(_require_admin),
):
    try:
        new_status = "accepted" if body.action == "accept" else "rejected"
        result = await db.execute(
            text("""
                UPDATE anomalies
                SET status = :status, review_notes = :notes, reviewed_at = NOW()
                WHERE id = :id
                RETURNING id, status
            """),
            {"status": new_status, "notes": body.notes, "id": anomaly_id},
        )
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Anomaly not found")

        await db.commit()

        # If accepted — flip the data_point to is_current
        if body.action == "accept":
            await _apply_anomaly(db, anomaly_id)

        return {"id": anomaly_id, "status": new_status}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _apply_anomaly(db: AsyncSession, anomaly_id: str):
    """
    When an anomaly is accepted:
    1. Find the data_point for this anomaly's new_value
    2. Flip prior is_current=TRUE to FALSE
    3. Set new data_point is_current=TRUE
    4. Re-trigger ROI score computation (stubbed for Week 2)
    """
    result = await db.execute(
        text("SELECT program_id, field_name, new_value FROM anomalies WHERE id = :id"),
        {"id": anomaly_id},
    )
    row = result.fetchone()
    if not row:
        return

    program_id, field_name, new_value = row.program_id, row.field_name, row.new_value

    # Retire old current value
    await db.execute(text("""
        UPDATE data_points SET is_current = FALSE
        WHERE program_id = :pid AND field_name = :field AND is_current = TRUE
    """), {"pid": program_id, "field": field_name})

    # Mark new value as current
    await db.execute(text("""
        UPDATE data_points SET is_current = TRUE
        WHERE program_id = :pid AND field_name = :field AND raw_value = :val
        AND id = (
            SELECT id FROM data_points
            WHERE program_id = :pid AND field_name = :field AND raw_value = :val
            ORDER BY scraped_at DESC LIMIT 1
        )
    """), {"pid": program_id, "field": field_name, "val": new_value})

    await db.commit()


@router.get("/feedback")
async def list_feedback(
    db: AsyncSession = Depends(get_db),
    status: str = "pending",
    _: None = Depends(_require_admin),
):
    try:
        result = await db.execute(text("""
            SELECT * FROM educator_feedback
            WHERE status = :status
            ORDER BY created_at DESC
            LIMIT 100
        """), {"status": status})
        rows = [dict(r._mapping) for r in result]
        return {"data": rows, "total": len(rows)}
    except Exception:
        return {"data": [], "total": 0}


@router.post("/feedback")
async def submit_feedback(
    body: FeedbackCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Public endpoint — educators submit corrections (no auth required)."""
    try:
        await db.execute(text("""
            INSERT INTO educator_feedback
            (field_name, old_value, new_value, source_url, submitter_confidence, notes, submitter_email)
            VALUES (:field, :old, :new, :url, :conf, :notes, :email)
        """), {
            "field": body.field_name,
            "old": body.old_value,
            "new": body.new_value,
            "url": body.source_url,
            "conf": body.confidence,
            "notes": body.notes,
            "email": body.submitter_email,
        })
        await db.commit()
        return {"status": "received", "message": "Thank you. Your submission is in the review queue."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scrapes")
async def list_scrape_runs(
    db: AsyncSession = Depends(get_db),
    limit: int = 20,
    _: None = Depends(_require_admin),
):
    try:
        result = await db.execute(text("""
            SELECT * FROM scrape_runs
            ORDER BY started_at DESC
            LIMIT :limit
        """), {"limit": limit})
        rows = [dict(r._mapping) for r in result]
        return {"data": rows, "total": len(rows)}
    except Exception:
        return {"data": [], "total": 0}


@router.post("/scrapes/trigger")
async def trigger_scrape(
    source: str,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(_require_admin),
):
    """
    Manually trigger a scrape run.
    In production: sends message to Airflow DAG trigger API.
    """
    valid_sources = ["nirf", "ambitionbox", "naukri", "reddit", "plfs", "worldbank"]
    if source not in valid_sources:
        raise HTTPException(status_code=400, detail=f"Invalid source. Valid: {valid_sources}")

    try:
        result = await db.execute(text("""
            INSERT INTO scrape_runs (source_name, status)
            VALUES (:source, 'running')
            RETURNING id
        """), {"source": source})
        run_id = result.scalar()
        await db.commit()
        return {
            "status": "triggered",
            "run_id": str(run_id),
            "source": source,
            "message": f"Scrape run queued for {source}. Monitor at /api/admin/scrapes/{run_id}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def list_models(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(_require_admin),
):
    try:
        result = await db.execute(text("""
            SELECT * FROM model_versions ORDER BY trained_at DESC LIMIT 20
        """))
        rows = [dict(r._mapping) for r in result]
        return {"data": rows, "total": len(rows)}
    except Exception:
        return {"data": [], "total": 0}


@router.get("/stats")
async def dashboard_stats(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(_require_admin),
):
    """Dashboard summary for admin panel overview tab."""
    try:
        stats = {}

        # Program count
        r = await db.execute(text("SELECT COUNT(*) FROM programs WHERE is_active = TRUE"))
        stats["programs_indexed"] = r.scalar() or 0

        # Pending anomalies
        r = await db.execute(text("SELECT COUNT(*) FROM anomalies WHERE status = 'pending'"))
        stats["pending_anomalies"] = r.scalar() or 0

        # Pending feedback
        r = await db.execute(text("SELECT COUNT(*) FROM educator_feedback WHERE status = 'pending'"))
        stats["pending_feedback"] = r.scalar() or 0

        # Latest scrape
        r = await db.execute(text(
            "SELECT source_name, completed_at, status FROM scrape_runs ORDER BY started_at DESC LIMIT 1"
        ))
        row = r.fetchone()
        stats["last_scrape"] = dict(row._mapping) if row else None

        # Student reports
        r = await db.execute(text("SELECT COUNT(*) FROM student_reports"))
        stats["student_reports"] = r.scalar() or 0

        return stats
    except Exception:
        return {
            "programs_indexed": 0,
            "pending_anomalies": 0,
            "pending_feedback": 0,
            "last_scrape": None,
            "student_reports": 0,
        }
