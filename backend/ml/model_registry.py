"""
Model Registry
==============
Tracks all trained model versions — their metrics, artifacts,
training timestamps, and champion/challenger status.

Stored in:
  - DB: model_versions table (source of truth)
  - Filesystem: ml/artifacts/ (pkl / pt files)

Usage:
    registry = ModelRegistry(db)
    await registry.register(version_tag, metrics, champion=True)
    current = await registry.get_champion()
"""
import json
import logging
import pickle
from pathlib import Path
from typing import Dict, Optional, Any, List
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

logger = logging.getLogger(__name__)

ARTIFACTS_DIR = Path(__file__).parent / "artifacts"
ARTIFACTS_DIR.mkdir(exist_ok=True)


class ModelRegistry:
    """
    Manages model versioning, promotion, and rollback.
    All state is persisted in PostgreSQL model_versions table.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(
        self,
        version_tag: str,
        trigger_type: str,
        training_records: int,
        metrics: Dict[str, float],
        changelog: str = "",
        is_live: bool = False,
    ) -> str:
        """Register a newly trained model version. Returns version_tag."""
        await self.db.execute(text("""
            INSERT INTO model_versions
                (version_tag, is_live, trigger_type, training_records,
                 validation_mae, validation_r2, changelog)
            VALUES
                (:tag, :live, :trigger, :n_records,
                 :mae, :r2, :changelog)
            ON CONFLICT (version_tag) DO UPDATE SET
                is_live = EXCLUDED.is_live,
                training_records = EXCLUDED.training_records,
                validation_mae = EXCLUDED.validation_mae,
                validation_r2 = EXCLUDED.validation_r2
        """), {
            "tag": version_tag,
            "live": is_live,
            "trigger": trigger_type,
            "n_records": training_records,
            "mae": metrics.get("mae_y5", 0),
            "r2": metrics.get("r2_y5", 0),
            "changelog": changelog,
        })
        await self.db.commit()
        logger.info(f"[Registry] Registered model {version_tag} (live={is_live})")
        return version_tag

    async def promote(self, version_tag: str) -> bool:
        """
        Promote version_tag to champion (is_live=True).
        Demotes all other versions.
        """
        # Demote all
        await self.db.execute(
            text("UPDATE model_versions SET is_live = FALSE WHERE is_live = TRUE")
        )
        # Promote new
        result = await self.db.execute(text("""
            UPDATE model_versions SET is_live = TRUE, promoted_at = NOW()
            WHERE version_tag = :tag RETURNING version_tag
        """), {"tag": version_tag})
        row = result.fetchone()
        if not row:
            logger.error(f"[Registry] Cannot promote: version {version_tag} not found")
            return False
        await self.db.commit()
        logger.info(f"[Registry] Promoted {version_tag} → CHAMPION")
        return True

    async def rollback(self) -> Optional[str]:
        """
        Rollback to the previous champion (most recent non-current is_live=True in history).
        Returns the version_tag rolled back to, or None.
        """
        result = await self.db.execute(text("""
            SELECT version_tag FROM model_versions
            WHERE is_live = FALSE AND promoted_at IS NOT NULL
            ORDER BY promoted_at DESC
            LIMIT 1
        """))
        row = result.fetchone()
        if not row:
            logger.warning("[Registry] No previous champion to roll back to")
            return None
        prev_tag = row.version_tag
        await self.promote(prev_tag)
        logger.info(f"[Registry] Rolled back to {prev_tag}")
        return prev_tag

    async def get_champion(self) -> Optional[Dict]:
        """Get the currently live (champion) model version."""
        result = await self.db.execute(text("""
            SELECT * FROM model_versions WHERE is_live = TRUE LIMIT 1
        """))
        row = result.fetchone()
        if not row:
            return None
        return dict(row._mapping)

    async def list_versions(self, limit: int = 20) -> List[Dict]:
        """List all model versions, newest first."""
        result = await self.db.execute(text("""
            SELECT * FROM model_versions ORDER BY trained_at DESC LIMIT :lim
        """), {"lim": limit})
        return [dict(r._mapping) for r in result]

    async def compare(self, version_a: str, version_b: str) -> Dict:
        """Compare two model versions on all stored metrics."""
        result = await self.db.execute(text("""
            SELECT version_tag, validation_mae, validation_r2, training_records,
                   trained_at, is_live
            FROM model_versions WHERE version_tag IN (:a, :b)
        """), {"a": version_a, "b": version_b})
        rows = {r.version_tag: dict(r._mapping) for r in result}

        a = rows.get(version_a, {})
        b = rows.get(version_b, {})

        if not a or not b:
            return {"error": "One or both versions not found"}

        mae_winner = version_a if (a.get("validation_mae", 999) < b.get("validation_mae", 999)) else version_b

        return {
            "version_a": a,
            "version_b": b,
            "recommendation": mae_winner,
            "mae_improvement_pct": round(
                (b.get("validation_mae", 0) - a.get("validation_mae", 0)) /
                max(b.get("validation_mae", 1), 1) * 100, 1
            ),
        }

    def artifact_path(self, version_tag: str, artifact_type: str = "salary_predictor") -> Path:
        return ARTIFACTS_DIR / f"{artifact_type}_{version_tag}.pkl"

    def artifact_exists(self, version_tag: str, artifact_type: str = "salary_predictor") -> bool:
        return self.artifact_path(version_tag, artifact_type).exists()
