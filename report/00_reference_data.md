# Reference Data: Quantitative Figures from Research Sources
## AI Impact on Job Market — MIS502 Final Project

> **Extraction methodology (per NotebookLM):** Figures were located by systematically scanning each source document for numerical digits, percentage symbols, and text-based quantitative markers (e.g., "quarter," "doubled," "fourfold"). For each number found, the surrounding sentence and paragraph were read to verify exactly what the metric measures, what time period it covers, and which organization produced it. Figures are quoted directly from source text — not paraphrased — to prevent hallucination or misattribution. Confidence level: **high** for all figures below.
>
> **Reliability note:** The Kaggle dataset is **synthetic**, generated to reflect patterns from BLS, OECD, McKinsey, and WEF public reports (2024–2030 period). It does not constitute original empirical data. All real-world statistics below come from primary institutional sources. These figures will be used as **benchmark comparators** during data mining — i.e., we test whether our synthetic dataset's patterns align with what real-world research shows.

---

## Source 1: Brookings Institution
**"Measuring US Workers' Capacity to Adapt to AI-Driven Job Displacement"**

### High-Level Workforce Statistics
| Statistic | Value | Notes |
|---|---|---|
| U.S. workers in top AI exposure quartile | 37.1 million | — |
| High-exposure workers with above-median adaptive capacity | 26.5 million (~70%) | Well-positioned for transition |
| High-exposure + low adaptive capacity workers | 6.1 million | The core vulnerable group |
| Vulnerable workers as % of U.S. workforce | 4.2% | — |
| Vulnerable workers who are women | 86% | — |
| National average share in vulnerable occupations | 3.9% | Across U.S. metro areas |
| Range across metro areas | 2.4%–6.9% | — |
| Older workers' re-employment disadvantage | −16 pp | Ages 55–64 vs. 35–44 (post-Great Recession) |
| Occupations in final dataset | 356 | Met data quality thresholds |
| Metro/micro areas analyzed | 927 | Mapped to 2024 Census boundaries |
| U.S. workforce coverage | 95.9% | Final dataset |

### Occupation-Level Data: High Exposure / HIGH Adaptive Capacity
| Occupation | Jobs | % Female | AI Exposure | Adaptive Capacity |
|---|---|---|---|---|
| Computer & Information Systems Managers | 646,000 | 30% | 56% | 99% |
| Marketing Managers | 385,000 | 54% | 60% | 100% |
| Financial & Investment Analysts | 341,000 | 42% | 50% | 99% |
| Other Mathematical Science Occupations | 270,000 | 47% | 66% | 99% |
| Software QA Analysts & Testers | 200,000 | 33% | 60% | 97% |
| Other Financial Specialists | 184,000 | 55% | 58% | 97% |
| Information Security Analysts | 179,000 | 21% | 54% | 97% |
| Computer Network Architects | 177,000 | 14% | 56% | 99% |
| Other Life Scientists | 175,000 | 56% | 55% | 97% |
| Producers & Directors | 145,000 | 42% | 52% | 100% |
| Public Relations & Fundraising Managers | 113,000 | 68% | 54% | 96% |
| Web & Digital Interface Designers | 111,000 | 39% | 68% | 100% |
| Chemists & Materials Scientists | 92,000 | 41% | 46% | 96% |
| Web Developers | 79,000 | 34% | 64% | 97% |
| Computer & Information Research Scientists | 38,000 | 28% | 50% | 97% |

### Occupation-Level Data: High Exposure / LOW Adaptive Capacity (The 6.1M)
| Occupation | Jobs | % Female | AI Exposure | Adaptive Capacity |
|---|---|---|---|---|
| Office Clerks, General | 2,500,000 | 84% | 50% | 22% |
| Secretaries & Admin Assistants (excl. legal/medical/exec) | 1,700,000 | 96% | 59% | 14% |
| Receptionists & Information Clerks | 965,000 | 92% | 58% | 30% |
| Medical Secretaries & Admin Assistants | 831,000 | 94% | 63% | 23% |
| Insurance Sales Agents | 469,000 | 55% | 53% | 24% |
| Insurance Claims & Policy Processing Clerks | 229,000 | 84% | 54% | 30% |
| Court, Municipal & License Clerks | 170,000 | 85% | 58% | 11% |
| Payroll & Timekeeping Clerks | 157,000 | 89% | 50% | 15% |
| Eligibility Interviewers, Govt Programs | 156,000 | 81% | 59% | 18% |
| Legal Secretaries & Admin Assistants | 155,000 | 96% | 75% | 37% |
| Tax Preparers | 74,000 | 63% | 63% | 30% |
| Property Appraisers & Assessors | 59,000 | 43% | 50% | 15% |
| Tax Examiners, Collectors & Revenue Agents | 54,000 | 64% | 62% | 18% |
| Interpreters & Translators | 53,000 | 77% | 82% | 29% |
| Door-to-Door Sales / Street Vendors | 5,000 | 43% | 50% | 3% |

---

## Source 2: Bureau of Labor Statistics (BLS)
**"AI Impacts in BLS Employment Projections" — Projection period: 2023–2033**

### Growing Occupations (High AI Exposure, Positive Growth)
| Occupation | 2023 Jobs | 2033 Jobs | Change | Growth % |
|---|---|---|---|---|
| Software Developers | 1,692,100 | 1,995,700 | +303,700 | **+17.9%** |
| Personal Financial Advisors | 321,000 | 375,900 | +55,000 | +17.1% |
| Computer Occupations (total) | 5,021,800 | 5,608,500 | +586,800 | +11.7% |
| Database Architects | 61,400 | 68,000 | +6,600 | +10.8% |
| Financial & Investment Analysts | 347,400 | 380,500 | +33,100 | +9.5% |
| Electrical Engineers | 189,100 | 206,300 | +17,200 | +9.1% |
| Electronics Engineers (excl. computer) | 98,700 | 107,600 | +8,900 | +9.1% |
| Database Administrators | 80,500 | 87,100 | +6,600 | +8.2% |
| Aerospace Eng. & Operations Technicians | 11,000 | 11,900 | +900 | +7.9% |
| Computer Hardware Engineers | 84,100 | 90,200 | +6,100 | +7.2% |
| Business & Financial Operations | 10,977,200 | 11,738,500 | +761,300 | +6.9% |
| Architecture & Engineering Occupations | 2,639,700 | 2,819,700 | +180,000 | +6.8% |
| Civil Engineers | 341,800 | 363,900 | +22,100 | +6.5% |
| Aerospace Engineers | 68,900 | 73,000 | +4,100 | +6.0% |
| Lawyers | 859,000 | 903,300 | +44,200 | +5.2% |
| Budget Analysts | 50,800 | 52,700 | +2,000 | +3.9% |
| Legal Occupations (total) | 1,394,400 | 1,446,200 | +51,800 | +3.7% |
| Electrical & Electronic Engineering Technicians | 99,600 | 102,600 | +3,000 | +3.0% |
| Paralegals & Legal Assistants | 366,200 | 370,500 | +4,300 | +1.2% |
| **All Occupations (total)** | **167,849,800** | **174,589,000** | **+6,739,200** | **+4.0%** |

### Declining Occupations (High AI Exposure, Negative Growth)
| Occupation | 2023 Jobs | 2033 Jobs | Change | Growth % |
|---|---|---|---|---|
| Credit Analysts | 73,700 | 70,800 | −2,800 | **−3.9%** |
| Claims Adjusters, Examiners & Investigators | 345,200 | 330,000 | −15,200 | **−4.4%** |
| Insurance Appraisers, Auto Damage | 10,500 | 9,500 | −1,000 | **−9.2%** |

### Key Aggregate Finding
- For every **10 percentage point** increase in observed AI task coverage → BLS projected employment growth drops by **0.6 percentage points** (Anthropic × BLS cross-analysis)
- Total jobs tracked in U.S. Job Market Visualizer (BLS OOH): **143 million** across **342 occupations**

---

## Source 3: Anthropic Economic Research
**"Labor Market Impacts of AI: A New Measure and Early Evidence" — March 2026**

### Theoretical vs. Observed AI Exposure
| Metric | Value | Notes |
|---|---|---|
| Claude usage on theoretically feasible tasks | 97% | Tasks rated as LLM-speedable |
| Claude usage on fully feasible tasks (β=1) | 68% | LLM alone can double speed |
| Claude usage on non-feasible tasks (β=0) | 3% | — |
| Theoretical exposure: Computer & Math tasks | 94% | Tasks theoretically LLM-exposed |
| Theoretical exposure: Office & Admin tasks | 90% | Tasks theoretically LLM-exposed |
| **Actual** observed AI coverage: Computer & Math | **33%** | Real Claude usage |
| Actual observed coverage: Computer Programmers | 75% | Highest-exposure occupation |
| Actual observed coverage: Data Entry Keyers | 67% | — |
| Workers with zero observed AI task coverage | 30% | Too infrequent in usage data |

### Demographics of Highly Exposed Workers (vs. Unexposed)
| Metric | Value |
|---|---|
| More likely to be female (high vs. unexposed) | +16 percentage points |
| More likely to be white | +11 percentage points |
| More likely to be Asian | ~2× |
| Earnings premium | +47% higher wages |
| Graduate degree rate — unexposed workers | 4.5% |
| Graduate degree rate — highly exposed workers | 17.4% (~4× more) |

### Labor Market Impact Signals (Young Workers, Post-ChatGPT)
| Metric | Value |
|---|---|
| Monthly job-finding rate into low-exposure roles | 2% (stable) |
| Drop in monthly job-finding rate into high-exposure roles | ~0.5 pp |
| Relative drop in job-finding rate (exposed, post-ChatGPT) | **−14%** vs. 2022 baseline |
| Employment growth ages 22–25: high AI exposure | **−6.5%** (Oct 2022–Dec 2025) |
| Employment growth ages 22–25: low AI exposure | **+11.9%** (same period) |

### Stress-Test Scenarios
| Scenario | Unemployment Impact |
|---|---|
| Top 10% of exposed workers laid off → top quartile | 3%→43% unemployed |
| Top 10% laid off → national aggregate | 4%→13% unemployed |
| "White-collar Great Recession" → top quartile | 6%→16% unemployed |

---

## Source 4: Economic Innovation Group (EIG) & Census Bureau
**"AI and Jobs: The Final Word (Until the Next One)" — August 2025**

| Metric | Value | Notes |
|---|---|---|
| Unemployment increase: most AI-exposed quintile (2022–Q1 2025) | +0.30 pp | Small, stable |
| Unemployment increase: least AI-exposed quintile (same period) | +0.94 pp | 3× larger |
| Share of least-exposed workers who are men | 70% | As of 2025 |
| U.S. businesses using AI in production (early 2024) | 5% | Census Bureau |
| U.S. businesses using AI in production (Aug 2025) | 9% | Census Bureau |
| Businesses in information sector using AI | 27% | — |
| Businesses in publishing using AI | 36% | — |
| Businesses in data processing/computing using AI | 35% | — |
| Firms reporting no net employment impact from AI | ~95% | 2025 |
| Firms expecting employment increase from AI (next 6 mo.) | 6.5% | Late 2025/early 2026 |
| Firms expecting employment decrease from AI (next 6 mo.) | 6.1% | Late 2025/early 2026 |
| AI-using firms that replaced worker tasks with AI | 27% | 2025 |

### Employment Growth by Age & AI Exposure (Oct 2022–Dec 2025)
*Source: Brynjolfsson, Chandar, and Chen (2025)*

| Age Group | High AI Exposure | Low AI Exposure | Overall |
|---|---|---|---|
| 22–25 | **−6.5%** | +11.9% | +2.5% |
| 26–30 | +0.6% | +9.8% | +4.5% |
| 31–34 | +4.0% | +10.5% | +6.7% |
| 35–40 | +11.0% | +16.7% | +13.2% |
| 41–49 | +11.1% | +12.7% | +11.7% |
| 50+ | +7.5% | +8.3% | +7.8% |

---

## Source 5: The Hamilton Project
**"Research on AI and the Labor Market is Still in the First Inning" — March 2026**

| Metric | Value |
|---|---|
| Firms currently using AI in any capacity | <20% (Census BTOS, March 2026) |
| Detectable unemployment increase (Eloundou GPT-4 measure) | +0.2 pp (2022–23 vs. 2024–25) |
| Detectable unemployment increase (Eisfeldt measure) | +0.3 pp (same period) |
| Task classified as "directly exposed" if LLM offers | ≥50% time reduction |

### Historical Rate of Change in Occupational Mix (Kolko 2018 / Census Bureau)
| Decade | Rate of Change |
|---|---|
| 1860s | 6.2% |
| 1870s | 5.9% |
| 1880s–1890s | 3.8% |
| 1900s | 4.6% |
| 1910s | 8.4% |
| 1920s | 6.3% |
| 1930s | 6.7% |
| 1940s | 10.0% |
| 1950s | 10.4% |
| 1960s | 6.3% |
| 1970s | 5.3% |
| 1980s | 5.4% |
| 1990s | 4.1% |
| 2000s | 4.8% |
| 2010–2019 | 5.1% |
| 2019–2024 | **6.1%** |

---

## Source 6: ILO / Gmyrek et al. (2025)
**"Generative AI and Jobs: A Refined Global Index of Occupational Exposure" — ILO Working Paper 140, May 2025**
*Joint study: International Labour Organization & NASK (Poland's National Research Institute)*

| Metric | Value | Notes |
|---|---|---|
| Occupations scored (ISCO-08 4-digit) | 427 | Global coverage |
| Tasks evaluated | 29,753 | Via Polish occupational classification |
| Survey respondents | 1,640 | One per 1-digit ISCO group |
| Data points collected | 52,558 | Task-level automation potential ratings |
| Global employment in exposed occupations | 25% | Of all global employment |
| Share in high-income countries | 34% | Higher due to knowledge-work concentration |
| Highest exposure tier (Gradient 4) | 3.3% of global employment | — |
| Female employment in Gradient 4 | 4.7% | Vs. 2.4% male — gender gap persists into GenAI era |
| Score range | 0–1 | 0 = no GenAI potential; 1 = fully automatable by GenAI |
| Highest-scored occupation (our pipeline) | Data entry keyers | 0.70 |
| Lowest-scored occupation (our pipeline) | Construction laborers / Brickmasons | 0.09 |
| Computer & Math avg GenAI exposure | 56% | vs. 13% traditional automation (F&O 2013) — largest positive shift |
| Production sector avg GenAI exposure | 20% | vs. 82% traditional automation — largest negative shift |

### Key Methodological Differences from Frey & Osborne (2013)
| Dimension | Frey & Osborne (2013) | ILO Gmyrek et al. (2025) |
|---|---|---|
| Question asked | Can the whole occupation be automated? | Which specific tasks can GenAI perform or assist? |
| Technology scope | Machine learning / robotics | Generative AI (LLMs, multimodal) |
| Validation | Expert panel + ML classifier | Worker survey + dual AI scoring (GPT-4o, Gemini) |
| Geographic scope | US only | Global (ISCO-08) |
| Output | Single probability per occupation | Mean score + SD + 4-tier gradient |
| Era | 2013 (predates deep learning dominance) | 2025 (post-ChatGPT, GPT-4 era) |

---

## Source 7: Kaggle Dataset (Synthetic)
**Primary dataset — AI Impact on Job Market, 2024–2030**
*Generated to reflect OECD, McKinsey, and WEF labor market patterns*

| Feature | Value/Distribution |
|---|---|
| Total rows | 30,000 jobs |
| Total columns | 13 features |
| Entertainment industry share | 13% |
| Manufacturing industry share | 13% |
| Other industries | 74% (22,250 jobs) |
| Jobs with Increasing status | 50% |
| Jobs with Decreasing status | 50% |
| High AI impact level | 33% |
| Moderate AI impact level | 33% |
| Low AI impact level | 33% (~9,953 jobs) |
| Requiring Bachelor's Degree | 20% |
| Requiring Master's Degree | 20% |
| Other education levels | 59% (17,757 jobs) |

> **Important:** The 50/50 split between increasing/decreasing jobs and the even distribution across AI impact levels suggest the dataset was constructed to be balanced for analytical purposes. This is atypical of real labor markets (BLS shows mostly growth). Flag this in the Dataset Description report — it is a **synthetic artifact**, not an empirical finding.

---

## How These Figures Feed into the Project

### Stage 3 (Data Wrangling) — Benchmark Validation
After cleaning the Kaggle dataset, compare its distributions against real-world benchmarks:
- Does the dataset's automation risk distribution align with Anthropic's 33% observed coverage for Computer & Math?
- Does gender diversity in high-risk roles reflect Brookings' 86% female finding?
- Flag and document any divergences as synthetic artifacts

### Stage 4 (Data Mining) — Hypothesis Testing Against Benchmarks
Use these figures as **expected values** when interpreting cluster outputs and regression results:
- Clusters should produce a "vulnerable" segment resembling the Brookings 6.1M profile (high exposure, ~85% female, low salary)
- Regression of automation risk → job openings should produce a negative coefficient consistent with Anthropic's −0.6 pp per 10 pp finding
- If the Kaggle data tells a different story, explain why (synthetic construction vs. real market dynamics)

---

*Data extracted: 2026-03-17 | Source: NotebookLM session 8d50f537 & 1e39265f*
*All figures verified against source documents within NotebookLM. Confidence: High.*
