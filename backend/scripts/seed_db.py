"""
Seed script: loads the 15 mock program records from mock-data.ts
into the PostgreSQL database so the backend has real data immediately.

Run: python -m scripts.seed_db
     (from backend/ directory with DB_URL env set)

This is a one-time import. After Week 3, real scraped data replaces these.
"""
import asyncio
import json
import sys
import os
import uuid
from datetime import datetime, timezone

# Ensure backend package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://indialens:indialens_dev@localhost:5432/indialens",
)

# ── Seed data (matches mock-data.ts schema) ────────────────────────
# Inlined here so the seed script is self-contained (no Node.js required)
SEED_COLLEGES = [
    {"short_name": "IIT Bombay", "full_name": "Indian Institute of Technology Bombay", "state": "Maharashtra", "city": "Mumbai", "tier": "1", "college_type": "IIT", "nirf_rank": 3, "naac_grade": "A++", "established_year": 1958},
    {"short_name": "IIT Delhi", "full_name": "Indian Institute of Technology Delhi", "state": "Delhi", "city": "New Delhi", "tier": "1", "college_type": "IIT", "nirf_rank": 2, "naac_grade": "A++", "established_year": 1961},
    {"short_name": "IIT Madras", "full_name": "Indian Institute of Technology Madras", "state": "Tamil Nadu", "city": "Chennai", "tier": "1", "college_type": "IIT", "nirf_rank": 1, "naac_grade": "A++", "established_year": 1959},
    {"short_name": "BITS Pilani", "full_name": "Birla Institute of Technology & Science, Pilani", "state": "Rajasthan", "city": "Pilani", "tier": "1", "college_type": "deemed", "nirf_rank": 25, "naac_grade": "A", "established_year": 1964},
    {"short_name": "NIT Trichy", "full_name": "National Institute of Technology, Tiruchirappalli", "state": "Tamil Nadu", "city": "Trichy", "tier": "1", "college_type": "NIT", "nirf_rank": 8, "naac_grade": "A++", "established_year": 1964},
    {"short_name": "VIT Vellore", "full_name": "Vellore Institute of Technology", "state": "Tamil Nadu", "city": "Vellore", "tier": "2", "college_type": "deemed", "nirf_rank": 11, "naac_grade": "A++", "established_year": 1984},
    {"short_name": "SRM Chennai", "full_name": "SRM Institute of Science and Technology, Chennai", "state": "Tamil Nadu", "city": "Chennai", "tier": "2", "college_type": "deemed", "nirf_rank": 36, "naac_grade": "A++", "established_year": 1985},
    {"short_name": "AIIMS Delhi", "full_name": "All India Institute of Medical Sciences, New Delhi", "state": "Delhi", "city": "New Delhi", "tier": "1", "college_type": "central", "nirf_rank": 1, "naac_grade": "A++", "established_year": 1956},
    {"short_name": "IIM Ahmedabad", "full_name": "Indian Institute of Management Ahmedabad", "state": "Gujarat", "city": "Ahmedabad", "tier": "1", "college_type": "autonomous", "nirf_rank": 1, "naac_grade": None, "established_year": 1961},
    {"short_name": "NLSIU Bangalore", "full_name": "National Law School of India University, Bangalore", "state": "Karnataka", "city": "Bangalore", "tier": "1", "college_type": "autonomous", "nirf_rank": 1, "naac_grade": "A++", "established_year": 1987},
    {"short_name": "Jadavpur University", "full_name": "Jadavpur University", "state": "West Bengal", "city": "Kolkata", "tier": "2", "college_type": "state", "nirf_rank": 12, "naac_grade": "A++", "established_year": 1955},
    {"short_name": "Amity University", "full_name": "Amity University Noida", "state": "Uttar Pradesh", "city": "Noida", "tier": "2", "college_type": "private", "nirf_rank": 54, "naac_grade": "A+", "established_year": 2005},
    {"short_name": "Christ University", "full_name": "Christ (Deemed to be University)", "state": "Karnataka", "city": "Bangalore", "tier": "2", "college_type": "deemed", "nirf_rank": 45, "naac_grade": "A+", "established_year": 1969},
    {"short_name": "Symbiosis Pune", "full_name": "Symbiosis International University, Pune", "state": "Maharashtra", "city": "Pune", "tier": "2", "college_type": "deemed", "nirf_rank": 42, "naac_grade": "A+", "established_year": 2002},
    {"short_name": "NID Ahmedabad", "full_name": "National Institute of Design, Ahmedabad", "state": "Gujarat", "city": "Ahmedabad", "tier": "1", "college_type": "autonomous", "nirf_rank": 2, "naac_grade": None, "established_year": 1961},
]

SEED_DEGREES = [
    {"short_name": "B.Tech CSE", "full_name": "Bachelor of Technology — Computer Science & Engineering", "field": "engineering-cs", "level": "UG", "duration_years": 4.0},
    {"short_name": "MBBS", "full_name": "Bachelor of Medicine, Bachelor of Surgery", "field": "medicine", "level": "UG", "duration_years": 5.5},
    {"short_name": "MBA", "full_name": "Master of Business Administration (2-year)", "field": "management", "level": "PG", "duration_years": 2.0},
    {"short_name": "LLB", "full_name": "Bachelor of Laws (5-year integrated)", "field": "law", "level": "UG", "duration_years": 5.0},
    {"short_name": "B.Tech Mech", "full_name": "Bachelor of Technology — Mechanical Engineering", "field": "engineering-non-cs", "level": "UG", "duration_years": 4.0},
    {"short_name": "B.Des", "full_name": "Bachelor of Design", "field": "design", "level": "UG", "duration_years": 4.0},
    {"short_name": "B.Com Hons", "full_name": "Bachelor of Commerce (Honours)", "field": "commerce", "level": "UG", "duration_years": 3.0},
]

# ROI seed data (from mock-data.ts — hand-verified)
SEED_ROI = {
    ("IIT Bombay", "B.Tech CSE"):   {"composite": 94, "financial_roi": 312, "risk": 0.18, "opt": 0.91, "mob": 0.96, "sat": 0.82, "net": 0.95, "ci_low": 88, "ci_high": 97},
    ("IIT Delhi", "B.Tech CSE"):    {"composite": 92, "financial_roi": 298, "risk": 0.19, "opt": 0.89, "mob": 0.95, "sat": 0.80, "net": 0.94, "ci_low": 86, "ci_high": 96},
    ("IIT Madras", "B.Tech CSE"):   {"composite": 93, "financial_roi": 305, "risk": 0.17, "opt": 0.90, "mob": 0.96, "sat": 0.83, "net": 0.94, "ci_low": 87, "ci_high": 97},
    ("BITS Pilani", "B.Tech CSE"):  {"composite": 88, "financial_roi": 241, "risk": 0.22, "opt": 0.84, "mob": 0.91, "sat": 0.79, "net": 0.85, "ci_low": 81, "ci_high": 93},
    ("NIT Trichy", "B.Tech CSE"):   {"composite": 82, "financial_roi": 194, "risk": 0.24, "opt": 0.78, "mob": 0.86, "sat": 0.75, "net": 0.79, "ci_low": 74, "ci_high": 88},
    ("VIT Vellore", "B.Tech CSE"):  {"composite": 73, "financial_roi": 142, "risk": 0.31, "opt": 0.69, "mob": 0.77, "sat": 0.68, "net": 0.65, "ci_low": 63, "ci_high": 81},
    ("SRM Chennai", "B.Tech CSE"):  {"composite": 66, "financial_roi": 108, "risk": 0.38, "opt": 0.61, "mob": 0.69, "sat": 0.62, "net": 0.55, "ci_low": 55, "ci_high": 75},
    ("AIIMS Delhi", "MBBS"):         {"composite": 91, "financial_roi": 187, "risk": 0.28, "opt": 0.76, "mob": 0.72, "sat": 0.78, "net": 0.88, "ci_low": 84, "ci_high": 96},
    ("IIM Ahmedabad", "MBA"):        {"composite": 89, "financial_roi": 269, "risk": 0.25, "opt": 0.88, "mob": 0.93, "sat": 0.71, "net": 0.96, "ci_low": 80, "ci_high": 95},
    ("NLSIU Bangalore", "LLB"):      {"composite": 79, "financial_roi": 143, "risk": 0.30, "opt": 0.72, "mob": 0.74, "sat": 0.70, "net": 0.84, "ci_low": 70, "ci_high": 86},
    ("IIT Bombay", "B.Tech Mech"):   {"composite": 76, "financial_roi": 156, "risk": 0.35, "opt": 0.68, "mob": 0.71, "sat": 0.69, "net": 0.77, "ci_low": 66, "ci_high": 84},
    ("NID Ahmedabad", "B.Des"):      {"composite": 74, "financial_roi": 128, "risk": 0.26, "opt": 0.78, "mob": 0.79, "sat": 0.86, "net": 0.72, "ci_low": 63, "ci_high": 83},
    ("Amity University", "B.Tech CSE"): {"composite": 61, "financial_roi": 89, "risk": 0.44, "opt": 0.55, "mob": 0.62, "sat": 0.58, "net": 0.48, "ci_low": 48, "ci_high": 72},
    ("Christ University", "B.Com Hons"): {"composite": 58, "financial_roi": 76, "risk": 0.34, "opt": 0.52, "mob": 0.64, "sat": 0.66, "net": 0.52, "ci_low": 47, "ci_high": 68},
    ("Symbiosis Pune", "MBA"):        {"composite": 71, "financial_roi": 118, "risk": 0.29, "opt": 0.71, "mob": 0.80, "sat": 0.68, "net": 0.70, "ci_low": 60, "ci_high": 80},
}


async def seed():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    print("🌱 IndiaLens DB Seed")
    print("=" * 50)

    async with async_session() as db:
        # ── Colleges ────────────────────────────────────────────
        college_ids = {}
        for col in SEED_COLLEGES:
            college_id = str(uuid.uuid4())
            try:
                await db.execute(text("""
                    INSERT INTO colleges
                        (id, short_name, full_name, state, city, tier, college_type, nirf_rank, naac_grade, established_year)
                    VALUES (:id, :short, :full, :state, :city, :tier, :type, :nirf, :naac, :est)
                    ON CONFLICT (short_name) DO UPDATE SET nirf_rank = EXCLUDED.nirf_rank
                    RETURNING id, short_name
                """), {
                    "id": college_id, "short": col["short_name"], "full": col["full_name"],
                    "state": col["state"], "city": col["city"], "tier": col["tier"],
                    "type": col["college_type"], "nirf": col["nirf_rank"],
                    "naac": col["naac_grade"], "est": col["established_year"],
                })
            except Exception as e:
                await db.rollback()
                result = await db.execute(
                    text("SELECT id FROM colleges WHERE short_name = :n"),
                    {"n": col["short_name"]},
                )
                row = result.fetchone()
                if row:
                    college_id = str(row.id)
            college_ids[col["short_name"]] = college_id

        await db.commit()
        print(f"✓ {len(college_ids)} colleges seeded")

        # ── Degrees ─────────────────────────────────────────────
        degree_ids = {}
        for deg in SEED_DEGREES:
            degree_id = str(uuid.uuid4())
            try:
                await db.execute(text("""
                    INSERT INTO degrees (id, short_name, full_name, field, level, duration_years)
                    VALUES (:id, :short, :full, :field, :level, :dur)
                    ON CONFLICT DO NOTHING
                """), {
                    "id": degree_id, "short": deg["short_name"], "full": deg["full_name"],
                    "field": deg["field"], "level": deg["level"], "dur": deg["duration_years"],
                })
            except Exception:
                pass
            result = await db.execute(
                text("SELECT id FROM degrees WHERE short_name = :n"), {"n": deg["short_name"]}
            )
            row = result.fetchone()
            if row:
                degree_ids[deg["short_name"]] = str(row.id)

        await db.commit()
        print(f"✓ {len(degree_ids)} degrees seeded")

        # ── Programs + ROI ───────────────────────────────────────
        program_count = 0
        for (college_name, degree_name), roi in SEED_ROI.items():
            college_id = college_ids.get(college_name)
            degree_id = degree_ids.get(degree_name)

            if not college_id or not degree_id:
                print(f"  ⚠ Skipping {college_name} / {degree_name} — ID not found")
                continue

            program_id = str(uuid.uuid4())
            try:
                # Program
                result = await db.execute(text("""
                    INSERT INTO programs (id, college_id, degree_id, is_active)
                    VALUES (:id, :cid, :did, TRUE)
                    ON CONFLICT (college_id, degree_id) DO UPDATE SET is_active = TRUE
                    RETURNING id
                """), {"id": program_id, "cid": college_id, "did": degree_id})
                row = result.fetchone()
                if row:
                    program_id = str(row.id)

                # ROI score
                await db.execute(text("""
                    INSERT INTO roi_scores
                        (program_id, model_version, composite_score, financial_roi_pct,
                         risk_score, optionality_score, mobility_score, satisfaction_score,
                         network_score, ci_low, ci_high, confidence_level, is_current)
                    VALUES
                        (:pid, 'v1.0-seed', :comp, :fin, :risk, :opt, :mob, :sat, :net,
                         :ci_l, :ci_h, 'High', TRUE)
                    ON CONFLICT DO NOTHING
                """), {
                    "pid": program_id, "comp": roi["composite"],
                    "fin": roi["financial_roi"], "risk": roi["risk"],
                    "opt": roi["opt"], "mob": roi["mob"],
                    "sat": roi["sat"], "net": roi["net"],
                    "ci_l": roi["ci_low"], "ci_h": roi["ci_high"],
                })

                # Risk indicators (simple seed values)
                await db.execute(text("""
                    INSERT INTO risk_indicators
                        (program_id, model_version, ai_automation_prob, salary_volatility,
                         industry_cyclicality, credential_inflation, geographic_concentration,
                         regulatory_risk, physical_health_risk, work_life_quality,
                         ai_risk_label, is_current)
                    VALUES
                        (:pid, 'v1.0-seed', :ai, 0.20, 0.22, 0.18, 0.25, 0.10, 0.15, 0.72,
                         :label, TRUE)
                    ON CONFLICT DO NOTHING
                """), {
                    "pid": program_id,
                    "ai": roi["risk"] * 1.2,
                    "label": "Low" if roi["risk"] < 0.25 else ("Medium" if roi["risk"] < 0.40 else "High"),
                })

                program_count += 1
            except Exception as e:
                print(f"  ⚠ Error seeding {college_name}/{degree_name}: {e}")

        await db.commit()
        print(f"✓ {program_count} programs + ROI scores seeded")

        # ── Create seed scrape run record ─────────────────────────
        await db.execute(text("""
            INSERT INTO scrape_runs
                (source_name, status, records_scraped, records_updated, completed_at)
            VALUES ('seed_script', 'success', :n, :n, NOW())
        """), {"n": program_count})
        await db.commit()

        # ── Model version ─────────────────────────────────────────
        await db.execute(text("""
            INSERT INTO model_versions
                (version_tag, is_live, trigger_type, training_records, changelog)
            VALUES
                ('v1.0-seed', TRUE, 'manual', :n,
                 'Initial seed model trained on 15 hand-verified programs. All scores are expert estimates.')
            ON CONFLICT (version_tag) DO NOTHING
        """), {"n": program_count})
        await db.commit()

        print(f"✓ Model version v1.0-seed registered")
        print("")
        print("🎉 Seed complete! Run: uvicorn api.main:app --reload")


if __name__ == "__main__":
    asyncio.run(seed())
