"""
Reddit NLP Extractor — PRAW + regex + optional BERT NER
Subreddits: r/india, r/cscareerquestions_india, r/CAstudents,
            r/IndiaTech, r/medicalschool_india, r/IndiaInvestments

Extracts:
  - Salary + company + YoE from "I got a package of X LPA at Y company"
  - College reputation signals from "IIT Bombay vs VIT for CS" type posts
  - Career outcomes by degree mentions
"""
import re
import logging
from typing import List, Optional, Dict, Any

from .base_scraper import BaseScraper, ScrapeResult

logger = logging.getLogger(__name__)

# Subreddits to scrape
TARGET_SUBREDDITS = [
    {"sub": "india", "field": None, "topics": ["salary", "package", "LPA", "job", "placement"]},
    {"sub": "cscareerquestions_india", "field": "engineering-cs", "topics": ["salary", "offer", "CTC"]},
    {"sub": "CAstudents", "field": "commerce", "topics": ["salary", "CA", "articleship", "package"]},
    {"sub": "IndiaTech", "field": "engineering-cs", "topics": ["salary", "FAANG", "startup"]},
    {"sub": "IndiaInvestments", "field": "commerce", "topics": ["salary", "finance", "job"]},
    {"sub": "medicalschool_india", "field": "medicine", "topics": ["stipend", "salary", "MBBS", "PG"]},
    {"sub": "LawStudents", "field": "law", "topics": ["salary", "NLU", "law school", "job"]},
]

# Salary extraction regex patterns (Indian context)
SALARY_PATTERNS = [
    # "I got X LPA / package of X LPA"
    (r"(?:got|got a|received|offered|package of|CTC|ctc|salary)\s+(?:of\s+)?(\d+(?:\.\d+)?)\s*(?:L|LPA|lakh|lakhs|lpa)", "lpa"),
    # "X-Y LPA range"
    (r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*(?:L|LPA|lakh|lpa)", "lpa_range"),
    # "₹X per month"
    (r"₹\s*(\d+(?:,\d+)*)\s*(?:per\s*month|pm|/month)", "pm"),
    # "X thousand per month"
    (r"(\d+)\s*(?:thousand|k)\s*(?:per\s*month|pm|/month)", "k_pm"),
]

# YoE extraction
YOE_PATTERNS = [
    r"(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp|work)",
    r"(?:with|after)\s*(\d+)\s*(?:years?|yrs?)",
    r"fresher|fresh\s*graduate",
]

# College mention detection
COLLEGE_MENTIONS = {
    r"\bIIT\s+(\w+)\b": "IIT {match}",
    r"\bNIT\s+(\w+)\b": "NIT {match}",
    r"\bBITS\b": "BITS",
    r"\bVIT\b": "VIT",
    r"\bSRM\b": "SRM",
}


class RedditScraper(BaseScraper):
    """
    Uses PRAW (Python Reddit API Wrapper) to extract salary data from Indian career subreddits.
    Falls back to pushshift.io API if PRAW credentials are not configured.

    Configuration:
        REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET in .env
    """

    SOURCE_NAME = "reddit"
    REQUEST_DELAY = 1.0   # Reddit API is more lenient
    POSTS_PER_SUBREDDIT = 100
    COMMENT_DEPTH = 2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._reddit = None

    def _init_praw(self):
        """Initialize PRAW client. Returns None if not configured."""
        try:
            import praw
            if not self.settings or not self.settings.reddit_client_id:
                return None
            return praw.Reddit(
                client_id=self.settings.reddit_client_id,
                client_secret=self.settings.reddit_client_secret,
                user_agent=self.settings.reddit_user_agent,
                ratelimit_seconds=2,
            )
        except ImportError:
            logger.warning("[Reddit] PRAW not installed. Install: pip install praw")
            return None
        except Exception as e:
            logger.warning(f"[Reddit] PRAW init failed: {e}")
            return None

    def _extract_salary(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract salary from text using regex patterns."""
        text_clean = text.replace(",", "").replace("\n", " ")

        for pattern, salary_type in SALARY_PATTERNS:
            match = re.search(pattern, text_clean, re.IGNORECASE)
            if match:
                try:
                    if salary_type == "lpa":
                        lpa = float(match.group(1))
                        return {
                            "annual_inr": int(lpa * 100_000),
                            "confidence": 0.85,
                            "pattern": pattern,
                        }
                    elif salary_type == "lpa_range":
                        low = float(match.group(1))
                        high = float(match.group(2))
                        mid = (low + high) / 2
                        return {
                            "annual_inr": int(mid * 100_000),
                            "range_low_inr": int(low * 100_000),
                            "range_high_inr": int(high * 100_000),
                            "confidence": 0.75,
                            "pattern": pattern,
                        }
                    elif salary_type == "pm":
                        monthly = int(match.group(1))
                        return {
                            "annual_inr": monthly * 12,
                            "confidence": 0.7,
                            "pattern": pattern,
                        }
                    elif salary_type == "k_pm":
                        monthly = int(match.group(1)) * 1000
                        return {
                            "annual_inr": monthly * 12,
                            "confidence": 0.65,
                            "pattern": pattern,
                        }
                except (ValueError, IndexError):
                    continue
        return None

    def _extract_yoe(self, text: str) -> Optional[int]:
        """Extract years of experience from text."""
        if re.search(r"\bfresher\b|\bfresh\s+graduate\b", text, re.IGNORECASE):
            return 0

        for pattern in YOE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except (ValueError, IndexError):
                    continue
        return None

    def _detect_degree_field(self, text: str, subreddit_field: Optional[str]) -> str:
        """Infer degree field from text context."""
        if subreddit_field:
            return subreddit_field

        text_lower = text.lower()
        if any(k in text_lower for k in ["software", "coding", "developer", "cs", "computer", "python", "java"]):
            return "engineering-cs"
        if any(k in text_lower for k in ["ca", "accountant", "finance", "bcom", "commerce"]):
            return "commerce"
        if any(k in text_lower for k in ["doctor", "mbbs", "medical", "hospital", "neet"]):
            return "medicine"
        if any(k in text_lower for k in ["mba", "management", "consultant", "iim", "cat"]):
            return "management"
        if any(k in text_lower for k in ["mechanical", "civil", "electrical", "core engineering"]):
            return "engineering-non-cs"
        if any(k in text_lower for k in ["law", "lawyer", "llb", "nlu", "advocate"]):
            return "law"
        return "engineering-cs"   # default fallback

    async def _scrape_with_praw(self, reddit, target: dict) -> List[Dict]:
        """Use PRAW to fetch posts + comments from subreddit."""
        posts_data = []
        try:
            subreddit = reddit.subreddit(target["sub"])
            search_query = " OR ".join(target["topics"])

            for post in subreddit.search(search_query, limit=self.POSTS_PER_SUBREDDIT, time_filter="month"):
                text = f"{post.title} {post.selftext}"
                posts_data.append({
                    "post_id": post.id,
                    "title": post.title,
                    "text": text[:2000],  # cap at 2000 chars
                    "subreddit": target["sub"],
                    "created_utc": post.created_utc,
                })

                # Top-level comments
                post.comments.replace_more(limit=0)
                for comment in list(post.comments)[:20]:
                    if hasattr(comment, "body") and len(comment.body) > 30:
                        posts_data.append({
                            "post_id": f"{post.id}_c_{comment.id}",
                            "title": "",
                            "text": comment.body[:1000],
                            "subreddit": target["sub"],
                            "created_utc": comment.created_utc,
                        })
        except Exception as e:
            logger.warning(f"[Reddit] PRAW error for r/{target['sub']}: {e}")
        return posts_data

    async def _scrape_with_pushshift(self, target: dict) -> List[Dict]:
        """
        Fallback: use Pushshift API when PRAW is not configured.
        Note: Pushshift availability varies — use as backup only.
        """
        posts_data = []
        query = "+".join(target["topics"][:2])
        url = f"https://api.pushshift.io/reddit/search/submission?subreddit={target['sub']}&q={query}&size=100&sort=desc"

        try:
            resp = await self.get(url)
            data = resp.json()
            for post in data.get("data", []):
                text = f"{post.get('title', '')} {post.get('selftext', '')}"
                posts_data.append({
                    "post_id": post.get("id", ""),
                    "title": post.get("title", ""),
                    "text": text[:2000],
                    "subreddit": target["sub"],
                    "created_utc": post.get("created_utc"),
                })
        except Exception as e:
            logger.warning(f"[Reddit/Pushshift] Failed for r/{target['sub']}: {e}")
        return posts_data

    async def scrape(self) -> List[ScrapeResult]:
        results: List[ScrapeResult] = []
        self._reddit = self._init_praw()
        seen_posts = set()

        for target in TARGET_SUBREDDITS:
            logger.info(f"[Reddit] Scraping r/{target['sub']}")

            if self._reddit:
                import asyncio
                # PRAW is synchronous — run in executor
                loop = __import__("asyncio").get_event_loop()
                posts = await loop.run_in_executor(
                    None, lambda: list(self._reddit.subreddit(target["sub"]).search(
                        " OR ".join(target["topics"]),
                        limit=self.POSTS_PER_SUBREDDIT,
                        time_filter="month",
                    ))
                )
                posts_data = [
                    {
                        "post_id": p.id,
                        "title": p.title,
                        "text": f"{p.title} {p.selftext}"[:2000],
                        "subreddit": target["sub"],
                        "created_utc": p.created_utc,
                    }
                    for p in posts
                ]
            else:
                posts_data = await self._scrape_with_pushshift(target)

            for post in posts_data:
                post_id = post["post_id"]
                if post_id in seen_posts:
                    continue
                seen_posts.add(post_id)

                text = post["text"]
                salary = self._extract_salary(text)
                if not salary:
                    continue  # skip posts with no salary signal

                yoe = self._extract_yoe(text)
                degree_field = self._detect_degree_field(text, target.get("field"))

                results.append(ScrapeResult(
                    program_id=None,
                    field_name="reddit_salary_signal",
                    raw_value=str(salary["annual_inr"]),
                    parsed_value=float(salary["annual_inr"]),
                    unit="INR",
                    source_url=f"https://reddit.com/r/{target['sub']}/comments/{post_id}",
                    confidence=salary.get("confidence", 0.6),
                    metadata={
                        "subreddit": target["sub"],
                        "post_id": post_id,
                        "title": post.get("title", "")[:100],
                        "degree_field": degree_field,
                        "yoe": yoe,
                        "range_low": salary.get("range_low_inr"),
                        "range_high": salary.get("range_high_inr"),
                    },
                ))

        logger.info(f"[Reddit] Extracted {len(results)} salary signals")
        return results
