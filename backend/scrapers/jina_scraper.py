"""
Jina AI Reader Scraper — 100% free, no API key required.

Jina Reader (r.jina.ai) converts any webpage to clean markdown.
Just prepend https://r.jina.ai/ to any URL.
Rate limit: ~20 req/min on free tier.

Usage:
    python -m scrapers.jina_scraper --dry-run
"""
import asyncio
import re
import logging
from typing import Optional, List
from .base_scraper import BaseScraper, ScrapeResult

logger = logging.getLogger(__name__)

JINA_BASE = "https://r.jina.ai/"

INDIA_SALARY_TARGETS = [
    {
        "url": "https://www.payscale.com/research/IN/Job=Software_Engineer/Salary",
        "field": "engineering-cs",
        "role": "Software Engineer",
    },
    {
        "url": "https://www.payscale.com/research/IN/Job=Data_Scientist/Salary",
        "field": "engineering-cs", 
        "role": "Data Scientist",
    },
    {
        "url": "https://www.payscale.com/research/IN/Job=Mechanical_Engineer/Salary",
        "field": "engineering-non-cs",
        "role": "Mechanical Engineer",
    },
    {
        "url": "https://www.payscale.com/research/IN/Job=Civil_Engineer/Salary",
        "field": "engineering-non-cs",
        "role": "Civil Engineer",
    },
    {
        "url": "https://www.payscale.com/research/IN/Job=Doctor/Salary",
        "field": "medicine",
        "role": "Doctor",
    },
    {
        "url": "https://www.payscale.com/research/IN/Job=Lawyer/Salary",
        "field": "law",
        "role": "Lawyer",
    },
    {
        "url": "https://www.payscale.com/research/IN/Job=Chartered_Accountant_(CA)/Salary",
        "field": "commerce",
        "role": "Chartered Accountant",
    },
    {
        "url": "https://www.payscale.com/research/IN/Job=Marketing_Manager/Salary",
        "field": "management",
        "role": "Marketing Manager",
    },
    {
        "url": "https://www.ambitionbox.com/salaries/software-engineer-salaries",
        "field": "engineering-cs",
        "role": "Software Engineer (AmbitionBox)",
    },
    {
        "url": "https://www.ambitionbox.com/salaries/data-analyst-salaries",
        "field": "engineering-cs",
        "role": "Data Analyst (AmbitionBox)",
    },
]


class JinaScraper(BaseScraper):
    SOURCE_NAME = "jina_reader"

    async def fetch_as_markdown(self, url: str) -> Optional[str]:
        jina_url = f"{JINA_BASE}{url}"
        headers = {
            "Accept": "text/markdown",
            "X-Return-Format": "markdown",
        }
        try:
            # use self.get which handles retries and backoff
            response = await self.get(jina_url, headers=headers)
            return response.text
        except Exception as e:
            logger.error(f"Jina fetch error for {url}: {e}")
            return None

    def _extract_inr_salary(self, text: str) -> Optional[int]:
        patterns = [
            (r'₹\s*(\d+\.?\d*)\s*[Ll](?:akh)?', 100000),
            (r'(\d+\.?\d*)\s*LPA', 100000),
            (r'₹\s*([\d,]+)', 1),
            (r'(\d+\.?\d*)\s+lakh', 100000),
        ]
        for pattern, multiplier in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value_str = match.group(1).replace(',', '')
                try:
                    value = float(value_str) * multiplier
                    if 50000 <= value <= 100000000:
                        return int(value)
                except ValueError:
                    continue
        return None

    async def scrape(self) -> List[ScrapeResult]:
        results = []
        for target in INDIA_SALARY_TARGETS:
            logger.info(f"[Jina] Fetching: {target['role']} ({target['url']})")
            markdown = await self.fetch_as_markdown(target["url"])
            if not markdown:
                logger.warning(f"[Jina] No content for {target['role']}")
                continue

            salary = self._extract_inr_salary(markdown)
            if salary:
                logger.info(f"[Jina] {target['role']}: ₹{salary:,}")
                results.append(ScrapeResult(
                    program_id=None,
                    field_name="jina_median_salary_inr",
                    raw_value=str(salary),
                    parsed_value=float(salary),
                    unit="INR",
                    source_url=target["url"],
                    metadata={
                        "role": target["role"],
                        "degree_field": target["field"],
                        "extracted_from": "markdown",
                    }
                ))
            else:
                logger.warning(f"[Jina] Could not extract salary for {target['role']}")

        logger.info(f"[Jina] Done: {len(results)} salary data points extracted")
        return results


if __name__ == "__main__":
    import argparse
    import uuid
    import os
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--url", help="Test a specific URL")
    args = parser.parse_args()

    async def main():
        db_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
        engine = create_async_engine(db_url)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as db:
            run_id = str(uuid.uuid4())
            scraper = JinaScraper(db=db, run_id=run_id)
            async with scraper:
                if args.url:
                    md = await scraper.fetch_as_markdown(args.url)
                    print(md[:2000] if md else "No content")
                    return
                
                results = await scraper.scrape()
                for r in results:
                    print(f"  {r.field_name}: {r.parsed_value:,.0f} {r.unit} — {r.metadata.get('role')} ({r.metadata.get('degree_field')})")
                
                if not args.dry_run:
                    # In real usage, anomaly detector might need a DB schema to be set up.
                    # We attempt persist_results here.
                    try:
                        await scraper.persist_results(results)
                        print(f"Saved {len(results)} results to DB")
                    except Exception as e:
                        print(f"Failed to save to DB: {e}")

    asyncio.run(main())
