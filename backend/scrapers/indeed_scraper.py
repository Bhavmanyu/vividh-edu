"""
Indeed Scraper — Scrapes Indeed India for job volumes and median salary for roles.
"""
import argparse
import asyncio
import logging
import re
from typing import List
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

from .base_scraper import BaseScraper, ScrapeResult

logger = logging.getLogger(__name__)

SEARCH_TARGETS = [
    ("Software Engineer", ["Bangalore", "Hyderabad", "Pune", "Chennai", "Delhi"]),
    ("Data Scientist", ["Bangalore", "Mumbai", "Delhi"]),
    ("Mechanical Engineer", ["Pune", "Chennai", "Ahmedabad"]),
    ("Doctor", ["Delhi", "Mumbai", "Bangalore"]),
    ("CA", ["Mumbai", "Delhi", "Bangalore"]),
    ("Lawyer", ["Delhi", "Mumbai"])
]

class IndeedScraper(BaseScraper):
    SOURCE_NAME = "indeed"
    BASE_URL = "https://in.indeed.com/jobs"
    REQUEST_DELAY = 2.0

    def __init__(self, db, run_id: str, settings=None, dry_run: bool = False):
        super().__init__(db, run_id, settings)
        self.dry_run = dry_run

    async def scrape(self) -> List[ScrapeResult]:
        results = []
        for role, cities in SEARCH_TARGETS:
            for city in cities:
                for page in range(5):
                    url = f"{self.BASE_URL}?q={quote_plus(role)}&l={quote_plus(city)}&start={page*10}"
                    logger.info(f"Scraping Indeed: {role} in {city} (Page {page})")
                    try:
                        resp = await self.get(url)
                        soup = BeautifulSoup(resp.text, 'html.parser')
                        
                        # Just getting the results from first page to determine volume
                        if page == 0:
                            count_elem = soup.find("div", class_="jobsearch-JobCountAndSortPane-jobCount")
                            if count_elem:
                                count_text = count_elem.get_text(strip=True)
                                match = re.search(r'(\d[,0-9]*)', count_text)
                                if match:
                                    volume = float(match.group(1).replace(',', ''))
                                    results.append(ScrapeResult(
                                        program_id=role.lower().replace(' ', '_'),
                                        field_name="indeed_job_volume",
                                        raw_value=str(volume),
                                        parsed_value=volume,
                                        unit="count",
                                        source_url=url,
                                        metadata={"city": city}
                                    ))

                        salary_snippets = soup.find_all("div", class_="salary-snippet")
                        salaries = []
                        for snippet in salary_snippets:
                            text = snippet.get_text(strip=True)
                            # extremely basic salary extraction
                            matches = re.findall(r'₹([\d,]+)', text)
                            if matches:
                                salaries.extend([float(m.replace(',', '')) for m in matches])
                        
                        if salaries:
                            salaries.sort()
                            median_salary = salaries[len(salaries)//2]
                            results.append(ScrapeResult(
                                program_id=role.lower().replace(' ', '_'),
                                field_name="indeed_median_salary_listed",
                                raw_value=str(median_salary),
                                parsed_value=median_salary,
                                unit="INR",
                                source_url=url,
                                metadata={"city": city}
                            ))
                            
                    except Exception as e:
                        logger.error(f"Error parsing Indeed {role} in {city}: {e}")
                        
        return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    
    async def main():
        logging.basicConfig(level=logging.INFO)
        scraper = IndeedScraper(db=None, run_id="manual", dry_run=args.dry_run)
        async with scraper:
            res = await scraper.scrape()
            if args.dry_run:
                print(res)
    
    asyncio.run(main())
