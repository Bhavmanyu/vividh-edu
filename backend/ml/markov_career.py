"""
Markov Chain Career State Transition Model
==========================================
Models career progression as a discrete-time Markov chain where
states = { Fresher, Junior, Mid, Senior, Lead, Executive, Entrepreneur }

Each degree field has its own transition matrix calibrated from:
  - LinkedIn seniority data (scraped, Week 4)
  - AambitionBox experience-salary curves
  - PLFS employment surveys
  - Expert priors for medicine, law, and academia

Usage:
    model = CareerMarkovModel(field="engineering-cs")
    path = model.simulate(n_years=20, n_simulations=5000)
    # → DataFrame with probabilities at each year

Key output: state distribution at years 1, 3, 5, 10, 20
Used for: expected years to seniority, probability of hitting
          each salary tier, career volatility score
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# ── Career states ─────────────────────────────────────────────────────
STATES = ["Fresher", "Junior", "Mid", "Senior", "Lead", "Executive", "Entrepreneur", "Exit"]
STATE_IDX = {s: i for i, s in enumerate(STATES)}
N_STATES = len(STATES)

# ── Salary multipliers per state (relative to Fresher = 1.0) ─────────
# Source: AmbitionBox experience-salary analysis + PLFS
STATE_SALARY_MULT = {
    "Fresher":     1.0,
    "Junior":      1.6,
    "Mid":         2.8,
    "Senior":      5.0,
    "Lead":        9.0,
    "Executive":  18.0,
    "Entrepreneur": 5.0,   # high variance — median, not mean
    "Exit":        0.0,
}

# ── Annual transition matrices per field ──────────────────────────────
# Rows = from state, Cols = to state
# Row must sum to 1.0 (plus small rounding tolerance)
# Matrix is calibrated so avg time to Senior ≈ 8-10 years for CS IIT

TRANSITION_MATRICES: Dict[str, np.ndarray] = {}

# Engineering-CS (calibrated on IIT/NIT/private data)
TRANSITION_MATRICES["engineering-cs"] = np.array([
    # Fr     Jr     Mid    Sr     Lead   Exec   Entr   Exit
    [0.00,  0.85,  0.05,  0.00,  0.00,  0.00,  0.05,  0.05],  # Fresher
    [0.00,  0.40,  0.50,  0.03,  0.00,  0.00,  0.04,  0.03],  # Junior
    [0.00,  0.00,  0.45,  0.42,  0.04,  0.01,  0.05,  0.03],  # Mid
    [0.00,  0.00,  0.05,  0.50,  0.33,  0.05,  0.04,  0.03],  # Senior
    [0.00,  0.00,  0.00,  0.10,  0.55,  0.25,  0.05,  0.05],  # Lead
    [0.00,  0.00,  0.00,  0.00,  0.10,  0.75,  0.05,  0.10],  # Executive
    [0.00,  0.00,  0.00,  0.00,  0.00,  0.05,  0.88,  0.07],  # Entrepreneur
    [0.00,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00,  1.00],  # Exit (absorbing)
], dtype=np.float64)

# Medicine — slower progression, higher Exit due to residency/PG
TRANSITION_MATRICES["medicine"] = np.array([
    [0.00,  0.70,  0.10,  0.00,  0.00,  0.00,  0.00,  0.20],  # Fresher (residency)
    [0.00,  0.30,  0.55,  0.05,  0.00,  0.00,  0.02,  0.08],  # Junior
    [0.00,  0.00,  0.40,  0.45,  0.05,  0.02,  0.03,  0.05],  # Mid
    [0.00,  0.00,  0.05,  0.55,  0.28,  0.06,  0.03,  0.03],  # Senior
    [0.00,  0.00,  0.00,  0.10,  0.60,  0.22,  0.03,  0.05],  # Lead
    [0.00,  0.00,  0.00,  0.00,  0.10,  0.78,  0.02,  0.10],  # Executive
    [0.00,  0.00,  0.00,  0.00,  0.00,  0.02,  0.92,  0.06],  # Entrepreneur
    [0.00,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00,  1.00],  # Exit
], dtype=np.float64)

# Management (MBA) — faster to senior, high exit via entrepreneurship
TRANSITION_MATRICES["management"] = np.array([
    [0.00,  0.75,  0.08,  0.00,  0.00,  0.00,  0.08,  0.09],  # Fresher
    [0.00,  0.30,  0.48,  0.08,  0.02,  0.00,  0.07,  0.05],  # Junior
    [0.00,  0.00,  0.38,  0.44,  0.08,  0.02,  0.05,  0.03],  # Mid
    [0.00,  0.00,  0.05,  0.45,  0.32,  0.08,  0.06,  0.04],  # Senior
    [0.00,  0.00,  0.00,  0.08,  0.50,  0.28,  0.08,  0.06],  # Lead
    [0.00,  0.00,  0.00,  0.00,  0.08,  0.72,  0.10,  0.10],  # Executive
    [0.00,  0.00,  0.00,  0.00,  0.00,  0.05,  0.88,  0.07],  # Entrepreneur
    [0.00,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00,  1.00],  # Exit
], dtype=np.float64)

# Law — very slow progression, partnership-driven
TRANSITION_MATRICES["law"] = np.array([
    [0.00,  0.80,  0.06,  0.00,  0.00,  0.00,  0.05,  0.09],  # Fresher
    [0.00,  0.45,  0.42,  0.04,  0.00,  0.00,  0.04,  0.05],  # Junior
    [0.00,  0.00,  0.48,  0.38,  0.05,  0.01,  0.04,  0.04],  # Mid
    [0.00,  0.00,  0.06,  0.55,  0.28,  0.04,  0.04,  0.03],  # Senior
    [0.00,  0.00,  0.00,  0.12,  0.60,  0.18,  0.05,  0.05],  # Lead
    [0.00,  0.00,  0.00,  0.00,  0.12,  0.75,  0.03,  0.10],  # Executive
    [0.00,  0.00,  0.00,  0.00,  0.00,  0.02,  0.92,  0.06],  # Entrepreneur
    [0.00,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00,  1.00],  # Exit
], dtype=np.float64)

# Engineering non-CS — slower progression, high automation risk
TRANSITION_MATRICES["engineering-non-cs"] = np.array([
    [0.00,  0.80,  0.07,  0.00,  0.00,  0.00,  0.04,  0.09],  # Fresher
    [0.00,  0.45,  0.42,  0.04,  0.00,  0.00,  0.04,  0.05],  # Junior
    [0.00,  0.00,  0.50,  0.36,  0.05,  0.01,  0.04,  0.04],  # Mid
    [0.00,  0.00,  0.08,  0.55,  0.25,  0.04,  0.04,  0.04],  # Senior
    [0.00,  0.00,  0.00,  0.14,  0.60,  0.16,  0.05,  0.05],  # Lead
    [0.00,  0.00,  0.00,  0.00,  0.14,  0.74,  0.02,  0.10],  # Executive
    [0.00,  0.00,  0.00,  0.00,  0.00,  0.02,  0.90,  0.08],  # Entrepreneur
    [0.00,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00,  1.00],  # Exit
], dtype=np.float64)

# Default (commerce, design, social-sciences, arts)
TRANSITION_MATRICES["default"] = np.array([
    [0.00,  0.78,  0.06,  0.00,  0.00,  0.00,  0.05,  0.11],
    [0.00,  0.42,  0.44,  0.04,  0.00,  0.00,  0.05,  0.05],
    [0.00,  0.00,  0.48,  0.36,  0.06,  0.01,  0.05,  0.04],
    [0.00,  0.00,  0.07,  0.53,  0.28,  0.04,  0.04,  0.04],
    [0.00,  0.00,  0.00,  0.12,  0.58,  0.20,  0.05,  0.05],
    [0.00,  0.00,  0.00,  0.00,  0.12,  0.73,  0.05,  0.10],
    [0.00,  0.00,  0.00,  0.00,  0.00,  0.03,  0.90,  0.07],
    [0.00,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00,  1.00],
], dtype=np.float64)

# Tier adjustment: better tier → faster progression
TIER_SPEED_MULTIPLIER = {"1": 1.15, "2": 1.0, "3": 0.88}


class CareerMarkovModel:
    """
    Simulates career state distributions using Monte Carlo + Markov transitions.
    """

    def __init__(self, field: str = "engineering-cs", tier: str = "1"):
        field_key = field if field in TRANSITION_MATRICES else "default"
        self.T = TRANSITION_MATRICES[field_key].copy()
        self.field = field
        self.tier = tier

        # Apply tier speed multiplier by scaling transition rows
        speed = TIER_SPEED_MULTIPLIER.get(tier, 1.0)
        self._apply_tier_adjustment(speed)

    def _apply_tier_adjustment(self, speed: float):
        """
        Speed > 1 shifts probability mass from stay-in-state to next-state.
        Simplified: increase off-diagonal transitions proportionally.
        """
        for i in range(len(STATES) - 1):  # not Exit row
            diag = self.T[i, i]
            if diag > 0:
                shift = diag * min(0.15, abs(speed - 1.0))
                if speed > 1.0:
                    # Move some probability from stay to forward
                    next_state = min(i + 1, N_STATES - 2)
                    self.T[i, i] = max(0, diag - shift)
                    self.T[i, next_state] += shift
                else:
                    # Slower: shift back to stay
                    next_state = min(i + 1, N_STATES - 2)
                    actual_shift = min(shift, self.T[i, next_state])
                    self.T[i, next_state] = max(0, self.T[i, next_state] - actual_shift)
                    self.T[i, i] += actual_shift

            # Re-normalise row
            row_sum = self.T[i].sum()
            if row_sum > 0:
                self.T[i] /= row_sum

    def simulate(
        self,
        n_years: int = 20,
        n_simulations: int = 5000,
        start_state: str = "Fresher",
    ) -> pd.DataFrame:
        """
        Monte Carlo simulation. Returns DataFrame:
            columns = STATES, index = year (0..n_years)
            values = probability of being in each state at each year
        """
        start_idx = STATE_IDX[start_state]
        state_counts = np.zeros((n_years + 1, N_STATES), dtype=np.int32)

        # Batch simulate using vectorised random choices
        current_states = np.full(n_simulations, start_idx, dtype=np.int32)
        state_counts[0, start_idx] = n_simulations

        for year in range(1, n_years + 1):
            next_states = np.zeros(n_simulations, dtype=np.int32)
            for state in range(N_STATES):
                mask = current_states == state
                n = mask.sum()
                if n > 0:
                    transitions = self.T[state]
                    next_states[mask] = np.random.choice(N_STATES, size=n, p=transitions)
            current_states = next_states
            for s in range(N_STATES):
                state_counts[year, s] = (current_states == s).sum()

        probs = state_counts / n_simulations
        return pd.DataFrame(probs, columns=STATES, index=range(n_years + 1))

    def expected_time_to_state(self, target_state: str, n_years: int = 20) -> float:
        """
        Expected years to first reach target_state.
        Returns n_years + 1 if not reached within horizon.
        """
        dist = self.simulate(n_years=n_years, n_simulations=3000)
        cumulative = dist[target_state].cumsum()
        threshold_50 = cumulative[cumulative >= 0.5]
        if len(threshold_50) == 0:
            return float(n_years + 1)
        return float(threshold_50.index[0])

    def salary_trajectory(
        self,
        base_salary_y1: int,
        n_years: int = 20,
        n_simulations: int = 5000,
    ) -> Dict[str, Dict[str, int]]:
        """
        Project salary trajectory using state distributions × salary multipliers.
        Returns {y1, y3, y5, y10, y15, y20} each with {p10, p25, p50, p75, p90}.
        """
        dist = self.simulate(n_years=n_years, n_simulations=n_simulations)

        # For each year, compute expected salary weighted by state probabilities
        result = {}
        checkpoints = [1, 3, 5, 10, 15, 20]

        for year in checkpoints:
            if year > n_years:
                continue
            year_dist = dist.iloc[year]

            # Expected state for this year (weighted by probability)
            expected_mult = sum(
                year_dist[state] * STATE_SALARY_MULT[state]
                for state in STATES
                if state != "Exit"
            )

            # Simulate salary distribution using Markov state probs
            samples = []
            for _ in range(1000):
                state_probs = year_dist[STATES].values
                state_probs = np.maximum(state_probs, 0)
                state_probs = state_probs / state_probs.sum()
                sampled_state = np.random.choice(STATES, p=state_probs)
                mult = STATE_SALARY_MULT[sampled_state]
                # Add log-normal noise within state
                noise = np.random.lognormal(0, 0.25)
                samples.append(base_salary_y1 * mult * noise)

            samples = np.array(samples)
            result[f"y{year}"] = {
                "p10": int(np.percentile(samples, 10)),
                "p25": int(np.percentile(samples, 25)),
                "p50": int(np.percentile(samples, 50)),
                "p75": int(np.percentile(samples, 75)),
                "p90": int(np.percentile(samples, 90)),
            }

        return result

    def career_risk_score(self, n_years: int = 10) -> float:
        """
        Career risk = probability of being in Exit state within n_years.
        0 = no risk, 1 = guaranteed exit.
        """
        dist = self.simulate(n_years=n_years, n_simulations=2000)
        exit_probs = dist["Exit"].values
        return float(exit_probs[-1])

    def to_api_dict(
        self,
        base_salary_y1: int,
        program_name: str = "",
    ) -> Dict:
        """Full output for API /colleges/{id} endpoint."""
        trajectory = self.salary_trajectory(base_salary_y1, n_simulations=2000)
        exit_risk = self.career_risk_score()
        time_to_senior = self.expected_time_to_state("Senior")

        dist = self.simulate(n_years=20, n_simulations=2000)

        return {
            "field": self.field,
            "tier": self.tier,
            "trajectory": trajectory,
            "exit_risk_10yr": round(exit_risk, 3),
            "expected_years_to_senior": round(time_to_senior, 1),
            "state_distribution_at_10yr": {
                state: round(float(dist.iloc[10][state]), 3)
                for state in STATES
            },
            "state_distribution_at_20yr": {
                state: round(float(dist.iloc[20][state]), 3)
                for state in STATES
            },
        }
