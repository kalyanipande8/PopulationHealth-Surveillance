import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from src.simulate_surveillance import simulate, OUTCOMES, CENTERS, QUARTERS
from src.trend_analysis import overall_trends, trends_by_center
from src.disparity_detection import detect_disparities, top_disparities


@pytest.fixture(scope="module")
def df():
    return simulate()


def test_dataset_has_2400_plus_records(df):
    assert len(df) >= 2400


def test_eight_centers_four_quarters_five_outcomes(df):
    assert df["center"].nunique() == 8
    assert set(df["center"].unique()) == set(CENTERS)
    assert df["quarter"].nunique() == 4
    assert len(OUTCOMES) == 5


def test_each_patient_has_one_record_per_quarter(df):
    counts = df.groupby("patient_id").size()
    assert (counts == 4).all()


def test_overall_trends_cover_all_outcomes(df):
    trends = overall_trends(df)
    assert set(trends["outcome"]) == set(OUTCOMES)


def test_trends_by_center_cover_all_center_outcome_pairs(df):
    trends = trends_by_center(df)
    assert len(trends) == len(CENTERS) * len(OUTCOMES)


def test_disparity_detection_finds_the_built_in_center_disparity(df):
    """Center-3 and Center-7 are deliberately under-resourced in the
    simulation -- the disparity detector should flag at least one of them
    as significantly worse on at least one outcome."""
    disparities = detect_disparities(df, most_recent_quarter=QUARTERS[-1])
    flagged_centers = set(
        disparities.loc[(disparities["significant"]) & (disparities["dimension"] == "center"), "subgroup"]
    )
    assert "Center-3" in flagged_centers or "Center-7" in flagged_centers


def test_top_disparities_are_a_subset_of_significant_ones(df):
    disparities = detect_disparities(df, most_recent_quarter=QUARTERS[-1])
    top3 = top_disparities(disparities, n=3)
    assert len(top3) <= 3
    assert top3["significant"].all()


def test_insurance_disparity_detected(df):
    """Uninsured/Medicaid patients have a built-in access disparity --
    confirm it's detectable in at least one outcome."""
    disparities = detect_disparities(df, most_recent_quarter=QUARTERS[-1])
    insurance_disparities = disparities[
        (disparities["dimension"] == "insurance") & (disparities["significant"])
    ]
    assert len(insurance_disparities) > 0
