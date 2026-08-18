"""
Pydantic schemas for API request/response validation.
All monetary values in INR unless suffixed _usd or _ppp.
"""
from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import Optional, List, Literal
from uuid import UUID
from datetime import datetime
from enum import Enum


# ── Enums ──────────────────────────────────────────────────────────

class CollegeTier(str, Enum):
    T1 = "1"
    T2 = "2"
    T3 = "3"

class CollegeType(str, Enum):
    IIT = "IIT"
    NIT = "NIT"
    PRIVATE = "private"
    DEEMED = "deemed"
    CENTRAL = "central"
    AUTONOMOUS = "autonomous"
    STATE = "state"

class DegreeField(str, Enum):
    ENG_CS = "engineering-cs"
    ENG_NON_CS = "engineering-non-cs"
    MEDICINE = "medicine"
    MANAGEMENT = "management"
    COMMERCE = "commerce"
    DESIGN = "design"
    LAW = "law"
    PURE_SCI = "pure-sciences"
    SOCIAL_SCI = "social-sciences"
    ARTS = "arts"

class ConfidenceLevel(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class AnomalyStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class FeedbackStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    MERGED = "merged"


# ── College schemas ────────────────────────────────────────────────

class CollegeBase(BaseModel):
    short_name: str
    full_name: str
    state: str
    city: str
    tier: CollegeTier
    college_type: CollegeType
    naac_grade: Optional[str] = None
    nirf_rank: Optional[int] = None
    established_year: Optional[int] = None

class CollegeOut(CollegeBase):
    id: UUID
    created_at: datetime
    model_config = {"from_attributes": True}


# ── Degree schemas ─────────────────────────────────────────────────

class DegreeBase(BaseModel):
    short_name: str
    full_name: str
    field: DegreeField
    level: Literal["UG", "PG", "PhD", "Diploma"]
    duration_years: float

class DegreeOut(DegreeBase):
    id: UUID
    model_config = {"from_attributes": True}


# ── Salary trajectory ──────────────────────────────────────────────

class SalaryBand(BaseModel):
    p25: int
    p50: int
    p75: int
    p90: Optional[int] = None

class SalaryTrajectoryOut(BaseModel):
    year1: SalaryBand
    year5: SalaryBand
    year10: SalaryBand
    year20: SalaryBand


# ── ROI scores ─────────────────────────────────────────────────────

class ROIScoreOut(BaseModel):
    composite_score: float
    financial_roi_pct: float
    risk_score: float
    optionality_score: float
    mobility_score: float
    satisfaction_score: float
    network_score: float
    ci_low: float
    ci_high: float
    confidence_level: ConfidenceLevel
    model_version: str


# ── Risk indicators ────────────────────────────────────────────────

class RiskIndicatorsOut(BaseModel):
    ai_automation_prob: float
    salary_volatility: float
    industry_cyclicality: float
    credential_inflation: float
    geographic_concentration: float
    regulatory_risk: float
    physical_health_risk: float
    work_life_quality: float
    ai_risk_label: str


# ── Placement ──────────────────────────────────────────────────────

class PlacementOut(BaseModel):
    placement_rate_pct: Optional[float] = None
    highest_salary_inr: Optional[int] = None
    median_salary_inr: Optional[int] = None
    average_salary_inr: Optional[int] = None
    companies_visited: Optional[int] = None
    academic_year: Optional[str] = None


# ── Costs ──────────────────────────────────────────────────────────

class CostDataOut(BaseModel):
    total_tuition_inr: Optional[int] = None
    hostel_living_inr: Optional[int] = None
    exam_prep_costs_inr: Optional[int] = None
    opportunity_cost_inr: Optional[int] = None
    total_cost_of_degree: Optional[int] = None


# ── Full program (list view) ───────────────────────────────────────

class ProgramListItem(BaseModel):
    id: UUID
    college: CollegeOut
    degree: DegreeOut
    roi: ROIScoreOut
    placement_rate: Optional[float] = None
    ai_risk_label: Optional[str] = None
    data_freshness_days: int = 0
    model_config = {"from_attributes": True}


# ── Full program (detail view) ─────────────────────────────────────

class ProgramDetail(BaseModel):
    id: UUID
    college: CollegeOut
    degree: DegreeOut
    program: dict  # annual_tuition, seats etc
    roi: ROIScoreOut
    salary: SalaryTrajectoryOut
    placement: PlacementOut
    risk: RiskIndicatorsOut
    costs: CostDataOut
    meta: dict
    model_config = {"from_attributes": True}


# ── List response ──────────────────────────────────────────────────

class ProgramListResponse(BaseModel):
    data: List[ProgramListItem]
    total: int
    page: int
    per_page: int
    model_version: str
    generated_at: datetime


# ── Analyze / intake ───────────────────────────────────────────────

class StudentProfile(BaseModel):
    # Section 1
    tenth_pct: Optional[float] = Field(None, ge=0, le=100)
    twelfth_pct: Optional[float] = Field(None, ge=0, le=100)
    twelfth_stream: Optional[str] = None
    jee_rank: Optional[int] = None
    neet_score: Optional[int] = None
    backlog: str = "none"
    learning_style: str = "mixed"

    # Section 2
    family_income: Optional[str] = None
    total_budget: int = 20   # lakhs
    loan_willingness: str = "up-to-5l"
    family_support_needed: str = "no"

    # Section 3
    home_state: Optional[str] = None
    relocation_india: str = "yes"
    relocation_abroad: str = "maybe"
    return_home: str = "no"

    # Section 4
    primary_goals: List[str] = []
    risk_appetite: int = Field(5, ge=1, le=10)
    wlb_priority: int = Field(5, ge=1, le=10)
    financial_independence_age: str = "30"
    lower_pay_meaningful: str = "depends"

    # Section 5
    sports_level: str = "none"
    arts_level: str = "none"
    coding_level: str = "none"
    entrepreneurship_level: str = "none"
    leadership_level: str = "none"

    # Sections 6-8
    p_q1: Optional[str] = None
    p_q2: Optional[str] = None
    p_q3: Optional[str] = None
    fields_of_interest: List[str] = []
    colleges_heard_of: Optional[str] = None
    fields_ruled_out: Optional[str] = None
    future_vision: Optional[str] = None
    preferred_work_structure: Optional[str] = None
    exciting_industries: List[str] = []
    one_thing_never: Optional[str] = None


class AnalyzeResponse(BaseModel):
    token: str
    recommendations: List[dict]
    profile_parsed: dict
    flags: List[dict]
    model_version: str
    generated_at: datetime


# ── Admin schemas ──────────────────────────────────────────────────

class AnomalyReviewRequest(BaseModel):
    action: Literal["accept", "reject"]
    notes: Optional[str] = None

class AnomalyOut(BaseModel):
    id: UUID
    program_id: UUID
    college_name: str
    degree_name: str
    field_name: str
    prior_value: Optional[str]
    new_value: str
    delta_pct: float
    status: AnomalyStatus
    created_at: datetime
    model_config = {"from_attributes": True}

class FeedbackCreateRequest(BaseModel):
    college_degree_id: Optional[str] = None
    field_name: str
    old_value: str
    new_value: str
    source_url: str
    confidence: Literal["high", "medium", "low"]
    notes: Optional[str] = None
    submitter_email: Optional[str] = None

class ScrapeRunOut(BaseModel):
    id: UUID
    source_name: str
    started_at: datetime
    completed_at: Optional[datetime]
    status: str
    records_scraped: int
    records_updated: int
    records_flagged: int
    error_message: Optional[str]
    model_config = {"from_attributes": True}
