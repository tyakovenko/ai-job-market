"""
02_analyze.py
-------------
Stage 5: Data Visualization
Generates all figures for the report and dashboard.

Inputs:
  data/processed/cleaned_main.csv
  data/processed/clustered.csv

Outputs (figures/):
  fig1_risk_distribution.png
  fig2_automation_vs_growth.png + .html
  fig3_top_at_risk.png
  fig4_top_safe.png
  fig5_wage_by_risk.png
  fig6_education_by_risk.png
  fig7_bubble_risk_wage_openings.png
  fig8_industry_avg_risk.png
  fig9_correlation_heatmap.png
  fig10_salary_vulnerability_boxplot.png
  fig11_risk_vs_growth_trend.png + .html
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import os

os.makedirs("figures", exist_ok=True)

df = pd.read_csv("data/processed/cleaned_main.csv")
clustered = pd.read_csv("data/processed/clustered.csv")

PALETTE = {"Low": "#2ecc71", "Medium": "#f39c12", "High": "#e74c3c"}
sns.set_theme(style="whitegrid", font_scale=1.1)

# ── Fig 1: Automation risk tier distribution ─────────────────────────────────
counts = df["risk_tier"].value_counts().reindex(["Low", "Medium", "High"])
fig, ax = plt.subplots(figsize=(7, 4))
counts.plot(kind="bar", ax=ax, color=[PALETTE[t] for t in counts.index], edgecolor="white")
ax.set_title("Occupations by Automation Risk Tier", fontweight="bold")
ax.set_xlabel("Risk Tier"); ax.set_ylabel("Number of Occupations")
ax.set_xticklabels(counts.index, rotation=0)
for i, v in enumerate(counts):
    ax.text(i, v + 1, str(v), ha="center", fontweight="bold")
plt.tight_layout()
fig.savefig("figures/fig1_risk_distribution.png", dpi=150)
plt.close()
print("Saved fig1")

# ── Fig 2: Scatter — automation prob vs. projected growth (interactive) ───────
fig2 = px.scatter(
    df.dropna(subset=["emp_change_pct"]),
    x="automation_prob", y="emp_change_pct",
    color="risk_tier", color_discrete_map=PALETTE,
    hover_name="occupation",
    hover_data={"median_wage_2024": ":$,.0f", "education_required": True,
                "occupation_group": True, "automation_prob": ":.0%"},
    labels={"automation_prob": "Automation Probability (Frey & Osborne)",
            "emp_change_pct": "Projected Employment Change 2024–34 (%)",
            "risk_tier": "Risk Tier"},
    title="Automation Risk vs. Projected Job Growth (BLS 2024–2034)",
    template="plotly_white", height=520,
)
fig2.add_vline(x=0.5, line_dash="dash", line_color="gray",
               annotation_text="50% automation threshold", annotation_position="top right")
fig2.add_hline(y=0, line_dash="dash", line_color="gray",
               annotation_text="No net change")
pio.write_image(fig2, "figures/fig2_automation_vs_growth.png", scale=2)
fig2.write_html("figures/fig2_automation_vs_growth.html")
print("Saved fig2")

# ── Fig 3: Top 15 most at-risk occupations ────────────────────────────────────
at_risk = (df[df["emp_change_pct"].notna()]
           .sort_values(["automation_prob", "emp_change_pct"])
           .head(15))
fig, ax = plt.subplots(figsize=(9, 5))
sns.barplot(data=at_risk, x="emp_change_pct", y="occupation",
            hue="occupation", palette="Reds_r", ax=ax, legend=False)
ax.set_title("Top 15 Most At-Risk Occupations\n(Highest automation + lowest projected growth)",
             fontweight="bold")
ax.set_xlabel("Projected Employment Change (%)"); ax.set_ylabel("")
ax.axvline(0, color="black", linewidth=0.8, linestyle="--")
plt.tight_layout()
fig.savefig("figures/fig3_top_at_risk.png", dpi=150)
plt.close()
print("Saved fig3")

# ── Fig 4: Top 15 safest/fastest-growing occupations ─────────────────────────
safe = (df[df["emp_change_pct"].notna() & (df["automation_prob"] < 0.3)]
        .sort_values("emp_change_pct", ascending=False).head(15))
fig, ax = plt.subplots(figsize=(9, 5))
sns.barplot(data=safe, x="emp_change_pct", y="occupation",
            hue="occupation", palette="Greens_r", ax=ax, legend=False)
ax.set_title("Top 15 Safest Growing Occupations\n(Low automation risk + strongest projected growth)",
             fontweight="bold")
ax.set_xlabel("Projected Employment Change (%)"); ax.set_ylabel("")
plt.tight_layout()
fig.savefig("figures/fig4_top_safe.png", dpi=150)
plt.close()
print("Saved fig4")

# ── Fig 5: Median wage by risk tier ──────────────────────────────────────────
wage_df = df.groupby("risk_tier")["median_wage_2024"].median().reindex(["Low", "Medium", "High"])
fig, ax = plt.subplots(figsize=(7, 4))
wage_df.plot(kind="bar", ax=ax, color=[PALETTE[t] for t in wage_df.index], edgecolor="white")
ax.set_title("Median Annual Wage by Automation Risk Tier", fontweight="bold")
ax.set_xlabel("Risk Tier"); ax.set_ylabel("Median Annual Wage (USD)")
ax.set_xticklabels(["Low", "Medium", "High"], rotation=0)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
plt.tight_layout()
fig.savefig("figures/fig5_wage_by_risk.png", dpi=150)
plt.close()
print("Saved fig5")

# ── Fig 6: Education vs. risk tier (stacked bar) ──────────────────────────────
edu_order = [
    "No formal educational credential", "High school diploma or equivalent",
    "Some college, no degree", "Associate's degree",
    "Bachelor's degree", "Master's degree", "Doctoral or professional degree"
]
edu_risk = (df[df["education_required"].notna()]
            .groupby(["education_required", "risk_tier"]).size()
            .unstack(fill_value=0)
            .reindex([e for e in edu_order if e in df["education_required"].unique()]))
fig, ax = plt.subplots(figsize=(10, 5))
edu_risk.plot(kind="bar", stacked=True, ax=ax,
              color=[PALETTE[t] for t in edu_risk.columns])
ax.set_title("Automation Risk Distribution by Education Level Required", fontweight="bold")
ax.set_xlabel(""); ax.set_ylabel("Number of Occupations")
ax.set_xticklabels(ax.get_xticklabels(), rotation=35, ha="right")
ax.legend(title="Risk Tier")
plt.tight_layout()
fig.savefig("figures/fig6_education_by_risk.png", dpi=150)
plt.close()
print("Saved fig6")

# ── Fig 7: Bubble chart — automation risk vs. wage; size = annual openings ────
bubble_df = df.dropna(subset=["emp_change_pct", "median_wage_2024", "annual_openings"])
fig7 = px.scatter(
    bubble_df,
    x="automation_prob",
    y="median_wage_2024",
    size="annual_openings",
    color="risk_tier",
    color_discrete_map=PALETTE,
    hover_name="occupation",
    hover_data={"emp_change_pct": True, "education_required": True,
                "annual_openings": ":,.0f"},
    labels={"automation_prob": "Automation Probability",
            "median_wage_2024": "Median Annual Wage ($)",
            "risk_tier": "Risk Tier",
            "annual_openings": "Annual Openings"},
    title="Automation Risk vs. Wage — Bubble Size = Annual Job Openings",
    template="plotly_white", height=520,
    size_max=40,
)
fig7.update_yaxes(tickprefix="$", tickformat=",")
pio.write_image(fig7, "figures/fig7_bubble_risk_wage_openings.png", scale=2)
fig7.write_html("figures/fig7_bubble_risk_wage_openings.html")
print("Saved fig7")

# ── Fig 8: Average automation risk by occupation group ────────────────────────
grp_risk = (df.groupby("occupation_group")["automation_prob"]
            .mean().sort_values(ascending=False))
colors8 = ["#e74c3c" if v > 0.5 else "#3498db" for v in grp_risk.values]
fig, ax = plt.subplots(figsize=(10, 6))
grp_risk.plot(kind="barh", ax=ax, color=colors8, alpha=0.85)
ax.axvline(0.5, color="gray", linestyle="--", linewidth=0.9, label="50% threshold")
ax.set_title("Average Automation Risk by Occupation Group", fontweight="bold")
ax.set_xlabel("Average Automation Probability"); ax.set_ylabel("")
ax.legend()
plt.tight_layout()
fig.savefig("figures/fig8_industry_avg_risk.png", dpi=150)
plt.close()
print("Saved fig8")

# ── Fig 9: Correlation heatmap ────────────────────────────────────────────────
corr_cols = ["automation_prob", "emp_change_pct", "median_wage_2024",
             "education_level", "adaptive_capacity_score", "annual_openings"]
corr_labels = ["Automation Risk", "Employment Change %", "Median Wage",
               "Education Level", "Adaptive Capacity", "Annual Openings"]
corr = df[corr_cols].corr()
fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0,
            xticklabels=corr_labels, yticklabels=corr_labels,
            ax=ax, linewidths=0.5)
ax.set_title("Correlation Matrix — Key Numeric Features", fontweight="bold")
plt.xticks(rotation=35, ha="right"); plt.yticks(rotation=0)
plt.tight_layout()
fig.savefig("figures/fig9_correlation_heatmap.png", dpi=150)
plt.close()
print("Saved fig9")

# ── Fig 10: Box plot — wage distribution by vulnerability flag ────────────────
df["Vulnerable"] = df["vulnerable"].map({True: "Vulnerable", False: "Not Vulnerable"})
fig, ax = plt.subplots(figsize=(7, 5))
sns.boxplot(data=df, x="Vulnerable", y="median_wage_2024",
            palette={"Vulnerable": "#e74c3c", "Not Vulnerable": "#2ecc71"}, ax=ax)
ax.set_title("Median Wage Distribution: Vulnerable vs. Not Vulnerable Jobs",
             fontweight="bold")
ax.set_xlabel(""); ax.set_ylabel("Median Annual Wage ($)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
plt.tight_layout()
fig.savefig("figures/fig10_salary_vulnerability_boxplot.png", dpi=150)
plt.close()
print("Saved fig10")

# ── Fig 11: Scatter + trend line — automation risk vs. projected openings ──────
trend_df = df.dropna(subset=["emp_change_pct"])
fig11 = px.scatter(
    trend_df, x="automation_prob", y="emp_change_pct",
    trendline="ols",
    color="risk_tier", color_discrete_map=PALETTE,
    hover_name="occupation",
    labels={"automation_prob": "Automation Probability",
            "emp_change_pct": "Projected Employment Change (%)"},
    title="Automation Risk vs. Employment Change — With Trend Line",
    template="plotly_white", height=480,
    opacity=0.5,
)
pio.write_image(fig11, "figures/fig11_risk_vs_growth_trend.png", scale=2)
fig11.write_html("figures/fig11_risk_vs_growth_trend.html")
print("Saved fig11")

print("\nAll figures generated.")
