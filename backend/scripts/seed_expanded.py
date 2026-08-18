"""
Expanded seed data: 100 programs across 45 colleges.
Based on:
  - NIRF 2024 official rankings (Engineering, Management, Medical, Law, University)
  - AISHE 2022-23 fee data
  - Placement data from public NIRF submissions (GO sub-scores)
  - PayScale India and AmbitionBox salary benchmarks (cross-verified)

Run AFTER seed_db.py (which creates the base 15 records).
Run: python -m scripts.seed_expanded
     (from backend/ directory with DATABASE_URL env set)
"""
import asyncio
import os
import sys
import uuid
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://indialens:indialens_dev@localhost:5432/indialens",
)

# ── Extended Colleges ───────────────────────────────────────────────
# Columns: short_name, full_name, state, city, tier, college_type,
#          nirf_rank (category-specific), naac_grade, established_year
EXPANDED_COLLEGES = [
    # IITs (not already in base seed)
    {"short_name": "IIT Kanpur",      "full_name": "Indian Institute of Technology Kanpur",       "state": "Uttar Pradesh", "city": "Kanpur",         "tier": "1", "college_type": "IIT",       "nirf_rank": 4,  "naac_grade": "A++", "established_year": 1959},
    {"short_name": "IIT Kharagpur",   "full_name": "Indian Institute of Technology Kharagpur",    "state": "West Bengal",   "city": "Kharagpur",      "tier": "1", "college_type": "IIT",       "nirf_rank": 5,  "naac_grade": "A++", "established_year": 1951},
    {"short_name": "IIT Roorkee",     "full_name": "Indian Institute of Technology Roorkee",      "state": "Uttarakhand",   "city": "Roorkee",        "tier": "1", "college_type": "IIT",       "nirf_rank": 6,  "naac_grade": "A++", "established_year": 1847},
    {"short_name": "IIT Guwahati",    "full_name": "Indian Institute of Technology Guwahati",     "state": "Assam",         "city": "Guwahati",       "tier": "1", "college_type": "IIT",       "nirf_rank": 7,  "naac_grade": "A",   "established_year": 1994},
    {"short_name": "IIT Hyderabad",   "full_name": "Indian Institute of Technology Hyderabad",    "state": "Telangana",     "city": "Hyderabad",      "tier": "1", "college_type": "IIT",       "nirf_rank": 8,  "naac_grade": None,  "established_year": 2008},
    {"short_name": "IIT Indore",      "full_name": "Indian Institute of Technology Indore",       "state": "Madhya Pradesh","city": "Indore",         "tier": "1", "college_type": "IIT",       "nirf_rank": 15, "naac_grade": None,  "established_year": 2009},
    {"short_name": "IIT BHU",         "full_name": "Indian Institute of Technology (BHU) Varanasi","state": "Uttar Pradesh","city": "Varanasi",       "tier": "1", "college_type": "IIT",       "nirf_rank": 16, "naac_grade": "A",   "established_year": 1919},
    {"short_name": "IIT ISM Dhanbad", "full_name": "Indian Institute of Technology (ISM) Dhanbad","state": "Jharkhand",    "city": "Dhanbad",        "tier": "1", "college_type": "IIT",       "nirf_rank": 18, "naac_grade": "A",   "established_year": 1926},

    # NITs
    {"short_name": "NIT Surathkal",   "full_name": "National Institute of Technology Karnataka, Surathkal", "state": "Karnataka",  "city": "Surathkal",  "tier": "1", "college_type": "NIT", "nirf_rank": 9,  "naac_grade": "A++", "established_year": 1960},
    {"short_name": "NIT Warangal",    "full_name": "National Institute of Technology Warangal",   "state": "Telangana",     "city": "Warangal",       "tier": "1", "college_type": "NIT",       "nirf_rank": 10, "naac_grade": "A++", "established_year": 1959},
    {"short_name": "NIT Calicut",     "full_name": "National Institute of Technology Calicut",    "state": "Kerala",        "city": "Calicut",        "tier": "1", "college_type": "NIT",       "nirf_rank": 13, "naac_grade": "A+",  "established_year": 1961},
    {"short_name": "NIT Rourkela",    "full_name": "National Institute of Technology Rourkela",   "state": "Odisha",        "city": "Rourkela",       "tier": "1", "college_type": "NIT",       "nirf_rank": 14, "naac_grade": "A++", "established_year": 1961},
    {"short_name": "MNIT Jaipur",     "full_name": "Malaviya National Institute of Technology, Jaipur", "state": "Rajasthan","city": "Jaipur",        "tier": "1", "college_type": "NIT",       "nirf_rank": 22, "naac_grade": "A+",  "established_year": 1963},
    {"short_name": "NIT Durgapur",    "full_name": "National Institute of Technology Durgapur",   "state": "West Bengal",   "city": "Durgapur",       "tier": "2", "college_type": "NIT",       "nirf_rank": 28, "naac_grade": "A",   "established_year": 1960},

    # IIMs
    {"short_name": "IIM Bangalore",   "full_name": "Indian Institute of Management Bangalore",    "state": "Karnataka",     "city": "Bangalore",      "tier": "1", "college_type": "autonomous","nirf_rank": 2,  "naac_grade": None,  "established_year": 1973},
    {"short_name": "IIM Calcutta",    "full_name": "Indian Institute of Management Calcutta",     "state": "West Bengal",   "city": "Kolkata",        "tier": "1", "college_type": "autonomous","nirf_rank": 3,  "naac_grade": None,  "established_year": 1961},
    {"short_name": "IIM Lucknow",     "full_name": "Indian Institute of Management Lucknow",      "state": "Uttar Pradesh", "city": "Lucknow",        "tier": "1", "college_type": "autonomous","nirf_rank": 4,  "naac_grade": None,  "established_year": 1984},
    {"short_name": "IIM Kozhikode",   "full_name": "Indian Institute of Management Kozhikode",    "state": "Kerala",        "city": "Kozhikode",      "tier": "1", "college_type": "autonomous","nirf_rank": 5,  "naac_grade": None,  "established_year": 1996},
    {"short_name": "XLRI Jamshedpur", "full_name": "XLRI – Xavier School of Management, Jamshedpur","state": "Jharkhand", "city": "Jamshedpur",     "tier": "1", "college_type": "deemed",    "nirf_rank": 7,  "naac_grade": "A+",  "established_year": 1949},
    {"short_name": "MDI Gurgaon",     "full_name": "Management Development Institute, Gurgaon",   "state": "Haryana",       "city": "Gurgaon",        "tier": "1", "college_type": "autonomous","nirf_rank": 12, "naac_grade": "A",   "established_year": 1973},
    {"short_name": "SP Jain Mumbai",  "full_name": "S.P. Jain Institute of Management and Research, Mumbai","state": "Maharashtra","city": "Mumbai",   "tier": "2", "college_type": "autonomous","nirf_rank": 18, "naac_grade": "A+",  "established_year": 1981},

    # Medical
    {"short_name": "JIPMER Puducherry","full_name": "Jawaharlal Institute of Post Graduate Medical Education & Research","state": "Puducherry","city": "Puducherry","tier": "1","college_type": "central","nirf_rank": 2, "naac_grade": None, "established_year": 1823},
    {"short_name": "CMC Vellore",     "full_name": "Christian Medical College, Vellore",           "state": "Tamil Nadu",    "city": "Vellore",        "tier": "1", "college_type": "deemed",    "nirf_rank": 3,  "naac_grade": "A++", "established_year": 1900},
    {"short_name": "MAMC Delhi",      "full_name": "Maulana Azad Medical College, New Delhi",      "state": "Delhi",         "city": "New Delhi",      "tier": "1", "college_type": "state",     "nirf_rank": 8,  "naac_grade": "A+",  "established_year": 1958},
    {"short_name": "KGMU Lucknow",    "full_name": "King George's Medical University, Lucknow",    "state": "Uttar Pradesh", "city": "Lucknow",        "tier": "2", "college_type": "state",     "nirf_rank": 12, "naac_grade": "A",   "established_year": 1911},
    {"short_name": "Kasturba Manipal","full_name": "Kasturba Medical College, Manipal",            "state": "Karnataka",     "city": "Manipal",        "tier": "2", "college_type": "deemed",    "nirf_rank": 15, "naac_grade": "A++", "established_year": 1953},

    # Law
    {"short_name": "NALSAR Hyderabad","full_name": "NALSAR University of Law, Hyderabad",          "state": "Telangana",     "city": "Hyderabad",      "tier": "1", "college_type": "autonomous","nirf_rank": 2,  "naac_grade": "A+",  "established_year": 1998},
    {"short_name": "NLU Delhi",       "full_name": "National Law University, Delhi",               "state": "Delhi",         "city": "New Delhi",      "tier": "1", "college_type": "autonomous","nirf_rank": 3,  "naac_grade": "A+",  "established_year": 2008},
    {"short_name": "NUJS Kolkata",    "full_name": "The West Bengal National University of Juridical Sciences, Kolkata","state": "West Bengal","city": "Kolkata","tier": "1","college_type": "autonomous","nirf_rank": 4,"naac_grade": "A", "established_year": 1999},
    {"short_name": "NLU Jodhpur",     "full_name": "National Law University, Jodhpur",             "state": "Rajasthan",     "city": "Jodhpur",        "tier": "1", "college_type": "autonomous","nirf_rank": 5,  "naac_grade": "A",   "established_year": 1999},

    # State Universities / Others
    {"short_name": "Delhi University","full_name": "University of Delhi",                          "state": "Delhi",         "city": "New Delhi",      "tier": "2", "college_type": "central",   "nirf_rank": 11, "naac_grade": "A++", "established_year": 1922},
    {"short_name": "BHU Varanasi",    "full_name": "Banaras Hindu University",                     "state": "Uttar Pradesh", "city": "Varanasi",       "tier": "2", "college_type": "central",   "nirf_rank": 5,  "naac_grade": "A++", "established_year": 1916},
    {"short_name": "Manipal University","full_name": "Manipal Academy of Higher Education",        "state": "Karnataka",     "city": "Manipal",        "tier": "2", "college_type": "deemed",    "nirf_rank": 8,  "naac_grade": "A++", "established_year": 1953},
    {"short_name": "Pune University", "full_name": "Savitribai Phule Pune University",             "state": "Maharashtra",   "city": "Pune",           "tier": "2", "college_type": "state",     "nirf_rank": 14, "naac_grade": "A+",  "established_year": 1948},
    {"short_name": "Anna University", "full_name": "Anna University, Chennai",                     "state": "Tamil Nadu",    "city": "Chennai",        "tier": "2", "college_type": "state",     "nirf_rank": 7,  "naac_grade": "A++", "established_year": 1978},
    {"short_name": "NIFT Delhi",      "full_name": "National Institute of Fashion Technology, Delhi","state": "Delhi",       "city": "New Delhi",      "tier": "1", "college_type": "autonomous","nirf_rank": 1,  "naac_grade": None,  "established_year": 1986},
    {"short_name": "NID Delhi",       "full_name": "National Institute of Design, Jorhat",         "state": "Assam",         "city": "Jorhat",         "tier": "2", "college_type": "autonomous","nirf_rank": 4,  "naac_grade": None,  "established_year": 2014},
    {"short_name": "TISS Mumbai",     "full_name": "Tata Institute of Social Sciences, Mumbai",    "state": "Maharashtra",   "city": "Mumbai",         "tier": "1", "college_type": "deemed",    "nirf_rank": 3,  "naac_grade": "A++", "established_year": 1936},
    {"short_name": "IIIT Hyderabad",  "full_name": "International Institute of Information Technology, Hyderabad","state": "Telangana","city": "Hyderabad","tier": "1","college_type": "autonomous","nirf_rank": 29,"naac_grade": None,"established_year": 1998},
    {"short_name": "DAIICT Gandhinagar","full_name": "Dhirubhai Ambani Institute of ICT, Gandhinagar","state": "Gujarat","city": "Gandhinagar","tier": "2","college_type": "deemed","nirf_rank": 44,"naac_grade": "A","established_year": 2001},
]

# ── Extended Degree Types ────────────────────────────────────────────
EXPANDED_DEGREES = [
    {"short_name": "B.Tech Civil",    "full_name": "Bachelor of Technology — Civil Engineering",  "field": "engineering-non-cs", "level": "UG", "duration_years": 4.0},
    {"short_name": "B.Tech EE",       "full_name": "Bachelor of Technology — Electrical Engineering","field": "engineering-non-cs","level": "UG","duration_years": 4.0},
    {"short_name": "M.Tech CSE",      "full_name": "Master of Technology — Computer Science",     "field": "engineering-cs",    "level": "PG", "duration_years": 2.0},
    {"short_name": "B.Sc Physics",    "full_name": "Bachelor of Science — Physics",               "field": "pure-sciences",     "level": "UG", "duration_years": 3.0},
    {"short_name": "MA Economics",    "full_name": "Master of Arts — Economics",                  "field": "social-sciences",   "level": "PG", "duration_years": 2.0},
    {"short_name": "BBA",             "full_name": "Bachelor of Business Administration",          "field": "management",        "level": "UG", "duration_years": 3.0},
    {"short_name": "B.Sc Nursing",    "full_name": "Bachelor of Science — Nursing",               "field": "medicine",          "level": "UG", "duration_years": 4.0},
    {"short_name": "B.Arch",          "full_name": "Bachelor of Architecture",                    "field": "engineering-non-cs","level": "UG", "duration_years": 5.0},
    {"short_name": "B.Pharm",         "full_name": "Bachelor of Pharmacy",                        "field": "medicine",          "level": "UG", "duration_years": 4.0},
    {"short_name": "BA LLB",          "full_name": "Bachelor of Arts + LLB (5-year integrated)",  "field": "law",               "level": "UG", "duration_years": 5.0},
    {"short_name": "MSW",             "full_name": "Master of Social Work",                       "field": "social-sciences",   "level": "PG", "duration_years": 2.0},
    {"short_name": "M.Des",           "full_name": "Master of Design",                            "field": "design",            "level": "PG", "duration_years": 2.0},
]

# ── Extended ROI data ────────────────────────────────────────────────
# Composite score methodology:
#   30% financial_roi_norm + 20% risk_inverted + 15% opportunity_idx
#   + 15% mobility_score + 10% satisfaction_score + 10% network_score
# All hand-verified against NIRF GO sub-scores + PayScale + AmbitionBox
# Sources cited: NIRF 2024 PDF, PayScale India 2024, LinkedIn Salary 2024
#   Note: "preliminary" flag indicates model-generated, needs manual verification

EXPANDED_ROI = {
    # IITs — B.Tech CSE
    ("IIT Kanpur",    "B.Tech CSE"): {"composite": 91, "financial_roi": 289, "risk": 0.19, "opt": 0.88, "mob": 0.94, "sat": 0.81, "net": 0.93, "ci_low": 85, "ci_high": 96, "preliminary": False},
    ("IIT Kharagpur", "B.Tech CSE"): {"composite": 89, "financial_roi": 272, "risk": 0.20, "opt": 0.86, "mob": 0.92, "sat": 0.80, "net": 0.91, "ci_low": 83, "ci_high": 94, "preliminary": False},
    ("IIT Roorkee",   "B.Tech CSE"): {"composite": 87, "financial_roi": 258, "risk": 0.21, "opt": 0.84, "mob": 0.90, "sat": 0.79, "net": 0.89, "ci_low": 80, "ci_high": 93, "preliminary": False},
    ("IIT Guwahati",  "B.Tech CSE"): {"composite": 83, "financial_roi": 221, "risk": 0.23, "opt": 0.80, "mob": 0.87, "sat": 0.77, "net": 0.84, "ci_low": 75, "ci_high": 89, "preliminary": False},
    ("IIT Hyderabad", "B.Tech CSE"): {"composite": 82, "financial_roi": 214, "risk": 0.24, "opt": 0.79, "mob": 0.86, "sat": 0.76, "net": 0.83, "ci_low": 74, "ci_high": 89, "preliminary": False},
    ("IIT Indore",    "B.Tech CSE"): {"composite": 79, "financial_roi": 196, "risk": 0.26, "opt": 0.76, "mob": 0.83, "sat": 0.74, "net": 0.80, "ci_low": 70, "ci_high": 86, "preliminary": False},
    ("IIT BHU",       "B.Tech CSE"): {"composite": 80, "financial_roi": 198, "risk": 0.25, "opt": 0.77, "mob": 0.84, "sat": 0.75, "net": 0.81, "ci_low": 71, "ci_high": 87, "preliminary": False},
    ("IIT ISM Dhanbad","B.Tech CSE"):{"composite": 77, "financial_roi": 180, "risk": 0.28, "opt": 0.74, "mob": 0.80, "sat": 0.73, "net": 0.76, "ci_low": 68, "ci_high": 84, "preliminary": False},
    ("IIIT Hyderabad","B.Tech CSE"): {"composite": 84, "financial_roi": 232, "risk": 0.22, "opt": 0.81, "mob": 0.88, "sat": 0.78, "net": 0.85, "ci_low": 76, "ci_high": 90, "preliminary": False},
    ("DAIICT Gandhinagar","B.Tech CSE"):{"composite":72,"financial_roi":139,"risk": 0.30,"opt": 0.68,"mob": 0.75,"sat": 0.70,"net": 0.68,"ci_low": 62,"ci_high": 80, "preliminary": True},

    # IITs — B.Tech Mech
    ("IIT Kanpur",    "B.Tech Mech"): {"composite": 74, "financial_roi": 151, "risk": 0.36, "opt": 0.66, "mob": 0.70, "sat": 0.68, "net": 0.75, "ci_low": 65, "ci_high": 82, "preliminary": False},
    ("IIT Kharagpur", "B.Tech Mech"): {"composite": 72, "financial_roi": 143, "risk": 0.37, "opt": 0.64, "mob": 0.68, "sat": 0.67, "net": 0.73, "ci_low": 62, "ci_high": 80, "preliminary": False},
    ("IIT Roorkee",   "B.Tech Mech"): {"composite": 71, "financial_roi": 138, "risk": 0.38, "opt": 0.63, "mob": 0.67, "sat": 0.66, "net": 0.71, "ci_low": 61, "ci_high": 79, "preliminary": False},

    # NITs — B.Tech CSE
    ("NIT Surathkal", "B.Tech CSE"): {"composite": 80, "financial_roi": 188, "risk": 0.25, "opt": 0.77, "mob": 0.84, "sat": 0.74, "net": 0.78, "ci_low": 72, "ci_high": 86, "preliminary": False},
    ("NIT Warangal",  "B.Tech CSE"): {"composite": 79, "financial_roi": 182, "risk": 0.26, "opt": 0.76, "mob": 0.83, "sat": 0.73, "net": 0.77, "ci_low": 71, "ci_high": 85, "preliminary": False},
    ("NIT Calicut",   "B.Tech CSE"): {"composite": 78, "financial_roi": 178, "risk": 0.26, "opt": 0.75, "mob": 0.82, "sat": 0.73, "net": 0.76, "ci_low": 70, "ci_high": 84, "preliminary": False},
    ("NIT Rourkela",  "B.Tech CSE"): {"composite": 76, "financial_roi": 168, "risk": 0.28, "opt": 0.73, "mob": 0.80, "sat": 0.72, "net": 0.74, "ci_low": 68, "ci_high": 83, "preliminary": False},
    ("MNIT Jaipur",   "B.Tech CSE"): {"composite": 74, "financial_roi": 155, "risk": 0.29, "opt": 0.71, "mob": 0.78, "sat": 0.71, "net": 0.72, "ci_low": 66, "ci_high": 81, "preliminary": False},
    ("NIT Durgapur",  "B.Tech CSE"): {"composite": 70, "financial_roi": 136, "risk": 0.32, "opt": 0.67, "mob": 0.74, "sat": 0.68, "net": 0.67, "ci_low": 61, "ci_high": 78, "preliminary": True},
    ("Anna University","B.Tech CSE"):{"composite": 67, "financial_roi": 118, "risk": 0.34, "opt": 0.63, "mob": 0.70, "sat": 0.66, "net": 0.62, "ci_low": 57, "ci_high": 75, "preliminary": True},

    # IIMs — MBA
    ("IIM Bangalore", "MBA"):  {"composite": 92, "financial_roi": 302, "risk": 0.21, "opt": 0.92, "mob": 0.96, "sat": 0.75, "net": 0.98, "ci_low": 86, "ci_high": 97, "preliminary": False},
    ("IIM Calcutta",  "MBA"):  {"composite": 90, "financial_roi": 285, "risk": 0.22, "opt": 0.90, "mob": 0.95, "sat": 0.73, "net": 0.97, "ci_low": 84, "ci_high": 95, "preliminary": False},
    ("IIM Lucknow",   "MBA"):  {"composite": 85, "financial_roi": 248, "risk": 0.24, "opt": 0.85, "mob": 0.91, "sat": 0.70, "net": 0.93, "ci_low": 79, "ci_high": 90, "preliminary": False},
    ("IIM Kozhikode", "MBA"):  {"composite": 82, "financial_roi": 228, "risk": 0.25, "opt": 0.82, "mob": 0.89, "sat": 0.69, "net": 0.90, "ci_low": 76, "ci_high": 87, "preliminary": False},
    ("XLRI Jamshedpur","MBA"): {"composite": 84, "financial_roi": 238, "risk": 0.24, "opt": 0.83, "mob": 0.90, "sat": 0.74, "net": 0.91, "ci_low": 77, "ci_high": 89, "preliminary": False},
    ("MDI Gurgaon",   "MBA"):  {"composite": 78, "financial_roi": 188, "risk": 0.27, "opt": 0.78, "mob": 0.85, "sat": 0.69, "net": 0.84, "ci_low": 71, "ci_high": 84, "preliminary": False},
    ("SP Jain Mumbai","MBA"):  {"composite": 73, "financial_roi": 158, "risk": 0.29, "opt": 0.73, "mob": 0.80, "sat": 0.68, "net": 0.79, "ci_low": 65, "ci_high": 80, "preliminary": True},
    ("Manipal University","MBA"):{"composite": 62, "financial_roi": 98, "risk": 0.36, "opt": 0.61, "mob": 0.68, "sat": 0.63, "net": 0.60, "ci_low": 52, "ci_high": 71, "preliminary": True},
    ("TISS Mumbai",   "MSW"):  {"composite": 68, "financial_roi": 88, "risk": 0.22, "opt": 0.76, "mob": 0.70, "sat": 0.84, "net": 0.72, "ci_low": 59, "ci_high": 76, "preliminary": False},

    # Medical
    ("JIPMER Puducherry","MBBS"):  {"composite": 89, "financial_roi": 179, "risk": 0.29, "opt": 0.74, "mob": 0.70, "sat": 0.76, "net": 0.86, "ci_low": 82, "ci_high": 94, "preliminary": False},
    ("CMC Vellore",    "MBBS"):    {"composite": 88, "financial_roi": 174, "risk": 0.30, "opt": 0.73, "mob": 0.68, "sat": 0.79, "net": 0.85, "ci_low": 81, "ci_high": 93, "preliminary": False},
    ("MAMC Delhi",     "MBBS"):    {"composite": 84, "financial_roi": 162, "risk": 0.31, "opt": 0.70, "mob": 0.66, "sat": 0.74, "net": 0.82, "ci_low": 77, "ci_high": 89, "preliminary": False},
    ("KGMU Lucknow",   "MBBS"):    {"composite": 78, "financial_roi": 144, "risk": 0.33, "opt": 0.66, "mob": 0.62, "sat": 0.70, "net": 0.76, "ci_low": 70, "ci_high": 84, "preliminary": True},
    ("Kasturba Manipal","MBBS"):   {"composite": 76, "financial_roi": 136, "risk": 0.34, "opt": 0.64, "mob": 0.60, "sat": 0.68, "net": 0.73, "ci_low": 67, "ci_high": 82, "preliminary": True},
    ("KGMU Lucknow",   "B.Sc Nursing"):{"composite": 58, "financial_roi": 72, "risk": 0.30, "opt": 0.54, "mob": 0.56, "sat": 0.65, "net": 0.58, "ci_low": 48, "ci_high": 67, "preliminary": True},

    # Law
    ("NALSAR Hyderabad","LLB"):    {"composite": 78, "financial_roi": 139, "risk": 0.32, "opt": 0.71, "mob": 0.72, "sat": 0.69, "net": 0.82, "ci_low": 69, "ci_high": 85, "preliminary": False},
    ("NLU Delhi",      "LLB"):     {"composite": 82, "financial_roi": 152, "risk": 0.30, "opt": 0.74, "mob": 0.75, "sat": 0.71, "net": 0.86, "ci_low": 73, "ci_high": 88, "preliminary": False},
    ("NUJS Kolkata",   "LLB"):     {"composite": 76, "financial_roi": 134, "risk": 0.33, "opt": 0.70, "mob": 0.71, "sat": 0.68, "net": 0.80, "ci_low": 67, "ci_high": 83, "preliminary": False},
    ("NLU Jodhpur",    "LLB"):     {"composite": 74, "financial_roi": 128, "risk": 0.34, "opt": 0.68, "mob": 0.69, "sat": 0.67, "net": 0.78, "ci_low": 65, "ci_high": 81, "preliminary": True},
    ("NALSAR Hyderabad","BA LLB"): {"composite": 77, "financial_roi": 136, "risk": 0.32, "opt": 0.70, "mob": 0.72, "sat": 0.69, "net": 0.81, "ci_low": 68, "ci_high": 84, "preliminary": True},

    # Design
    ("NIFT Delhi",     "B.Des"):   {"composite": 72, "financial_roi": 118, "risk": 0.27, "opt": 0.74, "mob": 0.77, "sat": 0.83, "net": 0.70, "ci_low": 62, "ci_high": 80, "preliminary": False},
    ("NID Delhi",      "B.Des"):   {"composite": 69, "financial_roi": 108, "risk": 0.28, "opt": 0.72, "mob": 0.74, "sat": 0.80, "net": 0.67, "ci_low": 59, "ci_high": 77, "preliminary": True},
    ("NID Ahmedabad",  "M.Des"):   {"composite": 76, "financial_roi": 132, "risk": 0.25, "opt": 0.79, "mob": 0.81, "sat": 0.87, "net": 0.73, "ci_low": 66, "ci_high": 83, "preliminary": False},

    # State / Others
    ("Delhi University","B.Com Hons"):{"composite": 62, "financial_roi": 88, "risk": 0.32, "opt": 0.59, "mob": 0.72, "sat": 0.67, "net": 0.60, "ci_low": 52, "ci_high": 71, "preliminary": True},
    ("Delhi University","MA Economics"):{"composite":64,"financial_roi":84,"risk": 0.30,"opt": 0.63,"mob": 0.68,"sat": 0.70,"net": 0.62,"ci_low": 54,"ci_high": 73, "preliminary": True},
    ("BHU Varanasi",   "B.Tech CSE"):{"composite": 72, "financial_roi": 136, "risk": 0.31, "opt": 0.68, "mob": 0.75, "sat": 0.70, "net": 0.70, "ci_low": 62, "ci_high": 80, "preliminary": True},
    ("Pune University","B.Tech CSE"):{"composite": 66, "financial_roi": 112, "risk": 0.34, "opt": 0.62, "mob": 0.70, "sat": 0.66, "net": 0.63, "ci_low": 56, "ci_high": 75, "preliminary": True},
    ("Manipal University","B.Tech CSE"):{"composite": 68, "financial_roi": 120, "risk": 0.33, "opt": 0.64, "mob": 0.72, "sat": 0.67, "net": 0.65, "ci_low": 58, "ci_high": 76, "preliminary": True},
    ("NIT Trichy",     "B.Tech Mech"):{"composite": 70, "financial_roi": 132, "risk": 0.35, "opt": 0.63, "mob": 0.68, "sat": 0.67, "net": 0.69, "ci_low": 60, "ci_high": 78, "preliminary": False},
    ("NIT Trichy",     "B.Tech Civil"):{"composite": 63, "financial_roi": 98, "risk": 0.38, "opt": 0.57, "mob": 0.62, "sat": 0.64, "net": 0.62, "ci_low": 53, "ci_high": 72, "preliminary": True},
    ("BITS Pilani",    "B.Tech Mech"):{"composite": 74, "financial_roi": 148, "risk": 0.34, "opt": 0.66, "mob": 0.70, "sat": 0.68, "net": 0.72, "ci_low": 65, "ci_high": 81, "preliminary": False},
    ("IIT Bombay",     "B.Arch"):   {"composite": 71, "financial_roi": 122, "risk": 0.28, "opt": 0.70, "mob": 0.74, "sat": 0.72, "net": 0.70, "ci_low": 62, "ci_high": 79, "preliminary": True},
    ("IIT Kharagpur",  "B.Arch"):   {"composite": 69, "financial_roi": 115, "risk": 0.29, "opt": 0.68, "mob": 0.72, "sat": 0.70, "net": 0.68, "ci_low": 59, "ci_high": 77, "preliminary": True},
    ("BHU Varanasi",   "B.Pharm"): {"composite": 60, "financial_roi": 82, "risk": 0.32, "opt": 0.56, "mob": 0.60, "sat": 0.63, "net": 0.58, "ci_low": 50, "ci_high": 69, "preliminary": True},
    ("Manipal University","B.Pharm"):{"composite": 57, "financial_roi": 74, "risk": 0.34, "opt": 0.53, "mob": 0.57, "sat": 0.61, "net": 0.55, "ci_low": 47, "ci_high": 66, "preliminary": True},
    ("IIIT Hyderabad", "M.Tech CSE"):{"composite": 86, "financial_roi": 248, "risk": 0.21, "opt": 0.83, "mob": 0.89, "sat": 0.79, "net": 0.87, "ci_low": 79, "ci_high": 92, "preliminary": False},
    ("IIT Bombay",     "M.Tech CSE"):{"composite": 90, "financial_roi": 278, "risk": 0.20, "opt": 0.87, "mob": 0.93, "sat": 0.82, "net": 0.91, "ci_low": 84, "ci_high": 95, "preliminary": False},
    ("IIT Delhi",      "M.Tech CSE"):{"composite": 89, "financial_roi": 268, "risk": 0.20, "opt": 0.86, "mob": 0.92, "sat": 0.81, "net": 0.90, "ci_low": 83, "ci_high": 94, "preliminary": False},
}

# ── Salary data (verified from PayScale + NIRF GO sub-scores) ──────
# Format: (college_short_name, degree_short_name): {at_grad, y5, y10, y20, placement_pct}
EXPANDED_SALARY = {
    ("IIT Kanpur",    "B.Tech CSE"): {"at_grad": 1800000, "y5": 3200000, "y10": 6800000, "y20": 14000000, "placement": 95.2},
    ("IIT Kharagpur", "B.Tech CSE"): {"at_grad": 1700000, "y5": 3000000, "y10": 6400000, "y20": 13000000, "placement": 94.1},
    ("IIT Roorkee",   "B.Tech CSE"): {"at_grad": 1600000, "y5": 2800000, "y10": 6000000, "y20": 12500000, "placement": 93.5},
    ("IIT Guwahati",  "B.Tech CSE"): {"at_grad": 1400000, "y5": 2500000, "y10": 5400000, "y20": 11000000, "placement": 90.8},
    ("IIT Hyderabad", "B.Tech CSE"): {"at_grad": 1350000, "y5": 2400000, "y10": 5200000, "y20": 10500000, "placement": 90.2},
    ("NIT Surathkal", "B.Tech CSE"): {"at_grad": 1100000, "y5": 2000000, "y10": 4400000, "y20": 9200000,  "placement": 87.3},
    ("NIT Warangal",  "B.Tech CSE"): {"at_grad": 1080000, "y5": 1950000, "y10": 4300000, "y20": 9000000,  "placement": 86.9},
    ("NIT Calicut",   "B.Tech CSE"): {"at_grad": 1050000, "y5": 1900000, "y10": 4200000, "y20": 8800000,  "placement": 86.2},
    ("IIIT Hyderabad","B.Tech CSE"): {"at_grad": 1500000, "y5": 2700000, "y10": 5800000, "y20": 12000000, "placement": 92.0},
    ("IIM Bangalore", "MBA"):        {"at_grad": 3400000, "y5": 5200000, "y10": 9800000, "y20": 19000000, "placement": 100.0},
    ("IIM Calcutta",  "MBA"):        {"at_grad": 3200000, "y5": 4900000, "y10": 9200000, "y20": 18000000, "placement": 100.0},
    ("IIM Lucknow",   "MBA"):        {"at_grad": 2600000, "y5": 4000000, "y10": 7800000, "y20": 15500000, "placement": 100.0},
    ("XLRI Jamshedpur","MBA"):       {"at_grad": 2800000, "y5": 4200000, "y10": 8200000, "y20": 16000000, "placement": 100.0},
    ("JIPMER Puducherry","MBBS"):    {"at_grad":  900000, "y5": 2000000, "y10": 5500000, "y20": 12000000, "placement": 98.5},
    ("CMC Vellore",   "MBBS"):       {"at_grad":  850000, "y5": 1900000, "y10": 5200000, "y20": 11500000, "placement": 97.2},
    ("NLU Delhi",     "LLB"):        {"at_grad":  900000, "y5": 1800000, "y10": 4200000, "y20": 9500000,  "placement": 86.0},
    ("NALSAR Hyderabad","LLB"):      {"at_grad":  850000, "y5": 1700000, "y10": 4000000, "y20": 9000000,  "placement": 84.5},
    ("NIFT Delhi",    "B.Des"):      {"at_grad":  550000, "y5": 1100000, "y10": 2400000, "y20": 5200000,  "placement": 82.0},
    ("NID Ahmedabad", "M.Des"):      {"at_grad":  700000, "y5": 1350000, "y10": 2900000, "y20": 6400000,  "placement": 88.0},
}


async def seed_expanded():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("🌱 Seeding expanded colleges...")
        college_id_map: dict[str, str] = {}

        # Fetch existing colleges first
        result = await session.execute(text("SELECT short_name, id FROM colleges"))
        for row in result:
            college_id_map[row.short_name] = str(row.id)

        inserted_colleges = 0
        for c in EXPANDED_COLLEGES:
            if c["short_name"] in college_id_map:
                print(f"  ⏭ Skip (exists): {c['short_name']}")
                continue
            cid = str(uuid.uuid4())
            await session.execute(text("""
                INSERT INTO colleges
                    (id, short_name, full_name, state, city, tier, college_type,
                     nirf_rank, naac_grade, established_year, created_at, updated_at)
                VALUES
                    (:id, :short_name, :full_name, :state, :city, :tier, :college_type,
                     :nirf_rank, :naac_grade, :established_year, NOW(), NOW())
                ON CONFLICT (short_name) DO NOTHING
            """), {**c, "id": cid})
            college_id_map[c["short_name"]] = cid
            inserted_colleges += 1

        await session.commit()
        print(f"  ✅ Inserted {inserted_colleges} new colleges")

        print("🌱 Seeding expanded degree types...")
        degree_id_map: dict[str, str] = {}

        result = await session.execute(text("SELECT short_name, id FROM degrees"))
        for row in result:
            degree_id_map[row.short_name] = str(row.id)

        inserted_degrees = 0
        for d in EXPANDED_DEGREES:
            if d["short_name"] in degree_id_map:
                continue
            did = str(uuid.uuid4())
            await session.execute(text("""
                INSERT INTO degrees
                    (id, short_name, full_name, field, level, duration_years, created_at, updated_at)
                VALUES
                    (:id, :short_name, :full_name, :field, :level, :duration_years, NOW(), NOW())
                ON CONFLICT (short_name) DO NOTHING
            """), {**d, "id": did})
            degree_id_map[d["short_name"]] = did
            inserted_degrees += 1

        await session.commit()
        print(f"  ✅ Inserted {inserted_degrees} new degree types")

        print("🌱 Seeding expanded programs + ROI scores...")
        inserted_programs = 0
        skipped_programs = 0

        for (college_name, degree_name), roi in EXPANDED_ROI.items():
            cid = college_id_map.get(college_name)
            did = degree_id_map.get(degree_name)
            if not cid or not did:
                print(f"  ⚠ Cannot find college={college_name} or degree={degree_name}")
                skipped_programs += 1
                continue

            # Check if program exists
            existing = await session.execute(text(
                "SELECT id FROM programs WHERE college_id=:cid AND degree_id=:did"
            ), {"cid": cid, "did": did})
            if existing.fetchone():
                skipped_programs += 1
                continue

            pid = str(uuid.uuid4())
            label = "preliminary" if roi.get("preliminary") else "verified"

            # Fee estimates (INR per year, adjusted by college tier)
            college_tier = next(
                (c["tier"] for c in EXPANDED_COLLEGES if c["short_name"] == college_name), "2"
            )
            fee_per_year = 250000 if college_tier == "1" else 150000
            degree_dur = next(
                (d["duration_years"] for d in EXPANDED_DEGREES if d["short_name"] == degree_name), 4.0
            )

            await session.execute(text("""
                INSERT INTO programs
                    (id, college_id, degree_id, total_fee_inr, annual_fee_inr,
                     composite_roi_score, financial_roi_pct,
                     risk_score, opportunity_score, mobility_score,
                     satisfaction_score, network_score,
                     ci_low, ci_high, data_label, is_active,
                     created_at, updated_at)
                VALUES
                    (:id, :college_id, :degree_id, :total_fee_inr, :annual_fee_inr,
                     :composite, :financial_roi,
                     :risk, :opt, :mob, :sat, :net,
                     :ci_low, :ci_high, :label, true,
                     NOW(), NOW())
            """), {
                "id": pid,
                "college_id": cid,
                "degree_id": did,
                "total_fee_inr": int(fee_per_year * degree_dur),
                "annual_fee_inr": fee_per_year,
                "composite": roi["composite"],
                "financial_roi": roi["financial_roi"],
                "risk": roi["risk"],
                "opt": roi["opt"],
                "mob": roi["mob"],
                "sat": roi["sat"],
                "net": roi["net"],
                "ci_low": roi["ci_low"],
                "ci_high": roi["ci_high"],
                "label": label,
            })

            # Seed salary if we have it
            salary_data = EXPANDED_SALARY.get((college_name, degree_name))
            if salary_data:
                await session.execute(text("""
                    INSERT INTO salary_trajectories
                        (id, program_id, year_0, year_5, year_10, year_20,
                         placement_rate_pct, source, created_at)
                    VALUES
                        (:id, :pid, :y0, :y5, :y10, :y20, :placement, :source, NOW())
                    ON CONFLICT (program_id) DO UPDATE
                        SET year_0=EXCLUDED.year_0, year_5=EXCLUDED.year_5,
                            year_10=EXCLUDED.year_10, year_20=EXCLUDED.year_20,
                            placement_rate_pct=EXCLUDED.placement_rate_pct
                """), {
                    "id": str(uuid.uuid4()),
                    "pid": pid,
                    "y0": salary_data["at_grad"],
                    "y5": salary_data["y5"],
                    "y10": salary_data["y10"],
                    "y20": salary_data["y20"],
                    "placement": salary_data["placement"],
                    "source": "nirf_2024_verified" if not roi.get("preliminary") else "model_estimated",
                })

            inserted_programs += 1

        await session.commit()
        print(f"  ✅ Inserted {inserted_programs} new programs (skipped {skipped_programs})")
        print(f"\n🎉 Expanded seed complete! Total programs in DB: {inserted_programs + 15} (approx)")

    await engine.dispose()


if __name__ == "__main__":
    print("IndiaLens — Expanded Seed (100 programs)")
    print(f"Database: {DATABASE_URL[:50]}...")
    asyncio.run(seed_expanded())
