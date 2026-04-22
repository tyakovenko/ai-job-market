# Milestone 3 — Data Preparation, Mining, and Visualization
**Taya Yakovenko — AI's Impact on the Job Market**

---

## Data Preparation

The original Kaggle dataset was rejected after preliminary inspection showed near-zero correlations across all variables — a sign of synthetic data with no real signal. The analysis uses three real-world sources instead: Frey & Osborne automation probability scores (702 occupations), BLS employment projections 2024–2034, and the ILO 2025 GenAI Exposure Index (427 ISCO-08 occupations).

The F&O and BLS datasets were joined on SOC code, yielding **606 matched occupations** (86% match rate). The ILO data was bridged via the BLS ISCO-08 × SOC crosswalk, covering 600 of the 606 (99%).

Four features were engineered:
- **`risk_tier`** — Low / Medium / High automation risk bands
- **`occupation_group`** — 22 groups from SOC major code
- **`adaptive_capacity_score`** — normalized wage + education combined into a 0–1 resilience index
- **`vulnerable`** — binary flag: high automation risk + bottom-third adaptive capacity → **144 occupations (23.8%)**

Key data facts: automation probability is bimodal (most jobs cluster at the extremes, not the middle); 65.3% of occupations show positive projected employment growth despite widespread automation risk; the vulnerable group has a median wage of $41,503 vs. $72,293 for non-vulnerable occupations.

---

## Data Mining

Two techniques were applied.

**K-Means clustering (k=3)** on automation risk and adaptive capacity features produced three interpretable segments:

| Cluster | Share | Avg Automation | Avg Wage | Avg Growth |
|---|---|---|---|---|
| High Risk / Low Resilience | 50.8% | 85% | $49,287 | −1.75% |
| Low Risk / Stable | 37.5% | 27% | $66,965 | +2.58% |
| Low Risk / High Skill | 11.7% | 9% | $126,322 | +5.51% |

Half the matched occupations are in the bottom cluster — high automation exposure with virtually no economic buffer.

**Linear regression** (target: projected employment change) confirmed both hypotheses:
- Automation risk negatively predicts employment change (coefficient −4.15; each +10pp automation → −0.42pp growth)
- But the full model — automation + wage + education + 21 occupation-group dummies — explains only **R² = 0.175** on the test set. Most of what determines a job's trajectory lies outside AI exposure.

The largest single predictor in the model was the Computer & Math sector dummy (+12.4pp), reflecting structural tech demand independent of automation risk.

---

## Data Visualization

14 figures were produced across 6 chart types. The full list is in `report/04_data_visualization.md`. Key visuals:

- **Scatter plot (fig2)** — shows the Automation Paradox directly: negative trend, but wide scatter means many high-risk jobs still grow
- **Ranked bars (fig3, fig4)** — clerical/production jobs face the steepest declines; healthcare/tech lead growth
- **Wage gap (fig5, fig10)** — $30,650 gap between high and low risk tiers; vulnerable workers have almost no high-earners in their cohort
- **Dumbbell chart (fig13)** — sector-level risk shift from 2013 to 2025: physical sectors de-risked, knowledge sectors newly exposed; Computer & Math reversed by +43 percentage points
- **Scatter (fig12) and diverging bar (fig14)** — occupation-level flip: writers, analysts, mathematicians are newly exposed; brickmasons, cement masons, landscapers are de-risked

---

*This document was drafted with the assistance of Claude (Anthropic) as a writing and analysis tool. All data, findings, code, and analytical decisions are the author's own.*
