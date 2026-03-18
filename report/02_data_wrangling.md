# Stage 3: Data Preparation / Data Wrangling
**MIS502 Final Project — AI's Impact on the Job Market**
**Points: 25 | Status: Complete — Updated with ILO 2025 GenAI integration**

---

## 1. All Steps and Outcomes

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
| `education_required` | 38 | Retained; excluded from education-specific analysis |
| `emp_change_pct` | 6 | Retained; excluded from projection analysis |
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

**6b. Load and parse the BLS crosswalk:** The crosswalk has 6 metadata rows before the header. After parsing, ISCO-08 codes are truncated to 4 digits (some entries include sub-codes) and SOC codes are stripped of whitespace.

**6c. Map ISCO-08 → SOC and aggregate fan-in:** The crosswalk is many-to-one in both directions. Some SOC codes map to multiple ISCO-08 codes (fan-in). For these, the GenAI exposure scores from each ISCO-08 occupation are averaged before assigning to the SOC code. This is the standard approach for many-to-one crosswalks and is appropriate here since occupations within a broad SOC category share similar GenAI exposure profiles.

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
The first two digits of the SOC code map to BLS major occupational groups (e.g., `15-xxxx` = Computer & Mathematical). This creates a grouping variable comparable to "industry" in the synthetic dataset.

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

Higher score = higher wage AND higher education = greater ability to adapt (retrain, transition, negotiate). Mean score: 0.251, Std: 0.198. Distribution is right-skewed — most occupations cluster at low adaptive capacity.

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
| Count | 600 (6 missing) |
| Missing | 6 (1%) |
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

**Comparison to traditional automation:**
- Traditional automation mean: 0.578; GenAI mean: 0.288 — GenAI is, on average, lower in overall exposure
- However, the *distribution* is fundamentally different by sector — see Stage 5 visualization for the sector-level flip

### Correlation Preview

| Feature | Correlation with `emp_change_pct` |
|---|---|
| `automation_prob` | **−0.414** |
| `adaptive_capacity_score` | +0.318 |
| `median_wage_2024` | +0.278 |
| `education_level` | +0.324 |

The negative correlation between automation probability and employment change (−0.414) confirms H1 directionally but is moderate, not deterministic — supporting the expectation that H2 will also hold (automation risk alone is an incomplete predictor).

---

## 3. Outcomes vs. Initial Expectations

### Was the data as clean as expected?
Yes, largely. Both datasets are professionally maintained and had minimal missing values. The primary challenge was format normalization (semicolon delimiters, BOM encoding, Excel header offsets) rather than data quality issues.

### Surprises in distributions?
- The automation probability distribution is more bimodal than expected — many occupations cluster at the extremes (very high or very low risk) rather than the middle. This is consistent with Frey & Osborne's finding that occupations tend to be either primarily routine-task-based or primarily non-routine.
- Employment projections are more optimistic than expected: 65.3% of occupations show positive projected growth even among high-automation-risk jobs. This is the Automation Paradox in the data.

### Did feature engineering produce expected variance?
- `adaptive_capacity_score` shows meaningful spread (std = 0.198) and a clear gap between vulnerable and non-vulnerable occupations (mean wage: $41,503 vs. $72,293).
- The vulnerability flag captures 23.8% of occupations — a meaningful but not overwhelming segment, consistent with the Brookings estimate of concentrated vulnerability in specific occupation categories.

### Benchmark Validation

| Metric | Our Data | External Benchmark | Assessment |
|---|---|---|---|
| Avg automation risk (matched occupations) | 57.8% | Frey & Osborne: 47% of all US employment at high risk | Slight overcount — our sample is skewed toward detailed occupations that matched both datasets |
| Occupations growing 2024–34 | 65.3% | BLS: overall 3.1% net growth projected | Consistent — most occupations grow, a minority decline |
| High-risk groups | Office & Admin (84%), Production (82%) | Frey & Osborne: 77% of office/admin at high risk | Directionally consistent |
| Low-risk groups | Healthcare Practitioners (12%), Computer & Math (13%) | Consistent with academic consensus | Validated |
| Vulnerable occupation median wage | $41,503 | Anthropic (2026): exposed workers in low-adaptive-capacity roles | Directionally consistent |
