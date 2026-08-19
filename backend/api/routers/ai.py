"""
/api/v1/ai — Router for AI Advisor & Psychometrics endpoints
- POST /ai/advisor       — Google Gemini 1.5 Flash interactive career counseling
- POST /ai/psychometrics — Hugging Face sentiment & Cronbach's alpha scoring
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from backend.services.gemini_advisor import gemini_advisor_service
from backend.services.psychometrics import psychometrics_service

router = APIRouter(prefix="/ai", tags=["AI Engine & Psychometrics"])


class AdvisorRequest(BaseModel):
    total_budget: float = Field(10.0, description="Total budget in INR Lakhs")
    target_field: str = Field("engineering-cs", description="Target field of study")
    risk_tolerance: str = Field("medium", description="Risk tolerance: low, medium, high")
    preferred_cities: List[str] = Field(default_factory=lambda: ["Bengaluru", "NCR"])
    top_programs: List[Dict[str, Any]] = Field(default_factory=list)


class PsychometricsRequest(BaseModel):
    college_id: Optional[str] = None
    reviews: List[str] = Field(..., min_items=1, description="List of raw student/alumni review texts")


@router.post("/advisor")
async def consult_ai_advisor(payload: AdvisorRequest):
    """Consult Google Gemini AI Advisor for personalized degree ROI & career strategy."""
    student_profile = {
        "total_budget": payload.total_budget,
        "target_field": payload.target_field,
        "risk_tolerance": payload.risk_tolerance,
        "preferred_cities": payload.preferred_cities,
    }
    return await gemini_advisor_service.generate_career_advice(
        student_profile=student_profile,
        top_programs=payload.top_programs,
    )


@router.post("/psychometrics")
async def evaluate_psychometrics(payload: PsychometricsRequest):
    """Run Hugging Face sentiment analysis & Cronbach's alpha psychometrics on review texts."""
    return await psychometrics_service.analyze_student_reviews(reviews=payload.reviews)
