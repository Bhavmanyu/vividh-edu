"""
Naukri.com Job Postings Scraper
Extracts: job demand by role/city, salary ranges from job descriptions,
          required skills distribution, experience curves.

Uses Naukri's public job search (no auth required for basic listings).
"""
import re
import logging
from typing import List, Optional, Dict, Any
import json
from urllib.parse import urlencode

from .base_scraper import BaseScraper, ScrapeResult

logger = logging.getLogger(__name__)

# Job roles to search — mapped to degree fields
SEARCH_TARGETS = [
    {"keywords": "software engineer developer", "field": "engineering-cs", "exp": "0,2"},
    {"keywords": "software engineer developer", "field": "engineering-cs", "exp": "3,5"},
    {"keywords": "software engineer developer", "field": "engineering-cs", "exp": "6,10"},
    {"keywords": "data scientist machine learning", "field": "engineering-cs", "exp": "0,5"},
    {"keywords": "mechanical engineer manufacturing", "field": "engineering-non-cs", "exp": "0,5"},
    {"keywords": "civil engineer construction", "field": "engineering-non-cs", "exp": "0,5"},
    {"keywords": "doctor physician medical officer", "field": "medicine", "exp": "0,5"},
    {"keywords": "chartered accountant finance", "field": "commerce", "exp": "0,5"},
    {"keywords": "management consultant MBA", "field": "management", "exp": "0,5"},
    {"keywords": "lawyer legal associate", "field": "law", "exp": "0,5"},
    {"keywords": "UX designer product designer", "field": "design", "exp": "0,5"},
]

# Salary regex patterns in job descriptions
SALARY_PATTERNS = [
    r"₹?\s*(\d+(?:\.\d+)?)\s*(?:to|-)\s*(\d+(?:\.\d+)?)\s*(?:L|lakh|lakhs|LPA)",
    r"(\d+(?:\.\d+)?)\s*(?:L|lakh|lakhs|LPA)\s*(?:to|-)\s*(\d+(?:\.\d+)?)\s*(?:L|lakh|lakhs|LPA)",
    r"(\d+(?:,\d+)*)\s*(?:to|-)\s*(\d+(?:,\d+)*)\s*per\s*(?:month|annum|year)",
    r"(?:CTC|ctc|salary).*?(\d+(?:\.\d+)?)\s*(?:L|lakh|LPA)",
]


class NaukriScraper(BaseScraper):
    """
    Scrapes Naukri.com for job posting data — demand signals and salary ranges.

    Note: Naukri has a JSON-based search API used internally by their React app.
    We target that endpoint which returns structured job data.
    """

    SOURCE_NAME = "naukri"
    REQUEST_DELAY = 2.0
    NAUKRI_API = "https://www.naukri.com/jobapi/v3/search"
    MAX_PAGES = 5   # scrape up to 5 pages per query (20 jobs/page = 100 max)

    def _extract_salary_from_text(self, text: str) -> Optional[Dict[str, int]]:
        """Extract salary range from job description text."""
        if not text:
            return None

        text = text.replace("\n", " ").replace(",", "")
        for pattern in SALARY_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    groups = match.groups()
                    if len(groups) >= 2 and groups[1]:
                        min_val = float(groups[0]) * 100_000  # LPA → INR
                        max_val = float(groups[1]) * 100_000
                        return {
                            "min_inr": int(min_val),
                            "max_inr": int(max_val),
                            "mid_inr": int((min_val + max_val) / 2),
                        }
                    elif len(groups) >= 1:
                        mid = float(groups[0]) * 100_000
                        return {"min_inr": None, "max_inr": None, "mid_inr": int(mid)}
                except (ValueError, IndexError):
                    continue
        return None

    def _extract_skills(self, job: dict) -> List[str]:
        """Extract key skills list from Naukri job object."""
        skills = job.get("keySkill", [])
        if isinstance(skills, list):
            return [s.get("label", s) if isinstance(s, dict) else s for s in skills[:10]]
        return []

    async def _search_jobs(self, keywords: str, exp_range: str, page: int = 1) -> List[dict]:
        """Call Naukri job search API and return raw job list."""
        try:
            headers = {
                "Accept": "application/json",
                "appid": "109",
                "systemid": "Naukri",
                "Referer": "https://www.naukri.com/",
            }
            params = {
                "noOfResults": 20,
                "urlType": "search_by_key_loc",
                "searchType": "adv",
                "keyword": keywords,
                "experience": exp_range,
                "pageNo": page,
                "k": keywords,
                "seoKey": keywords.replace(" ", "-"),
                "src": "jobsearchDesk",
            }
            resp = await self.get(
                self.NAUKRI_API,
                params=params,
                headers=headers,
            )
            data = resp.json()
            return data.get("jobDetails", [])
        except Exception as e:
            logger.warning(f"[Naukri] API call failed for '{keywords}': {e}")
            return []

    async def scrape(self) -> List[ScrapeResult]:
        results: List[ScrapeResult] = []
        total_jobs_processed = 0

        for target in SEARCH_TARGETS:
            keywords = target["keywords"]
            field = target["field"]
            exp = target["exp"]

            logger.info(f"[Naukri] Scraping: '{keywords}' exp={exp}")

            for page in range(1, self.MAX_PAGES + 1):
                jobs = await self._search_jobs(keywords, exp, page)
                if not jobs:
                    break

                for job in jobs:
                    total_jobs_processed += 1

                    # Extract salary from description
                    desc = job.get("jobDescription", "") or job.get("description", "")
                    salary_range = self._extract_salary_from_text(desc)

                    # Job posting demand data point
                    results.append(ScrapeResult(
                        program_id=None,   # aggregate — no specific program
                        field_name="naukri_job_demand",
                        raw_value=job.get("jobId", ""),
                        parsed_value=1.0,   # 1 job posting = 1 demand unit
                        unit="COUNT",
                        source_url=f"https://www.naukri.com/job-listings-{job.get('jobId', '')}",
                        metadata={
                            "title": job.get("title", ""),
                            "company": job.get("companyName", ""),
                            "city": job.get("placeholders", [{}])[0].get("label", "") if job.get("placeholders") else "",
                            "skills": self._extract_skills(job),
                            "degree_field": field,
                            "exp_range": exp,
                            "salary_range": salary_range,
                            "posted_date": job.get("footerPlaceholderLabel", ""),
                        },
                    ))

                    # Salary signal if extracted
                    if salary_range and salary_range.get("mid_inr"):
                        results.append(ScrapeResult(
                            program_id=None,
                            field_name=f"naukri_salary_{field}",
                            raw_value=str(salary_range["mid_inr"]),
                            parsed_value=float(salary_range["mid_inr"]),
                            unit="INR",
                            source_url=f"https://www.naukri.com/job-listings-{job.get('jobId', '')}",
                            metadata={
                                "degree_field": field,
                                "exp_range": exp,
                                "min_inr": salary_range.get("min_inr"),
                                "max_inr": salary_range.get("max_inr"),
                            },
                        ))

                if len(jobs) < 20:
                    break  # last page

        logger.info(f"[Naukri] Processed {total_jobs_processed} jobs → {len(results)} data points")
        return results
