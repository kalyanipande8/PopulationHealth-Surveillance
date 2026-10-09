"""Quarter-over-quarter trend analysis for each of the 5 tracked outcomes,
overall and by center -- real linear-regression trend slopes, not just a
visual "looks like it's improving" read."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from .simulate_surveillance import OUTCOMES, QUARTERS


def _quarter_index(df: pd.DataFrame) -> pd.Series:
    mapping = {q: i for i, q in enumerate(QUARTERS)}
    return df["quarter"].map(mapping)


def overall_trends(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for outcome in OUTCOMES:
        quarterly_rate = df.groupby("quarter")[outcome].mean().reindex(QUARTERS)
        x = np.arange(len(QUARTERS))
        slope, intercept, r, p, se = stats.linregress(x, quarterly_rate.values)
        rows.append({
            "outcome": outcome,
            "q1_rate": round(float(quarterly_rate.iloc[0]), 4),
            "q4_rate": round(float(quarterly_rate.iloc[-1]), 4),
            "absolute_change_q1_to_q4": round(float(quarterly_rate.iloc[-1] - quarterly_rate.iloc[0]), 4),
            "quarterly_slope": round(float(slope), 4),
            "trend_p_value": round(float(p), 5),
        })
    return pd.DataFrame(rows)


def trends_by_center(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for center, group in df.groupby("center"):
        for outcome in OUTCOMES:
            quarterly_rate = group.groupby("quarter")[outcome].mean().reindex(QUARTERS)
            x = np.arange(len(QUARTERS))
            slope, intercept, r, p, se = stats.linregress(x, quarterly_rate.values)
            rows.append({
                "center": center, "outcome": outcome,
                "q1_rate": round(float(quarterly_rate.iloc[0]), 4),
                "q4_rate": round(float(quarterly_rate.iloc[-1]), 4),
                "quarterly_slope": round(float(slope), 4),
            })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    from .simulate_surveillance import simulate

    df = simulate()
    print(overall_trends(df))
