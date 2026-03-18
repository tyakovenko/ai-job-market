# The Automation Paradox
### Who Really Gets Hurt When AI Takes Over?

**MIS502 Final Project — Data Management for Business**
**Author:** Taya Yakovenko

---

## What This Project Is

This project analyzes the real impact of artificial intelligence on the US job market using three authoritative datasets: Frey & Osborne's (2013) automation probability scores, the Bureau of Labor Statistics' 2024–2034 employment projections, and the ILO's 2025 Generative AI Occupational Exposure Index (Gmyrek et al., ILO Working Paper 140).

The central finding: automation risk and job loss are related but not the same thing. Workers most threatened by AI are also the least equipped to adapt — and that gap is widening. We call this the **Automation Paradox**. A second finding emerges from the then/now comparison: **the map of AI risk has fundamentally shifted**. Traditional automation threatened physical and routine manual jobs; GenAI now exposes knowledge workers, analysts, and creatives who were previously considered safe.

---

## Live Deployments

| Deliverable | URL |
|---|---|
| 📊 Interactive Dashboard | [ai-job-market-f9xiuyueob2e2waniawvbd.streamlit.app](https://ai-job-market-f9xiuyueob2e2waniawvbd.streamlit.app/) |
| 📄 Full Report (HTML) | [tyakovenko.github.io/ai-job-market](https://tyakovenko.github.io/ai-job-market) |
| 📑 Report (PDF) | [docs/report/report.pdf](docs/report/report.pdf) |

---

## Project Structure

```
ai-job-market/
├── src/
│   ├── 00_fetch.py          # Downloads all raw datasets (BLS, F&O, ILO, crosswalk)
│   ├── 01_clean.py          # Cleans, merges, engineers features + GenAI exposure scores
│   ├── 02_analyze.py        # Generates all 14 figures (incl. 3 then/now charts)
│   └── 03_mine.py           # K-Means clustering + linear regression
├── data/
│   ├── raw/                 # Downloaded source files (gitignored)
│   └── processed/           # Cleaned and merged CSVs (committed)
├── report/
│   ├── report.qmd           # Quarto comprehensive report (renders to HTML + PDF)
│   ├── 01_dataset_description.md
│   ├── 02_data_wrangling.md
│   ├── 03_data_mining.md
│   └── 04_data_visualization.md
├── dashboard/
│   └── app.py               # Streamlit interactive dashboard (6 tabs)
├── figures/                 # All exported chart PNGs and interactive HTMLs
├── docs/                    # Rendered Quarto site (served by GitHub Pages)
├── .github/workflows/
│   └── refresh.yml          # Annual auto-refresh via GitHub Actions
├── _quarto.yml              # Quarto project config
├── requirements.txt         # Python dependencies (dashboard runtime)
└── .python-version          # Python 3.12 pin for Streamlit Cloud
```

---

## Running Locally

### 1. Prerequisites

- Python 3.12
- [Quarto CLI](https://quarto.org/docs/get-started/) (for rendering the report)

### 2. Setup

```bash
# Clone the repo
git clone https://github.com/tyakovenko/ai-job-market.git
cd ai-job-market

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Download the raw data

```bash
python src/00_fetch.py
```

This downloads four files:
- **BLS Occupational Projections 2024–2034** from bls.gov
- **Frey & Osborne Automation Scores (2013)** from the public GitHub archive
- **ILO GenAI Occupational Exposure Index 2025** (Gmyrek et al., ILO WP140) from GitHub
- **BLS ISCO-08 × SOC 2010 Crosswalk** from bls.gov (bridges ILO ↔ pipeline SOC codes)

> If BLS releases a new projection cycle, pass the updated URL:
> ```bash
> python src/00_fetch.py --bls-url https://www.bls.gov/emp/ind-occ-matrix/occupation.xlsx
> ```

### 4. Run the pipeline

Run scripts in order:

```bash
python src/01_clean.py     # Clean, merge, engineer features → data/processed/
python src/03_mine.py      # Clustering + regression → data/processed/clustered.csv
python src/02_analyze.py   # Generate all 14 figures → figures/
```

> **Note:** `02_analyze.py` depends on both `cleaned_main.csv` and `clustered.csv`, so run `03_mine.py` before `02_analyze.py`.

### 5. Launch the dashboard

```bash
streamlit run dashboard/app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

### 6. Render the report

```bash
quarto render                              # Full site → docs/
quarto render report/report.qmd            # Single file (HTML + PDF)
quarto render report/report.qmd --to pdf   # PDF only
```

---

## Dashboard Guide

The dashboard has 6 tabs:

| Tab | What it shows |
|---|---|
| **Overview** | Risk distribution, wage gap by tier, education vs. risk, vulnerable vs. not box plot |
| **Job Explorer** | Interactive bubble chart (hover any occupation), top 15 at-risk / safest jobs, full data table |
| **By Sector** | Average automation risk ranked by occupation group, sector summary table |
| **Clusters** | K-Means cluster PCA visualization, per-cluster profiles, deep-dive table |
| **The Paradox** | Narrative walkthrough of the Automation Paradox with OLS trend line |
| **Then vs. Now** | ILO 2025 GenAI exposure vs. Frey & Osborne 2013 — the GenAI risk flip, by occupation and sector |

**Sidebar filters** (risk tier, occupation group, wage range, automation probability) apply across all tabs except Clusters.

---

## Data Sources

| Dataset | Source | Coverage | Role |
|---|---|---|---|
| Automation Probability Scores | Frey & Osborne (2013), *The Future of Employment* | 702 US occupations, SOC-coded | Traditional automation baseline |
| Occupational Employment Projections | US Bureau of Labor Statistics, 2024–2034 | ~832 detailed occupations | Employment outlook |
| GenAI Occupational Exposure Index | Gmyrek et al. (2025), ILO Working Paper 140 | 427 ISCO-08 occupations | GenAI exposure "now" |
| ISCO-08 × SOC Crosswalk | US Bureau of Labor Statistics | ~1,100 occupation mappings | Bridges ILO ↔ BLS datasets |

Frey & Osborne and BLS are joined on **SOC codes** → **606 matched occupations**. The ILO GenAI dataset is bridged via the BLS ISCO-08 × SOC crosswalk, covering **600 of 606 occupations (99%)**.

---

## Key Findings

**Traditional automation analysis (2013 baseline):**
- **46.7%** of matched occupations carry high (>70%) automation risk
- High-risk jobs pay a median of **$48,350/year** vs. **$79,000** for low-risk — a $30,650 gap
- Automation risk explains only **17.5% of variance** in employment change (R² = 0.175) — the Paradox
- **3 clusters** identified: High Risk/Low Resilience (50%), Low Risk/Stable (37%), Low Risk/High Skill (12%)
- Most at-risk sector: **Office & Administrative Support** (84% avg automation probability)

**Then vs. Now — the GenAI risk shift (2013 → 2025):**
- The average GenAI exposure score (29%) is substantially lower than traditional automation risk (54%) — but concentrated in different sectors
- **Computer & Math** reversed from low traditional risk (13%) to highest GenAI exposure (56%) — the biggest positive shift (+43 pp)
- **Production, Building & Grounds, Construction** remain high on traditional automation but score low on GenAI exposure (delta: −0.61 to −0.62)
- Top newly-exposed roles: Credit counselors, Operations research analysts, Writers, Editors, Mathematicians — all previously considered "safe"
- The GenAI risk map has effectively inverted: white-collar knowledge work is now the frontier

---

## Automated Data Refresh

A GitHub Actions workflow ([`.github/workflows/refresh.yml`](.github/workflows/refresh.yml)) runs every **January 1st** and:

1. Downloads the latest BLS projections, Frey & Osborne data, ILO GenAI index, and crosswalk
2. Re-runs the full pipeline (`00_fetch` → `01_clean` → `03_mine` → `02_analyze`)
3. Re-renders the Quarto report to `docs/`
4. Commits and pushes all changes — Streamlit Cloud redeploys automatically

To trigger a manual refresh at any time:
1. Go to the **Actions** tab on GitHub
2. Select **"Refresh Data & Redeploy"**
3. Click **"Run workflow"**

---

## Milestone Reports

| Stage | Points | Report |
|---|---|---|
| Dataset Description | 15 pts | [report/01_dataset_description.md](report/01_dataset_description.md) |
| Data Wrangling | 25 pts | [report/02_data_wrangling.md](report/02_data_wrangling.md) |
| Data Mining | 25 pts | [report/03_data_mining.md](report/03_data_mining.md) |
| Data Visualization | 25 pts | [report/04_data_visualization.md](report/04_data_visualization.md) |
| Final Report | — | [report/report.qmd](report/report.qmd) |

---

## References

- Frey, C.B. & Osborne, M.A. (2013). *The Future of Employment: How Susceptible Are Jobs to Computerisation?* Oxford Martin School.
- U.S. Bureau of Labor Statistics (2024). *Employment Projections 2024–2034.* U.S. Department of Labor.
- Gmyrek, P. et al. (2025). *Generative AI and Jobs: A Refined Global Index of Occupational Exposure.* ILO Working Paper 140. International Labour Organization.
- Acemoglu, D. & Restrepo, P. (2018). *Artificial Intelligence, Automation, and Work.* NBER Working Paper 24196.
