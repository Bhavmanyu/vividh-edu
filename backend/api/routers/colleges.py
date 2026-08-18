"""
/api/colleges — ROI Index endpoints
GET /colleges          — paginated, filtered list
GET /colleges/{id}     — full program detail
GET /colleges/compare  — side-by-side comparison
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from typing import Optional, List
from uuid import UUID
from datetime import datetime
import io
import csv

from ..db.database import get_db
from ..schemas import (
    ProgramListResponse, ProgramDetail, ProgramListItem,
    DegreeField, CollegeTier
)
from ..config import settings

router = APIRouter()


# ── Helper: build mock-compatible response from DB row ─────────────
def _build_program_item(row: dict) -> dict:
    """
    Maps flat DB row (from v_programs_full) into nested API response.
    In Week 2 this still falls back to mock data when DB is empty.
    """
    return {
        "id": str(row.get("program_id", "")),
        "college": {
            "id": str(row.get("college_id", "")),
            "shortName": row.get("college_short_name", ""),
            "name": row.get("college_full_name", ""),
            "state": row.get("state", ""),
            "city": row.get("city", ""),
            "tier": int(row.get("tier", 2)),
            "type": row.get("college_type", "private"),
            "nirfRank": row.get("nirf_rank"),
        },
        "degree": {
            "id": str(row.get("degree_id", "")),
            "shortName": row.get("degree_short_name", ""),
            "name": row.get("degree_full_name", ""),
            "field": row.get("degree_field", ""),
            "durationYears": float(row.get("duration_years", 4)),
            "level": row.get("degree_level", "UG"),
        },
        "roi": {
            "compositeScore": float(row.get("composite_score", 0)),
            "financialRoiPct": float(row.get("financial_roi_pct", 0)),
            "riskScore": float(row.get("risk_score", 0.5)),
            "confidenceIntervalLow": float(row.get("ci_low", 0)),
            "confidenceIntervalHigh": float(row.get("ci_high", 0)),
            "confidenceLevel": row.get("confidence_level", "Medium"),
            "modelVersion": row.get("model_version", settings.current_model_version),
        },
        "meta": {
            "aiRiskLabel": row.get("ai_risk_label", "Medium"),
            "dataFreshnessDays": 0,
        },
        "placement": {
            "rate": float(row.get("placement_rate_pct", 0)),
            "medianSalaryInr": row.get("median_salary_inr"),
        },
    }


@router.get("/colleges")
async def list_colleges(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    field: Optional[str] = None,
    state: Optional[str] = None,
    tier: Optional[str] = None,
    ai_risk: Optional[str] = None,
    q: Optional[str] = None,
    sort_by: str = "composite_score",
    sort_dir: str = "desc",
):
    """
    Returns paginated list of programs from the database.
    Falls back to mock data JSON if DB is empty (Week 2 transition period).
    """
    try:
        # Try DB first
        filters = ["p.is_active = TRUE"]
        params: dict = {}

        if field:
            filters.append("d.field = :field")
            params["field"] = field
        if state:
            filters.append("c.state = :state")
            params["state"] = state
        if tier:
            filters.append("c.tier = :tier")
            params["tier"] = tier
        if ai_risk:
            filters.append("ri.ai_risk_label = :ai_risk")
            params["ai_risk"] = ai_risk
        if q:
            filters.append("(c.full_name ILIKE :q OR d.full_name ILIKE :q)")
            params["q"] = f"%{q}%"

        where_clause = " AND ".join(filters)
        sort_col = {
            "composite_score": "r.composite_score",
            "financial_roi": "r.financial_roi_pct",
            "placement_rate": "pl.placement_rate_pct",
            "risk_score": "r.risk_score",
        }.get(sort_by, "r.composite_score")
        sort_direction = "DESC" if sort_dir == "desc" else "ASC"

        count_query = text(f"""
            SELECT COUNT(*) FROM programs p
            JOIN colleges c ON c.id = p.college_id
            JOIN degrees d ON d.id = p.degree_id
            LEFT JOIN roi_scores r ON r.program_id = p.id AND r.is_current = TRUE
            LEFT JOIN risk_indicators ri ON ri.program_id = p.id AND ri.is_current = TRUE
            LEFT JOIN placement_data pl ON pl.program_id = p.id AND pl.is_current = TRUE
            WHERE {where_clause}
        """)

        data_query = text(f"""
            SELECT
                p.id AS program_id,
                c.id AS college_id, c.short_name AS college_short_name,
                c.full_name AS college_full_name, c.state, c.city, c.tier,
                c.college_type, c.nirf_rank,
                d.id AS degree_id, d.short_name AS degree_short_name,
                d.full_name AS degree_full_name, d.field AS degree_field,
                d.level AS degree_level, d.duration_years,
                r.composite_score, r.financial_roi_pct, r.risk_score,
                r.ci_low, r.ci_high, r.confidence_level, r.model_version,
                ri.ai_risk_label,
                pl.placement_rate_pct, pl.median_salary_inr
            FROM programs p
            JOIN colleges c ON c.id = p.college_id
            JOIN degrees d ON d.id = p.degree_id
            LEFT JOIN roi_scores r ON r.program_id = p.id AND r.is_current = TRUE
            LEFT JOIN risk_indicators ri ON ri.program_id = p.id AND ri.is_current = TRUE
            LEFT JOIN placement_data pl ON pl.program_id = p.id AND pl.is_current = TRUE
            WHERE {where_clause}
            ORDER BY {sort_col} {sort_direction} NULLS LAST
            LIMIT :limit OFFSET :offset
        """)

        params["limit"] = per_page
        params["offset"] = (page - 1) * per_page

        total_result = await db.execute(count_query, params)
        total = total_result.scalar() or 0

        if total == 0:
            # DB is empty — return mock indicator for frontend fallback
            return {
                "data": [],
                "total": 0,
                "page": page,
                "per_page": per_page,
                "model_version": settings.current_model_version,
                "generated_at": datetime.utcnow().isoformat(),
                "_source": "empty_db_use_mock",
            }

        rows = await db.execute(data_query, params)
        programs = [_build_program_item(dict(row._mapping)) for row in rows]

        return {
            "data": programs,
            "total": total,
            "page": page,
            "per_page": per_page,
            "model_version": settings.current_model_version,
            "generated_at": datetime.utcnow().isoformat(),
            "_source": "database",
        }

    except Exception as e:
        # Graceful degradation — let Next.js fall back to mock
        return {
            "data": [],
            "total": 0,
            "page": page,
            "per_page": per_page,
            "model_version": settings.current_model_version,
            "generated_at": datetime.utcnow().isoformat(),
            "_source": "error",
            "_error": str(e),
        }


@router.get("/colleges/{program_id}")
async def get_college_detail(
    program_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Full program detail with salary trajectories, risk indicators, costs."""
    try:
        query = text("""
            SELECT
                p.id AS program_id, p.annual_tuition_inr, p.total_seats,
                c.id AS college_id, c.short_name AS college_short_name,
                c.full_name AS college_full_name, c.state, c.city, c.tier,
                c.college_type, c.nirf_rank, c.naac_grade, c.established_year,
                d.id AS degree_id, d.short_name AS degree_short_name,
                d.full_name AS degree_full_name, d.field AS degree_field,
                d.level AS degree_level, d.duration_years,
                r.composite_score, r.financial_roi_pct, r.risk_score,
                r.optionality_score, r.mobility_score, r.satisfaction_score,
                r.network_score, r.ci_low, r.ci_high, r.confidence_level, r.model_version,
                ri.ai_automation_prob, ri.salary_volatility, ri.industry_cyclicality,
                ri.credential_inflation, ri.geographic_concentration, ri.regulatory_risk,
                ri.physical_health_risk, ri.work_life_quality, ri.ai_risk_label,
                pl.placement_rate_pct, pl.highest_salary_inr, pl.median_salary_inr,
                pl.average_salary_inr, pl.companies_visited, pl.academic_year,
                cd.total_tuition_inr, cd.hostel_living_inr, cd.exam_prep_costs_inr,
                cd.opportunity_cost_inr, cd.total_cost_of_degree
            FROM programs p
            JOIN colleges c ON c.id = p.college_id
            JOIN degrees d ON d.id = p.degree_id
            LEFT JOIN roi_scores r ON r.program_id = p.id AND r.is_current = TRUE
            LEFT JOIN risk_indicators ri ON ri.program_id = p.id AND ri.is_current = TRUE
            LEFT JOIN placement_data pl ON pl.program_id = p.id AND pl.is_current = TRUE
            LEFT JOIN cost_data cd ON cd.program_id = p.id AND cd.is_current = TRUE
            WHERE p.id = :program_id
        """)

        result = await db.execute(query, {"program_id": program_id})
        row = result.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Program not found")

        row_dict = dict(row._mapping)

        # Fetch salary trajectory
        sal_query = text("""
            SELECT year_number, p25_inr, p50_inr, p75_inr
            FROM salary_trajectories
            WHERE program_id = :program_id AND is_current = TRUE
            ORDER BY year_number
        """)
        sal_result = await db.execute(sal_query, {"program_id": program_id})
        sal_rows = {r.year_number: r for r in sal_result}

        def sal_band(year: int) -> dict:
            r = sal_rows.get(year)
            if r:
                return {"p25": r.p25_inr, "p50": r.p50_inr, "p75": r.p75_inr}
            return {"p25": 0, "p50": 0, "p75": 0}

        return {
            "id": program_id,
            "college": {
                "id": str(row_dict["college_id"]),
                "shortName": row_dict["college_short_name"],
                "name": row_dict["college_full_name"],
                "state": row_dict["state"],
                "city": row_dict["city"],
                "tier": int(row_dict["tier"]),
                "type": row_dict["college_type"],
                "nirfRank": row_dict["nirf_rank"],
                "naacGrade": row_dict["naac_grade"],
            },
            "degree": {
                "id": str(row_dict["degree_id"]),
                "shortName": row_dict["degree_short_name"],
                "name": row_dict["degree_full_name"],
                "field": row_dict["degree_field"],
                "durationYears": float(row_dict["duration_years"]),
                "level": row_dict["degree_level"],
            },
            "roi": {
                "compositeScore": float(row_dict["composite_score"] or 0),
                "financialRoiPct": float(row_dict["financial_roi_pct"] or 0),
                "riskScore": float(row_dict["risk_score"] or 0.5),
                "optionalityScore": float(row_dict["optionality_score"] or 0.5),
                "mobilityScore": float(row_dict["mobility_score"] or 0.5),
                "satisfactionScore": float(row_dict["satisfaction_score"] or 0.5),
                "networkScore": float(row_dict["network_score"] or 0.5),
                "confidenceIntervalLow": float(row_dict["ci_low"] or 0),
                "confidenceIntervalHigh": float(row_dict["ci_high"] or 0),
                "confidenceLevel": row_dict["confidence_level"] or "Medium",
                "modelVersion": row_dict["model_version"] or settings.current_model_version,
            },
            "salary": {
                "year1": sal_band(1),
                "year5": sal_band(5),
                "year10": sal_band(10),
                "year20": sal_band(20),
            },
            "risk": {
                "aiAutomationProbability": float(row_dict["ai_automation_prob"] or 0),
                "salaryVolatility": float(row_dict["salary_volatility"] or 0),
                "industryCyclicality": float(row_dict["industry_cyclicality"] or 0),
                "credentialInflation": float(row_dict["credential_inflation"] or 0),
                "geographicConcentration": float(row_dict["geographic_concentration"] or 0),
                "regulatoryRisk": float(row_dict["regulatory_risk"] or 0),
                "physicalHealthRisk": float(row_dict["physical_health_risk"] or 0),
                "workLifeQuality": float(row_dict["work_life_quality"] or 0.5),
                "aiRiskLabel": row_dict["ai_risk_label"] or "Medium",
            },
            "placement": {
                "rate": float(row_dict["placement_rate_pct"] or 0),
                "highestSalaryInr": row_dict["highest_salary_inr"],
                "medianSalaryInr": row_dict["median_salary_inr"],
                "companiesVisited": row_dict["companies_visited"],
                "academicYear": row_dict["academic_year"],
            },
            "costs": {
                "totalTuitionInr": row_dict["total_tuition_inr"],
                "hostelLivingInr": row_dict["hostel_living_inr"],
                "examPrepCostsInr": row_dict["exam_prep_costs_inr"],
                "opportunityCostInr": row_dict["opportunity_cost_inr"],
                "totalCostOfDegreeInr": row_dict["total_cost_of_degree"],
            },
            "meta": {
                "modelVersion": row_dict["model_version"] or settings.current_model_version,
                "dataFreshnessDays": 0,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/colleges/export/csv")
async def export_colleges_csv(
    db: AsyncSession = Depends(get_db),
    field: Optional[str] = None,
    state: Optional[str] = None,
):
    """Stream CSV export of filtered programs."""
    # In production: query DB and stream. For now, return structure.
    async def generate():
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Program ID", "College", "Degree", "State", "Tier",
            "Composite Score", "Financial ROI %", "AI Risk", "Placement Rate %",
            "Median Salary Y1 (INR)", "Model Version"
        ])
        yield output.getvalue()

    return StreamingResponse(
        generate(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=indialens-export.csv"},
    )
