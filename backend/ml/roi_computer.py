"""
ROI Score Computer
==================
Computes the composite ROI score for each program from constituent sub-scores.

Formula (transparent, auditable):
  composite = (
      0.30 × financial_roi_normalised +
      0.20 × optionality_score +
      0.15 × mobility_score +
      0.15 × (1 - risk_score) +
      0.10 × satisfaction_score +
      0.10 × network_score
  ) × 100

All sub-scores are computed from ML model outputs and scraped data.
The methodology page (frontend) renders these weights live.

Financial ROI formula:
  NPV_lifetime_earnings - NPV_education_costs
  ─────────────────────────────────────────────
          NPV_education_costs

Where NPV is computed using 8% discount rate (real, inflation-adjusted)
over 20-year horizon.
"""
import numpy as np
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# ── Weights (must sum to 1.0) ─────────────────────────────────────────
WEIGHTS = {
    "financial_roi":   0.30,
    "optionality":     0.20,
    "mobility":        0.15,
    "safety":          0.15,   # (1 - risk_score)
    "satisfaction":    0.10,
    "network":         0.10,
}
assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9

DISCOUNT_RATE = 0.08   # real annual discount rate for NPV
INCOME_TAX_RATE = 0.25 # effective marginal rate (India 2026 new regime)


def _npv(annual_salaries: list, discount_rate: float = DISCOUNT_RATE) -> float:
    """Compute NPV of a salary stream (Year 1 = first payment)."""
    npv = 0.0
    for t, salary in enumerate(annual_salaries, start=1):
        npv += salary / ((1 + discount_rate) ** t)
    return npv


def _compute_financial_roi(
    trajectory: Dict[str, Dict],
    total_cost_inr: float,
    duration_years: float,
    opportunity_cost_annual: float = 300_000,   # foregone income during study (₹3L/yr)
) -> float:
    """
    Compute financial ROI as (NPV_net_earnings - NPV_total_investment) / NPV_total_investment × 100.
    Returns percentage (e.g. 200 means 200% ROI over 20 years).
    """
    # Build 20-year annual salary series from trajectory percentile midpoints
    annual_salaries = []
    for year in range(1, 21):
        key = f"y{year}"
        if key in trajectory:
            p50 = trajectory[key].get("p50", 0)
        else:
            # Interpolate from nearest checkpoints
            prev_key = f"y{max(1, year - (year % 5 or 5))}"
            next_key = f"y{min(20, year + (5 - year % 5))}"
            p50_prev = trajectory.get(prev_key, {}).get("p50", 0)
            p50_next = trajectory.get(next_key, {}).get("p50", p50_prev)
            p50 = (p50_prev + p50_next) / 2

        # Apply post-tax
        after_tax = p50 * (1 - INCOME_TAX_RATE)
        annual_salaries.append(after_tax)

    npv_earnings = _npv(annual_salaries)

    # Investment: tuition + living + opportunity cost during study
    total_investment = total_cost_inr + (opportunity_cost_annual * duration_years)
    npv_investment = total_investment   # already at t=0

    if npv_investment == 0:
        return 0.0

    roi_pct = (npv_earnings - npv_investment) / npv_investment * 100
    return round(roi_pct, 1)


def _compute_optionality(
    degree_field: str,
    tier: str,
    college_type: str,
) -> float:
    """
    Optionality = number of career paths available / max observed.
    Based on degree field diversity mapping + tier network effects.
    """
    field_optionality = {
        "engineering-cs": 0.95,
        "management": 0.90,
        "medicine": 0.72,
        "law": 0.74,
        "engineering-non-cs": 0.65,
        "design": 0.70,
        "commerce": 0.62,
        "pure-sciences": 0.55,
        "social-sciences": 0.50,
        "arts": 0.45,
    }
    base = field_optionality.get(degree_field, 0.60)
    tier_boost = {"1": 0.08, "2": 0.0, "3": -0.05}.get(tier, 0.0)
    college_boost = {"IIT": 0.05, "autonomous": 0.04, "NIT": 0.03}.get(college_type, 0.0)
    return min(1.0, base + tier_boost + college_boost)


def _compute_mobility(
    state: str,
    geographic_concentration: float,
    field: str,
) -> float:
    """
    Geographic + role mobility.
    High mobility = you can work in many cities + roles.
    """
    field_mobility = {
        "engineering-cs": 0.95,   # fully remote-capable
        "management": 0.88,
        "design": 0.82,
        "commerce": 0.72,
        "law": 0.55,               # bar council state-specific
        "medicine": 0.60,          # MCI registration + hospital-tied
        "engineering-non-cs": 0.65,
        "pure-sciences": 0.55,
        "social-sciences": 0.50,
        "arts": 0.45,
    }
    base = field_mobility.get(field, 0.65)
    # Geographic concentration: high concentration → lower mobility
    mobility = base * (1 - 0.30 * geographic_concentration)
    return max(0.0, min(1.0, mobility))


def _compute_satisfaction(
    placement_rate: float,
    work_life_quality: float,
    ai_automation_prob: float,
) -> float:
    """
    Composite satisfaction proxy from:
      - Placement rate (proxy for demand → job security → satisfaction)
      - WLB quality score
      - Low AI automation prob (job is meaningful / not yet commoditised)
    """
    return (0.40 * placement_rate +
            0.40 * work_life_quality +
            0.20 * (1 - ai_automation_prob))


def _compute_network(
    tier: str,
    college_type: str,
    nirf_rank: Optional[int],
) -> float:
    """Alumni network strength proxy."""
    tier_base = {"1": 0.90, "2": 0.65, "3": 0.40}.get(tier, 0.55)
    type_mod = {"IIT": 0.08, "NIT": 0.04, "autonomous": 0.06, "deemed": 0.02, "private": -0.05}.get(college_type, 0.0)
    rank_mod = 0.0
    if nirf_rank:
        if nirf_rank <= 10:   rank_mod = 0.05
        elif nirf_rank <= 50: rank_mod = 0.02
        elif nirf_rank > 150: rank_mod = -0.05
    return max(0.0, min(1.0, tier_base + type_mod + rank_mod))


def _compute_risk(
    ai_automation_prob: float,
    salary_volatility: float,
    industry_cyclicality: float,
    credential_inflation: float,
    geographic_concentration: float,
) -> float:
    """Composite risk = weighted average of risk factors. 0=safe, 1=high risk."""
    return (
        0.30 * ai_automation_prob +
        0.20 * salary_volatility +
        0.20 * industry_cyclicality +
        0.15 * credential_inflation +
        0.15 * geographic_concentration
    )


def _normalise_financial_roi(roi_pct: float) -> float:
    """Map financial ROI % to 0–1 scale. 300%+ → 1.0, 0% → 0.0."""
    return min(1.0, max(0.0, roi_pct / 300.0))


def compute_roi(
    program: Dict[str, Any],
    trajectory: Dict[str, Dict],
) -> Dict[str, Any]:
    """
    Master ROI computation. Takes program dict + salary trajectory.
    Returns full ROI score dict ready for DB insertion.

    Args:
        program: DB row from v_programs_full (or seed dict)
        trajectory: {y1, y5, y10, y20, ...} each with {p25, p50, p75, p90}

    Returns:
        Dict with composite_score, sub-scores, CI, model diagnostics
    """
    field = program.get("degree_field", "engineering-cs")
    tier = str(program.get("tier", "2"))
    college_type = program.get("college_type", "private")
    state = program.get("state", "Maharashtra")
    nirf_rank = program.get("nirf_rank")
    total_cost = float(program.get("total_cost_of_degree_inr") or 1_000_000)
    duration_years = float(program.get("duration_years") or 4.0)
    placement_rate = float(program.get("placement_rate_pct") or 0.65)
    ai_automation_prob = float(program.get("ai_automation_prob") or 0.30)
    salary_volatility = float(program.get("salary_volatility") or 0.20)
    industry_cyclicality = float(program.get("industry_cyclicality") or 0.22)
    credential_inflation = float(program.get("credential_inflation") or 0.18)
    geographic_concentration = float(program.get("geographic_concentration") or 0.25)
    work_life_quality = float(program.get("work_life_quality") or 0.70)

    # Compute sub-scores
    financial_roi_pct = _compute_financial_roi(trajectory, total_cost, duration_years)
    financial_roi_norm = _normalise_financial_roi(financial_roi_pct)
    optionality = _compute_optionality(field, tier, college_type)
    mobility = _compute_mobility(state, geographic_concentration, field)
    risk = _compute_risk(ai_automation_prob, salary_volatility, industry_cyclicality,
                         credential_inflation, geographic_concentration)
    satisfaction = _compute_satisfaction(placement_rate, work_life_quality, ai_automation_prob)
    network = _compute_network(tier, college_type, nirf_rank)

    # Composite score
    composite_raw = (
        WEIGHTS["financial_roi"]   * financial_roi_norm +
        WEIGHTS["optionality"]     * optionality +
        WEIGHTS["mobility"]        * mobility +
        WEIGHTS["safety"]          * (1 - risk) +
        WEIGHTS["satisfaction"]    * satisfaction +
        WEIGHTS["network"]         * network
    )
    composite_score = round(composite_raw * 100, 1)

    # Confidence interval based on data quality
    placement_confidence = min(1.0, placement_rate)
    trajectory_data_quality = 1.0 if "y1" in trajectory and "y20" in trajectory else 0.6
    overall_confidence = (placement_confidence + trajectory_data_quality) / 2

    ci_half_width = (1 - overall_confidence) * 15  # ±0–15 points
    ci_low = max(0, round(composite_score - ci_half_width, 1))
    ci_high = min(100, round(composite_score + ci_half_width, 1))

    confidence_level = "High" if overall_confidence > 0.8 else ("Medium" if overall_confidence > 0.5 else "Low")

    return {
        "composite_score": composite_score,
        "financial_roi_pct": financial_roi_pct,
        "risk_score": round(risk, 3),
        "optionality_score": round(optionality, 3),
        "mobility_score": round(mobility, 3),
        "satisfaction_score": round(satisfaction, 3),
        "network_score": round(network, 3),
        "ci_low": ci_low,
        "ci_high": ci_high,
        "confidence_level": confidence_level,
        "sub_scores": {
            "financial_roi_normalised": round(financial_roi_norm, 3),
            "optionality": round(optionality, 3),
            "mobility": round(mobility, 3),
            "safety": round(1 - risk, 3),
            "satisfaction": round(satisfaction, 3),
            "network": round(network, 3),
        },
        "formula_weights": WEIGHTS,
        "npv_inputs": {
            "discount_rate": DISCOUNT_RATE,
            "tax_rate": INCOME_TAX_RATE,
            "total_cost_inr": total_cost,
            "duration_years": duration_years,
        },
    }
