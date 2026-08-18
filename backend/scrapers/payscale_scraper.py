"""
PayScale Scraper — Salary data for various roles in India.
"""
import re
import json
import logging
import asyncio
import argparse
from typing import List

from .base_scraper import BaseScraper, ScrapeResult

logger = logging.getLogger(__name__)

ROLE_MAP = {
    'Software_Engineer': 'engineering-cs',
    'Data_Scientist': 'engineering-cs', 
    'Mechanical_Engineer': 'engineering-non-cs',
    'Civil_Engineer': 'engineering-non-cs',
    'Physician_/_Doctor,_General_Practice': 'medicine',
    'Chartered_Accountant_(CA)': 'commerce',
    'Lawyer': 'law',
    'Marketing_Manager': 'management',
    'UX_Designer': 'design',
    'Business_Analyst': 'management',
}

class PayscaleScraper(BaseScraper):
    SOURCE_NAME = "payscale"
    REQUEST_DELAY = 2.0
    BASE_URL = "https://www.payscale.com/research/IN/Job={}/Salary"

    def _parse_html(self, html: str, role: str, degree_field: str) -> List[ScrapeResult]:
        results = []
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")
            
            median = None
            p25 = None
            p75 = None
            sample_size = None
            
            # Try to parse ld+json
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    data = json.loads(script.string)
                    if data.get('@type') == 'Occupation':
                        # Depending on structure, extract salaries
                        pass
                except Exception:
                    pass
            
            # If ld+json didn't have it, look for text
            # Often median is in paycharts__value
            median_el = soup.find(class_='paycharts__value')
            if median_el:
                median_text = median_el.text.replace('₹', '').replace(',', '').strip()
                try:
                    median = float(median_text)
                except ValueError:
                    pass
                    
            # p25 and p75 in percentile-chart
            p25_el = soup.find('div', class_='percentile-chart__low')
            if p25_el:
                m = re.search(r'₹([\d\.]+)([km]?)', p25_el.text, re.I)
                if m:
                    val = float(m.group(1))
                    if m.group(2).lower() == 'k':
                        val *= 1000
                    elif m.group(2).lower() == 'm':
                        val *= 1000000
                    p25 = val

            p75_el = soup.find('div', class_='percentile-chart__high')
            if p75_el:
                m = re.search(r'₹([\d\.]+)([km]?)', p75_el.text, re.I)
                if m:
                    val = float(m.group(1))
                    if m.group(2).lower() == 'k':
                        val *= 1000
                    elif m.group(2).lower() == 'm':
                        val *= 1000000
                    p75 = val

            url = self.BASE_URL.format(role)
            metadata = {
                "role": role,
                "degree_field": degree_field,
                "sample_size": sample_size,
                "currency": "INR"
            }

            if median is not None:
                results.append(ScrapeResult(
                    program_id=None,
                    field_name="payscale_median_salary_inr",
                    raw_value=str(median),
                    parsed_value=median,
                    unit="INR",
                    source_url=url,
                    metadata=metadata
                ))
            if p25 is not None:
                results.append(ScrapeResult(
                    program_id=None,
                    field_name="payscale_p25_salary_inr",
                    raw_value=str(p25),
                    parsed_value=p25,
                    unit="INR",
                    source_url=url,
                    metadata=metadata
                ))
            if p75 is not None:
                results.append(ScrapeResult(
                    program_id=None,
                    field_name="payscale_p75_salary_inr",
                    raw_value=str(p75),
                    parsed_value=p75,
                    unit="INR",
                    source_url=url,
                    metadata=metadata
                ))

        except Exception as e:
            logger.error(f"[Payscale] Parse error for {role}: {e}")

        return results

    async def scrape(self) -> List[ScrapeResult]:
        all_results = []
        for role, degree_field in ROLE_MAP.items():
            url = self.BASE_URL.format(role)
            logger.info(f"[Payscale] Scraping {role}: {url}")
            try:
                response = await self.get(url)
                res = self._parse_html(response.text, role, degree_field)
                all_results.extend(res)
            except Exception as e:
                logger.error(f"[Payscale] Failed for {role}: {e}")
        
        logger.info(f"[Payscale] Total results extracted: {len(all_results)}")
        return all_results

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='Print output instead of DB write')
    args = parser.parse_args()

    async def main():
        scraper = PayscaleScraper(db=None, run_id="dry-run")
        async with scraper:
            results = await scraper.scrape()
            if args.dry_run:
                import json
                for r in results:
                    print(json.dumps(r.__dict__))

    asyncio.run(main())
