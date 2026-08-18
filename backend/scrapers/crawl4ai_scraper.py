"""
Crawl4AI Scraper — Free, open-source, handles JavaScript-rendered pages.
"""
import asyncio
import re
import logging
import os
from typing import Optional, List
from .base_scraper import BaseScraper, ScrapeResult

logger = logging.getLogger(__name__)

AMBITIONBOX_TARGETS = [
    {
        "url": "https://www.ambitionbox.com/salaries/software-engineer-salaries",
        "role": "Software Engineer",
        "field": "engineering-cs",
    },
    {
        "url": "https://www.ambitionbox.com/salaries/data-analyst-salaries",
        "role": "Data Analyst",
        "field": "engineering-cs",
    },
    {
        "url": "https://www.ambitionbox.com/salaries/data-scientist-salaries",
        "role": "Data Scientist",
        "field": "engineering-cs",
    },
    {
        "url": "https://www.ambitionbox.com/salaries/business-analyst-salaries",
        "role": "Business Analyst",
        "field": "management",
    },
    {
        "url": "https://www.ambitionbox.com/salaries/mechanical-engineer-salaries",
        "role": "Mechanical Engineer",
        "field": "engineering-non-cs",
    },
]

NAUKRI_TARGETS = [
    {
        "url": "https://www.naukri.com/software-engineer-jobs",
        "role": "Software Engineer",
        "field": "engineering-cs",
    },
    {
        "url": "https://www.naukri.com/data-scientist-jobs",
        "role": "Data Scientist",
        "field": "engineering-cs",
    },
]


class Crawl4AIScraper(BaseScraper):
    SOURCE_NAME = "crawl4ai"

    def __init__(self, db, run_id, settings=None):
        super().__init__(db, run_id, settings)
        self._available = self._check_availability()

    def _check_availability(self) -> bool:
        try:
            import crawl4ai  # noqa
            return True
        except ImportError:
            logger.warning("crawl4ai not installed. Run: pip install crawl4ai && crawl4ai-setup")
            return False

    async def crawl_url(self, url: str) -> Optional[str]:
        if not self._available:
            logger.info(f"[Crawl4AI] Falling back to Jina Reader for {url}")
            try:
                r = await self.get(f"https://r.jina.ai/{url}", headers={"Accept": "text/markdown"})
                return r.text
            except Exception as e:
                logger.error(f"Jina fallback failed: {e}")
                return None
        
        try:
            from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
            
            config = CrawlerRunConfig(
                word_count_threshold=10,
                remove_overlay_elements=True,
                process_iframes=False,
                wait_for="body",
                page_timeout=20000,
                magic=True,
            )
            
            async with AsyncWebCrawler(verbose=False) as crawler:
                result = await crawler.arun(url=url, config=config)
                if result.success:
                    return result.markdown
                logger.warning(f"[Crawl4AI] Failed to crawl {url}: {result.error_message}")
                return None
        except Exception as e:
            logger.error(f"[Crawl4AI] Error crawling {url}: {e}")
            return None

    def _extract_salary(self, text: str, role: str) -> Optional[float]:
        patterns = [
            (r'₹\s*(\d+(?:\.\d+)?)\s*(?:L|lakh|LPA)', 100000),
            (r'(\d+(?:\.\d+)?)\s*LPA', 100000),
            (r'(\d+(?:\.\d+)?)\s+lakh', 100000),
            (r'(\d+(?:\.\d+)?)\s*(?:lakhs|Lakhs)', 100000),
        ]
        salaries = []
        for pattern, multiplier in patterns:
            for match in re.finditer(pattern, text[:5000], re.IGNORECASE):
                try:
                    val = float(match.group(1)) * multiplier
                    if 100000 <= val <= 50000000:
                        salaries.append(val)
                except ValueError:
                    pass
        if salaries:
            salaries.sort()
            return salaries[len(salaries)//2]
        return None

    async def scrape(self) -> List[ScrapeResult]:
        results = []
        all_targets = AMBITIONBOX_TARGETS + NAUKRI_TARGETS
        
        for target in all_targets:
            logger.info(f"[Crawl4AI] Scraping: {target['role']} — {target['url']}")
            markdown = await self.crawl_url(target["url"])
            
            if not markdown:
                logger.warning(f"[Crawl4AI] No content for {target['role']}")
                continue
            
            salary = self._extract_salary(markdown, target["role"])
            if salary:
                logger.info(f"[Crawl4AI] {target['role']}: ₹{salary:,.0f}")
                results.append(ScrapeResult(
                    program_id=None,
                    field_name="crawl4ai_median_salary_inr",
                    raw_value=str(salary),
                    parsed_value=float(salary),
                    unit="INR",
                    source_url=target["url"],
                    metadata={
                        "role": target["role"],
                        "degree_field": target["field"],
                        "method": "crawl4ai" if self._available else "jina_fallback",
                    }
                ))
            
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
    parser.add_argument("--url", help="Test crawl a specific URL")
    args = parser.parse_args()

    async def main():
        db_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
        engine = create_async_engine(db_url)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as db:
            run_id = str(uuid.uuid4())
            scraper = Crawl4AIScraper(db=db, run_id=run_id)
            async with scraper:
                if args.url:
                    md = await scraper.crawl_url(args.url)
                    print(md[:3000] if md else "No content")
                    return
                results = await scraper.scrape()
                for r in results:
                    print(f"  {r.field_name}: ₹{r.parsed_value:,.0f} — {r.metadata.get('role')} ({r.metadata.get('degree_field')})")
                if not args.dry_run:
                    try:
                        await scraper.persist_results(results)
                    except Exception as e:
                        print(f"Failed to save to DB: {e}")
    
    asyncio.run(main())
