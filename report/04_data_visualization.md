# Stage 5: Data Visualization
**MIS502 Final Project — AI's Impact on the Job Market**
**Points: 25 | Status: Complete**

---

## Overview

This stage produces 11 visualizations across 5 chart types to support the project narrative. All figures are saved as high-resolution PNGs in `figures/` and interactive HTML versions are provided for the 3 Plotly charts. Source code is in `src/02_analyze.py`.

---

## Chart 1: Bar Chart — Automation Risk Tier Distribution

**File:** `figures/fig1_risk_distribution.png`
**Chart type:** Bar chart

**Variables:** `risk_tier` (categorical: Low/Medium/High), count of occupations

**Why this chart type:** A bar chart is the clearest way to compare counts across a small number of discrete categories. Pie charts would obscure the magnitude differences; this allows direct comparison.

**What it reveals:** Of 606 matched occupations, 283 (46.7%) fall in the High risk tier, 204 (33.7%) in Low, and only 119 (19.6%) in Medium. The distribution is bimodal — occupations cluster at the extremes rather than the middle. This reflects the nature of task structure: jobs are either heavily routine (automatable) or heavily non-routine (not automatable), with fewer jobs genuinely in between.

---

## Chart 2: Scatter Plot — Automation Risk vs. Employment Change (Interactive)

**File:** `figures/fig2_automation_vs_growth.png` | `figures/fig2_automation_vs_growth.html`
**Chart type:** Scatter plot (colored by risk tier)

**Variables:** `automation_prob` (x-axis), `emp_change_pct` (y-axis), `risk_tier` (color)

**Why this chart type:** A scatter plot reveals the relationship between two continuous variables simultaneously for all 600 occupations. Color encoding adds a third dimension. Reference lines at x=0.5 and y=0 create four quadrants, making it easy to identify the most concerning segment (high automation + declining employment).

**What it reveals:** There is a clear negative trend — high-risk occupations are more likely to appear in the lower portion of the chart (declining employment). However, the relationship is far from deterministic: many high-automation occupations still show positive growth, illustrating the Automation Paradox. The upper-left quadrant (low automation, growing) is dominated by healthcare and technology occupations.

---

## Chart 3: Horizontal Bar — Top 15 Most At-Risk Occupations

**File:** `figures/fig3_top_at_risk.png`
**Chart type:** Ranked horizontal bar chart

**Variables:** `occupation` (y-axis), `emp_change_pct` (x-axis)
**Selection:** Sorted by automation probability ascending, then by emp_change_pct ascending — the most automated jobs with the worst growth prospects.

**Why this chart type:** A ranked bar chart is ideal for showing a clear "top/bottom" list. Horizontal orientation accommodates long occupation names without truncation.

**What it reveals:** The most at-risk occupations are concentrated in clerical, administrative, and production roles: data entry keyers, word processors, insurance underwriters, and watch repairers — all with automation probabilities exceeding 95% and declining employment projections. These are exactly the roles where automation is not merely theoretical but already underway.

---

## Chart 4: Horizontal Bar — Top 15 Safest Growing Occupations

**File:** `figures/fig4_top_safe.png`
**Chart type:** Ranked horizontal bar chart

**Variables:** `occupation` (y-axis), `emp_change_pct` (x-axis)
**Selection:** Occupations with automation probability < 0.30 and highest positive employment change.

**Why this chart type:** Same rationale as Chart 3 — ranked horizontal bars for clear comparison of named occupations. The green color palette visually contrasts with the red-coded at-risk chart, reinforcing the narrative of two diverging futures.

**What it reveals:** The fastest-growing low-risk occupations are concentrated in healthcare (nurse practitioners, physician assistants, home health aides) and technology (software developers, data scientists). These roles require complex human judgment, physical dexterity in unpredictable environments, or deep domain expertise — all barriers to automation. Projected growth rates reach 20%+ over the decade.

---

## Chart 5: Bar Chart — Median Wage by Risk Tier

**File:** `figures/fig5_wage_by_risk.png`
**Chart type:** Bar chart

**Variables:** `risk_tier` (x-axis), median of `median_wage_2024` (y-axis)

**Why this chart type:** A simple bar chart is appropriate for comparing a single summary statistic (median) across three groups. The result is clear and immediately interpretable.

**What it reveals:** A stark wage gradient by risk tier: Low risk occupations have a median annual wage of **$79,000**, Medium risk **$57,150**, and High risk only **$48,350**. The $30,650 wage gap between high-risk and low-risk occupations means that the workers most threatened by AI are also the least able to afford retraining or career transitions. This is the economic core of the Automation Paradox.

---

## Chart 6: Stacked Bar — Education Level by Risk Tier

**File:** `figures/fig6_education_by_risk.png`
**Chart type:** Stacked bar chart

**Variables:** `education_required` (x-axis, ordered from least to most), `risk_tier` (stacked color)

**Why this chart type:** A stacked bar chart shows both the absolute count and the composition (risk tier mix) within each education level simultaneously. This reveals whether higher education is protective.

**What it reveals:** Jobs requiring no formal credential or a high school diploma are overwhelmingly high-risk (red dominates). As education level rises, the share of high-risk occupations falls and the green (low risk) share increases. Doctoral/professional degree occupations are almost entirely low or medium risk. Education is the strongest protective factor in the dataset — more so than wage alone.

---

## Chart 7: Bubble Chart — Automation Risk vs. Wage (Size = Annual Openings)

**File:** `figures/fig7_bubble_risk_wage_openings.png` | `figures/fig7_bubble_risk_wage_openings.html`
**Chart type:** Bubble scatter plot

**Variables:** `automation_prob` (x), `median_wage_2024` (y), `annual_openings` (bubble size), `risk_tier` (color)

**Why this chart type:** A bubble chart encodes four variables simultaneously. The bubble size adds volume information (how many jobs are opening each year), making it possible to identify not just risky jobs but risky jobs *at scale* — the ones that matter most for the overall workforce.

**What it reveals:** Large red bubbles in the lower-left corner represent the highest-risk, lowest-wage, highest-volume occupations — the jobs displacing the most people. Large green bubbles in the upper area represent the safe, high-wage occupations generating new openings. The chart visually summarizes the inequality divide that AI is amplifying.

---

## Chart 8: Horizontal Bar — Average Automation Risk by Occupation Group

**File:** `figures/fig8_industry_avg_risk.png`
**Chart type:** Ranked horizontal bar chart

**Variables:** `occupation_group` (y-axis), mean of `automation_prob` (x-axis)

**Why this chart type:** A ranked horizontal bar chart makes sector-level comparisons clear and sortable. The color coding (red above 50%, blue below) instantly identifies which groups are above or below the threshold.

**What it reveals:** Office & Administrative Support (84%), Production (82%), Farming & Fishing (78%), Building & Grounds (78%), and Food Preparation (76%) are the highest-risk groups. Community & Social Service (5%), Healthcare Practitioners (12%), Computer & Math (13%), and Management (14%) are the lowest risk. This is consistent with Frey & Osborne's original findings and with the academic consensus: routine physical and cognitive tasks are most automatable.

---

## Chart 9: Heatmap — Correlation Matrix

**File:** `figures/fig9_correlation_heatmap.png`
**Chart type:** Correlation heatmap

**Variables:** `automation_prob`, `emp_change_pct`, `median_wage_2024`, `education_level`, `adaptive_capacity_score`, `annual_openings`

**Why this chart type:** A heatmap is the standard tool for visualizing a full correlation matrix. The diverging color scale (red for negative, blue for positive) makes patterns immediately visible.

**What it reveals:**
- `automation_prob` has a moderate negative correlation with `emp_change_pct` (−0.41) — confirming H1
- `education_level` and `median_wage_2024` are positively correlated with `emp_change_pct` (+0.32, +0.28) — confirming H3
- `adaptive_capacity_score` correlates strongly with `median_wage_2024` (+0.74) by construction (wage is a component)
- No single variable dominates — this multicollinearity explains the moderate R² in the regression

---

## Chart 10: Box Plot — Wage by Vulnerability Flag

**File:** `figures/fig10_salary_vulnerability_boxplot.png`
**Chart type:** Box plot

**Variables:** `vulnerable` (binary, x-axis), `median_wage_2024` (y-axis)

**Why this chart type:** Box plots show the full distribution (median, IQR, whiskers, outliers) rather than just a mean. This is important for wage data, which is right-skewed. Comparing two distributions side-by-side makes the disparity immediately visible.

**What it reveals:** Vulnerable occupations (high automation risk + low adaptive capacity) have a tightly clustered wage distribution centered at $41,503 with very little spread ($36,010–$55,000 IQR). Non-vulnerable occupations span a much wider range, with a median of $63,280 and a long right tail reaching $226,600. The gap is not just in averages — vulnerable workers have almost no high-earners in their cohort.

---

## Chart 11: Scatter + OLS Trend Line — Automation Risk vs. Employment Change

**File:** `figures/fig11_risk_vs_growth_trend.png` | `figures/fig11_risk_vs_growth_trend.html`
**Chart type:** Scatter plot with OLS regression trend line

**Variables:** `automation_prob` (x), `emp_change_pct` (y), `risk_tier` (color), OLS fit line per tier

**Why this chart type:** Adding a trend line to a scatter plot makes the direction and approximate magnitude of the relationship visible at a glance without requiring the reader to interpret regression coefficients. Per-tier trend lines reveal whether the automation-growth relationship differs across risk levels.

**What it reveals:** The downward slope of the overall trend line confirms the negative relationship between automation risk and employment change. High-risk occupations have a steeper negative slope than low-risk ones. Notably, the confidence interval widens in the high-risk zone — some high-automation occupations are still growing, which is the core empirical evidence for the Automation Paradox.

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
