# Stage 2: Dataset Description
**MIS502 Final Project — AI's Impact on the Job Market**
**Points: 15 | Status: Complete — Updated with ILO 2025 GenAI dataset**

---

## 1. Nature and Context of the Datasets

### Why Real-World Data Instead of Synthetic

This project uses two peer-reviewed and government-published datasets rather than the available synthetic Kaggle dataset. Preliminary exploration of the Kaggle dataset revealed that all numeric variables — automation risk, salary, employment projections — had near-zero correlations with each other (r ≈ 0.001–0.012). This is a hallmark of purely random synthetic generation, not real labor market dynamics. Using synthetic data with no internal signal would produce meaningless findings. The two real-world datasets used here are authoritative, widely cited, and directly relevant to the research question.

---

### Dataset 1: Frey & Osborne Automation Probability Scores

**Source:** Frey, C.B. & Osborne, M.A. (2013). *The Future of Employment: How Susceptible Are Jobs to Computerisation?* Oxford Martin School Working Paper.

**Coverage:** 702 US occupations, classified using US Standard Occupational Classification (SOC) codes.

**Key variables:**

| Variable | Description |
|---|---|
| `soc_code` | 6-digit US SOC code — links to BLS data |
| `automation_prob` | Probability (0.003–0.99) that the occupation is automatable based on machine learning capabilities |
| `occupation` | Occupation title as classified in O\*NET |

**How the scores were generated:** Frey and Osborne used a machine learning classifier trained on hand-labeled occupations (based on engineering bottlenecks: perception, manipulation, creativity, social intelligence) to estimate the probability that each job's tasks could be replicated by an algorithm within roughly 20 years. A score of 0.99 means near-certain automation risk; 0.003 means nearly impossible.

**Distribution:** Of 702 occupations, 316 (45%) score above 0.70 (high risk), 145 (21%) score 0.30–0.70 (medium), and 241 (34%) score below 0.30 (low risk).

---

### Dataset 2: BLS Occupational Employment Projections 2024–2034

**Source:** U.S. Bureau of Labor Statistics, *Employment Projections Program*, Table 1.2, released 2024.

**Coverage:** 832 detailed line-item occupations across the US economy (2024 baseline).

**Key variables:**

| Variable | Description |
|---|---|
| `soc_code` | SOC code — links to Frey & Osborne |
| `occupation` | Official BLS occupation title |
| `emp_2024` | Estimated total employment in 2024 (thousands) |
| `emp_2034` | Projected employment in 2034 (thousands) |
| `emp_change_pct` | Percent change in employment 2024–2034 |
| `median_wage_2024` | Median annual wage in 2024 (USD) |
| `education_required` | Typical entry-level education required |
| `annual_openings` | Average annual job openings 2024–2034 |

**Authority:** BLS projections are the US government's official forward-looking labor market estimates, developed using industry-occupation matrices, macroeconomic models, and historical trend analysis. They represent the best available empirical baseline for employment change.

---

---

### Dataset 3: ILO Generative AI Occupational Exposure Index (2025)

**Source:** Gmyrek, P., Berg, J., & Bescond, D. (2025). *Generative AI and Jobs: A Refined Global Index of Occupational Exposure.* ILO Working Paper 140. International Labour Organization & NASK (Poland's National Research Institute).

**Coverage:** 427 ISCO-08 4-digit occupations globally; task-level scoring aggregated from 29,753 tasks across 2,861 sub-tasks, validated by surveys of 1,640 workers.

**Key variables:**

| Variable | Description |
|---|---|
| `ISCO_08` | 4-digit ISCO-08 international occupation code |
| `mean_score_2025` | Mean GenAI exposure score (0–1) in 2025 — how much of the occupation's tasks can be performed or substantially assisted by GenAI |
| `mean_score_2023` | Same score for the 2023 baseline (pre-2025 update) — used as the "early GenAI" comparison point |
| `potential25` | Categorical exposure gradient: Not Exposed, Minimal Exposure, Exposed: Gradient 1–4 |

**How the scores were generated:** Human raters and AI models (GPT-4o and Gemini) independently scored 29,753 occupation tasks on a 0–1 scale for GenAI exposure. Scores were calibrated using semantic similarity to anchor tasks, validated against a worker survey, and aggregated to the occupation level. This is a methodological step beyond Frey & Osborne: instead of predicting *full automation*, it measures *task-level augmentation or replacement* by current GenAI tools.

**Distribution (2025):** 231 occupations (54%) are Not Exposed, 84 (20%) Minimal Exposure, 17+44+38+13 = 112 (26%) in Exposed Gradients 1–4. Only 13 occupations (3%) fall in the highest exposure tier (Gradient 4).

**Bridging to our pipeline:** The ILO dataset uses ISCO-08 codes; our pipeline uses US SOC codes. The BLS official ISCO-08 × SOC 2010 crosswalk was used to map ILO occupations to SOC codes. Where multiple ISCO-08 codes map to one SOC code (fan-in), GenAI exposure scores are averaged. This produced coverage of **600 of 606 occupations (99%)**.

---

### Merged Dataset

The three datasets are combined into a single analysis file of **606 occupations**:
- Frey & Osborne × BLS join: inner join on SOC code → 606 occupations (86% of F&O matches BLS)
- ILO 2025 join: left join via ISCO-SOC crosswalk → 600 of 606 matched (99%)

The 6 unmatched occupations (residual "all other" and niche categories with no ISCO-08 equivalent) retain NaN for GenAI scores and are excluded only from the then/now comparison analysis.

---

## 2. Potential Outcomes from the Analysis

Three hypotheses guide this project:

**H1 — Automation risk is negatively correlated with projected employment growth.**
Expected: occupations with higher automation probability (Frey & Osborne) show lower or negative employment projections (BLS). If automation displaces workers, this should appear as a negative correlation between `automation_prob` and `emp_change_pct`.

**H2 — Automation risk alone is a weak predictor of employment change.**
Counterintuitive hypothesis supported by recent research: automation may raise productivity and wages without eliminating jobs. If R² from a regression of `emp_change_pct` on `automation_prob` alone is low, it suggests that other factors (education, wage level, occupation category) matter more than raw automation exposure.

**H3 — Adaptive capacity (wage + education) separates vulnerable from resilient workers.**
Workers in high-automation occupations with low wages and low education have no safety net. An `adaptive_capacity_score` combining normalized wage and education level should better predict employment vulnerability than automation probability alone. The gap in median wages between vulnerable and non-vulnerable occupations is expected to be significant.

Expected patterns:
- Office & Administrative Support, Production, and Food Preparation will be the highest-risk occupation groups
- Healthcare and Computer & Math occupations will show low automation risk and strong growth
- A "resilience corridor" exists: high automation exposure but also high wages/education (e.g., data scientists, software engineers)

---

## 3. Data Quality, Integrity, and Ethics

### Data Quality Assessment

**Frey & Osborne:**
- No missing values — all 702 occupations have complete scores
- Scores are continuous (0.003–0.99); no outlier issues
- Limitation: published in 2013; machine learning has advanced significantly since then. Some occupations now have lower practical risk than the score suggests (e.g., radiologists), while others may be higher. The scores are widely cited in academic literature despite this age.

**BLS Projections:**
- 6 occupations (of 606 merged) have missing wage data — these are excluded from wage analysis but retained elsewhere
- 38 occupations have missing education level data
- Employment projections are point estimates, not probability distributions — uncertainty is not expressed in the data

**Merged dataset:**
- 696 → 606 occupations after inner join (SOC code mismatches account for 14% loss). BLS occasionally reclassifies or splits occupations between cycles, causing some codes not to match.
- The merge is conservative (inner join): only occupations with exact SOC code matches are included. This reduces sample size but prevents mismatches.

### Ethical Considerations

**Aggregation bias:** Both datasets report at the occupation level, not the individual level. Conclusions about which *jobs* are at risk should not be applied to *people* without acknowledging that workers often hold multiple skills and can transition across occupations.

**Representativeness:** Frey & Osborne's 2013 sample was based on US labor market structure. The automation probabilities may not generalize equally to other countries, genders, or age groups. BLS projections are US-specific.

**Determinism risk:** Presenting automation probability scores as fixed destinies overstates the certainty of the findings. Technology adoption depends on cost, regulation, labor market conditions, and social acceptance — none of which are captured in the data.

**No demographic data:** Unlike the synthetic Kaggle dataset, neither real dataset includes gender or race. The analysis cannot directly test demographic disparities in automation exposure, though this is acknowledged as an important gap.
