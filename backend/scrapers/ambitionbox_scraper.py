"""
AmbitionBox Scraper — salary and workplace data
Sources:
  - https://www.ambitionbox.com/salaries/{company}
  - Search API: https://www.ambitionbox.com/api/v2/salaries?profile={role}&exp={years}

Data extracted:
  - Salary ranges by role and experience (p25, p50, p75)
  - Work-life balance score
  - Job security score
  - Company culture score

Rate limit: 1 request / 2s to avoid detection.
Requires: httpx, BeautifulSoup, fake_useragent (optional)
"""
import re
import logging
from typing import List, Optional, Dict
import json

from .base_scraper import BaseScraper, ScrapeResult

logger = logging.getLogger(__name__)

# Role → DegreeField mapping
ROLE_TO_FIELD: Dict[str, str] = {
    "Software Engineer": "engineering-cs",
    "Software Developer": "engineering-cs",
    "Data Scientist": "engineering-cs",
    "ML Engineer": "engineering-cs",
    "Product Manager": "management",
    "Business Analyst": "management",
    "Chartered Accountant": "commerce",
    "Financial Analyst": "commerce",
    "Mechanical Engineer": "engineering-non-cs",
    "Civil Engineer": "engineering-non-cs",
    "MBBS Doctor": "medicine",
    "Medical Officer": "medicine",
    "Lawyer": "law",
    "Associate": "law",
    "UX Designer": "design",
    "Graphic Designer": "design",
}

# Roles to scrape by experience bucket
SCRAPE_TARGETS = [
    {"role": "Software Engineer", "exp_min": 0, "exp_max": 2},
    {"role": "Software Engineer", "exp_min": 3, "exp_max": 5},
    {"role": "Software Engineer", "exp_min": 6, "exp_max": 10},
    {"role": "Software Engineer", "exp_min": 11, "exp_max": 20},
    {"role": "Data Scientist", "exp_min": 0, "exp_max": 3},
    {"role": "Data Scientist", "exp_min": 4, "exp_max": 10},
    {"role": "Product Manager", "exp_min": 0, "exp_max": 5},
    {"role": "Product Manager", "exp_min": 5, "exp_max": 15},
    {"role": "Mechanical Engineer", "exp_min": 0, "exp_max": 5},
    {"role": "Mechanical Engineer", "exp_min": 5, "exp_max": 15},
    {"role": "Chartered Accountant", "exp_min": 0, "exp_max": 5},
    {"role": "Chartered Accountant", "exp_min": 5, "exp_max": 15},
    {"role": "MBBS Doctor", "exp_min": 0, "exp_max": 5},
    {"role": "MBBS Doctor", "exp_min": 5, "exp_max": 15},
    {"role": "Lawyer", "exp_min": 0, "exp_max": 5},
    {"role": "UX Designer", "exp_min": 0, "exp_max": 5},
    {"role": "Business Analyst", "exp_min": 0, "exp_max": 5},
]

AB_SALARY_API = "https://www.ambitionbox.com/api/v2/salaries"
AB_REVIEW_API = "https://www.ambitionbox.com/api/v1/companies/{company_slug}/reviews/summary"


class AmbitionBoxScraper(BaseScraper):
    """
    Scrapes salary and satisfaction data from AmbitionBox.

    Strategy:
    1. Use the semi-public salary search API with role + experience filters
    2. Parse percentile salary data (min/median/max → p25/p50/p75 approximation)
    3. Map role → degree field for program association
    4. Store at aggregate level (field × experience → salary band)
    """

    SOURCE_NAME = "ambitionbox"
    REQUEST_DELAY = 2.5   # AmbitionBox is strict about rate limits

    def _parse_salary_inr(self, s: str) -> Optional[int]:
        """Parse '₹12.5L' or '12,50,000' → integer INR."""
        if not s:
            return None
        s = s.replace("₹", "").replace(",", "").strip()
        if "L" in s.upper():
            return int(float(s.replace("L", "").replace("l", "")) * 100_000)
        if "K" in s.upper():
            return int(float(s.replace("K", "").replace("k", "")) * 1_000)
        try:
            return int(float(s))
        except ValueError:
            return None

    async def _fetch_salary_data(self, role: str, exp_min: int, exp_max: int) -> Optional[dict]:
        """
        Fetch salary range data from AmbitionBox search API.
        Returns dict with min_salary, median_salary, max_salary, sample_size.
        """
        try:
            params = {
                "profile": role,
                "expMin": exp_min,
                "expMax": exp_max,
                "city": "",
                "limit": 20,
            }
            headers = {
                "Accept": "application/json",
                "Referer": "https://www.ambitionbox.com/salaries",
                "X-Requested-With": "XMLHttpRequest",
            }
            resp = await self.get(
                AB_SALARY_API,
                params=params,
                headers=headers,
            )
            data = resp.json()

            # AmbitionBox returns structured salary object
            if not data.get("data"):
                return None

            salary_info = data["data"]
            return {
                "min_salary_inr": self._parse_salary_inr(salary_info.get("minSalary")),
                "median_salary_inr": self._parse_salary_inr(salary_info.get("medianSalary")),
                "max_salary_inr": self._parse_salary_inr(salary_info.get("maxSalary")),
                "sample_size": salary_info.get("sampleSize", 0),
                "role": role,
                "exp_min": exp_min,
                "exp_max": exp_max,
            }
        except Exception as e:
            logger.warning(f"[AmbitionBox] Failed for {role} ({exp_min}-{exp_max} yrs): {e}")
            return None

    async def scrape(self) -> List[ScrapeResult]:
        results: List[ScrapeResult] = []

        for target in SCRAPE_TARGETS:
            role = target["role"]
            exp_min = target["exp_min"]
            exp_max = target["exp_max"]

            logger.info(f"[AmbitionBox] Scraping: {role} ({exp_min}-{exp_max} yrs)")
            data = await self._fetch_salary_data(role, exp_min, exp_max)

            if not data:
                continue

            degree_field = ROLE_TO_FIELD.get(role, "engineering-cs")
            field_key = f"salary_{degree_field}_y{exp_min}_{exp_max}"

            # Store median salary as a field-level aggregate (not program-specific yet)
            # Program-specific association happens in the ML pipeline (Week 3)
            if data.get("median_salary_inr"):
                results.append(ScrapeResult(
                    program_id=None,  # aggregate — matched to programs in ML step
                    field_name=f"ambitionbox_median_salary",
                    raw_value=str(data["median_salary_inr"]),
                    parsed_value=float(data["median_salary_inr"]),
                    unit="INR",
                    source_url=f"{AB_SALARY_API}?profile={role}&exp={exp_min}-{exp_max}",
                    confidence=min(1.0, data["sample_size"] / 100),
                    metadata={
                        "role": role,
                        "degree_field": degree_field,
                        "exp_min": exp_min,
                        "exp_max": exp_max,
                        "sample_size": data["sample_size"],
                        "min_salary_inr": data.get("min_salary_inr"),
                        "max_salary_inr": data.get("max_salary_inr"),
                    },
                ))

        logger.info(f"[AmbitionBox] Extracted {len(results)} salary data points")
        return results
