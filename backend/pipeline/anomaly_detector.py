"""
Anomaly Detector — flags suspicious data point changes.

Rules:
  1. Delta > THRESHOLD_PCT (default 25%) → FLAG for human review
  2. Delta < AUTO_ACCEPT_PCT (default 5%) → auto-accept (no human needed)
  3. New value is literally 0 when prior > 0 → always FLAG (suspected scraper error)
  4. Field-specific overrides: placement_rate_pct threshold = 15%
  5. Reddit salary signals have higher tolerance (50%) due to anecdotal nature

When a flag is created:
  - data_point row is inserted but is_current stays FALSE
  - anomaly row is created with status='pending'
  - Admin queue shows it for human review
  - If accepted → flip is_current to TRUE + re-run ROI computation
  - If rejected → mark data_point as is_anomaly=TRUE
"""
import logging
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

logger = logging.getLogger(__name__)

# Default thresholds
ANOMALY_THRESHOLD_PCT = 25.0
AUTO_ACCEPT_THRESHOLD_PCT = 5.0

# Field-specific thresholds (override default)
FIELD_THRESHOLDS = {
    "placement_rate_pct": 15.0,        # more sensitive
    "median_salary_inr": 30.0,         # wider range acceptable
    "nirf_rank": 20.0,                 # rank jumps are real
    "reddit_salary_signal": 50.0,      # anecdotal data — wide tolerance
    "ambitionbox_median_salary": 35.0,
    "naukri_salary_*": 40.0,
    "nirf_go_score": 15.0,
}


def _get_threshold(field_name: str) -> Tuple[float, float]:
    """Return (anomaly_threshold, auto_accept_threshold) for the given field."""
    # Wildcard match for fields like "naukri_salary_engineering-cs"
    for pattern, threshold in FIELD_THRESHOLDS.items():
        if pattern.endswith("*"):
            if field_name.startswith(pattern[:-1]):
                return threshold, AUTO_ACCEPT_THRESHOLD_PCT
        elif field_name == pattern:
            return threshold, AUTO_ACCEPT_THRESHOLD_PCT

    return ANOMALY_THRESHOLD_PCT, AUTO_ACCEPT_THRESHOLD_PCT


class AnomalyDetector:
    """
    Stateless detector — instantiated per scrape run.
    Checks each incoming data point against the current value in the DB.
    """

    def __init__(self, db: AsyncSession, run_id: str):
        self.db = db
        self.run_id = run_id

    async def check(
        self,
        program_id: str,
        field_name: str,
        new_value: str,
        new_parsed: Optional[float],
    ) -> Tuple[bool, float, Optional[str]]:
        """
        Compare new scraped value against current DB value.

        Returns:
            (is_anomaly: bool, delta_pct: float, prior_value: str | None)
        """
        # Fetch current value
        result = await self.db.execute(text("""
            SELECT raw_value, parsed_value
            FROM data_points
            WHERE program_id = :pid AND field_name = :field AND is_current = TRUE
            LIMIT 1
        """), {"pid": program_id, "field": field_name})
        row = result.fetchone()

        if not row:
            # No prior value — this is a new data point, always accept
            return False, 0.0, None

        prior_raw = row.raw_value
        prior_parsed = row.parsed_value

        # If we have numeric values, compute delta
        if new_parsed is not None and prior_parsed is not None and prior_parsed != 0:
            delta_pct = abs((new_parsed - float(prior_parsed)) / float(prior_parsed)) * 100

            anomaly_threshold, auto_accept_threshold = _get_threshold(field_name)

            # Special case: value went to zero (likely scraper error)
            if new_parsed == 0 and float(prior_parsed) > 0:
                logger.warning(
                    f"Value dropped to 0 for {program_id}/{field_name} "
                    f"(was {prior_parsed}). Auto-flagging."
                )
                return True, 100.0, prior_raw

            # Auto-accept small changes (no human review needed)
            if delta_pct <= auto_accept_threshold:
                return False, delta_pct, prior_raw

            # Flag large changes
            if delta_pct > anomaly_threshold:
                return True, delta_pct, prior_raw

            return False, delta_pct, prior_raw

        # Non-numeric or missing parsed value — always accept string changes
        if new_value == prior_raw:
            return False, 0.0, prior_raw

        return False, 0.0, prior_raw

    async def log_anomaly(
        self,
        program_id: str,
        field_name: str,
        prior_value: Optional[str],
        new_value: str,
        delta_pct: float,
    ):
        """
        Insert anomaly record. The new data_point is also inserted
        but with is_current=FALSE — it waits for admin approval.
        """
        # Determine if auto-acceptable (small delta but above noise floor)
        _, auto_accept_threshold = _get_threshold(field_name)
        auto_accepted = delta_pct <= auto_accept_threshold

        status = "auto_accepted" if auto_accepted else "pending"

        await self.db.execute(text("""
            INSERT INTO anomalies
                (program_id, scrape_run_id, field_name, prior_value, new_value, delta_pct, status, auto_accepted)
            VALUES (:pid, :run_id, :field, :prior, :new, :delta, :status, :auto)
            ON CONFLICT DO NOTHING
        """), {
            "pid": program_id,
            "run_id": self.run_id,
            "field": field_name,
            "prior": prior_value,
            "new": new_value,
            "delta": delta_pct,
            "status": status,
            "auto": auto_accepted,
        })

        # Insert the pending data_point (not current yet)
        await self.db.execute(text("""
            INSERT INTO data_points
                (program_id, scrape_run_id, field_name, raw_value, parsed_value, unit, source_url, is_current)
            VALUES (:pid, :run_id, :field, :raw, NULL, 'PENDING', '', FALSE)
        """), {
            "pid": program_id,
            "run_id": self.run_id,
            "field": field_name,
            "raw": new_value,
        })

        await self.db.commit()

        if auto_accepted:
            logger.info(
                f"[Anomaly] Auto-accepted small delta: {program_id}/{field_name} "
                f"Δ{delta_pct:.1f}% (< {auto_accept_threshold}%)"
            )
        else:
            logger.warning(
                f"[Anomaly] Flagged for review: {program_id}/{field_name} "
                f"Δ{delta_pct:.1f}% ({prior_value} → {new_value})"
            )

    async def get_pending_count(self) -> int:
        """Return count of pending anomalies for dashboard."""
        result = await self.db.execute(
            text("SELECT COUNT(*) FROM anomalies WHERE status = 'pending'")
        )
        return result.scalar() or 0

    async def auto_resolve_stale(self, days: int = 7):
        """
        Auto-accept anomalies that have been pending > N days
        without human review (timeout acceptance).
        Only applies to anomalies with delta < 40%.
        """
        await self.db.execute(text("""
            UPDATE anomalies
            SET status = 'auto_accepted', reviewed_at = NOW(),
                review_notes = 'Auto-resolved: pending > :days days with delta < 40%'
            WHERE status = 'pending'
                AND created_at < NOW() - INTERVAL ':days days'
                AND ABS(delta_pct) < 40
        """), {"days": days})
        await self.db.commit()
