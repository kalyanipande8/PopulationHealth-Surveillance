"""End-to-end pipeline: simulate the longitudinal surveillance dataset,
compute trends, detect disparities, and export dashboard data."""
import json
import os

from src.simulate_surveillance import simulate, OUTCOMES, CENTERS, QUARTERS
from src.trend_analysis import overall_trends, trends_by_center
from src.disparity_detection import detect_disparities, top_disparities
from src.export_dashboard_data import export

os.makedirs("data", exist_ok=True)
os.makedirs("results", exist_ok=True)

print("=== Simulating longitudinal surveillance dataset ===")
df = simulate()
df.to_csv("data/surveillance_records.csv", index=False)
print(f"{len(df)} patient-quarter records, {df['patient_id'].nunique()} patients, "
      f"{len(CENTERS)} centers, {len(QUARTERS)} quarters, {len(OUTCOMES)} outcomes")

print("\n=== Overall quarterly trends ===")
overall = overall_trends(df)
print(overall)
overall.to_csv("results/overall_trends.csv", index=False)

print("\n=== Trends by center ===")
by_center = trends_by_center(df)
by_center.to_csv("results/trends_by_center.csv", index=False)

print("\n=== Disparity detection (most recent quarter) ===")
disparities = detect_disparities(df, most_recent_quarter=QUARTERS[-1])
disparities.to_csv("results/all_disparity_comparisons.csv", index=False)
n_significant = int(disparities["significant"].sum())
print(f"{n_significant} significant disparities found out of {len(disparities)} comparisons tested")

top3 = top_disparities(disparities, n=3)
print("\nTop 3 disparities by effect size:")
print(top3[["outcome", "dimension", "subgroup", "subgroup_rate", "comparison_rate", "risk_difference", "p_value"]])

print("\n=== Exporting dashboard data ===")
export(df)

summary = {
    "n_records": len(df),
    "n_patients": int(df["patient_id"].nunique()),
    "n_centers": len(CENTERS),
    "n_quarters": len(QUARTERS),
    "n_outcomes": len(OUTCOMES),
    "n_disparity_comparisons_tested": len(disparities),
    "n_significant_disparities_found": n_significant,
    "top_3_disparities": top3[["outcome", "dimension", "subgroup", "risk_difference", "p_value"]].to_dict(orient="records"),
}
with open("results/summary.json", "w") as f:
    json.dump(summary, f, indent=2, default=str)

print("\n=== Summary ===")
print(json.dumps(summary, indent=2, default=str))
