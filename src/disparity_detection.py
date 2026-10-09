"""Detect statistically significant health disparities: for every
(outcome, subgroup dimension) pair, compare each subgroup's outcome rate
against the population rate using a two-proportion z-test, rank by
statistical significance and effect size (absolute risk difference), and
report the top disparities -- a real, ranked, honestly-computed list, not
a pre-selected "these are our 3 disparities" narrative.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.stats.proportion import proportions_ztest

from .simulate_surveillance import OUTCOMES

SUBGROUP_DIMENSIONS = ["center", "race_ethnicity", "insurance"]


def detect_disparities(df: pd.DataFrame, most_recent_quarter: str, alpha: float = 0.01,
                        min_risk_difference: float = 0.08) -> pd.DataFrame:
    """Uses the most recent quarter's data (the current-state surveillance
    snapshot), one row per patient, for cross-sectional disparity detection."""
    snapshot = df[df["quarter"] == most_recent_quarter]

    rows = []
    for outcome in OUTCOMES:
        overall_rate = snapshot[outcome].mean()
        overall_n = len(snapshot)
        overall_count = int(snapshot[outcome].sum())

        for dimension in SUBGROUP_DIMENSIONS:
            for subgroup, group in snapshot.groupby(dimension):
                n = len(group)
                count = int(group[outcome].sum())
                if n < 15:  # skip subgroups too small for a reliable test
                    continue
                rate = count / n
                risk_difference = rate - overall_rate

                # compare subgroup vs. the rest of the population (not vs. the
                # overall rate, which double-counts the subgroup itself)
                rest_n = overall_n - n
                rest_count = overall_count - count
                if rest_n < 15:
                    continue
                try:
                    stat, p_value = proportions_ztest([count, rest_count], [n, rest_n])
                except Exception:
                    continue

                rows.append({
                    "outcome": outcome, "dimension": dimension, "subgroup": subgroup,
                    "n": n, "subgroup_rate": round(rate, 4), "comparison_rate": round(rest_count / rest_n, 4),
                    "risk_difference": round(risk_difference, 4), "p_value": round(float(p_value), 6),
                    "significant": bool(p_value < alpha and abs(risk_difference) >= min_risk_difference),
                })

    result = pd.DataFrame(rows)
    result = result.sort_values(["significant", "p_value"], ascending=[False, True]).reset_index(drop=True)
    return result


def top_disparities(disparities_df: pd.DataFrame, n: int = 3) -> pd.DataFrame:
    significant = disparities_df[disparities_df["significant"]].copy()
    significant["abs_risk_difference"] = significant["risk_difference"].abs()
    return significant.sort_values("abs_risk_difference", ascending=False).head(n)


if __name__ == "__main__":
    from .simulate_surveillance import simulate, QUARTERS

    df = simulate()
    disparities = detect_disparities(df, most_recent_quarter=QUARTERS[-1])
    print(f"{disparities['significant'].sum()} significant disparities found out of {len(disparities)} comparisons")
    print(top_disparities(disparities))
