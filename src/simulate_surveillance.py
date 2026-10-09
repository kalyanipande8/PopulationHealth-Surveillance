"""Simulate a longitudinal population-health surveillance dataset: 8 health
centers, 4 quarters, 5 tracked health outcomes, with realistic center-level
and subgroup-level disparities built in by construction (so the disparity
detection step has genuine, known signal to find -- not guaranteed to
surface as exactly the headline number, honestly reported either way).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

N_PATIENTS = 620
QUARTERS = ["2025-Q1", "2025-Q2", "2025-Q3", "2025-Q4"]
CENTERS = [f"Center-{i+1}" for i in range(8)]
OUTCOMES = [
    "diabetes_in_control",      # HbA1c < 8%
    "hypertension_in_control",  # BP < 140/90
    "obesity_screened",         # BMI screening completed
    "tobacco_free",             # non-smoker / cessation success
    "depression_screen_negative",  # PHQ-9 below clinical threshold
]
SEED = 37


def simulate(n_patients: int = N_PATIENTS, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    # per-center baseline quality (deliberately uneven -- 2 under-resourced
    # centers, reflecting real resource-disparity patterns)
    center_quality = {c: rng.normal(0, 0.35) for c in CENTERS}
    center_quality["Center-3"] -= 0.9  # under-resourced center: worse across the board
    center_quality["Center-7"] -= 0.6  # under-resourced center

    patients = []
    for i in range(n_patients):
        center = CENTERS[rng.integers(0, len(CENTERS))]
        race_ethnicity = rng.choice(
            ["White", "Black or African American", "Hispanic or Latino", "Asian", "Other/Unknown"],
            p=[0.45, 0.20, 0.22, 0.08, 0.05],
        )
        insurance = rng.choice(["Commercial", "Medicare", "Medicaid", "Uninsured"], p=[0.45, 0.25, 0.22, 0.08])
        age = rng.normal(52, 16, 1)[0].clip(18, 90)
        patients.append({
            "patient_id": f"PH-{i:05d}", "center": center,
            "race_ethnicity": race_ethnicity, "insurance": insurance, "age": round(float(age), 1),
        })
    patients_df = pd.DataFrame(patients)

    # subgroup effect: uninsured and Medicaid patients have systematically
    # worse outcomes across the board (a real, documented access disparity)
    insurance_effect = {"Commercial": 0.15, "Medicare": 0.10, "Medicaid": -0.25, "Uninsured": -0.55}

    rows = []
    for _, p in patients_df.iterrows():
        base = center_quality[p["center"]] + insurance_effect[p["insurance"]]
        for q_idx, quarter in enumerate(QUARTERS):
            # small overall secular improvement over the year (real programs
            # do shift metrics quarter over quarter, usually modestly)
            secular_trend = 0.05 * q_idx
            row = {"patient_id": p["patient_id"], "center": p["center"], "race_ethnicity": p["race_ethnicity"],
                   "insurance": p["insurance"], "age": p["age"], "quarter": quarter}
            for outcome in OUTCOMES:
                outcome_noise = rng.normal(0, 0.5)
                logit = -0.2 + base + secular_trend + outcome_noise
                prob = 1 / (1 + np.exp(-logit))
                row[outcome] = int(rng.random() < prob)
            rows.append(row)

    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = simulate()
    print(df.shape)
    print(df.groupby("center")[OUTCOMES].mean().round(3))
