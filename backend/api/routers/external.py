"""
/api/v1/external — Router for external open data APIs
- GET /external/data-gov    — AISHE higher education & MoSPI datasets
- GET /external/job-market  — Adzuna & JSearch real-time city demand & salaries
- GET /external/ecosystem   — GitHub developer activity & Wikidata alumni network
"""
from fastapi import APIRouter, Query, HTTPException, BackgroundTasks
from typing import Optional
from backend.services.external_apis import external_api_service
from backend.services.tavily_auto_service import tavily_auto_service

router = APIRouter(prefix="/external", tags=["External APIs"])


@router.get("/data-gov")
async def get_data_gov_trends(limit: int = Query(10, ge=1, le=100)):
    """Fetch live or benchmarked higher education statistics from Data.gov.in (OGD platform)."""
    return await external_api_service.fetch_data_gov_aishe(limit=limit)


@router.get("/job-market")
async def get_job_market_demand(
    background_tasks: BackgroundTasks,
    field: str = Query("engineering-cs", description="Target academic degree field"),
    city: str = Query("bengaluru", description="Target Indian city hub"),
):
    """Fetch active hiring postings and salary benchmarks from Adzuna / JSearch API."""
    background_tasks.add_task(
        tavily_auto_service.auto_trigger_for_college,
        f"India {city}",
        field,
        f"India {field} salary {city} freshers 2024 placement average CTC",
    )
    return await external_api_service.fetch_job_market_metrics(field=field, city=city)


@router.get("/ecosystem")
async def get_university_ecosystem(
    university_name: str = Query("IIT Bombay", description="Target university or college name"),
):
    """Fetch GitHub open-source activity and Wikidata university alumni metadata."""
    github_data = await external_api_service.fetch_github_ecosystem(query=university_name)
    wikidata_data = await external_api_service.fetch_wikidata_university(university_name=university_name)

    return {
        "university": university_name,
        "github": github_data,
        "wikidata": wikidata_data,
    }
