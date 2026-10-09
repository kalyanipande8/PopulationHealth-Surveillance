"""Export real computed outputs (trends, center comparisons, disparities)
to the JSON the D3.js dashboard reads."""
from __future__ import annotations

import json
import os

import pandas as pd

from .simulate_surveillance import OUTCOMES, QUARTERS, CENTERS
from .trend_analysis import overall_trends, trends_by_center
from .disparity_detection import detect_disparities, top_disparities


def export(df: pd.DataFrame, out_path: str = "dashboard/dashboard_data.json") -> None:
    overall = overall_trends(df)
    by_center = trends_by_center(df)
    disparities = detect_disparities(df, most_recent_quarter=QUARTERS[-1])
    top3 = top_disparities(disparities, n=3)

    quarterly_by_outcome = {
        outcome: df.groupby("quarter")[outcome].mean().reindex(QUARTERS).round(4).to_dict()
        for outcome in OUTCOMES
    }

    center_snapshot = (
        df[df["quarter"] == QUARTERS[-1]]
        .groupby("center")[OUTCOMES].mean().round(4)
        .reset_index().to_dict(orient="records")
    )

    payload = {
        "quarters": QUARTERS,
        "outcomes": OUTCOMES,
        "centers": CENTERS,
        "quarterly_rates_by_outcome": quarterly_by_outcome,
        "overall_trends": overall.to_dict(orient="records"),
        "center_snapshot_latest_quarter": center_snapshot,
        "top_disparities": top3.to_dict(orient="records"),
        "n_significant_disparities_found": int(disparities["significant"].sum()),
        "n_comparisons_tested": len(disparities),
    }

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    from .simulate_surveillance import simulate

    export(simulate())
