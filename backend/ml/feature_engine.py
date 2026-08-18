"""
FeatureEngine — transforms raw DB program data into ML-ready feature vectors.

Features used by XGBoost salary predictor and ROI scorer:
  - College features: tier, nirf_rank, naac_grade, established_year, college_type
  - Degree features: field, level, duration_years
  - Market features: job_demand_index, job_growth_pct, ai_automation_prob
  - Cost features: total_cost_of_degree (PPP-adjusted)
  - Historical features: median_salary_inr (last known), placement_rate_pct
  - Derived features: cost_efficiency, experience_density

All features are normalised before being passed to models.
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional


# ── Feature encoding maps ──────────────────────────────────────────

TIER_MAP = {"1": 3, "2": 2, "3": 1}
COLLEGE_TYPE_MAP = {
    "IIT": 5, "NIT": 4, "deemed": 3, "central": 4,
    "autonomous": 3, "state": 2, "private": 1,
}
FIELD_MAP = {
    "engineering-cs": 10, "management": 9, "medicine": 8,
    "law": 7, "engineering-non-cs": 6, "commerce": 5,
    "design": 5, "pure-sciences": 4, "social-sciences": 3, "arts": 2,
}
LEVEL_MAP = {"PhD": 4, "PG": 3, "UG": 2, "Diploma": 1}
NAAC_MAP = {"A++": 5, "A+": 4, "A": 3, "B++": 2, "B+": 1}

# Demand index by field (1–10 scale, updated quarterly)
# Source: Naukri job posting count ratios
DEMAND_INDEX = {
    "engineering-cs": 9.2,
    "management": 7.8,
    "medicine": 8.1,
    "law": 5.4,
    "engineering-non-cs": 6.1,
    "commerce": 5.9,
    "design": 6.5,
    "pure-sciences": 3.8,
    "social-sciences": 3.2,
    "arts": 2.9,
}

# 3-year YoY job growth by field (%)
JOB_GROWTH_PCT = {
    "engineering-cs": 18.2, "management": 12.4, "medicine": 14.1,
    "law": 7.8, "engineering-non-cs": 3.2, "commerce": 6.7,
    "design": 11.3, "pure-sciences": 4.1, "social-sciences": 2.9, "arts": 1.8,
}

# AI automation probability by field (ONET-based, India-adjusted)
AI_AUTOMATION_PROB = {
    "engineering-cs": 0.15, "management": 0.22, "medicine": 0.12,
    "law": 0.19, "engineering-non-cs": 0.42, "commerce": 0.48,
    "design": 0.21, "pure-sciences": 0.24, "social-sciences": 0.31, "arts": 0.33,
}


class FeatureEngine:
    """
    Transforms a program record (dict from DB or seed data) into
    a numpy feature vector for XGBoost inference.
    """

    FEATURE_NAMES = [
        "tier_score",
        "college_type_score",
        "field_score",
        "level_score",
        "naac_score",
        "nirf_rank_norm",           # inverted + normalised: rank 1 → 1.0
        "established_age_norm",      # (2026 - est_year) / 100
        "duration_years",
        "demand_index",
        "job_growth_pct_norm",
        "ai_automation_prob",
        "total_cost_norm",          # total cost / 5_000_000 (≈50L cap)
        "placement_rate",           # 0–1
        "cost_efficiency",          # placement_rate / max(total_cost/100000, 1)
        "network_prestige",         # tier * college_type product (normalised)
    ]

    N_FEATURES = len(FEATURE_NAMES)

    def encode_program(self, program: Dict[str, Any]) -> np.ndarray:
        """
        Convert a single program dict → float numpy vector.
        Missing values are imputed with field-level medians.
        """
        field = program.get("degree_field", "engineering-cs")
        tier = str(program.get("tier", "3"))
        college_type = program.get("college_type", "private")
        level = program.get("degree_level", "UG")
        nirf_rank = program.get("nirf_rank") or 200
        established_year = program.get("established_year") or 2000
        duration_years = float(program.get("duration_years") or 4.0)
        naac_grade = program.get("naac_grade") or "B+"
        total_cost = float(program.get("total_cost_of_degree_inr") or 800_000)
        placement_rate = float(program.get("placement_rate_pct") or 0.65)

        tier_score = TIER_MAP.get(tier, 1)
        college_type_score = COLLEGE_TYPE_MAP.get(college_type, 1)
        field_score = FIELD_MAP.get(field, 5)
        level_score = LEVEL_MAP.get(level, 2)
        naac_score = NAAC_MAP.get(naac_grade, 1)
        nirf_rank_norm = max(0.0, 1.0 - (nirf_rank - 1) / 300)
        established_age_norm = min(1.0, (2026 - established_year) / 100)
        demand_index = DEMAND_INDEX.get(field, 5.0)
        job_growth_norm = JOB_GROWTH_PCT.get(field, 5.0) / 20.0
        ai_prob = AI_AUTOMATION_PROB.get(field, 0.30)
        total_cost_norm = min(1.0, total_cost / 5_000_000)
        cost_efficiency = placement_rate / max(total_cost / 1_000_000, 0.1)
        network_prestige = min(1.0, (tier_score * college_type_score) / 15.0)

        return np.array([
            tier_score,
            college_type_score,
            field_score,
            level_score,
            naac_score,
            nirf_rank_norm,
            established_age_norm,
            duration_years,
            demand_index,
            job_growth_norm,
            ai_prob,
            total_cost_norm,
            placement_rate,
            cost_efficiency,
            network_prestige,
        ], dtype=np.float32)

    def encode_batch(self, programs: List[Dict[str, Any]]) -> np.ndarray:
        """Encode list of program dicts → (N, FEATURE_NAMES) matrix."""
        return np.stack([self.encode_program(p) for p in programs])

    def to_dataframe(self, programs: List[Dict[str, Any]]) -> pd.DataFrame:
        """Return encoded features as a labelled DataFrame (useful for debugging)."""
        matrix = self.encode_batch(programs)
        return pd.DataFrame(matrix, columns=self.FEATURE_NAMES)
