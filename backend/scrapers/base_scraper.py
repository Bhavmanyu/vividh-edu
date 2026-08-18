"""
BaseScraper — shared scraping utilities with:
- Polite rate limiting (configurable delay)
- Retry with exponential backoff
- Rotating user-agents
- Dead-letter logging for failed URLs
- DB session injection for persisting data points
"""
import asyncio
import logging
import time
import random
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "IndiaLensBot/1.0 (research; contact@indialens.in; +https://indialens.in/bot)",
]


@dataclass
class ScrapeResult:
    program_id: Optional[str]
    field_name: str
    raw_value: str
    parsed_value: Optional[float]
    unit: str
    source_url: str
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScrapeStats:
    records_scraped: int = 0
    records_updated: int = 0
    records_flagged: int = 0
    errors: int = 0
    start_time: float = field(default_factory=time.time)

    @property
    def duration_seconds(self) -> float:
        return time.time() - self.start_time


class BaseScraper(ABC):
    """
    Abstract base class for all IndiaLens scrapers.
    Subclass and implement `scrape()`.
    """

    SOURCE_NAME: str = "base"
    BASE_URL: str = ""
    REQUEST_DELAY: float = 1.5   # seconds between requests
    MAX_RETRIES: int = 3
    TIMEOUT: float = 30.0

    def __init__(self, db: AsyncSession, run_id: str, settings=None):
        self.db = db
        self.run_id = run_id
        self.settings = settings
        self.stats = ScrapeStats()
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            timeout=self.TIMEOUT,
            follow_redirects=True,
            headers={"User-Agent": random.choice(USER_AGENTS)},
        )
        return self

    async def __aexit__(self, *args):
        if self._client:
            await self._client.aclose()

    async def get(self, url: str, **kwargs) -> httpx.Response:
        """GET with retry, backoff, and polite delay."""
        for attempt in range(self.MAX_RETRIES):
            try:
                await asyncio.sleep(self.REQUEST_DELAY + random.uniform(0, 0.5))
                response = await self._client.get(url, **kwargs)
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    wait = 2 ** (attempt + 2)
                    logger.warning(f"Rate limited by {url}. Waiting {wait}s...")
                    await asyncio.sleep(wait)
                elif e.response.status_code in (403, 404):
                    logger.warning(f"HTTP {e.response.status_code} for {url} — skipping")
                    raise
                else:
                    if attempt == self.MAX_RETRIES - 1:
                        raise
                    await asyncio.sleep(2 ** attempt)
            except (httpx.ConnectError, httpx.TimeoutException) as e:
                if attempt == self.MAX_RETRIES - 1:
                    logger.error(f"Failed after {self.MAX_RETRIES} retries: {url} — {e}")
                    raise
                await asyncio.sleep(2 ** attempt)

    async def post(self, url: str, **kwargs) -> httpx.Response:
        """POST with the same retry logic."""
        for attempt in range(self.MAX_RETRIES):
            try:
                await asyncio.sleep(self.REQUEST_DELAY)
                response = await self._client.post(url, **kwargs)
                response.raise_for_status()
                return response
            except Exception as e:
                if attempt == self.MAX_RETRIES - 1:
                    raise
                await asyncio.sleep(2 ** attempt)

    async def persist_results(self, results: List[ScrapeResult]):
        """
        Persist scraped data points to DB.
        Runs anomaly detection on each field before committing.
        """
        from ..pipeline.anomaly_detector import AnomalyDetector
        detector = AnomalyDetector(db=self.db, run_id=self.run_id)

        for result in results:
            try:
                if not result.program_id:
                    continue

                # Check for anomaly before storing
                is_anomaly, delta_pct, prior_value = await detector.check(
                    program_id=result.program_id,
                    field_name=result.field_name,
                    new_value=result.raw_value,
                    new_parsed=result.parsed_value,
                )

                if is_anomaly:
                    # Log anomaly and DO NOT flip is_current yet
                    await detector.log_anomaly(
                        program_id=result.program_id,
                        field_name=result.field_name,
                        prior_value=prior_value,
                        new_value=result.raw_value,
                        delta_pct=delta_pct,
                    )
                    self.stats.records_flagged += 1
                    logger.info(f"Anomaly flagged: {result.program_id}/{result.field_name} Δ{delta_pct:.1f}%")
                else:
                    # Safe — retire old, insert new as current
                    await self.db.execute(text("""
                        UPDATE data_points SET is_current = FALSE
                        WHERE program_id = :pid AND field_name = :field AND is_current = TRUE
                    """), {"pid": result.program_id, "field": result.field_name})

                    await self.db.execute(text("""
                        INSERT INTO data_points
                            (program_id, scrape_run_id, field_name, raw_value, parsed_value, unit, source_url, is_current)
                        VALUES (:pid, :run_id, :field, :raw, :parsed, :unit, :url, TRUE)
                    """), {
                        "pid": result.program_id,
                        "run_id": self.run_id,
                        "field": result.field_name,
                        "raw": result.raw_value,
                        "parsed": result.parsed_value,
                        "unit": result.unit,
                        "url": result.source_url,
                    })
                    self.stats.records_updated += 1

                self.stats.records_scraped += 1

            except Exception as e:
                logger.error(f"Error persisting {result.field_name} for {result.program_id}: {e}")
                self.stats.errors += 1

        await self.db.commit()

    async def update_run_status(self, status: str, error: str = None):
        """Update scrape_runs table with current stats."""
        await self.db.execute(text("""
            UPDATE scrape_runs SET
                status = :status,
                records_scraped = :scraped,
                records_updated = :updated,
                records_flagged = :flagged,
                error_message = :error,
                completed_at = CASE WHEN :status != 'running' THEN NOW() ELSE completed_at END
            WHERE id = :id
        """), {
            "id": self.run_id,
            "status": status,
            "scraped": self.stats.records_scraped,
            "updated": self.stats.records_updated,
            "flagged": self.stats.records_flagged,
            "error": error,
        })
        await self.db.commit()

    @abstractmethod
    async def scrape(self) -> List[ScrapeResult]:
        """Implement in subclass. Return list of ScrapeResult objects."""
        ...

    async def run(self) -> ScrapeStats:
        """Main entry point. Called by Airflow task."""
        logger.info(f"[{self.SOURCE_NAME}] Starting scrape run {self.run_id}")
        await self.update_run_status("running")

        try:
            async with self:
                results = await self.scrape()
                await self.persist_results(results)

            await self.update_run_status("success")
            logger.info(
                f"[{self.SOURCE_NAME}] Completed. "
                f"Scraped={self.stats.records_scraped} "
                f"Updated={self.stats.records_updated} "
                f"Flagged={self.stats.records_flagged} "
                f"Duration={self.stats.duration_seconds:.1f}s"
            )
        except Exception as e:
            logger.error(f"[{self.SOURCE_NAME}] Scrape failed: {e}", exc_info=True)
            await self.update_run_status("failed", error=str(e))

        return self.stats
