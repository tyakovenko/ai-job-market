# The Automation Paradox: Who Really Gets Hurt When AI Takes Over?
**MIS502 · Data Analytics for Business**
**Target duration: 10 minutes**

---

## Slide 1 — Hook
**[Visual: Full-bleed image of office workers or a mixed office/factory scene. Title text large and white, overlaid. No bullets.]**

> *"Everyone says AI is killing jobs. The data says it's more complicated — and more worrying — than that."*

---

## Slide 2 — The Question
**[Visual: White background, three rows. Each row: icon + one question line. No other text.]**

- 🔍 Which jobs are *actually* at risk — and are those the same ones projected to decline?
- ⚖️ Does AI exposure predict job loss, or does something else matter more?
- 🛡️ Can we identify *who* is most vulnerable before displacement hits?

---

## Slide 3 — The Data
**[Visual: Three horizontal cards side by side. Each card: source name bold, one-line description, one stat. Add a small callout box in a different color for the Kaggle note.]**

| Card color | Source | What it contains | Key stat |
|---|---|---|---|
| Blue | Frey & Osborne (2013) | Automation probability for US occupations | 702 occupations |
| Green | BLS Projections 2024–2034 | Government employment forecasts + wages | 832 occupations |
| Red | ILO GenAI Exposure (2025) | Task-level GenAI exposure by occupation | 427 ISCO-08 occupations |

**Callout box:**
> Original Kaggle dataset was synthetic — cross-variable correlations r ≈ 0.001. No usable signal. Discarded before wrangling.

**Speaker notes:** Each source captures a different layer. Frey & Osborne tells us which jobs *could* be automated. BLS tells us which jobs are actually *growing or shrinking*. ILO tells us how that picture has changed now that GenAI is in the mix.

---

## Slide 4 — Data Preparation
**[Visual: Left side — numbered 4-step list. Right side — one summary box with final dataset stats. Clean, minimal.]**

**How three datasets became one:**

1. **Loaded** — Frey & Osborne CSV, BLS Excel projection table, ILO GenAI Excel, BLS ISCO↔SOC crosswalk
2. **Filtered** — BLS had 1,117 rows including subtotals; kept only 832 line-item occupations
3. **Merged** — Inner join on SOC code: 702 × 832 → **606 matched occupations** (86% match rate)
4. **Engineered features:**
   - `risk_tier` — Low / Medium / High automation bands
   - `adaptive_capacity_score` — composite of normalized wage + education (0–1 scale)
   - `vulnerable` — binary flag: high automation risk AND low adaptive capacity
   - `genai_exposure_2025` — ILO score added via ISCO-08 crosswalk (99% coverage)

**Summary box:**
- Final dataset: **606 occupations, 20 columns**
- Vulnerable occupations: **144 (23.8%)**
- Missing values: handled contextually — no rows dropped

**Speaker notes:** The merge step is where the project's integrity lives. An 86% match rate across a decade-old taxonomy is strong — the 14% loss is BLS recoding occupations between 2013 and 2024, not data quality issues.

---

## Slide 5 — The Automation Paradox
**[Visual: `fig11_risk_vs_growth_trend.png` fills 80% of slide. Title only above chart. One annotation directly on the chart pointing to a high-risk dot above the zero line: "High-risk job, still growing."]**

**`FIGURE: figures/fig11_risk_vs_growth_trend.png`**
*(Scatter plot: automation probability on x-axis, projected employment change % on y-axis, with OLS trend line)*

**Speaker notes:** The trend line slopes downward — that's real. But look at the spread. Plenty of high-automation jobs are still projected to grow. The correlation is −0.41, not −1.0. Automation risk is a signal, not a sentence.

---

## Slide 6 — Who Is Actually Vulnerable?
**[Visual: Two-column split. Left: five jobs in large red text with their decline numbers. Right: wage comparison with a downward arrow. No chart — this is designed text.]**

**Left column — Biggest projected declines among high-risk jobs:**

| Occupation | Projected Change |
|---|---|
| Word processors & typists | −36% |
| Telephone operators | −28% |
| Data entry keyers | −26% |
| Telemarketers | −22% |
| Payroll & timekeeping clerks | −17% |

**Right column — The resource gap:**

```
High-risk workers:   $36,490 median wage
Low-risk workers:    $72,080 median wage
                         ↓
  Same threat. Half the resources to adapt.
```

**Speaker notes:** This is the double bind. The jobs declining fastest are also the lowest paid — the workers least able to fund retraining or weather a transition period are the ones most exposed.

---

## Slide 7 — Data Mining: Three Worker Segments
**[Visual: Three colored cards or a horizontal bar chart. Each card: cluster name, size, key stats. Color: red / yellow / green.]**

**`FIGURE: figures/fig_clusters_profile.png`**
*(Bar chart showing cluster profiles by automation probability, adaptive capacity, wage)*

**K-Means clustering (k=3) found three distinct groups among 600 occupations:**

| Segment | Size | Avg Automation Risk | Avg Wage | Employment Trend |
|---|---|---|---|---|
| 🔴 High Risk / Low Resilience | 305 (51%) | 85% | $49K | −1.75% |
| 🟡 Low Risk / Stable | 225 (38%) | 27% | $67K | +2.58% |
| 🟢 Low Risk / High Skill | 70 (12%) | 9% | $126K | +5.51% |

*High Risk / Low Resilience examples: data entry clerks, cashiers, telemarketers*
*Low Risk / High Skill examples: software developers, physicians, financial managers*

**Speaker notes:** The elbow method pointed to k=4, but three clusters told a cleaner story with no loss in interpretability. The wage gap between the bottom and top clusters is 2.6× — $49K vs $126K.

---

## Slide 8 — Data Mining: Does Automation Actually Predict Job Loss?
**[Visual: `fig_regression.png` on left (~50% width). Key findings as 3 bullet points on right. Title only above.]**

**`FIGURE: figures/fig_regression.png`**
*(Scatter of actual vs. predicted employment change from regression model)*

**Linear regression — predicting employment change from automation risk + worker characteristics:**

- **Coefficient:** Each 10-point increase in automation probability → **−0.42 percentage points** in employment growth
- **Wage effect:** Largest single predictor in the model — Computer & Math occupations: **+12.4 pp** vs. baseline
- **Model fit:** R² = 0.175 on held-out test data — automation risk is a *real* signal, not the whole story

> "Automation risk explains part of the picture. Wage and occupation type fill in the rest."

**Speaker notes:** R² of 0.175 sounds low, but that's the test set — no data leakage. Train R² was 0.40. The gap reflects 21 occupation-group dummies on ~480 training rows — a known limitation we documented. The -0.42 coefficient is statistically meaningful and directionally consistent with H1.

---

## Slide 9 — The GenAI Twist
**[Visual: `fig13_sector_risk_shift.png` fills 80% of slide. Title only. Two annotations directly on the chart.]**

**`FIGURE: figures/fig13_sector_risk_shift.png`**
*(Dumbbell chart: each row is a sector, left dot = F&O 2013 automation score, right dot = ILO 2025 GenAI exposure score)*

**Annotations to add on the chart:**
- Circle Computer & Math: *"13% → 56%"*
- Circle Production: *"82% → 20%"*

**Speaker notes:** This is the reversal. In 2013, factory workers and clerks were the at-risk population. In 2025, GenAI has flipped the exposure map — knowledge workers, analysts, and creatives now carry the highest exposure. The workers who thought they were safe are not.

---

## Slide 10 — So What?
**[Visual: White background, three rows, icon + one sentence each. No chart.]**

1. 🎯 **Target retraining** — the vulnerable population is identifiable by occupation code today, before displacement hits
2. 💰 **Income and training together** — wage support is as necessary as program access; the workers most at risk can't afford the gap
3. 🏥 **Healthcare is the hedge** — fastest-growing sector, lowest automation exposure, driven by demographics that won't reverse

**Speaker notes:** These aren't abstract policy points — they follow directly from the data. Cluster 1 is named. The income gap is measured. Healthcare's growth trajectory is in the BLS projections.

---

## Slide 11 — One Takeaway
**[Visual: Single quote, centered, large font. Dark or light background — nothing else on the slide.]**

> *"AI exposure and job loss aren't the same thing — but for workers who are both highly exposed and have no financial buffer, the distinction doesn't matter."*

---

## Timing Guide

| Slide | Topic | Target |
|---|---|---|
| 1 | Hook | 0:30 |
| 2 | The Question | 1:00 |
| 3 | The Data | 2:00 |
| 4 | Data Preparation | 3:30 |
| 5 | Automation Paradox (viz) | 4:30 |
| 6 | Who Is Vulnerable (viz) | 5:30 |
| 7 | Data Mining — Clusters | 7:00 |
| 8 | Data Mining — Regression | 8:00 |
| 9 | GenAI Twist (viz) | 9:00 |
| 10 | So What | 9:45 |
| 11 | Takeaway | 10:00 |

---

## Figures Needed

| Slide | File | Notes |
|---|---|---|
| 5 | `figures/fig11_risk_vs_growth_trend.png` | Add annotation: "High-risk job, still growing." on a dot above zero line in high-risk zone |
| 7 | `figures/fig_clusters_profile.png` | Bar chart of cluster profiles — use as-is |
| 8 | `figures/fig_regression.png` | Actual vs. predicted scatter — use as-is |
| 9 | `figures/fig13_sector_risk_shift.png` | Add two annotations: Computer & Math "13%→56%", Production "82%→20%" |

---

## Design Notes
- Slides with charts: chart fills 80%, title line only, no bullets
- Slides without charts: icon + one sentence per row, max three rows
- Color coding throughout: red = high risk, green = low risk, yellow/orange = medium
- Speaker notes are for *you only* — nothing on those slides goes on screen
