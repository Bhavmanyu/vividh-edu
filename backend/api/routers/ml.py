"""
/api/ml — ML model management endpoints

GET  /ml/status              — current champion + model health
GET  /ml/feature-importance  — top features from XGBoost
POST /ml/retrain             — trigger retraining (admin)
POST /ml/promote/{version}   — promote a version to champion (admin)
POST /ml/rollback            — rollback to previous champion (admin)
GET  /ml/versions            — list all versions
GET  /ml/compare             — compare two versions
"""
from fastapi import APIRouter, Depends, HTTPException, Header, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional
import asyncio

from ..db.database import get_db
from ..config import settings

router = APIRouter()


def _require_admin(x_api_key: Optional[str] = Header(None)):
    if not x_api_key or x_api_key != settings.api_key_admin:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@router.get("/status")
async def model_status(db: AsyncSession = Depends(get_db)):
    """Public: current model version, training metadata, data freshness."""
    try:
        result = await db.execute(text("""
            SELECT version_tag, trained_at, training_records,
                   validation_mae, validation_r2, changelog
            FROM model_versions WHERE is_live = TRUE LIMIT 1
        """))
        row = result.fetchone()
        champion = dict(row._mapping) if row else None

        # Data freshness
        result2 = await db.execute(text("""
            SELECT MAX(scraped_at) AS last_scrape FROM data_points
        """))
        last_scrape = result2.scalar()

        # Program count
        result3 = await db.execute(text("SELECT COUNT(*) FROM programs WHERE is_active = TRUE"))
        program_count = result3.scalar() or 0

        return {
            "champion": champion,
            "programs_indexed": program_count,
            "last_data_update": last_scrape.isoformat() if last_scrape else None,
            "model_health": "healthy" if champion else "no_model",
        }
    except Exception:
        return {
            "champion": {"version_tag": settings.current_model_version},
            "programs_indexed": 15,
            "last_data_update": None,
            "model_health": "seed_mode",
        }


@router.get("/feature-importance")
async def feature_importance():
    """Return top feature importances from the current XGBoost model."""
    try:
        from ...ml.salary_predictor import get_predictor
        predictor = get_predictor(settings.current_model_version)
        importances = predictor.feature_importance(top_n=10)
        return {
            "model_version": settings.current_model_version,
            "features": importances,
            "description": "Importance of each feature in predicting 5-year salary (y5 model). Higher = more influential.",
        }
    except Exception as e:
        # Return static importances from seed training if model not loaded
        return {
            "model_version": settings.current_model_version,
            "features": [
                {"feature": "tier_score",           "importance": 0.2841},
                {"feature": "demand_index",          "importance": 0.1923},
                {"feature": "field_score",           "importance": 0.1654},
                {"feature": "nirf_rank_norm",        "importance": 0.1210},
                {"feature": "college_type_score",    "importance": 0.0882},
                {"feature": "placement_rate",        "importance": 0.0741},
                {"feature": "total_cost_norm",       "importance": 0.0389},
                {"feature": "ai_automation_prob",    "importance": 0.0360},
            ],
            "description": "Static importances (seed model). Train on more data to refresh.",
            "_source": "static",
        }


@router.post("/retrain")
async def trigger_retrain(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    version_tag: Optional[str] = None,
    _: None = Depends(_require_admin),
):
    """Trigger async retraining. Returns immediately; training runs in background."""
    async def _run_pipeline():
        from ...ml.training_pipeline import run_training_pipeline
        async_result = await run_training_pipeline(
            db=db,
            version_tag=version_tag,
            trigger="manual",
            promote_if_better=True,
        )
        return async_result

    background_tasks.add_task(_run_pipeline)
    return {
        "status": "training_started",
        "version_tag": version_tag or "auto",
        "message": "Training pipeline running in background. Check /ml/versions for progress.",
    }


@router.post("/promote/{version_tag}")
async def promote_version(
    version_tag: str,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(_require_admin),
):
    from ...ml.model_registry import ModelRegistry
    registry = ModelRegistry(db)
    success = await registry.promote(version_tag)
    if not success:
        raise HTTPException(status_code=404, detail=f"Version {version_tag} not found")
    return {"status": "promoted", "version_tag": version_tag}


@router.post("/rollback")
async def rollback(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(_require_admin),
):
    from ...ml.model_registry import ModelRegistry
    registry = ModelRegistry(db)
    rolled_back_to = await registry.rollback()
    if not rolled_back_to:
        raise HTTPException(status_code=400, detail="No previous champion found to roll back to")
    return {"status": "rolled_back", "version_tag": rolled_back_to}


@router.get("/versions")
async def list_versions(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(_require_admin),
):
    from ...ml.model_registry import ModelRegistry
    registry = ModelRegistry(db)
    versions = await registry.list_versions()
    return {"versions": versions, "total": len(versions)}


@router.get("/compare")
async def compare_versions(
    version_a: str,
    version_b: str,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(_require_admin),
):
    from ...ml.model_registry import ModelRegistry
    registry = ModelRegistry(db)
    comparison = await registry.compare(version_a, version_b)
    return comparison
