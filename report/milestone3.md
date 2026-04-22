# Milestone 3 — Data Preparation, Mining, and Visualization
**MIS502 Final Project — AI's Impact on the Job Market**
**Taya Yakovenko | Total Points: 75 (25 + 25 + 25) | Status: Complete**

---

# Stage 3: Data Preparation / Data Wrangling
**Points: 25**

---

## 1. All Steps and Outcomes

> **Note on dataset selection:** A synthetic Kaggle dataset (*AI Impact on Job Market, 2024–2030*) was considered but set aside before wrangling began. Preliminary inspection showed near-zero cross-variable correlations (r ≈ 0.001–0.012), indicating that all numeric fields — automation risk, salary, employment change — were generated independently with no relationship to each other. A dataset with no internal signal cannot produce meaningful findings. The pipeline below uses three real-world, institutionally sourced datasets instead.

### Step 1 — Load Raw Data

Four raw files are loaded:
- `data/raw/frey_osborne_automation_scores.csv` — semicolon-delimited, UTF-8 BOM encoded, 702 rows
- `data/raw/bls_occupational_projections_2024_2034.xlsx` — Excel file, Table 1.2, header on row 2
- `data/raw/ilo_genai_exposure_2025.xlsx` — ILO/Gmyrek et al. 2025, task-level rows (3,265 rows, 427 unique ISCO-08 occupations)
- `data/raw/bls_isco_soc_crosswalk.xls` — BLS ISCO-08 × SOC 2010 crosswalk, header on row 7

```python
fo = pd.read_csv("data/raw/frey_osborne_automation_scores.csv", sep=";", encoding="utf-8-sig")
xl = pd.ExcelFile("data/raw/bls_occupational_projections_2024_2034.xlsx")
bls_raw = xl.parse("Table 1.2", header=1)
```

### Step 2 — Rename Columns

All columns are renamed to snake_case for consistency and to remove special characters from BLS column names (which include em-dashes in the year range).

### Step 3 — Filter BLS to Line-Item Occupations

BLS Table 1.2 includes both summary rows (major groups, subgroups) and line-item occupations. Only line-item rows are retained for analysis, reducing 1,117 rows to 832 detailed occupations.

```python
bls = bls[bls["occ_type"] == "Line item"].copy()
```

### Step 4 — Handle Missing Values

| Column | Missing Count | Strategy |
|---|---|---|
| `median_wage_2024` | 6 | Retained in dataset; excluded from wage-specific analysis |
| `education_level` | 38 | Retained; excluded from education-specific analysis |
| `emp_change_pct` | 0 | No missing values in merged dataset |
| All Frey & Osborne columns | 0 | No action needed |

No rows were dropped outright — missing values are handled contextually at analysis time.

### Step 5 — Merge on SOC Code

An inner join on `soc_code` links the BLS projections to the Frey & Osborne automation scores.

```python
merged = pd.merge(bls, fo[["soc_code", "automation_prob"]], on="soc_code", how="inner")
```

**Result:** 702 F&O occupations × 832 BLS occupations → **606 matched occupations** (86% match rate). The 14% loss is primarily due to BLS reclassifying or recoding occupations between 2013 and 2024.

### Step 6 — ILO GenAI Exposure Integration (Then vs. Now)

The ILO dataset is task-level: each row represents one task within an ISCO-08 occupation. The columns `mean_score_2025` and `mean_score_2023` are occupation-level averages, repeated identically across all tasks for a given occupation. The processing steps are:

**6a. Collapse to occupation level:** Deduplicate on `ISCO_08` to get one row per occupation (702 → 427 unique ISCO-08 codes).

**6b. Load and parse the BLS crosswalk:** The crosswalk has 6 metadata rows before the header. After parsing, ISCO-08 codes are truncated to 4 digits and SOC codes are stripped of whitespace.

**6c. Map ISCO-08 → SOC and aggregate fan-in:** The crosswalk is many-to-one in both directions. Some SOC codes map to multiple ISCO-08 codes (fan-in). For these, the GenAI exposure scores from each ISCO-08 occupation are averaged before assigning to the SOC code.

```python
soc_genai = (
    ilo_mapped
    .groupby("soc_code")
    .agg(genai_exposure_2025=("mean_score_2025", "mean"),
         genai_exposure_2023=("mean_score_2023", "mean"))
    .reset_index()
)
```

**6d. Left-join to main dataset:** The aggregated GenAI scores are joined to `cleaned_main.csv` on `soc_code` (left join — retains all 606 rows; unmatched get NaN).

**Crosswalk coverage results:**

| Category | Count |
|---|---|
| SOC codes with exactly 1 ISCO-08 match | 660 crosswalk entries |
| SOC codes with 2+ ISCO-08 matches (averaged) | 151 crosswalk entries |
| Max ISCO-08 codes converging on one SOC | 17 |
| Our occupations matched (have GenAI score) | 600 (99%) |
| Our occupations unmatched (NaN) | 6 (1%) |

The 6 unmatched occupations are residual "all other" categories with no ISCO-08 equivalent: Physical scientists (19-2099), Costume attendants (39-3092), Counter and rental clerks (41-2021), Semiconductor processing technicians (51-9141), Airfield operations specialists (53-2022), Conveyor operators (53-7011).

### Step 7 — Feature Engineering

#### Automation Risk Tier
A categorical variable grouping automation probability into three bands:

```python
# Low < 0.30, Medium 0.30–0.70, High > 0.70
df["risk_tier"] = df["automation_prob"].apply(risk_tier)
```

Result: 283 High (46.7%), 119 Medium (19.6%), 204 Low (33.7%)

#### SOC Occupation Group
The first two digits of the SOC code map to BLS major occupational groups (e.g., `15-xxxx` = Computer & Mathematical).

```python
df["soc_major"] = df["soc_code"].str[:2]
df["occupation_group"] = df["soc_major"].map(SOC_GROUPS)
```

Result: 22 distinct occupation groups.

#### Education Level (Ordinal Encoding)
The `education_required` text field is encoded as an integer from 0 (no credential) to 6 (doctoral degree):

| Level | Code |
|---|---|
| No formal educational credential | 0 |
| High school diploma or equivalent | 1 |
| Some college, no degree | 2 |
| Associate's degree | 3 |
| Bachelor's degree | 4 |
| Master's degree | 5 |
| Doctoral or professional degree | 6 |

#### Adaptive Capacity Score
A composite index (0–1) measuring how well-positioned a worker is to adapt to automation pressure:

```python
df["wage_norm"] = MinMaxScaler().fit_transform(df[["median_wage_2024"]])
df["edu_norm"]  = MinMaxScaler().fit_transform(df[["education_level"]])
df["adaptive_capacity_score"] = (df["wage_norm"] + df["edu_norm"]) / 2
```

Higher score = higher wage AND higher education = greater ability to adapt. Mean: 0.251, Std: 0.198. Distribution is right-skewed — most occupations cluster at low adaptive capacity.

#### Vulnerability Flag
Binary flag for occupations combining high automation risk with low adaptive capacity:

```python
capacity_threshold = df["adaptive_capacity_score"].quantile(0.33)  # bottom third
df["vulnerable"] = (df["automation_prob"] >= 0.7) & (df["adaptive_capacity_score"] <= threshold)
```

Result: **144 vulnerable occupations (23.8%)** of the merged dataset.

---

## 2. Data Profiling

### Frey & Osborne: `automation_prob`
| Metric | Value |
|---|---|
| Type | float64 |
| Count | 606 |
| Missing | 0 (0%) |
| Min | 0.003 |
| Max | 0.99 |
| Mean | 0.578 |
| Median | 0.658 |
| Std | 0.287 |

Distribution: bimodal — large cluster of very high-risk jobs (0.85–0.99) and a cluster of very low-risk jobs (0.01–0.15), reflecting the binary nature of many task structures.

### BLS: `emp_change_pct`
| Metric | Value |
|---|---|
| Type | float64 |
| Count | 606 |
| Missing | 0 |
| Min | −36.1% |
| Max | +23.2% |
| Mean | +0.92% |
| Median | +2.30% |
| Std | 7.35 pp |
| Growing (>0) | 396 occupations (65.3%) |
| Declining (<0) | 204 occupations (33.7%) |

### BLS: `median_wage_2024`
| Metric | Value |
|---|---|
| Count | 600 |
| Missing | 6 |
| Min | $28,280 |
| Max | $226,600 |
| Mean | $66,640 |
| Median | $56,980 |
| Std | $32,450 |

### Engineered: `adaptive_capacity_score`
| Metric | Value |
|---|---|
| Count | 606 |
| Missing | 0 |
| Min | 0.000 |
| Max | 0.863 |
| Mean | 0.251 |
| Median | 0.157 |
| Std | 0.198 |

### ILO 2025: `genai_exposure_2025`
| Metric | Value |
|---|---|
| Type | float64 |
| Count | 600 (6 NaN from unmatched SOC codes) |
| Missing | 6 (1%) |
| Min | 0.09 |
| Max | 0.70 |
| Mean | 0.288 |
| Median | 0.260 |
| Std | 0.139 |

Distribution: right-skewed with a concentration of scores between 0.09–0.20 (physical occupations) and a secondary cluster around 0.35–0.55 (knowledge/office work). Highest score: Data entry keyers (0.70); lowest: Construction laborers and Brickmasons (0.09).

**Comparison to traditional automation:** Traditional automation mean: 0.578; GenAI mean: 0.288 — GenAI is, on average, lower in overall exposure. However, the distribution differs fundamentally by sector — see Stage 5 for the sector-level flip.

### Correlation Preview

| Feature | Correlation with `emp_change_pct` |
|---|---|
| `automation_prob` | **−0.414** |
| `adaptive_capacity_score` | +0.318 |
| `median_wage_2024` | +0.278 |
| `education_level` | +0.324 |

---

## 3. Outcomes vs. Initial Expectations

### Was the data as clean as expected?
Yes, largely. Both datasets are professionally maintained and had minimal missing values. The primary challenge was format normalization (semicolon delimiters, BOM encoding, Excel header offsets) rather than data quality issues.

### Surprises in distributions?
- The automation probability distribution is more bimodal than expected — many occupations cluster at the extremes rather than the middle, consistent with Frey & Osborne's finding that occupations tend to be either primarily routine-task-based or primarily non-routine.
- Employment projections are more optimistic than expected: 65.3% of occupations show positive projected growth even among high-automation-risk jobs. This is the Automation Paradox in the data.

### Did feature engineering produce expected variance?
- `adaptive_capacity_score` shows meaningful spread (std = 0.198) and a clear gap between vulnerable and non-vulnerable occupations (mean wage: $41,503 vs. $72,293).
- The vulnerability flag captures 23.8% of occupations — a meaningful but not overwhelming segment, consistent with the Brookings estimate of concentrated vulnerability in specific occupation categories.

### Benchmark Validation

| Metric | Our Data | External Benchmark | Assessment |
|---|---|---|---|
| Avg automation risk (matched occupations) | 57.8% | Frey & Osborne: 47% of all US employment at high risk | Slight overcount — sample skewed toward detailed occupations that matched both datasets |
| Occupations growing 2024–34 | 65.3% | BLS: overall 3.1% net growth projected | Consistent |
| High-risk groups | Office & Admin (84%), Production (82%) | Frey & Osborne: 77% of office/admin at high risk | Directionally consistent |
| Low-risk groups | Healthcare Practitioners (12%), Computer & Math (13%) | Consistent with academic consensus | Validated |
| Vulnerable occupation median wage | $41,503 | Anthropic (2026): exposed workers in low-adaptive-capacity roles | Directionally consistent |

---

# Stage 4: Data Mining
**Points: 25**

---

## Overview

Two machine learning techniques are applied to the merged dataset of 606 occupations:
1. **K-Means Clustering** — segments occupations into groups by automation exposure and adaptive capacity
2. **Linear Regression** — tests whether automation risk predicts employment change and quantifies the effect

Both techniques run on `data/processed/cleaned_main.csv`. Output is saved to `data/processed/clustered.csv` and `figures/`.

> **Note on dataset expansion:** `cleaned_main.csv` now includes `genai_exposure_2025` and `genai_exposure_2023` columns from the ILO 2025 GenAI Exposure Index. These columns are used in the "Then vs. Now" visualization stage but are intentionally excluded from the clustering and regression models here. Including a 2025-era variable alongside a 2013-era variable would conflate two different AI eras and obscure the Automation Paradox finding.

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

The elbow method runs K-Means for k = 2 through 9 and plots inertia (within-cluster sum of squares). The "elbow" occurs at k=4. After comparing interpretability across k=3 and k=4, k=3 was chosen for the final model: the additional cluster at k=4 did not represent a meaningfully distinct occupational profile. All three final clusters are fully separable and substantively interpretable.

*See `figures/fig_elbow.png`*

### Results

*Note: Clustering ran on 600 occupations (6 excluded due to missing `median_wage_2024`, required for `adaptive_capacity_score`). Percentages are of the 600 clustered occupations.*

| Cluster | Size | Avg Automation Prob | Avg Adaptive Capacity | Avg Employment Change % | Avg Median Wage |
|---|---|---|---|---|---|
| **High Risk / Low Resilience** | 305 (50.8%) | 0.851 | 0.113 | −1.75% | $49,287 |
| **Low Risk / Stable** | 225 (37.5%) | 0.271 | 0.155 | +2.58% | $66,965 |
| **Low Risk / High Skill** | 70 (11.7%) | 0.090 | 0.625 | +5.51% | $126,322 |

Representative occupations by cluster: **High Risk / Low Resilience** — data entry clerks, cashiers, telemarketers, assembly workers, office clerks. **Low Risk / Stable** — social workers, electricians, firefighters, physical therapists. **Low Risk / High Skill** — software developers, physicians, nurse practitioners, financial managers. The wage gap between the bottom and top clusters is 2.6×: $49,287 vs. $126,322.

### Benchmark Comparison

The "High Risk / Low Resilience" cluster profile closely matches the Brookings Institution's characterization of vulnerable US workers: high AI exposure, low adaptive capacity, concentrated in clerical and administrative occupations.

*See `figures/fig_clusters_scatter.png` and `figures/fig_clusters_profile.png`*

---

## Technique B: Linear Regression

### What It Is

Linear regression estimates the relationship between a target variable and one or more predictor variables by fitting a straight line through the data.

**In plain language:** If we know an occupation's automation risk and adaptive capacity score, how accurately can we predict its projected employment change? And which factor matters most?

### Why It Was Chosen

Regression directly tests H1 and H2: Is automation risk negatively associated with employment change? How strong is that relationship? Does adaptive capacity improve the prediction?

### Model Specification

**Target variable:** `emp_change_pct` (BLS projected employment change 2024–2034, in %)

**Predictor variables:**
- `automation_prob` — Frey & Osborne automation probability
- `adaptive_capacity_score` — composite wage + education score
- `wage_norm` — normalized wage
- `edu_norm` — normalized education level
- Occupation group dummy variables (21 dummies, one dropped as baseline)

**Train/test split:** 80% training, 20% test (random seed = 42)

### Results

| Metric | Value |
|---|---|
| R² (test set) | 0.175 |
| R² (train set) | 0.400 |
| Mean Absolute Error | 4.32 percentage points |

> **Note on the train/test gap:** The 0.225-point gap between train R² (0.40) and test R² (0.175) indicates overfitting from the 21 occupation-group dummies on ~480 training rows. The dummies provide structural signal — Computer & Math occupations show +12.4pp growth independent of other features — but they absorb variance that doesn't generalize perfectly. The test R² (0.175) is the appropriate figure for reporting predictive accuracy.

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

The Computer & Math +12.4 coefficient means these occupations are projected to grow ~12 percentage points faster than baseline even holding automation risk, wages, and education equal — reflecting AI-driven demand for tech roles.

### Interpretation

**H1 confirmed: automation risk negatively predicts employment change.** The coefficient of −4.15 on `automation_prob` is statistically meaningful. An occupation moving from 0% to 100% automation probability is associated with ~4.15 percentage points lower employment growth.

**H2 confirmed: automation risk alone is a weak predictor.** R² = 0.175 means the full model explains only 17.5% of variance in employment change. This is consistent with the Automation Paradox — other forces drive most of the variation.

**Benchmark comparison:** Anthropic's March 2026 research found −0.6 percentage points of job-finding rate reduction per 10 percentage point increase in AI task coverage. Our regression produces −0.42pp employment change per 10pp automation probability — similar in sign and order of magnitude.

*See `figures/fig_regression.png`*

---

## Summary of Findings

| Hypothesis | Result |
|---|---|
| H1: Automation risk negatively correlates with job growth | ✅ Confirmed (r = −0.414, coefficient = −4.15) |
| H2: Automation risk alone is a weak predictor | ✅ Confirmed (R² = 0.175) |
| H3: Adaptive capacity separates vulnerable from resilient | ✅ Confirmed (mean wage: $41,503 vs. $72,293; cluster separation) |

---

# Stage 5: Data Visualization
**Points: 25**

---

## Overview

This stage produces 14 visualizations across 6 chart types to support the project narrative. All figures are saved as high-resolution PNGs in `figures/` and interactive HTML versions are provided for Plotly charts. Source code is in `src/02_analyze.py`.

Figures 1–11 cover the core Automation Paradox analysis. Figures 12–14 are the "Then vs. Now" extension, comparing Frey & Osborne (2013) traditional automation risk against the ILO (2025) Generative AI exposure index.

---

## Chart 1: Bar Chart — Automation Risk Tier Distribution

**File:** `figures/fig1_risk_distribution.png`

**Variables:** `risk_tier` (categorical: Low/Medium/High), count of occupations

**Why this chart type:** A bar chart is the clearest way to compare counts across a small number of discrete categories. Pie charts would obscure the magnitude differences.

**What it reveals:** Of 606 matched occupations, 283 (46.7%) fall in the High risk tier, 204 (33.7%) in Low, and only 119 (19.6%) in Medium. The distribution is bimodal — occupations cluster at the extremes rather than the middle.

---

## Chart 2: Scatter Plot — Automation Risk vs. Employment Change (Interactive)

**File:** `figures/fig2_automation_vs_growth.png` | `figures/fig2_automation_vs_growth.html`

**Variables:** `automation_prob` (x-axis), `emp_change_pct` (y-axis), `risk_tier` (color)

**Why this chart type:** A scatter plot reveals the relationship between two continuous variables simultaneously for all 600 occupations. Reference lines at x=0.5 and y=0 create four quadrants for easy interpretation.

**What it reveals:** There is a clear negative trend — high-risk occupations are more likely to appear in the lower portion of the chart (declining employment). However, the relationship is far from deterministic: many high-automation occupations still show positive growth, illustrating the Automation Paradox.

---

## Chart 3: Horizontal Bar — Top 15 Most At-Risk Occupations

**File:** `figures/fig3_top_at_risk.png`

**Variables:** `occupation` (y-axis), `emp_change_pct` (x-axis)
**Selection:** Filtered to automation probability ≥70%, then sorted by `emp_change_pct` ascending.

**Why this chart type:** A ranked bar chart is ideal for a clear "bottom" list. Horizontal orientation accommodates long occupation names.

**What it reveals:** Word processors and typists (−36%), telephone operators (−28%), data entry keyers (−26%), telemarketers (−22%), and payroll and timekeeping clerks (−17%). These are concentrated in Office & Administrative Support and Production. Declines are not marginal — several exceed 20%.

---

## Chart 4: Horizontal Bar — Top 15 Safest Growing Occupations

**File:** `figures/fig4_top_safe.png`

**Variables:** `occupation` (y-axis), `emp_change_pct` (x-axis)
**Selection:** Occupations with automation probability < 0.30 and highest positive employment change.

**What it reveals:** The fastest-growing low-risk occupations are concentrated in healthcare (nurse practitioners, physician assistants, home health aides) and technology (software developers, data scientists). Projected growth rates reach 20%+ over the decade.

---

## Chart 5: Bar Chart — Median Wage by Risk Tier

**File:** `figures/fig5_wage_by_risk.png`

**Variables:** `risk_tier` (x-axis), median of `median_wage_2024` (y-axis)

**What it reveals:** Low risk occupations: median $79,000; Medium: $57,150; High: $48,350. The $30,650 wage gap means the workers most threatened by AI are also the least able to afford retraining or career transitions.

---

## Chart 6: Stacked Bar — Education Level by Risk Tier

**File:** `figures/fig6_education_by_risk.png`

**Variables:** `education_required` (x-axis, ordered), `risk_tier` (stacked color)

**Why this chart type:** A stacked bar chart shows both the absolute count and composition (risk tier mix) within each education level simultaneously.

**What it reveals:** Jobs requiring no formal credential or a high school diploma are overwhelmingly high-risk. As education level rises, the high-risk share falls. Doctoral/professional degree occupations are almost entirely low or medium risk. Education is the strongest protective factor in the dataset.

---

## Chart 7: Bubble Chart — Automation Risk vs. Wage (Size = Annual Openings)

**File:** `figures/fig7_bubble_risk_wage_openings.png` | `figures/fig7_bubble_risk_wage_openings.html`

**Variables:** `automation_prob` (x), `median_wage_2024` (y), `annual_openings` (bubble size), `risk_tier` (color)

**Why this chart type:** A bubble chart encodes four variables simultaneously, making it possible to identify not just risky jobs but risky jobs at scale.

**What it reveals:** Large red bubbles in the lower-right corner represent the highest-risk, lowest-wage, highest-volume occupations. Large green bubbles in the upper-left represent safe, high-wage occupations generating new openings. The chart summarizes the inequality divide that AI is amplifying.

---

## Chart 8: Horizontal Bar — Average Automation Risk by Occupation Group

**File:** `figures/fig8_industry_avg_risk.png`

**Variables:** `occupation_group` (y-axis), mean of `automation_prob` (x-axis)

**What it reveals:** Office & Administrative Support (84%), Production (82%), Farming & Fishing (78%), Building & Grounds (78%), and Food Preparation (76%) are the highest-risk groups. Community & Social Service (5%), Healthcare Practitioners (12%), Computer & Math (13%), and Management (14%) are the lowest risk.

---

## Chart 9: Heatmap — Correlation Matrix

**File:** `figures/fig9_correlation_heatmap.png`

**Variables:** `automation_prob`, `emp_change_pct`, `median_wage_2024`, `education_level`, `adaptive_capacity_score`, `annual_openings`

**What it reveals:**
- `automation_prob` has a moderate negative correlation with `emp_change_pct` (−0.41) — confirming H1
- `automation_prob` shows strong negative correlations with `median_wage_2024` (−0.53) and `education_level` (−0.68)
- `education_level` and `median_wage_2024` are positively correlated with `emp_change_pct` (+0.32, +0.28) — confirming H3
- `annual_openings` is effectively uncorrelated with everything else (max r = 0.07)

---

## Chart 10: Box Plot — Wage by Vulnerability Flag

**File:** `figures/fig10_salary_vulnerability_boxplot.png`

**Variables:** `vulnerable` (binary, x-axis), `median_wage_2024` (y-axis)

**Why this chart type:** Box plots show the full distribution (median, IQR, whiskers, outliers) rather than just a mean — important for right-skewed wage data.

**What it reveals:** Vulnerable occupations have a tightly clustered wage distribution centered near $41,503 ($36,010–$55,000 IQR). Non-vulnerable occupations span a much wider range, median $63,280, with a long right tail reaching $226,600. Vulnerable workers have almost no high-earners in their cohort.

---

## Chart 11: Scatter + OLS Trend Line — Automation Risk vs. Employment Change

**File:** `figures/fig11_risk_vs_growth_trend.png` | `figures/fig11_risk_vs_growth_trend.html`

**Variables:** `automation_prob` (x), `emp_change_pct` (y), `risk_tier` (color), OLS fit line per tier

**What it reveals:** The downward slope confirms the negative relationship. The most telling feature is the vertical spread within each tier: even within the High tier, projected employment change ranges from −36% to +15%. High automation risk does not determine employment fate — it tilts the distribution downward.

---

## Chart 12: Scatter — Traditional Automation (2013) vs. GenAI Exposure (2025)

**File:** `figures/fig12_then_vs_now_scatter.png` | `figures/fig12_then_vs_now_scatter.html`

**Variables:** `automation_prob` (x-axis, Frey & Osborne 2013), `genai_exposure_2025` (y-axis, ILO 2025), `occupation_group` (color)

**Why this chart type:** A scatter plot with a diagonal reference line (x = y) is the most direct way to show a shift between two comparable scores for the same set of observations. Points above the diagonal were underestimated by 2013 models; points below were overestimated.

**What it reveals:** Two distinct clouds emerge. A large cluster of physical/manual occupations sits below the diagonal — high traditional risk, low GenAI exposure. A second cluster of knowledge/office occupations sits above the diagonal — low or moderate traditional risk, elevated GenAI exposure. The Computer & Math sector is almost entirely above the diagonal.

---

## Chart 13: Dumbbell Chart — Sector-Level Risk Shift (2013 → 2025)

**File:** `figures/fig13_sector_risk_shift.png`

**Variables:** `occupation_group` (y-axis), mean `automation_prob` vs. mean `genai_exposure_2025` (x-axis), sorted by GenAI exposure

**Why this chart type:** A dumbbell chart places two data points for the same observation on a shared axis, connected by a line. It shows both the absolute values and the direction/magnitude of change simultaneously.

**What it reveals:** Every physical-labor sector (Production, Building & Grounds, Farming, Construction, Food Preparation, Transportation) shows a large leftward move. Every knowledge sector shows a rightward move or reversal. Computer & Math has the largest reversal: from 13% traditional risk to 56% GenAI exposure (+43 pp).

---

## Chart 14: Diverging Bar Chart — The Biggest Movers

**File:** `figures/fig14_biggest_movers.png`

**Variables:** `occupation` (y-axis), `risk_delta` = `genai_exposure_2025` − `automation_prob` (x-axis), split into top 15 newly exposed and top 15 de-risked

**Why this chart type:** Side-by-side horizontal bars for the extremes of a distribution communicate the occupational-level story in a concrete, name-by-name format.

**What it reveals:**
- **Newly exposed (red):** Credit counselors (+0.56), Operations research analysts (+0.53), Securities sales agents (+0.52), Mathematicians (+0.51), Writers (+0.51). All are information-processing, language-heavy, or analytical roles — precisely the task types GenAI handles best.
- **De-risked (blue):** Sewers by hand (−0.87), Log graders (−0.85), Cement masons (−0.84), Landscapers (−0.83), Construction helpers (−0.83). Physical, outdoor, or manual-dexterity roles where GenAI has no displacement mechanism.

---

## Visualization Summary

| Figure | Chart Type | Key Finding |
|---|---|---|
| fig1 | Bar | 46.7% of occupations are high-risk |
| fig2 | Scatter | Negative trend: higher automation → lower growth |
| fig3 | Ranked bar | Clerical/production jobs face highest displacement |
| fig4 | Ranked bar | Healthcare/tech are the safe-harbor sectors |
| fig5 | Bar | $30,650 wage gap between high and low risk tiers |
| fig6 | Stacked bar | Education is the strongest protective factor |
| fig7 | Bubble | High-risk, low-wage jobs have the most openings (scale of impact) |
| fig8 | Ranked bar | Office admin (84%) and Production (82%) are most exposed sectors |
| fig9 | Heatmap | Moderate correlation structure — no single dominant predictor |
| fig10 | Box plot | Vulnerable workers cluster tightly at low wages, no upside |
| fig11 | Scatter + OLS | Trend confirmed; high variance shows Paradox is real |
| fig12 | Scatter (interactive) | The GenAI flip: physical jobs below diagonal, knowledge jobs above |
| fig13 | Dumbbell | Every physical sector de-risked; Computer & Math reversed by +43 pp |
| fig14 | Diverging bar | Writers, analysts, counselors newly exposed; manual jobs de-risked |
