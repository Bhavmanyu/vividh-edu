"""
NIRF Scraper — National Institutional Ranking Framework
Sources:
  - Wikipedia NIRF tables
  - Hardcoded Top 50 Engineering (fallback)

Data extracted per institution:
  - nirf_rank
  - nirf_category
"""
import re
import logging
from typing import List, Optional
import argparse
import asyncio

from .base_scraper import BaseScraper, ScrapeResult

logger = logging.getLogger(__name__)

# Mapping of NIRF institution names → our college short names
NIRF_NAME_MAP = {
    "Indian Institute of Technology Bombay": "IIT Bombay",
    "IIT Bombay": "IIT Bombay",
    "Indian Institute of Technology Delhi": "IIT Delhi",
    "IIT Delhi": "IIT Delhi",
    "Indian Institute of Technology Madras": "IIT Madras",
    "IIT Madras": "IIT Madras",
    "Indian Institute of Technology Kanpur": "IIT Kanpur",
    "IIT Kanpur": "IIT Kanpur",
    "Indian Institute of Technology Kharagpur": "IIT Kharagpur",
    "IIT Kharagpur": "IIT Kharagpur",
    "Indian Institute of Technology Roorkee": "IIT Roorkee",
    "IIT Roorkee": "IIT Roorkee",
    "Indian Institute of Technology Guwahati": "IIT Guwahati",
    "IIT Guwahati": "IIT Guwahati",
    "Indian Institute of Technology Hyderabad": "IIT Hyderabad",
    "IIT Hyderabad": "IIT Hyderabad",
    "Indian Institute of Technology (BHU)": "IIT (BHU)",
    "IIT (BHU)": "IIT (BHU)",
    "Birla Institute of Technology and Science": "BITS Pilani",
    "National Institute of Technology Trichy": "NIT Trichy",
    "NIT Trichy": "NIT Trichy",
    "Jadavpur University": "Jadavpur University",
    "MANIPAL Academy of Higher Education": "Manipal",
    "Indian Institute of Technology (ISM) Dhanbad": "IIT ISM Dhanbad",
    "Indian School of Mines": "IIT ISM Dhanbad",
    "Vellore Institute of Technology": "VIT Vellore",
    "SRM Institute of Science and Technology": "SRM Chennai",
    "Amity University": "Amity University",
    "Christ University": "Christ University",
    "Symbiosis International University": "Symbiosis Pune",
    "The University of Delhi": "Delhi University",
    "University of Hyderabad": "University of Hyderabad",
}

FALLBACK_NIRF_2024 = [
    {"rank": 1, "name": "IIT Madras", "category": "engineering"},
    {"rank": 2, "name": "IIT Delhi", "category": "engineering"},
    {"rank": 3, "name": "IIT Bombay", "category": "engineering"},
    {"rank": 4, "name": "IIT Kanpur", "category": "engineering"},
    {"rank": 5, "name": "IIT Kharagpur", "category": "engineering"},
    {"rank": 6, "name": "IIT Roorkee", "category": "engineering"},
    {"rank": 7, "name": "IIT Guwahati", "category": "engineering"},
    {"rank": 8, "name": "IIT Hyderabad", "category": "engineering"},
    {"rank": 9, "name": "NIT Trichy", "category": "engineering"},
    {"rank": 10, "name": "Jadavpur University", "category": "engineering"},
    {"rank": 11, "name": "Vellore Institute of Technology", "category": "engineering"},
    {"rank": 12, "name": "NIT Surathkal", "category": "engineering"},
    {"rank": 13, "name": "Anna University", "category": "engineering"},
    {"rank": 14, "name": "IIT Indore", "category": "engineering"},
    {"rank": 15, "name": "IIT BHU", "category": "engineering"},
    {"rank": 16, "name": "NIT Rourkela", "category": "engineering"},
    {"rank": 17, "name": "IIT ISM Dhanbad", "category": "engineering"},
    {"rank": 18, "name": "IIT Gandhinagar", "category": "engineering"},
    {"rank": 19, "name": "Amrita Vishwa Vidyapeetham", "category": "engineering"},
    {"rank": 20, "name": "Thapar Institute of Engineering & Technology", "category": "engineering"},
]

class NIRFScraper(BaseScraper):
    SOURCE_NAME = "nirf"
    WIKI_URL = "https://en.wikipedia.org/wiki/National_Institutional_Ranking_Framework"

    def _fuzzy_match(self, nirf_name: str) -> str:
        # We don't have DB in dry-run necessarily, so we just return the mapped string or original
        our_name = NIRF_NAME_MAP.get(nirf_name)
        if our_name:
            return our_name

        nirf_lower = nirf_name.lower()
        for k, v in NIRF_NAME_MAP.items():
            if k.lower() in nirf_lower or nirf_lower in k.lower():
                return v

        return nirf_name

    def _parse_wikipedia(self, html: str) -> List[dict]:
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")
            tables = soup.find_all('table', {'class': 'wikitable'})
            rows = []
            
            categories_map = {
                'Engineering (Top 10)': 'engineering',
                'Management (Top 10)': 'management',
                'Medical (Top 10)': 'medical',
                'Law (Top 10)': 'law'
            }

            for t in tables:
                prev = t.find_previous(['h2', 'h3', 'h4'])
                if not prev:
                    continue
                heading = prev.text.strip()
                if heading in categories_map:
                    category = categories_map[heading]
                    for tr in t.find_all('tr')[1:]:
                        tds = tr.find_all(['td', 'th'])
                        if len(tds) >= 4:
                            try:
                                rank = int(tds[0].text.strip())
                                name = tds[1].text.strip()
                                rows.append({
                                    "rank": rank,
                                    "name": name,
                                    "category": category
                                })
                            except ValueError:
                                continue
            return rows
        except Exception as e:
            logger.error(f"[NIRF] Wikipedia parse error: {e}")
            return []

    async def scrape(self) -> List[ScrapeResult]:
        results: List[ScrapeResult] = []
        
        logger.info(f"[NIRF] Scraping Wikipedia: {self.WIKI_URL}")
        try:
            response = await self.get(self.WIKI_URL)
            rows = self._parse_wikipedia(response.text)
            
            if not rows:
                logger.warning("[NIRF] Wikipedia scrape yielded no results, using fallback")
                rows = FALLBACK_NIRF_2024
        except Exception as e:
            logger.error(f"[NIRF] Failed to fetch/parse wikipedia: {e}")
            rows = FALLBACK_NIRF_2024

        for row in rows:
            mapped_name = self._fuzzy_match(row["name"])
            
            results.append(ScrapeResult(
                program_id=None,
                field_name="nirf_rank",
                raw_value=str(row["rank"]),
                parsed_value=float(row["rank"]),
                unit="RANK",
                source_url=self.WIKI_URL,
                metadata={"college_name": mapped_name, "category": row["category"]},
            ))
            results.append(ScrapeResult(
                program_id=None,
                field_name="nirf_category",
                raw_value=row["category"],
                parsed_value=None,
                unit="CATEGORY",
                source_url=self.WIKI_URL,
                metadata={"college_name": mapped_name, "category": row["category"]},
            ))

        logger.info(f"[NIRF] Total results extracted: {len(results)}")
        return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='Print output instead of DB write')
    args = parser.parse_args()

    async def main():
        scraper = NIRFScraper(db=None, run_id="dry-run")
        async with scraper:
            results = await scraper.scrape()
            if args.dry_run:
                import json
                for r in results:
                    print(json.dumps(r.__dict__))

    asyncio.run(main())
