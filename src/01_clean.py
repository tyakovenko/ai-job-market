"""
01_clean.py
-----------
Loads, cleans, and engineers features for all datasets.
Produces the canonical merged dataset used in all downstream stages.

Inputs:
  data/raw/frey_osborne_automation_scores.csv        — Frey & Osborne (2013) traditional automation risk
  data/raw/bls_occupational_projections_2024_2034.xlsx — BLS 2024–2034 employment projections
  data/raw/ilo_genai_exposure_2025.xlsx              — ILO/Gmyrek et al. (2025) GenAI exposure index
  data/raw/bls_isco_soc_crosswalk.xls               — BLS ISCO-08 × SOC 2010 crosswalk

Outputs:
  data/processed/frey_osborne_clean.csv
  data/processed/bls_clean.csv
  data/processed/merged.csv          (inner join: BLS × Frey & Osborne on SOC code)
  data/processed/cleaned_main.csv    (merged + engineered features + GenAI exposure, analysis-ready)

Crosswalk methodology (ISCO-08 → SOC):
  The ILO dataset uses ISCO-08 4-digit codes; our pipeline uses SOC 2010 codes.
  The BLS ISCO-08 × SOC crosswalk bridges them.
  - 600 of 606 SOC codes matched (99%).
  - Where multiple ISCO-08 codes map to one SOC code (fan-in), GenAI scores are averaged.
  - 6 unmatched SOC codes receive NaN and are excluded from then/now charts only.
  See project-log.md § Crosswalk Analysis for the full breakdown.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# ── 1. Frey & Osborne Automation Scores ──────────────────────────────────────

fo = pd.read_csv(
    "data/raw/frey_osborne_automation_scores.csv",
    sep=";",
    encoding="utf-8-sig",
)

fo = fo.rename(columns={
    "Rank": "rank",
    "Probability": "automation_prob",
    "Label": "label",
    "SOC code": "soc_code",
    "Occupation": "occupation_fo",  # keep original F&O name for reference
})

fo = fo.drop(columns=["label", "rank"])
fo["soc_code"] = fo["soc_code"].astype(str).str.strip()

fo.to_csv("data/processed/frey_osborne_clean.csv", index=False)
print(f"Frey & Osborne: {len(fo)} occupations saved.")

# ── 2. BLS Occupational Projections 2024–2034 ────────────────────────────────

xl = pd.ExcelFile("data/raw/bls_occupational_projections_2024_2034.xlsx")
bls_raw = xl.parse("Table 1.2", header=1)

bls = bls_raw.rename(columns={
    "2024 National Employment Matrix title":       "occupation",
    "2024 National Employment Matrix code":        "soc_code",
    "Occupation type":                             "occ_type",
    "Employment, 2024":                            "emp_2024",
    "Employment, 2034":                            "emp_2034",
    "Employment change, numeric, 2024\u201334":    "emp_change_num",
    "Employment change, percent, 2024\u201334":    "emp_change_pct",
    "Median annual wage, dollars, 2024[1]":        "median_wage_2024",
    "Typical education needed for entry":          "education_required",
    "Occupational openings, 2024\u201334 annual average": "annual_openings",
})

# Keep only line-item occupations (exclude summary rows)
bls = bls[bls["occ_type"] == "Line item"].copy()

keep_cols = [
    "occupation", "soc_code", "emp_2024", "emp_2034",
    "emp_change_num", "emp_change_pct", "median_wage_2024",
    "education_required", "annual_openings",
]
bls = bls[keep_cols]

bls["soc_code"] = bls["soc_code"].astype(str).str.strip()

for col in ["emp_2024", "emp_2034", "emp_change_num", "emp_change_pct",
            "median_wage_2024", "annual_openings"]:
    bls[col] = pd.to_numeric(bls[col], errors="coerce")

bls.to_csv("data/processed/bls_clean.csv", index=False)
print(f"BLS Projections: {len(bls)} line-item occupations saved.")

# ── 3. Merge on SOC Code ─────────────────────────────────────────────────────

merged = pd.merge(
    bls,
    fo[["soc_code", "automation_prob", "occupation_fo"]],
    on="soc_code",
    how="inner",
)

merged.to_csv("data/processed/merged.csv", index=False)
print(f"Merged dataset: {len(merged)} occupations.")

# ── 4. Feature Engineering ───────────────────────────────────────────────────

df = merged.copy()

# --- 4a. Automation risk tier ---
def risk_tier(p):
    if p < 0.3:   return "Low"
    elif p < 0.7: return "Medium"
    else:         return "High"

df["risk_tier"] = df["automation_prob"].apply(risk_tier)

# --- 4b. SOC major group (first 2 digits of SOC code) ---
SOC_GROUPS = {
    "11": "Management",
    "13": "Business & Financial",
    "15": "Computer & Math",
    "17": "Architecture & Engineering",
    "19": "Life & Social Science",
    "21": "Community & Social Service",
    "23": "Legal",
    "25": "Education & Library",
    "27": "Arts & Media",
    "29": "Healthcare Practitioners",
    "31": "Healthcare Support",
    "33": "Protective Service",
    "35": "Food Preparation",
    "37": "Building & Grounds",
    "39": "Personal Care",
    "41": "Sales",
    "43": "Office & Admin Support",
    "45": "Farming & Fishing",
    "47": "Construction & Extraction",
    "49": "Installation & Repair",
    "51": "Production",
    "53": "Transportation",
}
df["soc_major"] = df["soc_code"].str[:2]
df["occupation_group"] = df["soc_major"].map(SOC_GROUPS).fillna("Other")

# --- 4c. Education level encoding (ordinal) ---
EDU_ORDER = {
    "No formal educational credential":        0,
    "High school diploma or equivalent":       1,
    "Some college, no degree":                 2,
    "Associate's degree":                      3,
    "Bachelor's degree":                       4,
    "Master's degree":                         5,
    "Doctoral or professional degree":         6,
}
df["education_level"] = df["education_required"].map(EDU_ORDER)

# --- 4d. Adaptive capacity score ---
# Composite of normalized wage + normalized education level.
# Higher score = more capacity to adapt to AI disruption.
scaler = MinMaxScaler()
df["wage_norm"] = scaler.fit_transform(df[["median_wage_2024"]].fillna(df["median_wage_2024"].median()))
df["edu_norm"]  = scaler.fit_transform(df[["education_level"]].fillna(df["education_level"].median()))
df["adaptive_capacity_score"] = (df["wage_norm"] + df["edu_norm"]) / 2  # 0–1

# --- 4e. Vulnerability flag ---
# High automation risk AND low adaptive capacity (below 33rd percentile)
capacity_threshold = df["adaptive_capacity_score"].quantile(0.33)
df["vulnerable"] = (
    (df["automation_prob"] >= 0.7) &
    (df["adaptive_capacity_score"] <= capacity_threshold)
)

# --- 4f. Employment change direction ---
df["growth_direction"] = df["emp_change_pct"].apply(
    lambda x: "Growing" if x > 0 else ("Declining" if x < 0 else "Stable")
    if pd.notna(x) else "Unknown"
)

# ── 5. ILO GenAI Exposure 2025 — Then vs. Now extension ──────────────────────
#
# The ILO file is task-level: each row is one task within an ISCO-08 occupation.
# The columns mean_score_2023 and mean_score_2025 are already occupation-level
# averages (same value repeated for every task in a given ISCO code), so we
# deduplicate to one row per occupation before merging.
#
# Crosswalk chain:
#   ISCO-08 4-digit  →  SOC 2010  →  our soc_code column
#   Fan-in (multiple ISCO codes → one SOC): resolved by averaging the GenAI scores.

# 5a. Load ILO task-level data and collapse to occupation level
ilo_raw = pd.read_excel("data/raw/ilo_genai_exposure_2025.xlsx")

ilo = (
    ilo_raw[["ISCO_08", "mean_score_2023", "mean_score_2025", "potential25"]]
    .drop_duplicates(subset="ISCO_08")
    .copy()
)
ilo["ISCO_08"] = ilo["ISCO_08"].astype(str).str.strip()
print(f"ILO 2025: {len(ilo)} unique ISCO-08 occupations loaded.")

# 5b. Load BLS ISCO-08 × SOC 2010 crosswalk
#   Row 6 (0-indexed) is the header; earlier rows are BLS cover notes.
xwalk_raw = pd.read_excel("data/raw/bls_isco_soc_crosswalk.xls", header=6)
xwalk_raw.columns = ["isco_code", "isco_title", "part", "soc_code", "soc_title", "comment"]

xwalk = (
    xwalk_raw[xwalk_raw["isco_code"].notna() & xwalk_raw["soc_code"].notna()]
    .copy()
)
# Truncate ISCO codes to 4 digits (crosswalk sometimes includes sub-codes)
xwalk["isco_code"] = xwalk["isco_code"].astype(str).str[:4].str.strip()
xwalk["soc_code"]  = xwalk["soc_code"].astype(str).str.strip()

# 5c. Join crosswalk to ILO scores → one row per (soc_code, isco_code) pair
ilo_mapped = xwalk.merge(ilo, left_on="isco_code", right_on="ISCO_08", how="inner")

# 5d. Aggregate to SOC level — average where multiple ISCO codes fan into one SOC.
#   This is correct because SOC categories are broader than ISCO-08; occupations
#   within a SOC group share similar GenAI exposure profiles.
soc_genai = (
    ilo_mapped
    .groupby("soc_code")
    .agg(
        genai_exposure_2025=("mean_score_2025", "mean"),
        genai_exposure_2023=("mean_score_2023", "mean"),
    )
    .reset_index()
)

# 5e. Merge GenAI scores into main dataset
df = df.merge(soc_genai, on="soc_code", how="left")

matched   = df["genai_exposure_2025"].notna().sum()
unmatched = df["genai_exposure_2025"].isna().sum()
print(f"GenAI scores merged: {matched} matched, {unmatched} unmatched (NaN).")

# ── 6. Final dataset ─────────────────────────────────────────────────────────

df.to_csv("data/processed/cleaned_main.csv", index=False)

print(f"\ncleaned_main.csv saved: {len(df)} rows, {df.shape[1]} columns.")
print("\n--- Feature summary ---")
print(f"Risk tiers:       {df['risk_tier'].value_counts().to_dict()}")
print(f"Vulnerable jobs:  {df['vulnerable'].sum()} ({df['vulnerable'].mean():.1%})")
print(f"Occupation groups: {df['occupation_group'].nunique()}")
print(f"Missing wages:    {df['median_wage_2024'].isna().sum()}")
print(f"Missing edu:      {df['education_level'].isna().sum()}")
print(f"Missing GenAI:    {df['genai_exposure_2025'].isna().sum()}")
print(f"\nAdaptive capacity stats:\n{df['adaptive_capacity_score'].describe().round(3)}")
print(f"\nGenAI exposure 2025 stats:\n{df['genai_exposure_2025'].describe().round(3)}")
