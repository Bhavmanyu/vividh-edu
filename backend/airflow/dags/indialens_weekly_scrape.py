"""
IndiaLens Weekly Scrape Pipeline — Airflow DAG
Runs every Sunday at 2:00 AM IST (20:30 UTC Saturday)

DAG topology:
  start
   ├── scrape_nirf
   ├── scrape_ambitionbox
   ├── scrape_naukri
   └── scrape_reddit
         ↓ (all complete)
   anomaly_report
         ↓
   retrain_trigger   (conditional — only if anomalies < 10% of total)
         ↓
   compute_roi_scores
         ↓
   invalidate_cache
         ↓
   notify_admin
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from airflow import DAG
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.models import Variable

logger = logging.getLogger(__name__)

# ── DAG defaults ────────────────────────────────────────────────────
DEFAULT_ARGS = {
    "owner": "indialens-data",
    "depends_on_past": False,
    "start_date": datetime(2026, 8, 1),
    "email": ["data@indialens.in"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(hours=2),
}

# ── Config pulled from Airflow Variables (set via UI or CLI) ────────
def get_config() -> dict:
    return {
        "database_url": Variable.get("INDIALENS_DATABASE_URL", default_var="postgresql://indialens:indialens_dev@postgres:5432/indialens"),
        "api_base": Variable.get("INDIALENS_API_BASE", default_var="http://api:8000"),
        "anomaly_threshold": float(Variable.get("ANOMALY_THRESHOLD_PCT", default_var="25.0")),
        "retrain_threshold": float(Variable.get("RETRAIN_ANOMALY_PCT", default_var="0.10")),
        "reddit_client_id": Variable.get("REDDIT_CLIENT_ID", default_var=""),
        "reddit_client_secret": Variable.get("REDDIT_CLIENT_SECRET", default_var=""),
    }


# ── Task functions ──────────────────────────────────────────────────

def _create_scrape_run(source_name: str, config: dict) -> str:
    """Create a scrape_run record and return its UUID."""
    import psycopg2
    import uuid

    run_id = str(uuid.uuid4())
    conn = psycopg2.connect(config["database_url"])
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO scrape_runs (id, source_name, status) VALUES (%s, %s, 'running')",
                (run_id, source_name),
            )
        conn.commit()
    finally:
        conn.close()
    return run_id


def _update_scrape_run(run_id: str, status: str, stats: dict, config: dict):
    """Update scrape_run status + stats."""
    import psycopg2

    conn = psycopg2.connect(config["database_url"])
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE scrape_runs SET
                    status = %s,
                    records_scraped = %s,
                    records_updated = %s,
                    records_flagged = %s,
                    completed_at = NOW()
                WHERE id = %s
            """, (
                status,
                stats.get("scraped", 0),
                stats.get("updated", 0),
                stats.get("flagged", 0),
                run_id,
            ))
        conn.commit()
    finally:
        conn.close()


def task_scrape_nirf(**context):
    """Scrape NIRF rankings."""
    import asyncio
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

    config = get_config()
    run_id = _create_scrape_run("nirf", config)
    context["task_instance"].xcom_push(key="nirf_run_id", value=run_id)

    async def _run():
        engine = create_async_engine(config["database_url"].replace("postgresql://", "postgresql+asyncpg://"))
        async_session = async_sessionmaker(engine, class_=AsyncSession)
        async with async_session() as session:
            from indialens.scrapers.nirf_scraper import NIRFScraper
            scraper = NIRFScraper(db=session, run_id=run_id)
            stats = await scraper.run()
            return stats

    stats = asyncio.run(_run())
    _update_scrape_run(run_id, "success", {
        "scraped": stats.records_scraped,
        "updated": stats.records_updated,
        "flagged": stats.records_flagged,
    }, config)

    logger.info(f"[NIRF] ✓ scraped={stats.records_scraped} updated={stats.records_updated} flagged={stats.records_flagged}")
    return {"run_id": run_id, "stats": stats.__dict__}


def task_scrape_ambitionbox(**context):
    """Scrape AmbitionBox salary data."""
    import asyncio
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

    config = get_config()
    run_id = _create_scrape_run("ambitionbox", config)
    context["task_instance"].xcom_push(key="ambitionbox_run_id", value=run_id)

    async def _run():
        engine = create_async_engine(config["database_url"].replace("postgresql://", "postgresql+asyncpg://"))
        async_session = async_sessionmaker(engine, class_=AsyncSession)
        async with async_session() as session:
            from indialens.scrapers.ambitionbox_scraper import AmbitionBoxScraper
            scraper = AmbitionBoxScraper(db=session, run_id=run_id)
            return await scraper.run()

    stats = asyncio.run(_run())
    _update_scrape_run(run_id, "success", {
        "scraped": stats.records_scraped,
        "updated": stats.records_updated,
        "flagged": stats.records_flagged,
    }, config)
    return {"run_id": run_id, "stats": stats.__dict__}


def task_scrape_naukri(**context):
    """Scrape Naukri.com job postings."""
    import asyncio
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

    config = get_config()
    run_id = _create_scrape_run("naukri", config)
    context["task_instance"].xcom_push(key="naukri_run_id", value=run_id)

    async def _run():
        engine = create_async_engine(config["database_url"].replace("postgresql://", "postgresql+asyncpg://"))
        async_session = async_sessionmaker(engine, class_=AsyncSession)
        async with async_session() as session:
            from indialens.scrapers.naukri_scraper import NaukriScraper
            scraper = NaukriScraper(db=session, run_id=run_id)
            return await scraper.run()

    stats = asyncio.run(_run())
    _update_scrape_run(run_id, "success", {
        "scraped": stats.records_scraped,
        "updated": stats.records_updated,
        "flagged": stats.records_flagged,
    }, config)
    return {"run_id": run_id, "stats": stats.__dict__}


def task_scrape_reddit(**context):
    """Extract salary signals from Reddit."""
    import asyncio
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

    config = get_config()
    run_id = _create_scrape_run("reddit", config)
    context["task_instance"].xcom_push(key="reddit_run_id", value=run_id)

    async def _run():
        engine = create_async_engine(config["database_url"].replace("postgresql://", "postgresql+asyncpg://"))
        async_session = async_sessionmaker(engine, class_=AsyncSession)
        async with async_session() as session:
            from indialens.scrapers.reddit_scraper import RedditScraper

            class MockSettings:
                reddit_client_id = config["reddit_client_id"]
                reddit_client_secret = config["reddit_client_secret"]
                reddit_user_agent = "IndiaLensBot/1.0"

            scraper = RedditScraper(db=session, run_id=run_id, settings=MockSettings())
            return await scraper.run()

    stats = asyncio.run(_run())
    _update_scrape_run(run_id, "success", {
        "scraped": stats.records_scraped,
        "updated": stats.records_updated,
        "flagged": stats.records_flagged,
    }, config)
    return {"run_id": run_id, "stats": stats.__dict__}


def task_scrape_worldbank(**context):
    """Scrape World Bank macroeconomic indicators."""
    import asyncio
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

    config = get_config()
    run_id = _create_scrape_run("worldbank", config)
    context["task_instance"].xcom_push(key="worldbank_run_id", value=run_id)

    async def _run():
        engine = create_async_engine(config["database_url"].replace("postgresql://", "postgresql+asyncpg://"))
        async_session = async_sessionmaker(engine, class_=AsyncSession)
        async with async_session() as session:
            from indialens.scrapers.worldbank_scraper import WorldBankScraper
            scraper = WorldBankScraper(db=session, run_id=run_id)
            return await scraper.run()

    stats = asyncio.run(_run())
    _update_scrape_run(run_id, "success", {
        "scraped": stats.records_scraped,
        "updated": stats.records_updated,
        "flagged": stats.records_flagged,
    }, config)
    return {"run_id": run_id, "stats": stats.__dict__}


def task_scrape_plfs(**context):
    """Ingest PLFS labour force data."""
    import asyncio
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

    config = get_config()
    run_id = _create_scrape_run("plfs", config)
    context["task_instance"].xcom_push(key="plfs_run_id", value=run_id)

    async def _run():
        engine = create_async_engine(config["database_url"].replace("postgresql://", "postgresql+asyncpg://"))
        async_session = async_sessionmaker(engine, class_=AsyncSession)
        async with async_session() as session:
            from indialens.scrapers.plfs_scraper import PLFSScraper
            scraper = PLFSScraper(db=session, run_id=run_id)
            return await scraper.run()

    stats = asyncio.run(_run())
    _update_scrape_run(run_id, "success", {
        "scraped": stats.records_scraped,
        "updated": stats.records_updated,
        "flagged": stats.records_flagged,
    }, config)
    return {"run_id": run_id, "stats": stats.__dict__}


def task_scrape_internshala(**context):
    """Scrape Internshala stipends & job demand."""
    import asyncio
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

    config = get_config()
    run_id = _create_scrape_run("internshala", config)
    context["task_instance"].xcom_push(key="internshala_run_id", value=run_id)

    async def _run():
        engine = create_async_engine(config["database_url"].replace("postgresql://", "postgresql+asyncpg://"))
        async_session = async_sessionmaker(engine, class_=AsyncSession)
        async with async_session() as session:
            from indialens.scrapers.internshala_scraper import InternshalaScraper
            scraper = InternshalaScraper(db=session, run_id=run_id)
            return await scraper.run()

    stats = asyncio.run(_run())
    _update_scrape_run(run_id, "success", {
        "scraped": stats.records_scraped,
        "updated": stats.records_updated,
        "flagged": stats.records_flagged,
    }, config)
    return {"run_id": run_id, "stats": stats.__dict__}


def task_scrape_indeed(**context):
    """Scrape Indeed job volumes and salaries."""
    import asyncio
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

    config = get_config()
    run_id = _create_scrape_run("indeed", config)
    context["task_instance"].xcom_push(key="indeed_run_id", value=run_id)

    async def _run():
        engine = create_async_engine(config["database_url"].replace("postgresql://", "postgresql+asyncpg://"))
        async_session = async_sessionmaker(engine, class_=AsyncSession)
        async with async_session() as session:
            from indialens.scrapers.indeed_scraper import IndeedScraper
            scraper = IndeedScraper(db=session, run_id=run_id)
            return await scraper.run()

    stats = asyncio.run(_run())
    _update_scrape_run(run_id, "success", {
        "scraped": stats.records_scraped,
        "updated": stats.records_updated,
        "flagged": stats.records_flagged,
    }, config)
    return {"run_id": run_id, "stats": stats.__dict__}


def task_scrape_placement(**context):
    """Scrape official college placement stats."""
    import asyncio
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

    config = get_config()
    run_id = _create_scrape_run("college_placement", config)
    context["task_instance"].xcom_push(key="placement_run_id", value=run_id)

    async def _run():
        engine = create_async_engine(config["database_url"].replace("postgresql://", "postgresql+asyncpg://"))
        async_session = async_sessionmaker(engine, class_=AsyncSession)
        async with async_session() as session:
            from indialens.scrapers.college_placement_scraper import CollegePlacementScraper
            scraper = CollegePlacementScraper(db=session, run_id=run_id)
            return await scraper.run()

    stats = asyncio.run(_run())
    _update_scrape_run(run_id, "success", {
        "scraped": stats.records_scraped,
        "updated": stats.records_updated,
        "flagged": stats.records_flagged,
    }, config)
    return {"run_id": run_id, "stats": stats.__dict__}


def task_anomaly_report(**context):
    """
    Summarise all anomalies from this scrape cycle.
    Pushes anomaly_pct to XCom for the retrain gate.
    """
    import psycopg2

    config = get_config()
    conn = psycopg2.connect(config["database_url"])

    with conn.cursor() as cur:
        # Total new records in last 24h
        cur.execute("""
            SELECT COUNT(*) FROM data_points WHERE scraped_at > NOW() - INTERVAL '24 hours'
        """)
        total_new = cur.fetchone()[0] or 1

        # Total anomalies in last 24h
        cur.execute("""
            SELECT COUNT(*) FROM anomalies WHERE created_at > NOW() - INTERVAL '24 hours'
        """)
        total_anomalies = cur.fetchone()[0] or 0

        # Pending anomalies
        cur.execute("SELECT COUNT(*) FROM anomalies WHERE status = 'pending'")
        pending = cur.fetchone()[0] or 0

    conn.close()

    anomaly_pct = total_anomalies / total_new
    logger.info(
        f"[AnomalyReport] new_records={total_new} anomalies={total_anomalies} "
        f"({anomaly_pct:.1%}) pending_queue={pending}"
    )

    context["task_instance"].xcom_push(key="anomaly_pct", value=anomaly_pct)
    context["task_instance"].xcom_push(key="pending_anomalies", value=pending)

    return {
        "total_new_records": total_new,
        "total_anomalies": total_anomalies,
        "anomaly_pct": anomaly_pct,
        "pending_anomalies": pending,
    }


def task_should_retrain(**context) -> bool:
    """
    Gate: only retrain if anomaly rate is low enough that the new data is trustworthy.
    Returns True (proceed) if anomaly_pct < RETRAIN_THRESHOLD.
    """
    config = get_config()
    anomaly_pct = context["task_instance"].xcom_pull(task_ids="anomaly_report", key="anomaly_pct") or 1.0
    retrain_threshold = config["retrain_threshold"]

    should_train = anomaly_pct < retrain_threshold
    logger.info(f"[RetrainGate] anomaly_pct={anomaly_pct:.1%} threshold={retrain_threshold:.1%} → {'GO' if should_train else 'SKIP'}")
    return should_train


def task_compute_roi_scores(**context):
    """
    Week 3: Full XGBoost + LSTM training pipeline.
    Trains a new model version, computes ROI for all programs,
    writes to DB, and conditionally promotes the new model.
    """
    import asyncio
    from datetime import datetime, timezone
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

    config = get_config()
    anomaly_pct = context["task_instance"].xcom_pull(task_ids="anomaly_report", key="anomaly_pct") or 0.0

    async def _run():
        db_url = config["database_url"].replace("postgresql://", "postgresql+asyncpg://")
        engine = create_async_engine(db_url)
        async_session = async_sessionmaker(engine, class_=AsyncSession)

        async with async_session() as db:
            from indialens.ml.training_pipeline import run_training_pipeline

            ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
            version_tag = f"v{ts}_airflow"

            result = await run_training_pipeline(
                db=db,
                version_tag=version_tag,
                trigger="scheduled",
                promote_if_better=True,
            )
            return result

    result = asyncio.run(_run())

    logger.info(
        f"[ROI/ML] Training complete — version={result['version_tag']} "
        f"programs={result['n_programs_updated']} "
        f"promoted={result['promoted']}"
    )

    context["task_instance"].xcom_push(key="ml_version_tag", value=result["version_tag"])
    context["task_instance"].xcom_push(key="ml_promoted", value=result["promoted"])

    return result


def task_invalidate_cache(**context):
    """
    Clear Redis cache for updated program IDs so Next.js
    picks up fresh data on next request.
    """
    try:
        import redis

        config = get_config()
        r = redis.from_url(Variable.get("REDIS_URL", default_var="redis://redis:6379/0"))

        # Invalidate all program cache keys
        keys = r.keys("indialens:program:*")
        if keys:
            r.delete(*keys)
        r.delete("indialens:index:*")

        logger.info(f"[Cache] Invalidated {len(keys)} cache keys")
        return {"invalidated_keys": len(keys)}
    except Exception as e:
        logger.warning(f"[Cache] Redis invalidation failed (non-fatal): {e}")
        return {"invalidated_keys": 0, "error": str(e)}


def task_notify_admin(**context):
    """Send email/webhook summary to the admin team."""
    ti = context["task_instance"]
    anomaly_report = ti.xcom_pull(task_ids="anomaly_report") or {}
    roi_result = ti.xcom_pull(task_ids="compute_roi_scores") or {}

    summary = {
        "run_date": context["ds"],
        "anomaly_pct": f"{anomaly_report.get('anomaly_pct', 0):.1%}",
        "pending_anomalies": anomaly_report.get("pending_anomalies", 0),
        "programs_updated": roi_result.get("programs_updated", 0),
    }

    logger.info(f"[Notify] Weekly scrape complete: {summary}")
    # TODO: send to Slack webhook or email in production
    return summary


# ── DAG definition ──────────────────────────────────────────────────

with DAG(
    dag_id="indialens_weekly_scrape",
    default_args=DEFAULT_ARGS,
    description="Weekly data pipeline: scrape → anomaly check → ROI recompute",
    schedule_interval="30 20 * * 6",   # 20:30 UTC Saturday = 02:00 IST Sunday
    catchup=False,
    max_active_runs=1,
    tags=["indialens", "scrape", "weekly"],
) as dag:

    start = EmptyOperator(task_id="start")

    # Parallel scrape tasks
    scrape_nirf = PythonOperator(
        task_id="scrape_nirf",
        python_callable=task_scrape_nirf,
        pool="scraper_pool",
    )

    scrape_ambitionbox = PythonOperator(
        task_id="scrape_ambitionbox",
        python_callable=task_scrape_ambitionbox,
        pool="scraper_pool",
    )

    scrape_naukri = PythonOperator(
        task_id="scrape_naukri",
        python_callable=task_scrape_naukri,
        pool="scraper_pool",
    )

    scrape_reddit = PythonOperator(
        task_id="scrape_reddit",
        python_callable=task_scrape_reddit,
        pool="scraper_pool",
    )

    scrape_worldbank = PythonOperator(
        task_id="scrape_worldbank",
        python_callable=task_scrape_worldbank,
        pool="scraper_pool",
    )

    scrape_plfs = PythonOperator(
        task_id="scrape_plfs",
        python_callable=task_scrape_plfs,
        pool="scraper_pool",
    )

    scrape_internshala = PythonOperator(
        task_id="scrape_internshala",
        python_callable=task_scrape_internshala,
        pool="scraper_pool",
    )

    scrape_indeed = PythonOperator(
        task_id="scrape_indeed",
        python_callable=task_scrape_indeed,
        pool="scraper_pool",
    )

    scrape_placement = PythonOperator(
        task_id="scrape_placement",
        python_callable=task_scrape_placement,
        pool="scraper_pool",
    )

    all_scrapers = [
        scrape_nirf, scrape_ambitionbox, scrape_naukri, scrape_reddit,
        scrape_worldbank, scrape_plfs, scrape_internshala, scrape_indeed, scrape_placement
    ]

    anomaly_report = PythonOperator(
        task_id="anomaly_report",
        python_callable=task_anomaly_report,
        trigger_rule=TriggerRule.ALL_DONE,   # run even if some scrapers fail
    )

    retrain_gate = ShortCircuitOperator(
        task_id="retrain_gate",
        python_callable=task_should_retrain,
    )

    compute_roi = PythonOperator(
        task_id="compute_roi_scores",
        python_callable=task_compute_roi_scores,
    )

    invalidate_cache = PythonOperator(
        task_id="invalidate_cache",
        python_callable=task_invalidate_cache,
    )

    notify = PythonOperator(
        task_id="notify_admin",
        python_callable=task_notify_admin,
        trigger_rule=TriggerRule.ALL_DONE,
    )

    # ── Wire up the DAG ─────────────────────────────────────────────
    start >> all_scrapers >> anomaly_report >> retrain_gate >> compute_roi >> invalidate_cache >> notify
