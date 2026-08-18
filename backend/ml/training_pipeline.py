"""
Training Pipeline
=================
Orchestrates the full ML retraining cycle:
  1. Pull training data from DB (data_points, anomalies resolved)
  2. Build feature matrix via FeatureEngine
  3. Train XGBoost salary predictor (4 horizons)
  4. Train LSTM trajectory (optional, needs torch)
  5. Evaluate on held-out 20% split
  6. Register new model version in registry
  7. Conditionally promote to champion if metrics improve

Called by:
  - Airflow DAG task: compute_roi_scores (after anomaly gate passes)
  - Admin API: POST /api/ml/retrain
  - Manual: python -m ml.training_pipeline --version v1.1

Also writes updated roi_scores and salary_trajectories to DB for all programs.
"""
import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text
import numpy as np

from .salary_predictor import SalaryPredictor
from .lstm_trajectory import LSTMTrajectoryModel
from .markov_career import CareerMarkovModel
from .roi_computer import compute_roi
from .model_registry import ModelRegistry
from .feature_engine import FeatureEngine

logger = logging.getLogger(__name__)


async def _fetch_programs(db: AsyncSession) -> List[Dict]:
    """Pull all active programs with their current data from the DB view."""
    try:
        result = await db.execute(text("""
            SELECT
                p.id AS program_id,
                c.short_name AS college_name,
                c.state, c.tier, c.college_type,
                c.nirf_rank, c.established_year, c.naac_grade,
                d.short_name AS degree_name,
                d.field AS degree_field,
                d.level AS degree_level,
                d.duration_years,
                cd.total_cost_of_degree AS total_cost_of_degree_inr,
                pl.placement_rate_pct,
                pl.median_salary_inr AS placement_median_salary,
                ri.ai_automation_prob,
                ri.salary_volatility,
                ri.industry_cyclicality,
                ri.credential_inflation,
                ri.geographic_concentration,
                ri.work_life_quality,
                r.composite_score AS current_composite_score
            FROM programs p
            JOIN colleges c ON c.id = p.college_id
            JOIN degrees d ON d.id = p.degree_id
            LEFT JOIN cost_data cd ON cd.program_id = p.id AND cd.is_current = TRUE
            LEFT JOIN placement_data pl ON pl.program_id = p.id AND pl.is_current = TRUE
            LEFT JOIN risk_indicators ri ON ri.program_id = p.id AND ri.is_current = TRUE
            LEFT JOIN roi_scores r ON r.program_id = p.id AND r.is_current = TRUE
            WHERE p.is_active = TRUE
        """))
        return [dict(r._mapping) for r in result]
    except Exception as e:
        logger.error(f"[Training] Failed to fetch programs: {e}")
        return []


async def _fetch_salary_training_rows(db: AsyncSession) -> List:
    """
    Pull salary data points confirmed as is_current=TRUE.
    Returns rows compatible with SEED_TRAINING_DATA format.
    """
    try:
        result = await db.execute(text("""
            SELECT
                c.short_name AS college_name,
                d.field AS degree_field,
                c.tier,
                c.college_type,
                c.nirf_rank,
                cd.total_cost_of_degree AS total_cost,
                pl.placement_rate_pct AS placement_rate,
                -- Use placement median as y1 anchor if scraped salary not available
                COALESCE(
                    (SELECT parsed_value FROM data_points dp
                     WHERE dp.program_id = p.id
                       AND dp.field_name IN ('ambitionbox_median_salary', 'naukri_salary')
                       AND dp.is_current = TRUE
                     LIMIT 1),
                    pl.median_salary_inr
                ) AS salary_y1
            FROM programs p
            JOIN colleges c ON c.id = p.college_id
            JOIN degrees d ON d.id = p.degree_id
            LEFT JOIN cost_data cd ON cd.program_id = p.id AND cd.is_current = TRUE
            LEFT JOIN placement_data pl ON pl.program_id = p.id AND pl.is_current = TRUE
            WHERE p.is_active = TRUE AND pl.median_salary_inr IS NOT NULL
        """))
        rows = []
        for r in result:
            row_dict = dict(r._mapping)
            salary_y1 = row_dict.get("salary_y1") or 800_000
            # Build synthetic trajectory anchors (real LSTM/scraping fills these in)
            rows.append((
                row_dict.get("college_name", "Unknown"),
                row_dict.get("degree_field", "engineering-cs"),
                str(row_dict.get("tier", "2")),
                row_dict.get("college_type", "private"),
                row_dict.get("nirf_rank") or 200,
                float(row_dict.get("total_cost") or 800_000),
                float(row_dict.get("placement_rate") or 0.65),
                int(salary_y1),
                int(salary_y1 * 2.4),   # y5 estimate
                int(salary_y1 * 5.0),   # y10 estimate
                int(salary_y1 * 12.0),  # y20 estimate
            ))
        return rows
    except Exception:
        return []


async def _write_roi_to_db(
    db: AsyncSession,
    program_id: str,
    roi: Dict,
    trajectory: Dict,
    model_version: str,
):
    """Persist updated ROI scores and trajectory to DB."""
    # Retire old current ROI
    await db.execute(text("""
        UPDATE roi_scores SET is_current = FALSE
        WHERE program_id = :pid AND is_current = TRUE
    """), {"pid": program_id})

    # Insert new
    await db.execute(text("""
        INSERT INTO roi_scores (
            program_id, model_version,
            composite_score, financial_roi_pct, risk_score,
            optionality_score, mobility_score, satisfaction_score,
            network_score, ci_low, ci_high, confidence_level, is_current
        ) VALUES (
            :pid, :mv,
            :comp, :fin, :risk,
            :opt, :mob, :sat,
            :net, :ci_l, :ci_h, :conf, TRUE
        )
    """), {
        "pid": program_id, "mv": model_version,
        "comp": roi["composite_score"],
        "fin": roi["financial_roi_pct"],
        "risk": roi["risk_score"],
        "opt": roi["optionality_score"],
        "mob": roi["mobility_score"],
        "sat": roi["satisfaction_score"],
        "net": roi["network_score"],
        "ci_l": roi["ci_low"],
        "ci_h": roi["ci_high"],
        "conf": roi["confidence_level"],
    })

    # Write trajectory checkpoints
    for checkpoint, bands in trajectory.items():
        year = int(checkpoint.replace("y", ""))
        await db.execute(text("""
            INSERT INTO salary_trajectories (
                program_id, model_version, year_from_graduation,
                p25_inr, p50_inr, p75_inr, p90_inr, is_current
            ) VALUES (
                :pid, :mv, :yr,
                :p25, :p50, :p75, :p90, TRUE
            )
            ON CONFLICT (program_id, year_from_graduation) DO UPDATE SET
                p25_inr = EXCLUDED.p25_inr, p50_inr = EXCLUDED.p50_inr,
                p75_inr = EXCLUDED.p75_inr, p90_inr = EXCLUDED.p90_inr,
                model_version = EXCLUDED.model_version,
                is_current = TRUE
        """), {
            "pid": program_id, "mv": model_version, "yr": year,
            "p25": bands.get("p25", 0),
            "p50": bands.get("p50", 0),
            "p75": bands.get("p75", 0),
            "p90": bands.get("p90", 0),
        })


async def run_training_pipeline(
    db: AsyncSession,
    version_tag: Optional[str] = None,
    trigger: str = "scheduled",
    promote_if_better: bool = True,
) -> Dict[str, Any]:
    """
    Full retraining cycle. Returns summary dict.

    Args:
        db: AsyncSession (injected by Airflow or FastAPI)
        version_tag: e.g. "v1.2" — auto-generated if None
        trigger: "scheduled" | "manual" | "anomaly_resolved"
        promote_if_better: promote new model if validation MAE < champion
    """
    if not version_tag:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
        version_tag = f"v{ts}"

    logger.info(f"[Pipeline] Starting training run — version={version_tag} trigger={trigger}")
    registry = ModelRegistry(db)

    # ── 1. Fetch data ──────────────────────────────────────────────
    programs = await _fetch_programs(db)
    extra_rows = await _fetch_salary_training_rows(db)

    logger.info(f"[Pipeline] Programs: {len(programs)}, Extra salary rows: {len(extra_rows)}")

    # ── 2. Train XGBoost ──────────────────────────────────────────
    predictor = SalaryPredictor(model_version=version_tag)
    try:
        metrics = predictor.train(extra_rows=extra_rows if extra_rows else None)
        predictor.save()
        logger.info(f"[Pipeline] XGBoost trained. MAE_y5: {metrics.get('mae_y5', '?'):.0f}")
    except Exception as e:
        logger.error(f"[Pipeline] XGBoost training failed: {e}")
        metrics = {}

    # ── 3. Train LSTM (optional) ──────────────────────────────────
    lstm = LSTMTrajectoryModel(model_version=version_tag)
    try:
        lstm_result = lstm.train()
        logger.info(f"[Pipeline] LSTM: {lstm_result}")
    except Exception as e:
        logger.warning(f"[Pipeline] LSTM training skipped: {e}")

    # ── 4. Compute ROI for all programs + write to DB ─────────────
    n_updated = 0
    errors = []

    for program in programs:
        program_id = str(program["program_id"])
        try:
            # Predict salary trajectory
            seed_salary = (
                program.get("placement_median_salary") or
                predictor.predict(program)["y1"]["p50"]
            )
            program["seed_salary_y1"] = seed_salary

            trajectory = lstm.predict_trajectory(program)
            roi = compute_roi(program, trajectory)

            await _write_roi_to_db(db, program_id, roi, trajectory, version_tag)
            n_updated += 1

        except Exception as e:
            logger.error(f"[Pipeline] ROI compute failed for {program_id}: {e}")
            errors.append({"program_id": program_id, "error": str(e)})

    await db.commit()
    logger.info(f"[Pipeline] ROI updated for {n_updated}/{len(programs)} programs. Errors: {len(errors)}")

    # ── 5. Register model version ──────────────────────────────────
    await registry.register(
        version_tag=version_tag,
        trigger_type=trigger,
        training_records=len(programs) + len(extra_rows),
        metrics=metrics,
        changelog=f"Retrain triggered by {trigger}. {n_updated} programs updated.",
        is_live=False,
    )

    # ── 6. Promote if better than current champion ─────────────────
    promoted = False
    if promote_if_better and metrics:
        champion = await registry.get_champion()
        if champion:
            champ_mae = champion.get("validation_mae") or float("inf")
            new_mae = metrics.get("mae_y5", float("inf"))
            if new_mae < champ_mae * 0.97:   # needs to be ≥3% better
                await registry.promote(version_tag)
                promoted = True
                logger.info(f"[Pipeline] Promoted {version_tag} (MAE {new_mae:.0f} < {champ_mae:.0f})")
            else:
                logger.info(f"[Pipeline] Not promoting: MAE {new_mae:.0f} vs champion {champ_mae:.0f}")
        else:
            # No champion yet — always promote first model
            await registry.promote(version_tag)
            promoted = True

    return {
        "version_tag": version_tag,
        "trigger": trigger,
        "n_programs_updated": n_updated,
        "n_training_records": len(programs) + len(extra_rows),
        "metrics": metrics,
        "promoted": promoted,
        "errors": errors[:5],   # first 5 only
    }


async def main():
    """CLI entry point: python -m ml.training_pipeline [--version v1.2]"""
    import sys
    import os

    version_arg = None
    if "--version" in sys.argv:
        idx = sys.argv.index("--version")
        if idx + 1 < len(sys.argv):
            version_arg = sys.argv[idx + 1]

    db_url = os.environ.get(
        "DATABASE_URL",
        "postgresql+asyncpg://indialens:indialens_dev@localhost:5432/indialens"
    )
    engine = create_async_engine(db_url)
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession)

    async with SessionLocal() as db:
        result = await run_training_pipeline(
            db=db,
            version_tag=version_arg,
            trigger="manual",
        )

    print("\n✅ Training pipeline complete:")
    print(f"  Version:   {result['version_tag']}")
    print(f"  Programs:  {result['n_programs_updated']} updated")
    print(f"  Records:   {result['n_training_records']}")
    print(f"  Promoted:  {result['promoted']}")
    if result.get("metrics"):
        for k, v in result["metrics"].items():
            print(f"  {k}: ₹{v:,.0f}")
    if result.get("errors"):
        print(f"  Errors ({len(result['errors'])} shown):")
        for e in result["errors"]:
            print(f"    {e}")


if __name__ == "__main__":
    asyncio.run(main())
