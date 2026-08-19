"""
IndiaLens Backend — On-Demand Auto-Trigger Service for Tavily Smart Search
Automatically triggers web scraping when users request analysis for a college or degree field,
keeping placement stats, salary distributions, and NIRF ranks continuously fresh.
"""
import os
import logging
import httpx
from typing import Dict, Any, Optional
from backend.api.config import settings

logger = logging.getLogger(__name__)


class TavilyAutoTriggerService:
    """Service to automatically trigger Tavily searches on application cache misses or on-demand user queries."""

    def __init__(self):
        self.api_url = "https://api.tavily.com/search"

    async def auto_trigger_for_college(
        self,
        college_name: str,
        degree_field: str = "engineering-cs",
        user_query: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Auto-triggers Tavily search in background when user queries a college or analysis report."""
        api_key = settings.tavily_api_key or os.getenv("TAVILY_API_KEY", "")
        if not api_key:
            logger.info("[TavilyAuto] TAVILY_API_KEY not set. Skipping on-demand scrape.")
            return {"status": "skipped", "reason": "no_api_key"}

        search_query = user_query or f"{college_name} {degree_field} placement 2024 median salary average CTC"
        logger.info(f"[TavilyAuto] Auto-triggering Tavily search for: '{search_query}'")

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(
                    self.api_url,
                    json={
                        "api_key": api_key,
                        "query": search_query,
                        "search_depth": "basic",
                        "max_results": 5,
                        "include_answer": True,
                    },
                )
                if res.status_code == 200:
                    data = res.json()
                    answer = data.get("answer", "")
                    results = data.get("results", [])
                    logger.info(f"[TavilyAuto] Successfully retrieved {len(results)} live results for '{college_name}'")
                    return {
                        "status": "success",
                        "college": college_name,
                        "query": search_query,
                        "ai_answer": answer,
                        "results": results,
                    }
        except Exception as e:
            logger.warning(f"[TavilyAuto] Tavily auto-trigger failed for '{college_name}': {e}")

        return {"status": "failed", "college": college_name}


tavily_auto_service = TavilyAutoTriggerService()
