# MIS502 Final Project Plan
## AI's Impact on the Job Market: The Automation Paradox

**Course:** MIS 502 — Data Management for Business
**Total Points:** 100
**Status:** Milestone 1 Complete (Data Selection)
**Narrative Theme:** *"The Automation Paradox: Who Really Gets Hurt When AI Takes Over?"*

---

## The Story We're Telling

Research from Brookings, BLS, and OECD reveals a deeply counterintuitive finding: **workers most exposed to AI are currently doing *better*, not worse**. They have lower unemployment and higher wages. Yet hiding inside that aggregate is a crisis — **6.1 million Americans in high-exposure, low-adaptive-capacity roles** (86% women, mostly clerical/administrative) face genuine displacement with no safety net.

Our project will use the Kaggle dataset to prove this paradox with data: AI is simultaneously an **augmenter** (boosts demand in tech/knowledge work) and an **automater** (destroys clerical jobs). The story is not "AI is taking all the jobs" — it's "AI is widening the inequality gap in ways most people aren't watching."

This narrative satisfies all rubric requirements while producing analysis that is genuinely surprising and policy-relevant.

---

## Datasets

| Dataset | Source | Size | Role |
|---|---|---|---|
| AI Impact on Job Market | Kaggle (synthetic, BLS/OECD/WEF-based) | 120,000+ records | Primary |
| AI Automation Resources | Kaggle | ~220 records | Secondary (enrichment) |

Key features available: `Automation Risk (%)`, `Salary (USD)`, `Gender Diversity (%)`, `Required Education`, `Projected Openings (2030)`, `Job Status`, `AI Replacement Score`, `Remote Feasibility`

## External Research Benchmarks

Quantitative figures extracted from all NotebookLM sources are compiled in **`report/00_reference_data.md`**.
These figures are used in Stages 3 and 4 as **ground-truth benchmarks** to validate the synthetic dataset and contextualize findings.

| Source | Key Figures Used |
|---|---|
| Brookings Institution | 6.1M vulnerable workers, 86% female, occupation-level AI exposure + adaptive capacity scores |
| BLS (2023–2033 projections) | Job growth rates by occupation (software dev +17.9%, insurance appraisers −9.2%), total workforce 167.8M |
| Anthropic (March 2026) | 33% actual AI task coverage (vs. 94% theoretical), −14% job-finding rate for young exposed workers, +47% wage premium |
| EIG / Census Bureau | −6.5% employment growth ages 22–25 in high-exposure roles, 9% of businesses using AI (Aug 2025) |
| Hamilton Project | <20% of firms use AI, occupational mix change 2019–2024: 6.1% |
| Kaggle dataset (synthetic) | 50/50 job status split, equal AI impact distribution — synthetic artifact, not empirical |

---

## Project Stages

---

### Stage 1: Project Setup
**Status:** ✅ Milestone 1 Complete
**Deliverable:** Initialized repo with folder structure, `.gitignore`, and both datasets downloaded

#### Tasks
- [x] Source datasets from Kaggle
- [x] Preliminary exploration of key features
- [ ] Finalize folder structure (see below)
- [ ] Create Python virtual environment
- [ ] Install dependencies (`pandas`, `numpy`, `scikit-learn`, `matplotlib`, `seaborn`, `plotly`, `dash` or `streamlit`, `jupyter`)

#### Folder Structure
```
ai-job-market/
├── data/
│   ├── raw/              # original CSVs, never modified
│   └── processed/        # cleaned outputs
├── notebooks/            # Jupyter notebooks (one per stage)
├── report/               # MD deliverables per stage
│   ├── 01_dataset_description.md
│   ├── 02_data_wrangling.md
│   ├── 03_data_mining.md
│   ├── 04_data_visualization.md
│   └── final_report.md
├── dashboard/            # interactive dashboard app
├── figures/              # exported charts
├── project-plan.md
├── project-log.md
└── requirements.txt
```

---

### Stage 2: Dataset Description
**Rubric:** 15 points
**Deliverable:** `report/01_dataset_description.md` + `notebooks/01_dataset_description.ipynb`

#### Required Content (per rubric)
1. **Nature and context of the dataset** (5 pts)
   - What it is, how it was generated, what real-world sources it reflects (BLS, OECD, WEF)
   - Key variables and their meaning
   - Why this dataset is appropriate for studying AI's job market impact
   - Description of secondary dataset and how it complements the primary

2. **Potential outcomes from the analysis** (5 pts)
   - Hypotheses based on the research narrative:
     - H1: Roles with high automation risk AND low salary are disproportionately female-dominated
     - H2: High automation risk does NOT reliably predict declining job openings
     - H3: "Adaptive Capacity" (salary + education level) predicts job vulnerability better than automation risk alone
   - Expected clusters, patterns, and anomalies we anticipate finding

3. **Data quality, integrity, and ethics issues** (5 pts)
   - Synthetic nature: implications for generalizability
   - Potential biases baked into synthetic generation (e.g., marketing industry skew)
   - Ethics: demographic data (gender diversity %) — how to handle responsibly
   - Missing values, outliers, class imbalance assessment

---

### Stage 3: Data Preparation / Data Wrangling
**Rubric:** 25 points
**Deliverable:** `report/02_data_wrangling.md` + `notebooks/02_data_wrangling.ipynb` + `data/processed/cleaned_main.csv`

#### Required Content (per rubric)
1. **All steps and outcomes** (10 pts)
   - Load both datasets
   - Handle missing values (document strategy for each column)
   - Remove or flag duplicates
   - Normalize/standardize numeric columns (`Automation Risk`, `Salary`, etc.)
   - Encode categorical variables (`Job Status`, `Required Education`, `Industry`)
   - Engineer new features:
     - **`adaptive_capacity_score`** = composite of normalized Salary + education level (key for our narrative)
     - **`vulnerability_flag`** = high automation risk AND low adaptive capacity score
   - Merge secondary dataset where applicable
   - Export cleaned dataset

2. **Data profiling for each element** (10 pts)
   - For every column: data type, count, null %, min/max/mean/median/std, unique values
   - Distribution plots for key numeric columns
   - Correlation matrix preview

3. **Compare outcomes to initial expectations** (5 pts)
   - Was the data as clean as expected (synthetic source)?
   - Were there surprises in distributions, nulls, or outliers?
   - Did feature engineering produce the expected variance?
   - **Benchmark validation table** — compare dataset distributions to real-world figures from `report/00_reference_data.md`:
     - Gender diversity in high-risk roles vs. Brookings' 86% female finding
     - Automation risk distribution vs. Anthropic's 33% observed coverage for Computer & Math
     - Job status split (50/50 in Kaggle) vs. BLS projections (mostly growth) — flag as synthetic artifact
     - Salary ranges vs. Anthropic's +47% wage premium for high-exposure workers

4. **Python code** — fully documented inline

---

### Stage 4: Data Mining
**Rubric:** 25 points
**Deliverable:** `report/03_data_mining.md` + `notebooks/03_data_mining.ipynb`

#### Required Content (per rubric)
1. **Techniques applied** (7 pts) — must use ≥2 techniques:

   **Technique A — K-Means Clustering** ("The Automation Paradox Segments")
   - Cluster jobs into groups based on: `automation_risk`, `adaptive_capacity_score`, `salary`, `gender_diversity_pct`
   - Expected clusters:
     - *High Exposure / High Resilience* (tech/knowledge workers)
     - *High Exposure / High Vulnerability* (clerical, female-dominated)
     - *Low Exposure / Stable* (trades, physical labor)
   - Use elbow method to determine optimal k

   **Technique B — Linear Regression** ("Does Automation Risk Predict Job Loss?")
   - Target: `projected_openings_2030` or `job_status` (encoded)
   - Features: `automation_risk`, `salary`, `required_education`, `industry`
   - Tests H2: automation risk alone is a poor predictor of job openings

2. **Explain each technique** (7 pts) — plain-language explanation in report
3. **Document results** (7 pts) — cluster profiles, R², coefficients, key findings
   - **Benchmark comparison for clusters:** Expected "vulnerable" cluster should resemble Brookings' 6.1M profile:
     - ~85–96% female, 50–82% AI exposure, adaptive capacity <37%
     - Occupations like secretaries (96% F, 59% exposure, 14% adaptive capacity) set the target
   - **Benchmark comparison for regression:** Anthropic found −0.6 pp job growth per +10 pp AI coverage.
     If our coefficient differs significantly, explain in terms of dataset's synthetic construction.
   - **Age exposure signal:** Reference EIG finding — ages 22–25 saw −6.5% employment growth in high-exposure roles vs. +11.9% in low-exposure. If dataset includes age, replicate this test.
4. **Python code** — fully documented inline

---

### Stage 5: Data Visualization
**Rubric:** 25 points
**Deliverable:** `report/04_data_visualization.md` + `notebooks/04_data_visualization.ipynb` + `figures/` (exported PNGs)

#### Required Content (per rubric)
1. **Techniques applied** (7 pts) — must use ≥3 chart types:

   | Chart | Variables | Story Point |
   |---|---|---|
   | Bubble scatter plot | Automation Risk vs. Salary; size = Job Openings; color = Gender Diversity % | The Pink-Collar Trap |
   | Grouped bar chart | Average Automation Risk by Industry | Who is most exposed? |
   | Heatmap | Correlation matrix of key numeric features | Feature relationships |
   | Box plot | Salary distribution by Vulnerability Flag | Adaptive capacity gap |
   | Scatter + trend line | Automation Risk vs. Projected Openings 2030 | The Productivity Paradox |

2. **Explain each technique** (7 pts) — why this chart type, what it reveals
3. **Document results** (7 pts) — key findings from each visualization
4. **Python code** — fully documented inline

---

### Stage 6: Interactive Dashboard *(Beyond Rubric — Strengthens Project)*
**Deliverable:** `dashboard/app.py` — runnable Plotly Dash or Streamlit app

#### Components
- **Overview tab:** Key metrics cards (avg automation risk, most vulnerable industries, % female in high-risk roles)
- **Explorer tab:** Interactive scatter plot — filter by industry, education level, job status; hover for job title details
- **Cluster tab:** 2D cluster visualization (PCA-reduced), toggle cluster labels
- **Narrative tab:** Guided story with embedded charts walking through the Automation Paradox finding

This makes the project stand out significantly and provides a hands-on deliverable for the presentation.

---

### Stage 7: Final Report Compilation
**Deliverable:** `report/final_report.md`

Compiled from all stage reports into one cohesive narrative document:

```
1. Executive Summary
2. Introduction & Research Context (Brookings, BLS, OECD findings)
3. Dataset Description
4. Data Wrangling
5. Data Mining
6. Data Visualization
7. The Automation Paradox: Key Findings
8. Policy Implications & Conclusion
9. Appendix: Python Code
```

The report must read as a **story**, not a list of steps. Each section should connect back to the central narrative.

---

### Stage 8: PowerPoint Presentation
**Rubric:** 7 points (slides) + 3 points (peer comments)
**Deliverable:** `presentation/MIS502_Final_Presentation.pptx`
**Target duration:** 10 minutes

#### Required Slides (per rubric)
1. Title + Team
2. The Question: "Is AI Really Taking Our Jobs?"
3. Dataset Description
4. Data Quality, Integrity & Ethics
5. Data Preparation / Wrangling Outcomes
6. Data Mining Outcomes (clusters, regression)
7. Data Visualization Highlights
8. The Automation Paradox: Our Answer
9. Summary & Takeaways

---

### Stage 9: Review & Submission
**Deliverable:** Finalized repo, submitted report, peer comments posted

- [ ] Re-read rubric and verify every point category is covered
- [ ] Ensure all Python code is documented inline in the report
- [ ] Dashboard runs without errors
- [ ] Peer comments posted on classmates' projects (3 pts)
- [ ] Push final version to GitHub

---

## Execution Order & Dependencies

```
Stage 1 (Setup)
    ↓
Stage 2 (Dataset Description)  ← NotebookLM research feeds narrative here
    ↓
Stage 3 (Data Wrangling)       ← Must complete before mining or viz
    ↓
Stage 4 (Mining) ──────────────┐
Stage 5 (Visualization) ───────┤  Run in parallel after Stage 3
    ↓                          ↓
Stage 6 (Dashboard)            ← Pulls from cleaned data + figures
    ↓
Stage 7 (Final Report)         ← Compiles all stage reports
    ↓
Stage 8 (Presentation)
    ↓
Stage 9 (Review & Submit)
```

---

## Rubric Coverage Checklist

| Category | Points | Covered In |
|---|---|---|
| Dataset nature & context | 5 | Stage 2 |
| Potential outcomes | 5 | Stage 2 |
| Data quality/integrity/ethics | 5 | Stage 2 |
| Wrangling steps & outcomes | 10 | Stage 3 |
| Data profiling | 10 | Stage 3 |
| Outcomes vs. expectations | 5 | Stage 3 |
| Mining techniques applied | 7 | Stage 4 |
| Mining explained | 7 | Stage 4 |
| Mining results documented | 7 | Stage 4 |
| Mining Python code | 4 | Stage 4 |
| Visualization techniques applied | 7 | Stage 5 |
| Visualization explained | 7 | Stage 5 |
| Visualization results documented | 7 | Stage 5 |
| Visualization Python code | 4 | Stage 5 |
| PowerPoint slides | 7 | Stage 8 |
| Peer comments | 3 | Stage 9 |
| **TOTAL** | **100** | |

---

*Plan generated: 2026-03-17 | Research sourced from NotebookLM (Brookings, BLS, OECD, WEF)*
