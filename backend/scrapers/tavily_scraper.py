"""
Tavily Search API Scraper — 1,000 FREE searches/month, no credit card.
"""
import asyncio
import os
import logging
import httpx
from typing import List
from .base_scraper import BaseScraper, ScrapeResult

logger = logging.getLogger(__name__)

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
TAVILY_API_URL = "https://api.tavily.com/search"

SEARCH_QUERIES = [
    {
        "query": "IIT Bombay BTech computer science placement 2024 median salary package",
        "field": "engineering-cs",
        "college": "IIT Bombay",
        "data_type": "placement_salary",
    },
    {
        "query": "IIT Delhi BTech placement 2024 highest average median package",
        "field": "engineering-cs", 
        "college": "IIT Delhi",
        "data_type": "placement_salary",
    },
    {
        "query": "IIM Ahmedabad MBA placement 2024 average salary CTC",
        "field": "management",
        "college": "IIM Ahmedabad",
        "data_type": "placement_salary",
    },
    {
        "query": "IIM Bangalore MBA placement 2024 median salary package",
        "field": "management",
        "college": "IIM Bangalore",
        "data_type": "placement_salary",
    },
    {
        "query": "NLSIU Bangalore law placement 2024 salary corporate firms",
        "field": "law",
        "college": "NLSIU Bangalore",
        "data_type": "placement_salary",
    },
    {
        "query": "India software engineer average salary 2024 freshers Bangalore Hyderabad",
        "field": "engineering-cs",
        "college": None,
        "data_type": "market_salary",
    },
    {
        "query": "India MBBS doctor salary 2024 government hospital private practice",
        "field": "medicine",
        "college": None,
        "data_type": "market_salary",
    },
    {
        "query": "India MBA graduate salary 2024 tier 1 tier 2 colleges average",
        "field": "management",
        "college": None,
        "data_type": "market_salary",
    },
    {
        "query": "India mechanical engineer fresher salary 2024 manufacturing auto sector",
        "field": "engineering-non-cs",
        "college": None,
        "data_type": "market_salary",
    },
    {
        "query": "India lawyer fresh graduate salary 2024 law firm corporate",
        "field": "law",
        "college": None,
        "data_type": "market_salary",
    },
    {
        "query": "India salary hike appraisal 2024 IT sector average increment",
        "field": "engineering-cs",
        "college": None,
        "data_type": "salary_growth",
    },
    {
        "query": "India unemployment rate educated graduates 2024 PLFS data",
        "field": "all",
        "college": None,
        "data_type": "unemployment",
    },
]

class TavilyScraper(BaseScraper):
    SOURCE_NAME = "tavily_search"

    def __init__(self, db, run_id, settings=None):
        super().__init__(db, run_id, settings)
        self.api_key = TAVILY_API_KEY

    async def search(self, query: str, max_results: int = 5) -> dict:
        if not self.api_key:
            logger.warning("TAVILY_API_KEY not set — skipping Tavily search")
            return {}
        try:
            # We can use self.post if we want, but BaseScraper.post signature just uses **kwargs.
            response = await self.post(
                TAVILY_API_URL,
                json={
                    "api_key": self.api_key,
                    "query": query,
                    "search_depth": "basic",
                    "max_results": max_results,
                    "include_answer": True,
                    "include_raw_content": False,
                    "topic": "general",
                }
            )
            return response.json()
        except Exception as e:
            logger.error(f"Tavily search error: {e}")
            return {}

    def _parse_salary_from_answer(self, answer: str, query: str) -> dict:
        import re
        result = {"raw_answer": answer, "query": query}
        
        patterns = [
            (r'₹\s*(\d+(?:\.\d+)?)\s*(?:lakh|L|LPA)', 100000, 'lpa'),
            (r'(\d+(?:\.\d+)?)\s*LPA', 100000, 'lpa'),
            (r'(\d+(?:\.\d+)?)\s*lakh', 100000, 'lakh'),
            (r'₹\s*([\d,]+)\s*(?:per annum|annually|/year|pa)', 1, 'absolute'),
            (r'(\d+(?:\.\d+)?)\s*crore', 10000000, 'crore'),
        ]
        
        salary_values = []
        for pattern, multiplier, unit in patterns:
            for match in re.finditer(pattern, answer, re.IGNORECASE):
                try:
                    val = float(match.group(1).replace(',', '')) * multiplier
                    if 100000 <= val <= 50000000:
                        salary_values.append(val)
                except ValueError:
                    pass
        
        if salary_values:
            salary_values.sort()
            result['median_salary'] = salary_values[len(salary_values)//2]
            result['min_salary'] = min(salary_values)
            result['max_salary'] = max(salary_values)
            result['salary_count'] = len(salary_values)
        
        return result

    async def scrape(self) -> List[ScrapeResult]:
        if not self.api_key:
            logger.info("[Tavily] TAVILY_API_KEY not set — get free key at tavily.com")
            return []
        
        results = []
        for query_config in SEARCH_QUERIES:
            query = query_config["query"]
            logger.info(f"[Tavily] Searching: {query[:60]}...")
            
            search_result = await self.search(query)
            if not search_result:
                continue
            
            answer = search_result.get("answer", "")
            sources = [r.get("url", "") for r in search_result.get("results", [])]
            
            if answer:
                parsed = self._parse_salary_from_answer(answer, query)
                
                if parsed.get("median_salary"):
                    field_name = (
                        f"tavily_placement_salary" 
                        if query_config["data_type"] == "placement_salary"
                        else "tavily_market_salary"
                    )
                    results.append(ScrapeResult(
                        program_id=None,
                        field_name=field_name,
                        raw_value=str(parsed["median_salary"]),
                        parsed_value=float(parsed["median_salary"]),
                        unit="INR",
                        source_url=sources[0] if sources else "https://tavily.com",
                        metadata={
                            "query": query,
                            "data_type": query_config["data_type"],
                            "college": query_config.get("college"),
                            "degree_field": query_config["field"],
                            "answer_summary": answer[:500],
                            "sources": sources[:3],
                            "salary_range": {
                                "min": parsed.get("min_salary"),
                                "max": parsed.get("max_salary"),
                            },
                        }
                    ))
                    logger.info(f"[Tavily] Extracted: ₹{parsed['median_salary']:,.0f} for {query_config.get('college', query_config['field'])}")
                else:
                    logger.info(f"[Tavily] No salary found in answer: {answer[:200]}")
            
        logger.info(f"[Tavily] Done: {len(results)} real-time data points")
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
    parser.add_argument("--query", help="Test a specific search query")
    args = parser.parse_args()

    async def main():
        db_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
        engine = create_async_engine(db_url)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as db:
            run_id = str(uuid.uuid4())
            scraper = TavilyScraper(db=db, run_id=run_id)
            async with scraper:
                if args.query:
                    result = await scraper.search(args.query)
                    print(f"Answer: {result.get('answer', 'No answer')}")
                    print(f"Sources: {[r.get('url') for r in result.get('results', [])[:3]]}")
                    return
                results = await scraper.scrape()
                for r in results:
                    col = r.metadata.get('college')
                    field = r.metadata.get('degree_field')
                    print(f"  {r.field_name}: ₹{r.parsed_value:,.0f} — {col or field}")
                if not args.dry_run and results:
                    try:
                        await scraper.persist_results(results)
                        print(f"Saved {len(results)} results to DB")
                    except Exception as e:
                        print(f"Failed to save to DB: {e}")

    asyncio.run(main())
