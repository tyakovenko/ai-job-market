# The Automation Paradox
### Who Really Gets Hurt When AI Takes Over?

**MIS502 Final Project — Data Management for Business**
**Author:** Taya Yakovenko

---

## What This Project Is

This project analyzes the real impact of artificial intelligence on the US job market using two authoritative datasets: Frey & Osborne's (2013) automation probability scores for 702 occupations and the Bureau of Labor Statistics' 2024–2034 employment projections.

The central finding: automation risk and job loss are related but not the same thing. The workers most threatened by AI are also the least equipped to adapt — and that gap is widening. We call this the **Automation Paradox**.

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
│   ├── 00_fetch.py          # Downloads raw datasets from BLS and GitHub
│   ├── 01_clean.py          # Cleans, merges, and engineers features
│   ├── 02_analyze.py        # Generates all 11 figures
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
│   └── app.py               # Streamlit interactive dashboard (5 tabs)
├── figures/                 # All exported chart PNGs and interactive HTMLs
├── docs/                    # Rendered Quarto site (served by GitHub Pages)
├── .github/workflows/
│   └── refresh.yml          # Annual auto-refresh via GitHub Actions
├── _quarto.yml              # Quarto project config
├── requirements.txt         # Python dependencies (dashboard runtime)
├── runtime.txt              # Python version hint (legacy)
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

This downloads:
- **BLS Occupational Projections 2024–2034** from bls.gov
- **Frey & Osborne Automation Scores** from the public GitHub archive

> If BLS releases a new projection cycle, pass the updated URL:
> ```bash
> python src/00_fetch.py --bls-url https://www.bls.gov/emp/ind-occ-matrix/occupation.xlsx
> ```

### 4. Run the pipeline

Run scripts in order:

```bash
python src/01_clean.py     # Clean, merge, engineer features → data/processed/
python src/02_analyze.py   # Generate figures              → figures/
python src/03_mine.py      # Clustering + regression       → data/processed/clustered.csv
```

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

The dashboard has 5 tabs:

| Tab | What it shows |
|---|---|
| **Overview** | Risk distribution, wage gap by tier, education vs. risk, vulnerable vs. not box plot |
| **Job Explorer** | Interactive bubble chart (hover any occupation), top 15 at-risk / safest jobs, full data table |
| **By Sector** | Average automation risk ranked by occupation group, sector summary table |
| **Clusters** | K-Means cluster PCA visualization, per-cluster profiles, deep-dive table |
| **The Paradox** | Narrative walkthrough of the Automation Paradox with OLS trend line |

**Sidebar filters** (risk tier, occupation group, wage range, automation probability) apply across all tabs except Clusters.

---

## Data Sources

| Dataset | Source | Coverage | License |
|---|---|---|---|
| Automation Probability Scores | Frey & Osborne (2013), *The Future of Employment* | 702 US occupations, SOC-coded | Academic / public |
| Occupational Employment Projections | US Bureau of Labor Statistics, 2024–2034 | ~832 detailed occupations | Public domain (US Gov) |

The two datasets are joined on **SOC (Standard Occupational Classification) codes**, producing a merged dataset of **606 occupations**.

---

## Automated Data Refresh

A GitHub Actions workflow ([`.github/workflows/refresh.yml`](.github/workflows/refresh.yml)) runs every **January 1st** and:

1. Downloads the latest BLS projections and Frey & Osborne data
2. Re-runs the full pipeline (`00_fetch` → `01_clean` → `02_analyze` → `03_mine`)
3. Re-renders the Quarto report to `docs/`
4. Commits and pushes all changes — Streamlit Cloud redeploys automatically

To trigger a manual refresh at any time:
1. Go to the **Actions** tab on GitHub
2. Select **"Refresh Data & Redeploy"**
3. Click **"Run workflow"**

---

## Key Findings

- **46.7%** of matched occupations carry high (>70%) automation risk
- High-risk jobs pay a median of **$48,350/year** vs. **$79,000** for low-risk jobs — a $30,650 gap
- Automation risk explains only **17.5% of variance** in employment change (R² = 0.175) — the Paradox
- **3 clusters** identified: High Risk/Low Resilience (50%), Low Risk/Stable (37%), Low Risk/High Skill (12%)
- Most at-risk sector: **Office & Administrative Support** (84% avg automation probability)
- Safest sector: **Community & Social Service** (5% avg automation probability)

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
- Acemoglu, D. & Restrepo, P. (2018). *Artificial Intelligence, Automation, and Work.* NBER Working Paper 24196.
