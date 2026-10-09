# Population Health Surveillance & Outcome Metrics Tracking

A longitudinal surveillance system tracking 5 health outcomes across 8
health centers over 4 quarters, with real quarterly trend analysis,
statistically tested health-disparity detection, and a D3.js population
health metrics dashboard.

> Designed a longitudinal surveillance system for 5 health outcomes;
> tracked 2,480 patient-quarter records (620 patients) across 8 health
> centers. Built a population health metrics dashboard; statistically
> tested 85 subgroup comparisons and flagged 21 significant disparities,
> surfacing the top 3 by effect size as requiring targeted intervention.

## What's real vs. synthetic — read this first

**Real:** the trend analysis (linear regression on real quarterly rates),
and the disparity detection (two-proportion z-tests via `statsmodels`,
ranked by statistical significance and effect size) are genuinely computed
by `run_all.py` actually running — every number below is measured, not
assumed. The dashboard reads real exported output, not placeholder data.

**Synthetic:** there is no real 8-center, 2,400+ record healthcare
surveillance dataset in this environment. The cohort
(`src/simulate_surveillance.py`) is simulated with deliberately built-in
disparities — 2 under-resourced centers (Center-3, Center-7) with worse
outcomes across the board, and an insurance-status access disparity
(uninsured and Medicaid patients systematically worse outcomes) — so the
disparity-detection step has genuine signal to find. The specific "3"
disparities in the headline summary are the *top 3 by effect size* out of
21 that were actually found significant (p<0.01, risk difference ≥8
percentage points) across all 85 subgroup comparisons tested — a ranked,
honestly-reported selection, not a pre-decided narrative.

## Scientific approach

1. **Longitudinal simulation** (`src/simulate_surveillance.py`): 620
   patients × 4 quarters = 2,480 records, 8 centers, 5 outcomes (diabetes
   control, hypertension control, obesity screening completion, tobacco-free
   status, depression-screen-negative rate), with center-level and
   insurance-status disparities built into the data-generating process.

2. **Trend analysis** (`src/trend_analysis.py`): linear-regression trend
   slope and p-value per outcome, overall and by center, across the 4
   quarters — a real statistical trend test, not a qualitative "looks
   improving" read.

3. **Disparity detection** (`src/disparity_detection.py`): for every
   (outcome, subgroup) pair across 3 dimensions (center, race/ethnicity,
   insurance), a two-proportion z-test compares the subgroup's latest-
   quarter rate against the rest of the population, flagged significant at
   p<0.01 and a risk difference of at least 8 percentage points. Results
   are ranked by effect size, and the top 3 are surfaced as requiring
   targeted intervention.

4. **Dashboard** (`dashboard/index.html`): a real D3.js (v7) dashboard —
   quarterly trend lines for all 5 outcomes, a latest-quarter center
   comparison bar chart, and the top-3 disparity table — reading
   `dashboard/dashboard_data.json`, exported directly from the pipeline's
   real outputs by `src/export_dashboard_data.py`.

## Results (real, from `run_all.py`, seed=37)

```
2,480 patient-quarter records, 620 patients, 8 centers, 4 quarters, 5 outcomes

85 subgroup comparisons tested (5 outcomes x 17 subgroups across
3 dimensions: center, race/ethnicity, insurance)
21 flagged significant (p<0.01, |risk difference| >= 8pp)

Top 3 disparities by effect size:
  1. Diabetes in control, Center-7:     -30.4pp vs. rest of population, p<0.0001
  2. Tobacco-free status, Center-3:     -27.6pp vs. rest of population, p<0.0001
  3. Obesity screening, Center-7:       -25.9pp vs. rest of population, p=0.000003
```

Both deliberately under-resourced centers (Center-3, Center-7) surface
independently in the top disparities, and the insurance-status access
disparity is also detected (confirmed by
`test_insurance_disparity_detected`) even though it didn't make the top 3
by raw effect size — worth mentioning if asked, since access disparities
by payer type are often a more actionable intervention target than
center-level quality gaps.

`tests/test_pipeline.py` (8 tests, all passing) checks: 2,400+ records,
8 centers/4 quarters/5 outcomes, one record per patient per quarter, trend
coverage of all outcomes and center×outcome pairs, that the built-in center
disparity is actually detected, that top disparities are a subset of the
significant ones, and that the insurance-status disparity is detected.

## Usage

```bash
pip install -r requirements.txt
python3 run_all.py                       # simulates, computes trends/disparities, exports dashboard data
python3 -m pytest tests/ -v                # run the test suite
python3 -m http.server 8000 --directory dashboard  # view the dashboard at localhost:8000
```

Outputs are written to `data/surveillance_records.csv` and `results/*.csv`/`.json`.

## Project structure

```
src/
  simulate_surveillance.py    # 8-center, 4-quarter, 5-outcome longitudinal simulation
  trend_analysis.py             # linear-regression quarterly trends, overall and by center
  disparity_detection.py          # two-proportion z-tests, ranked by significance and effect size
  export_dashboard_data.py          # exports real pipeline outputs to dashboard JSON
dashboard/
  index.html                          # real D3.js dashboard
run_all.py                                # end-to-end pipeline
tests/test_pipeline.py                      # pytest suite
```

## Tech stack

Python 3.11, scipy/statsmodels (statistical tests), pandas, numpy, D3.js v7, pytest.

## Limitations

- No real multi-center surveillance dataset is used — all data is
  simulated with a realistic but synthetic disparity structure.
- Disparity detection uses a simple two-proportion z-test per subgroup
  without multiple-comparison correction (e.g. Bonferroni/FDR) across the
  85 tests run — a real surveillance system at this comparison volume
  would need one, flagged here as a next step rather than silently applied
  after seeing how many tests came back significant.
- The "top 3" headline figure is a ranking choice (top 3 by effect size),
  not evidence that exactly 3 disparities exist — 21 were found significant
  in total, reported transparently.
