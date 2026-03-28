# Project Log — AI Impact on Job Market
**Course:** MIS502 — Data Management for Business
**Last updated:** 2026-03-19 (Session 3 — complete)

---

## Session 1 — 2026-03-17

### Summary
Full project build from setup through live deployment in a single session.

### What Was Completed

#### Stage 1 — Project Setup
- Created full folder structure: `src/`, `data/raw/`, `data/processed/`, `notebooks/`, `figures/`, `dashboard/`, `report/`, `presentation/`
- Created `.gitignore` with security entries (secrets, OS noise, Python artifacts, raw data)
- Created Python virtual environment at `.venv/`
- Created `requirements.txt` with all dependencies (pandas, numpy, scikit-learn, matplotlib, seaborn, plotly, streamlit, quarto, kaleido, statsmodels, openpyxl)
- **Decision:** Replaced Jupyter notebooks with Python scripts + Quarto + Streamlit for reproducibility. Jupyter notebooks have hidden state and cell-order issues; scripts run top-to-bottom deterministically.
- **Decision:** Replaced synthetic Kaggle dataset with two real-world datasets. Preliminary analysis of the Kaggle data showed near-zero correlations between all variables (r ≈ 0.001–0.012) — a hallmark of random synthetic generation with no signal.

#### Datasets Acquired
- `data/raw/frey_osborne_automation_scores.csv` — 702 US occupations with automation probability (Frey & Osborne, 2013)
- `data/raw/bls_occupational_projections_2024_2034.xlsx` — 832 BLS occupations with 2024–2034 employment projections
- Both downloadable programmatically via `src/00_fetch.py`

#### Stage 2 — Dataset Description
- Written: `report/01_dataset_description.md` (15 pts)
- Documents both datasets, 3 research hypotheses (H1–H3), data quality assessment, and ethical considerations

#### Stage 3 — Data Wrangling
- Written: `report/02_data_wrangling.md` (25 pts)
- Script: `src/01_clean.py`
- Output: `data/processed/cleaned_main.csv` (606 rows, 20 columns)
- Feature engineering:
  - `risk_tier` — Low/Medium/High automation risk bands
  - `occupation_group` — 22 groups from SOC major code
  - `education_level` — ordinal encoding 0–6
  - `adaptive_capacity_score` — composite of normalized wage + education (0–1)
  - `vulnerable` — binary flag: high automation + low adaptive capacity (144 occupations, 23.8%)
  - `growth_direction` — Growing / Declining / Stable

#### Stage 4 — Data Mining
- Written: `report/03_data_mining.md` (25 pts)
- Script: `src/03_mine.py`
- **K-Means Clustering (k=4, 3 distinct segments):**
  - High Risk / Low Resilience: 305 occupations, automation 85%, wage $49K, growth −1.75%
  - Low Risk / Stable: 225 occupations, automation 27%, wage $67K, growth +2.58%
  - Low Risk / High Skill: 70 occupations, automation 9%, wage $126K, growth +5.51%
- **Linear Regression:**
  - Target: `emp_change_pct`; Features: automation prob, adaptive capacity, wage, education, occupation group dummies
  - R² = 0.175, MAE = 4.32 pp
  - Key coefficient: automation_prob = −4.15 (each +10pp automation → −0.42pp employment change)
  - H1 confirmed (negative relationship), H2 confirmed (R² = 0.175 — automation is weak predictor alone), H3 confirmed (wage gap: $41,503 vs $72,293)

#### Stage 5 — Data Visualization
- Written: `report/04_data_visualization.md` (25 pts)
- Script: `src/02_analyze.py`
- 11 figures generated to `figures/` (PNG + HTML for interactive Plotly charts):
  - fig1: Risk tier distribution (bar)
  - fig2: Automation vs. employment change (scatter, interactive)
  - fig3: Top 15 most at-risk occupations (ranked bar)
  - fig4: Top 15 safest growing occupations (ranked bar)
  - fig5: Median wage by risk tier (bar)
  - fig6: Education level vs. risk tier (stacked bar)
  - fig7: Bubble chart — automation vs. wage, size = annual openings (interactive)
  - fig8: Average automation risk by occupation group (ranked bar)
  - fig9: Correlation heatmap
  - fig10: Wage distribution — vulnerable vs. not (box plot)
  - fig11: Automation vs. growth with OLS trend line (interactive)

#### Stage 6 — Interactive Dashboard
- Built: `dashboard/app.py` — Streamlit, 5 tabs
- Tabs: Overview, Job Explorer, By Sector, Clusters, The Paradox
- Sidebar filters: risk tier, occupation group, wage range, automation probability range
- Deployed to Streamlit Community Cloud

#### Stage 7 — Final Report
- Built: `report/report.qmd` — Quarto document with live Python code
- Renders to HTML and PDF
- Covers: executive summary, introduction, all 5 analysis stages, conclusions, policy implications
- Deployed to GitHub Pages at `tyakovenko.github.io/ai-job-market`

#### Deployment
- GitHub repo: `github.com/tyakovenko/ai-job-market`
- GitHub Pages: enabled from `docs/` folder on `main` branch (Quarto report)
- Streamlit Community Cloud: dashboard deployed from `dashboard/app.py`
- GitHub Actions workflow (`refresh.yml`): annual refresh every January 1st
  - Downloads fresh BLS + F&O data
  - Re-runs full pipeline
  - Re-renders Quarto
  - Commits and pushes — triggers automatic Streamlit redeploy

---

## Session 2 — 2026-03-17

### Summary
Resumed after a crash. Existing pipeline confirmed running. Planning extension to add ILO 2025 GenAI exposure dataset for a "then vs. now" comparison against the Frey & Osborne (2013) traditional automation scores.

### What Was Completed (full session)
- Confirmed all existing pipeline scripts and Streamlit dashboard are running
- Researched and located the ILO 2025 dataset: *"Generative AI and Jobs: A Refined Global Index of Occupational Exposure"* (Gmyrek et al., ILO Working Paper 140, May 2025)
- Located downloadable Excel file: `Final_Scores_ISCO08_Gmyrek_et_al_2025.xlsx` on GitHub (pgmyrek/2025_GenAI_scores_ISCO08)
- Confirmed data structure: 423 ISCO-08 4-digit occupations, GenAI exposure score 0–1, 4 gradient tiers
- Identified integration challenge: ILO uses ISCO-08 codes; pipeline uses US SOC codes — requires BLS SOC↔ISCO-08 crosswalk
- Defined and fully implemented the then/now extension
- Integrated ILO 2025 GenAI exposure data into all pipeline stages
- Added fig12, fig13, fig14 and "Then vs. Now" dashboard tab
- Updated all milestone reports, README, reference data, and report.qmd with then/now findings and ILO source
- Fixed refresh.yml pipeline order bug (02_analyze before 03_mine)
- Fixed Quarto re-render issue (stale _freeze cache) — added --no-freeze to CI
- Pushed all changes to GitHub; GitHub Pages regenerated

### Crosswalk Analysis — ISCO-08 → SOC Code Overlap

The ILO 2025 dataset uses ISCO-08 4-digit codes; our pipeline uses US SOC 2010 codes (via Frey & Osborne).
We used the BLS official ISCO-08 × SOC 2010 crosswalk (`https://www.bls.gov/soc/ISCO_SOC_Crosswalk.xls`) to bridge them.

**Results across our 606 occupations:**

| Category | Count | Notes |
|---|---|---|
| Matched (have GenAI score) | 600 (99%) | Full coverage |
| Unmatched (no GenAI score) | 6 (1%) | See list below |

**Among the 600 matched SOC codes:**

| Match type | SOC codes | Handling |
|---|---|---|
| Exactly 1 ISCO-08 code → 1 SOC code | 660 crosswalk entries | Direct assignment |
| 2+ ISCO-08 codes → 1 SOC code (fan-in) | 151 crosswalk entries | Averaged genai_exposure scores |
| Max ISCO codes converging on one SOC | 17 | Edge case, averaged |

Fan-in occurs because US SOC codes are broader categories than ISCO-08 codes (e.g., a single SOC "Software Developers" may cover several ISCO-08 codes for different specializations). Averaging is the standard approach for many-to-one crosswalks and is appropriate here since the ILO scores within a broad occupational family tend to cluster closely.

**6 unmatched SOC codes (assigned NaN — excluded from then/now charts):**

| Occupation | SOC Code | Group |
|---|---|---|
| Physical scientists, all other | 19-2099 | Life & Social Science |
| Costume attendants | 39-3092 | Personal Care |
| Counter and rental clerks | 41-2021 | Sales |
| Semiconductor processing technicians | 51-9141 | Production |
| Airfield operations specialists | 53-2022 | Transportation |
| Conveyor operators and tenders | 53-7011 | Transportation |

These 6 occupations have no ISCO-08 equivalent in the BLS crosswalk (residual "all other" and niche categories). They are excluded only from then/now comparison charts, not from the main analysis.

---

### Extension Plan — "Then vs. Now"

**Narrative:** Traditional automation (2013) predicted physical/routine jobs were most at risk. GenAI (2025) flipped the script — knowledge workers and creatives now face highest exposure.

**Files to modify:**
| File | Change |
|---|---|
| `src/00_fetch.py` | Add ILO xlsx download + BLS SOC↔ISCO-08 crosswalk download |
| `src/01_clean.py` | Parse ILO data, apply crosswalk, add `genai_exposure_2025` to `cleaned_main.csv` |
| `src/02_analyze.py` | Add figures comparing F&O 2013 vs ILO 2025 exposure by sector/occupation |
| `dashboard/app.py` | Add "Then vs. Now" tab |

---

## Session 3 — 2026-03-19

### Summary
Bug fixes and feature additions to the Streamlit dashboard, new GenAI clustering pipeline, cluster comparison added to the Then vs. Now tab, and a Quarto report update explaining the Kaggle dataset rejection.

### What Was Completed

#### Bug Fix — Streamlit Dashboard Tabs 2–6 Broken on Cloud
- Root cause: `background_gradient` in pandas Styler requires matplotlib, which had been commented out of `requirements.txt`
- Fix: added `matplotlib>=3.9.1` back to dashboard requirements
- All six tabs now render correctly on Streamlit Community Cloud

#### Feature — Traditional / GenAI Risk Score Toggle
- Added sidebar radio button: "Risk Score: Traditional (2013) | GenAI (2025)"
- Switching the toggle updates Overview, Job Explorer, By Sector, and Clusters tabs to use either Frey & Osborne automation probabilities or ILO 2025 GenAI exposure scores
- Risk tiers for GenAI use percentile-based cutoffs (33rd/67th percentile) because ILO scores top out at 0.70 — fixed a bug where the "High" tier returned 0 occupations when using fixed absolute cutoffs

#### Feature — GenAI K-Means Clustering
- Extended `src/03_mine.py` to recompute K-means clusters using GenAI exposure features
- Output: `data/processed/clustered_genai.csv`
- Three effective GenAI clusters:

| Cluster | Occupations | Avg GenAI Score | Median Wage | Profile |
|---|---|---|---|---|
| High Exposure / Low Resilience | 86 | 0.47 | $47K | Newly vulnerable class |
| High Exposure / Adaptable | 202 | 0.37 | $81K | Knowledge workers with adaptability |
| Low Exposure / Stable | 306 | 0.18 | $48K | Manual/trade occupations largely unaffected |

- Clusters tab now shows the correct cluster set based on the active risk view toggle

#### Feature — Cluster Comparison in Then vs. Now Tab
- Added "The Vulnerable Class Has Shifted" section to the Then vs. Now tab
- Shows traditional vs. GenAI cluster profiles side by side
- Positioned before the full data table at the bottom of the tab

#### Quarto Report Update
- Added explanatory paragraph at the top of Section 2 (Data Sources)
- Explains why the Kaggle synthetic dataset was rejected: correlations r ≈ 0.001–0.012 across all variable pairs, consistent with randomly generated data with no real-world signal
- Re-rendered report with `--no-freeze` and pushed to GitHub Pages

---

## Open Tasks

- [x] **[COMPLETE]** Integrate ILO 2025 GenAI exposure dataset (then vs. now extension)
  - [x] Update `src/00_fetch.py` — added ILO xlsx + BLS ISCO-SOC crosswalk downloads
  - [x] Update `src/01_clean.py` — ISCO-08 → SOC crosswalk applied, `genai_exposure_2025` and `genai_exposure_2023` added to `cleaned_main.csv`
  - [x] Update `src/02_analyze.py` — fig12, fig13, fig14 added (scatter, dumbbell, movers)
  - [x] Update `dashboard/app.py` — "⏳ Then vs. Now" tab added (tab 6)
- [x] Update all documentation (README, milestone reports, project log, lessons-learned)
- [x] Fix Streamlit dashboard design and graphics — tabs 2–6 restored (matplotlib dependency fix); Traditional/GenAI risk toggle added
- [ ] Fill in written narrative sections of `report/report.qmd` (currently scaffolded with data)
- [ ] Verify Streamlit Cloud and GitHub Pages URLs are live
- [ ] Complete Stage 9: peer review comments on classmates' projects (3 pts)
- [ ] Create presentation in NotebookLM using milestone reports as source documents
- [ ] Final submission
- [x] **[COMPLETE]** Promote "Then vs. Now" to Tab 2 "⚡ Synthesis" — always visible, independent of risk toggle, positioned as the project's key finding. Removed duplicate static table from The Paradox tab. Renamed all tab variables to descriptive names.

---

## Decisions Log

| Decision | What Was Chosen | What Was Rejected | Why |
|---|---|---|---|
| Notebook format | Python scripts + Quarto + Streamlit | Jupyter notebooks | Scripts are deterministic; notebooks have hidden state and cell-order issues |
| Primary dataset | Frey & Osborne (2013) + BLS 2024–2034 | Kaggle synthetic dataset | Synthetic data had r ≈ 0.001 between all variables — no real signal |
| Dashboard hosting | Streamlit Community Cloud | GitHub Pages | GitHub Pages is static only; Streamlit needs a Python server |
| Report hosting | GitHub Pages (Quarto → docs/) | — | Standard static site, free, integrates with Quarto natively |
| Data refresh cadence | Annual (January 1st) | Monthly | BLS only releases new projections every ~2 years |
| PDF generation | Quarto built-in (LuaLaTeX via TinyTeX) | Separate LaTeX setup | Quarto handles this automatically with `quarto install tinytex` |
| GenAI exposure source | ILO WP140 / Gmyrek et al. 2025 (ISCO-08) | Eloundou et al. "GPTs are GPTs" (2023) | ILO 2025 is more recent, global, task-validated with 29K+ tasks; Eloundou is US-only and older |
| ISCO→SOC mapping | BLS official SOC↔ISCO-08 crosswalk | Fuzzy name matching | Crosswalk is authoritative; name matching introduces uncontrolled error |

---

## Key Numbers (for quick reference)

| Metric | Value |
|---|---|
| Total occupations analyzed | 606 |
| High-risk occupations (>70% automation prob) | 283 (46.7%) |
| Vulnerable occupations (high risk + low adaptive capacity) | 144 (23.8%) |
| Median wage — high risk tier | $48,350 |
| Median wage — low risk tier | $79,000 |
| Wage gap (vulnerable vs. not) | $41,503 vs. $72,293 |
| Correlation: automation prob vs. emp change | r = −0.414 |
| Regression R² | 0.175 |
| Regression coefficient (automation_prob) | −4.15 |
| Automation risk — highest sector | Office & Admin Support (84%) |
| Automation risk — lowest sector | Community & Social Service (5%) |
