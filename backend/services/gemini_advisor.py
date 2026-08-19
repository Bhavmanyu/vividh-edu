"""
IndiaLens Backend — Google Gemini AI Advisor Service
Provides interactive student career guidance, personalized degree ROI advice,
and structured JSON parsing of unstructured college placement reports.
"""
import logging
from typing import Dict, Any, List, Optional
import httpx
from backend.api.config import settings

logger = logging.getLogger(__name__)


class GeminiAdvisorService:
    """Service wrapping Google Gemini 1.5/2.5 Flash API via AI Studio."""

    def __init__(self):
        self.api_key = settings.gemini_api_key
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

    async def generate_career_advice(
        self,
        student_profile: Dict[str, Any],
        top_programs: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Generate personalized AI advisor advice for student profile x program options."""
        if not self.api_key:
            logger.info("GEMINI_API_KEY not set. Returning template AI advisor response.")
            return {
                "engine": "gemini-1.5-flash (fallback)",
                "summary": f"Based on your budget of ₹{student_profile.get('total_budget', 10)} Lakhs and target in {student_profile.get('target_field', 'Engineering')}, tier-1/tier-2 programs deliver optimal 5-year IRR.",
                "recommendations": [
                    "Prioritize programs with high placement consistency (>85%) over brand prestige alone.",
                    "Focus on developing specialized technical skills to mitigate 10-year AI automation exposure.",
                    "Explore early internship opportunities in high-growth tech hubs (Bengaluru / NCR).",
                ],
                "risk_warning": "High tuition costs (>₹15 Lakhs) increase payback horizon beyond 4.5 years.",
            }

        prompt = f"""
        You are IndiaLens AI, an expert quantitative career and education advisor for Indian students.
        Analyze this student profile and top recommended college programs:
        
        Student Profile: {student_profile}
        Top Recommended Programs: {top_programs}
        
        Provide a structured advice summary, top 3 actionable recommendations, and a key risk warning.
        Keep advice grounded in Indian labor market realities, salary trajectories, and ROI.
        """

        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(
                    f"{self.api_url}?key={self.api_key}",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        return {
                            "engine": "gemini-1.5-flash",
                            "advice_markdown": text,
                        }
        except Exception as e:
            logger.warning(f"Gemini API call failed: {e}")

        return {
            "engine": "gemini-1.5-flash (fallback)",
            "summary": "AI advisor consultation complete. Recommended prioritizing low-cost high-placement engineering programs.",
            "recommendations": [
                "Target tier-1/tier-2 government & autonomous institutes to maximize Net Present Value.",
                "Upskill in cloud architecture & data engineering to protect against AI risk vectors.",
            ],
            "risk_warning": "Monitor economic cyclicality when choosing specialized domains.",
        }


gemini_advisor_service = GeminiAdvisorService()
