"""
Unit & Integration tests for IndiaLens external API routers, AI advisor, and psychometrics
"""
import pytest
from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_external_data_gov():
    response = client.get("/api/v1/external/data-gov?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "source" in data


def test_external_job_market():
    response = client.get("/api/v1/external/job-market?field=engineering-cs&city=bengaluru")
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Bengaluru"
    assert "avg_salary_inr" in data
    assert "demand_score" in data


def test_external_ecosystem():
    response = client.get("/api/v1/external/ecosystem?university_name=IIT%20Bombay")
    assert response.status_code == 200
    data = response.json()
    assert data["university"] == "IIT Bombay"
    assert "github" in data
    assert "wikidata" in data


def test_ai_advisor():
    payload = {
        "total_budget": 12.5,
        "target_field": "engineering-cs",
        "risk_tolerance": "medium",
        "preferred_cities": ["Bengaluru", "Pune"]
    }
    response = client.post("/api/v1/ai/advisor", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "engine" in data


def test_ai_psychometrics():
    payload = {
        "reviews": [
            "Great faculty and supportive peer network.",
            "Hostel infrastructure is decent, placement support is active.",
            "Work-life balance during exams is stressful but manageable."
        ]
    }
    response = client.post("/api/v1/ai/psychometrics", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "cronbach_alpha" in data
    assert data["cronbach_alpha"] >= 0.65
    assert "sub_scores" in data


def test_scrape_trigger():
    response = client.post("/api/scrape/trigger/worldbank")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "triggered"
    assert "run_id" in data
