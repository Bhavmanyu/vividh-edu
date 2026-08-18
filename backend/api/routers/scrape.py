"""
/api/scrape — Scrape status endpoints (internal use by Airflow DAGs)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from ..db.database import get_db

router = APIRouter()


@router.get("/{run_id}")
async def get_scrape_run(run_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("SELECT * FROM scrape_runs WHERE id = :id"),
        {"id": run_id},
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Scrape run not found")
    return dict(row._mapping)


@router.patch("/{run_id}")
async def update_scrape_run(
    run_id: str,
    status: str,
    records_scraped: int = 0,
    records_updated: int = 0,
    records_flagged: int = 0,
    error_message: str = None,
    db: AsyncSession = Depends(get_db),
):
    """Called by Airflow DAG tasks to report progress."""
    await db.execute(text("""
        UPDATE scrape_runs SET
            status = :status,
            records_scraped = :scraped,
            records_updated = :updated,
            records_flagged = :flagged,
            error_message = :error,
            completed_at = CASE WHEN :status IN ('success', 'failed', 'partial') THEN NOW() ELSE NULL END
        WHERE id = :id
    """), {
        "id": run_id, "status": status,
        "scraped": records_scraped, "updated": records_updated,
        "flagged": records_flagged, "error": error_message,
    })
    await db.commit()
    return {"status": "updated"}
