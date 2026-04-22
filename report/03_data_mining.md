# Stage 4: Data Mining
**MIS502 Final Project — AI's Impact on the Job Market**
**Points: 25 | Status: Complete — ILO 2025 GenAI columns present in dataset but excluded from models (see overview note)**

---

## Overview

Two machine learning techniques are applied to the merged dataset of 606 occupations:
1. **K-Means Clustering** — segments occupations into groups by automation exposure and adaptive capacity
2. **Linear Regression** — tests whether automation risk predicts employment change and quantifies the effect

Both techniques run on `data/processed/cleaned_main.csv`. Output is saved to `data/processed/clustered.csv` and `figures/`.

> **Note on dataset expansion:** `cleaned_main.csv` now includes `genai_exposure_2025` and `genai_exposure_2023` columns from the ILO 2025 GenAI Exposure Index (Gmyrek et al.). These columns are used in the "Then vs. Now" visualization stage (Stage 5) but are intentionally excluded from the clustering and regression models here. Reason: including a 2025-era variable alongside a 2013-era variable would conflate two different AI eras and obscure the Automation Paradox finding. The mining models represent the 2013-baseline analysis; the GenAI columns add a comparative layer in visualization.

---

## Technique A: K-Means Clustering

### What It Is

K-Means is an unsupervised machine learning algorithm that groups data points into k clusters by minimizing the distance between each point and its cluster's center (centroid). It does not require labeled outcomes — it discovers structure in the data.

**In plain language:** Given a list of occupations described by automation risk and adaptive capacity scores, K-Means asks: "Which occupations are most similar to each other?" It finds natural groupings without being told in advance what the groups should be.

### Why It Was Chosen

The central research question is not just "which jobs are at risk" but "which jobs are at risk *and* have no safety net." K-Means can discover this cluster structure directly from the data rather than imposing a manual definition.

### Features Used

| Feature | Why Included |
|---|---|
| `automation_prob` | Core measure of AI displacement risk |
| `adaptive_capacity_score` | Composite of wage + education (ability to absorb disruption) |
| `wage_norm` | Normalized median wage — economic resilience signal |
| `edu_norm` | Normalized education level — retraining capacity |

All features were standardized (mean=0, std=1) before clustering to prevent high-magnitude features from dominating.

### Choosing k — The Elbow Method

The elbow method runs K-Means for k = 2 through 9 and plots inertia (within-cluster sum of squares). The "elbow" — where adding more clusters produces diminishing improvement — occurs at k=4. After comparing interpretability across k=3 and k=4, k=3 was chosen for the final model: the additional cluster at k=4 did not represent a meaningfully distinct occupational profile. All three final clusters are fully separable and substantively interpretable.

*See `figures/fig_elbow.png`*

### Results

*Note: Clustering ran on 600 occupations (6 excluded due to missing `median_wage_2024`, which is required for `adaptive_capacity_score`). Percentages are of the 600 clustered occupations.*

| Cluster | Size | Avg Automation Prob | Avg Adaptive Capacity | Avg Employment Change % | Avg Median Wage |
|---|---|---|---|---|---|
| **High Risk / Low Resilience** | 305 (50.8%) | 0.851 | 0.113 | −1.75% | $49,287 |
| **Low Risk / Stable** | 225 (37.5%) | 0.271 | 0.155 | +2.58% | $66,965 |
| **Low Risk / High Skill** | 70 (11.7%) | 0.090 | 0.625 | +5.51% | $126,322 |

Representative occupations by cluster: **High Risk / Low Resilience** — data entry clerks, cashiers, telemarketers, assembly workers, office clerks. **Low Risk / Stable** — social workers, electricians, firefighters, physical therapists. **Low Risk / High Skill** — software developers, physicians, nurse practitioners, financial managers. The wage gap between the bottom and top clusters is 2.6×: $49,287 vs. $126,322.

### Benchmark Comparison

The "High Risk / Low Resilience" cluster profile closely matches the Brookings Institution's characterization of 6.1 million vulnerable US workers: high AI exposure (50–82%), low adaptive capacity (<37%), concentrated in clerical and administrative occupations. Our cluster shows 85% automation probability and 11.3% adaptive capacity — consistent with but more extreme than the Brookings benchmark, likely because our cluster includes only the most matched occupations rather than the full workforce.

*See `figures/fig_clusters_scatter.png` and `figures/fig_clusters_profile.png`*

---

## Technique B: Linear Regression

### What It Is

Linear regression estimates the relationship between a target variable and one or more predictor variables by fitting a straight line (or hyperplane) through the data. The model produces coefficients showing how much the target changes per unit increase in each predictor.

**In plain language:** If we know an occupation's automation risk and adaptive capacity score, how accurately can we predict its projected employment change? And which factor matters most?

### Why It Was Chosen

Regression directly tests H1 and H2: Is automation risk negatively associated with employment change? How strong is that relationship? Does adaptive capacity improve the prediction?

### Model Specification

**Target variable:** `emp_change_pct` (BLS projected employment change 2024–2034, in %)

**Predictor variables:**
- `automation_prob` — Frey & Osborne automation probability
- `adaptive_capacity_score` — composite wage + education score
- `wage_norm` — normalized wage (separated from adaptive capacity for coefficient interpretation)
- `edu_norm` — normalized education level
- Occupation group dummy variables (21 dummies, one dropped as baseline)

**Train/test split:** 80% training, 20% test (random seed = 42 for reproducibility)

### Results

| Metric | Value |
|---|---|
| R² (test set) | 0.175 |
| R² (train set) | 0.400 |
| Mean Absolute Error | 4.32 percentage points |

> **Note on the train/test gap:** The 0.225-point gap between train R² (0.40) and test R² (0.175) indicates that the 21 occupation-group dummies are overfitting on the training set (~480 rows). The dummies provide structural signal — Computer & Math occupations show +12.4pp growth independent of other features, while Office & Admin Support shows −7.8pp — but they absorb variance that doesn't generalize perfectly. The test R² (0.175) is the appropriate figure for reporting predictive accuracy.

**Coefficient table (key features):**

| Feature | Coefficient | Interpretation |
|---|---|---|
| `automation_prob` | **−4.15** | Each 10pp increase in automation probability → −0.42pp employment change |
| `adaptive_capacity_score` | **+1.04** | Higher adaptive capacity associated with stronger job growth |
| `wage_norm` | **+1.36** | Higher wages independently associated with employment growth |
| `edu_norm` | **+0.72** | Higher education requirements associated with stronger growth |

**Largest occupation-group dummy coefficients** (relative to Architecture & Engineering baseline):

| Occupation Group | Dummy Coefficient | Direction |
|---|---|---|
| Computer & Math | +12.4 | Strongest positive effect — high structural growth independent of other features |
| Healthcare Support | +5.8 | |
| Healthcare Practitioners | +2.6 | |
| Office & Admin Support | −7.8 | Strongest negative effect — structural decline beyond automation risk alone |
| Production | −6.9 | |
| Education & Library | −5.5 | |

The occupation-group dummies confirm that sector membership carries structural information beyond what automation risk and wages capture. Computer & Math's +12.4 coefficient means these occupations are projected to grow ~12 percentage points faster than the baseline even holding automation risk, wages, and education equal — reflecting AI-driven demand for tech roles.

### Interpretation

**H1 is confirmed: automation risk negatively predicts employment change.** The coefficient of −4.15 on `automation_prob` is statistically meaningful and directionally consistent with displacement theory. An occupation moving from 0% to 100% automation probability is associated with ~4.15 percentage points lower employment growth.

**H2 is also confirmed: automation risk alone is a weak predictor.** R² = 0.175 means the model (even with all four features plus occupation group dummies) explains only 17.5% of the variance in employment change. This is consistent with the Automation Paradox hypothesis — other forces (labor demand, sector growth, regulatory change, technology complementarity) drive most of the variation.

**Benchmark comparison:** Anthropic's March 2026 research found −0.6 percentage points of job-finding rate reduction per 10 percentage point increase in AI task coverage. Our regression produces −0.42pp employment change per 10pp automation probability increase — similar in sign and order of magnitude, though not directly comparable (different definitions of AI exposure and different time horizons).

*See `figures/fig_regression.png`*

---

## Summary of Findings

| Hypothesis | Result |
|---|---|
| H1: Automation risk negatively correlates with job growth | ✅ Confirmed (r = −0.414, coefficient = −4.15) |
| H2: Automation risk alone is a weak predictor | ✅ Confirmed (R² = 0.175) |
| H3: Adaptive capacity separates vulnerable from resilient | ✅ Confirmed (mean wage: $41,503 vs. $72,293; cluster separation) |

The data mining stage establishes that automation risk *matters* but is far from deterministic. Where workers land in the labor market depends heavily on whether they have the education and wages to adapt — a finding with direct policy implications.
