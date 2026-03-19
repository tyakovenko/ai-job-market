"""
dashboard/app.py
----------------
Interactive Streamlit dashboard for the AI Impact on Job Market analysis.
Run with: streamlit run dashboard/app.py
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="The Automation Paradox",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: #1e1e2e;
        border-radius: 12px;
        padding: 16px 20px;
        border-left: 4px solid;
    }
    .block-container { padding-top: 1.5rem; }
    h1 { font-size: 2rem !important; }
    h2 { font-size: 1.4rem !important; color: #a0aec0; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 8px 20px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df  = pd.read_csv("data/processed/cleaned_main.csv")
    cl  = pd.read_csv("data/processed/clustered.csv")
    return df, cl

df, clustered = load_data()

PALETTE = {"Low": "#2ecc71", "Medium": "#f39c12", "High": "#e74c3c"}
CLUSTER_COLORS = {
    "High Risk / Low Resilience":  "#e74c3c",
    "High Risk / High Resilience": "#e67e22",
    "Low Risk / High Skill":       "#2ecc71",
    "Low Risk / Stable":           "#3498db",
}

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🤖 The Automation Paradox")
st.markdown("**MIS502 Final Project** — Who really gets hurt when AI takes over? | BLS 2024–2034 × Frey & Osborne (2013) × ILO GenAI Index (2025)")
st.divider()

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.header("🔍 Filters")
st.sidebar.caption("Filters apply to all tabs except Clusters.")

# Risk data toggle — applies to Overview, Job Explorer, By Sector, Clusters
risk_view = st.sidebar.radio(
    "📊 Risk Score",
    ["Traditional (2013)", "GenAI (2025)"],
    index=0,
    horizontal=True,
    help="Switch between Frey & Osborne (2013) automation probability and ILO (2025) GenAI exposure index.",
)
use_genai = risk_view == "GenAI (2025)"
risk_col   = "genai_exposure_2025" if use_genai else "automation_prob"
risk_label = "GenAI Exposure — ILO (2025)" if use_genai else "Automation Risk — F&O (2013)"
risk_short = "GenAI Exposure" if use_genai else "Automation Risk"

st.sidebar.divider()

risk_filter = st.sidebar.multiselect(
    "Risk Tier",
    options=["Low", "Medium", "High"],
    default=["Low", "Medium", "High"],
)

grp_options = sorted(df["occupation_group"].dropna().unique())
grp_filter  = st.sidebar.multiselect(
    "Occupation Group",
    options=grp_options,
    default=grp_options,
)

wage_min = int(df["median_wage_2024"].min())
wage_max = int(df["median_wage_2024"].max())
wage_filter = st.sidebar.slider(
    "Median Annual Wage ($)",
    min_value=wage_min, max_value=wage_max,
    value=(wage_min, wage_max), step=1000,
    format="$%d",
)

auto_filter = st.sidebar.slider(
    f"{risk_short} Range",
    min_value=0.0, max_value=1.0,
    value=(0.0, 1.0), step=0.05,
    format="%.2f",
)

# ── Build view dataframe with dynamic risk tier ────────────────────────────────
df_view = df.copy()
if use_genai:
    df_view = df_view.dropna(subset=["genai_exposure_2025"])
    df_view["_risk_tier"] = pd.cut(
        df_view["genai_exposure_2025"],
        bins=[-0.001, 0.3, 0.7, 1.001],
        labels=["Low", "Medium", "High"],
    ).astype(str)
    df_view["_risk_tier"] = df_view["_risk_tier"].where(df_view["_risk_tier"] != "nan", other=None)
else:
    df_view["_risk_tier"] = df_view["risk_tier"]

filtered = df_view[
    df_view["_risk_tier"].isin(risk_filter) &
    df_view["occupation_group"].isin(grp_filter) &
    df_view["median_wage_2024"].between(wage_filter[0], wage_filter[1]) &
    df_view[risk_col].between(auto_filter[0], auto_filter[1])
]

# ── KPI strip ─────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Occupations", f"{len(filtered):,}", help="Matching current filters")
c2.metric("High-Risk Jobs", f"{(filtered['_risk_tier']=='High').sum():,}",
          delta=f"{(filtered['_risk_tier']=='High').mean():.0%} of filtered")
c3.metric(f"Avg {risk_short}", f"{filtered[risk_col].mean():.0%}")
c4.metric("Vulnerable Jobs",
          f"{filtered['vulnerable'].sum():,}",
          help="High traditional automation + low adaptive capacity")
c5.metric("Avg Projected Growth", f"{filtered['emp_change_pct'].mean():.1f}%")

st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Overview",
    "🔎 Job Explorer",
    "🏭 By Sector",
    "🧩 Clusters",
    "📖 The Paradox",
    "⏳ Then vs. Now",
])

# ────────────────────────────────────────────────────────────────────────────
# TAB 1 — OVERVIEW
# ────────────────────────────────────────────────────────────────────────────
with tab1:
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader(f"{risk_short} Distribution")
        counts = filtered["_risk_tier"].value_counts().reindex(["Low", "Medium", "High"]).reset_index()
        counts.columns = ["Risk Tier", "Count"]
        fig = px.bar(counts, x="Risk Tier", y="Count",
                     color="Risk Tier", color_discrete_map=PALETTE,
                     text="Count", template="plotly_white")
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False, height=340)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("Median Wage by Risk Tier")
        wage_df = (filtered.groupby("_risk_tier")["median_wage_2024"]
                   .median().reindex(["Low", "Medium", "High"]).reset_index())
        wage_df.columns = ["Risk Tier", "Median Wage"]
        fig = px.bar(wage_df, x="Risk Tier", y="Median Wage",
                     color="Risk Tier", color_discrete_map=PALETTE,
                     template="plotly_white", text_auto="$,.0f")
        fig.update_traces(textposition="outside")
        fig.update_yaxes(tickprefix="$", tickformat=",")
        fig.update_layout(showlegend=False, height=340)
        st.plotly_chart(fig, use_container_width=True)

    col_c, col_d = st.columns(2)

    with col_c:
        st.subheader(f"Education Level vs. {risk_short} Tier")
        edu_order = [
            "No formal educational credential",
            "High school diploma or equivalent",
            "Some college, no degree",
            "Associate's degree",
            "Bachelor's degree",
            "Master's degree",
            "Doctoral or professional degree",
        ]
        edu_risk = (filtered[filtered["education_required"].notna()]
                    .groupby(["education_required", "_risk_tier"])
                    .size().reset_index(name="count"))
        fig = px.bar(edu_risk, x="education_required", y="count",
                     color="_risk_tier", color_discrete_map=PALETTE,
                     category_orders={"education_required": edu_order,
                                      "_risk_tier": ["Low", "Medium", "High"]},
                     labels={"education_required": "", "count": "Occupations",
                             "_risk_tier": "Risk Tier"},
                     template="plotly_white", barmode="stack")
        fig.update_xaxes(tickangle=35)
        fig.update_layout(height=360, legend_title="Risk Tier")
        st.plotly_chart(fig, use_container_width=True)

    with col_d:
        st.subheader("Wage Gap: Vulnerable vs. Not Vulnerable")
        st.caption("Vulnerability is defined using traditional automation risk + adaptive capacity.")
        vul = filtered.copy()
        vul["Vulnerability"] = vul["vulnerable"].map({True: "Vulnerable", False: "Not Vulnerable"})
        fig = px.box(vul, x="Vulnerability", y="median_wage_2024",
                     color="Vulnerability",
                     color_discrete_map={"Vulnerable": "#e74c3c",
                                         "Not Vulnerable": "#2ecc71"},
                     template="plotly_white",
                     labels={"median_wage_2024": "Median Annual Wage ($)"})
        fig.update_yaxes(tickprefix="$", tickformat=",")
        fig.update_layout(showlegend=False, height=360)
        st.plotly_chart(fig, use_container_width=True)

# ────────────────────────────────────────────────────────────────────────────
# TAB 2 — JOB EXPLORER
# ────────────────────────────────────────────────────────────────────────────
with tab2:
    st.subheader(f"{risk_label} vs. Projected Employment Change")
    st.caption("Each dot is one occupation. Hover for details. Use sidebar filters to focus.")

    bubble_df = filtered.dropna(subset=["emp_change_pct", "annual_openings"])
    fig = px.scatter(
        bubble_df,
        x=risk_col, y="emp_change_pct",
        size="annual_openings", size_max=45,
        color="_risk_tier", color_discrete_map=PALETTE,
        hover_name="occupation",
        hover_data={
            "median_wage_2024":    ":$,.0f",
            "education_required":  True,
            "occupation_group":    True,
            "annual_openings":     ":,.0f",
            risk_col:              ":.0%",
            "emp_change_pct":      ":.1f",
            "_risk_tier":          False,
        },
        labels={
            risk_col:           risk_label,
            "emp_change_pct":   "Projected Employment Change 2024–34 (%)",
            "_risk_tier":       "Risk Tier",
            "annual_openings":  "Annual Openings",
        },
        template="plotly_white", height=560,
    )
    fig.add_vline(x=0.5, line_dash="dash", line_color="gray",
                  annotation_text="50% threshold",
                  annotation_position="top right")
    fig.add_hline(y=0, line_dash="dash", line_color="gray",
                  annotation_text="No net change",
                  annotation_position="right")
    fig.update_layout(legend_title="Risk Tier")
    st.plotly_chart(fig, use_container_width=True)

    col_l, col_r = st.columns(2)

    with col_l:
        st.subheader("⚠️ Most At-Risk Occupations")
        at_risk = (filtered[filtered["emp_change_pct"].notna()]
                   .sort_values([risk_col, "emp_change_pct"])
                   .head(15))
        fig = px.bar(at_risk, x="emp_change_pct", y="occupation",
                     orientation="h", color=risk_col,
                     color_continuous_scale="Reds",
                     hover_data={"median_wage_2024": ":$,.0f"},
                     labels={"emp_change_pct": "Projected Change (%)",
                             "occupation": "",
                             risk_col: risk_short},
                     template="plotly_white")
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=440,
                          coloraxis_colorbar_title=risk_short)
        fig.add_vline(x=0, line_dash="dash", line_color="black", line_width=0.8)
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.subheader("✅ Safest Growing Occupations")
        safe = (filtered[filtered["emp_change_pct"].notna() &
                         (filtered[risk_col] < 0.3)]
                .sort_values("emp_change_pct", ascending=False)
                .head(15))
        fig = px.bar(safe, x="emp_change_pct", y="occupation",
                     orientation="h", color=risk_col,
                     color_continuous_scale="Greens_r",
                     hover_data={"median_wage_2024": ":$,.0f"},
                     labels={"emp_change_pct": "Projected Change (%)",
                             "occupation": "",
                             risk_col: risk_short},
                     template="plotly_white")
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=440,
                          coloraxis_colorbar_title=risk_short)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Full Data Table")
    display_cols = ["occupation", "occupation_group", "_risk_tier",
                    risk_col, "emp_change_pct",
                    "median_wage_2024", "education_required", "vulnerable"]
    st.dataframe(
        filtered[display_cols].sort_values(risk_col, ascending=False)
        .rename(columns={
            "occupation":        "Occupation",
            "occupation_group":  "Group",
            "_risk_tier":        "Risk Tier",
            risk_col:            risk_short,
            "emp_change_pct":    "Projected Change %",
            "median_wage_2024":  "Median Wage $",
            "education_required":"Education Required",
            "vulnerable":        "Vulnerable",
        }),
        use_container_width=True,
        height=350,
    )

# ────────────────────────────────────────────────────────────────────────────
# TAB 3 — BY SECTOR
# ────────────────────────────────────────────────────────────────────────────
with tab3:
    st.subheader(f"Average {risk_short} by Occupation Group")

    grp_stats = (filtered.groupby("occupation_group")
                 .agg(avg_risk=(risk_col, "mean"),
                      avg_wage=("median_wage_2024", "median"),
                      avg_growth=("emp_change_pct", "mean"),
                      count=("occupation", "count"))
                 .reset_index()
                 .sort_values("avg_risk", ascending=False))

    fig = px.bar(grp_stats, x="avg_risk", y="occupation_group",
                 orientation="h",
                 color="avg_risk",
                 color_continuous_scale=["#2ecc71", "#f39c12", "#e74c3c"],
                 hover_data={"avg_wage": ":$,.0f",
                             "avg_growth": ":.1f",
                             "count": True},
                 labels={"avg_risk":          f"Avg {risk_short}",
                         "occupation_group":  "",
                         "avg_wage":          "Median Wage",
                         "avg_growth":        "Avg Growth %",
                         "count":             "# Occupations"},
                 template="plotly_white", height=560)
    fig.add_vline(x=0.5, line_dash="dash", line_color="gray",
                  annotation_text="50% threshold")
    fig.update_layout(yaxis={"categoryorder": "total ascending"},
                      coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Sector Summary Table")
    grp_stats_display = grp_stats.rename(columns={
        "occupation_group": "Group",
        "avg_risk":         f"Avg {risk_short}",
        "avg_wage":         "Median Wage ($)",
        "avg_growth":       "Avg Growth %",
        "count":            "# Occupations",
    }).style.format({
        f"Avg {risk_short}": "{:.0%}",
        "Median Wage ($)": "${:,.0f}",
        "Avg Growth %": "{:.1f}%",
    }).background_gradient(subset=[f"Avg {risk_short}"], cmap="RdYlGn_r")
    st.dataframe(grp_stats_display, use_container_width=True)

# ────────────────────────────────────────────────────────────────────────────
# TAB 4 — CLUSTERS
# ────────────────────────────────────────────────────────────────────────────
with tab4:
    st.subheader("K-Means Cluster Analysis")
    st.caption("4 clusters fitted on automation probability, adaptive capacity, wage, and education. "
               "Visualized using PCA (2 components). Sidebar filters do NOT apply here.")

    if use_genai:
        st.info(
            "ℹ️ Clusters are pre-computed from **Frey & Osborne (2013) traditional automation data**. "
            "Switching to GenAI view does not re-cluster occupations — the cluster assignments remain "
            "the same. The scatter below is colored by cluster as usual; use the **Then vs. Now** tab "
            "to explore the GenAI risk shift at the occupation level.",
            icon="ℹ️",
        )

    cl_data = clustered.dropna(subset=["cluster_label", "pca_1", "pca_2"])

    col_scatter, col_profile = st.columns([3, 2])

    with col_scatter:
        fig = px.scatter(
            cl_data,
            x="pca_1", y="pca_2",
            color="cluster_label",
            color_discrete_map=CLUSTER_COLORS,
            hover_name="occupation",
            hover_data={
                "automation_prob":        ":.0%",
                "adaptive_capacity_score":":.3f",
                "emp_change_pct":         ":.1f",
                "median_wage_2024":       ":$,.0f",
                "pca_1": False, "pca_2": False,
            },
            labels={"pca_1": "PC1 (variance explained)",
                    "pca_2": "PC2 (variance explained)",
                    "cluster_label": "Cluster"},
            title="Occupation Clusters (PCA 2D Projection)",
            template="plotly_white",
            height=480, opacity=0.65,
        )
        fig.update_layout(legend_title="Cluster", legend=dict(
            orientation="h", yanchor="bottom", y=-0.3, xanchor="left", x=0))
        st.plotly_chart(fig, use_container_width=True)

    with col_profile:
        st.markdown("#### Cluster Profiles")
        profile = (cl_data.groupby("cluster_label")
                   .agg(count=("occupation", "count"),
                        automation=("automation_prob", "mean"),
                        capacity=("adaptive_capacity_score", "mean"),
                        growth=("emp_change_pct", "mean"),
                        wage=("median_wage_2024", "median"))
                   .reset_index()
                   .sort_values("automation", ascending=False))

        for _, row in profile.iterrows():
            color = CLUSTER_COLORS.get(row["cluster_label"], "#888")
            st.markdown(f"""
<div style="border-left:4px solid {color}; padding:10px 14px;
            margin-bottom:10px; background:#1a1a2e; border-radius:0 8px 8px 0;">
<b style="color:{color}">{row['cluster_label']}</b><br>
<small>
{int(row['count'])} occupations &nbsp;|&nbsp;
Automation: {row['automation']:.0%} &nbsp;|&nbsp;
Adaptive Capacity: {row['capacity']:.3f}<br>
Median Wage: ${row['wage']:,.0f} &nbsp;|&nbsp;
Avg Growth: {row['growth']:+.1f}%
</small>
</div>
""", unsafe_allow_html=True)

    st.subheader("Cluster Deep Dive")
    chosen = st.selectbox("Select a cluster to explore:",
                          options=sorted(cl_data["cluster_label"].dropna().unique()))
    sub = cl_data[cl_data["cluster_label"] == chosen][
        ["occupation", "occupation_group", "automation_prob",
         "adaptive_capacity_score", "emp_change_pct", "median_wage_2024",
         "education_required"]
    ].sort_values("automation_prob", ascending=False)
    st.dataframe(
        sub.rename(columns={
            "occupation":             "Occupation",
            "occupation_group":       "Group",
            "automation_prob":        "Automation Prob",
            "adaptive_capacity_score":"Adaptive Capacity",
            "emp_change_pct":         "Growth %",
            "median_wage_2024":       "Median Wage $",
            "education_required":     "Education",
        }),
        use_container_width=True, height=340,
    )

# ────────────────────────────────────────────────────────────────────────────
# TAB 5 — THE PARADOX (narrative)
# ────────────────────────────────────────────────────────────────────────────
with tab5:
    st.subheader("📖 The Automation Paradox: A Data-Driven Story")

    st.markdown("""
### The Headline Is Wrong

Most AI-and-jobs coverage focuses on a simple story: AI takes jobs, workers suffer.
The data tells a more complicated — and more troubling — truth.

**Fact 1:** Most occupations, even high-automation ones, show *positive* projected
employment growth through 2034. 65% of the 606 occupations in this analysis are
expected to grow.

**Fact 2:** Automation risk and job loss are correlated (r = −0.41), but weakly.
A linear regression model using automation probability, wages, education, and
occupation group explains only **17.5% of the variance** in projected employment change.
Automation is one factor among many — not the dominant one.

**This is the Automation Paradox.** AI raises productivity and creates new roles even
as it displaces specific tasks. The aggregate numbers look fine. But averages hide
the distribution.
""")

    # Scatter with trend — always uses traditional automation for the paradox narrative
    fig = px.scatter(
        df.dropna(subset=["emp_change_pct"]),
        x="automation_prob", y="emp_change_pct",
        trendline="ols",
        color="risk_tier", color_discrete_map=PALETTE,
        hover_name="occupation",
        labels={"automation_prob": "Automation Probability (Frey & Osborne 2013)",
                "emp_change_pct": "Projected Employment Change (%)",
                "risk_tier": "Risk Tier"},
        template="plotly_white", height=420, opacity=0.45,
    )
    fig.add_vline(x=0.5, line_dash="dash", line_color="gray")
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
### Who Actually Gets Hurt

The paradox masks a concentrated crisis. Filter to the workers who are:
1. In high-automation occupations (>70% probability), AND
2. In the bottom third of adaptive capacity (low wages + low education)

**Result: 144 occupations, 23.8% of the dataset.**

These workers cannot afford to wait for aggregate employment growth. They lack the
wages to fund retraining, the education credentials to pivot careers, and the savings
to weather a job search. Their median annual wage is **$41,503** — compared to
**$63,280** for non-vulnerable workers.

### The Three Futures

The cluster analysis reveals three distinct paths for workers in the AI economy:

| Group | Share | Avg Wage | Outlook |
|---|---|---|---|
| **High Risk / Low Resilience** | 50% | $49,287 | Declining employment, no safety net |
| **Low Risk / Stable** | 37% | $66,965 | Modest growth, moderate security |
| **Low Risk / High Skill** | 12% | $126,322 | Strong growth, high wages |

The top 12% are pulling away. The bottom 50% are at risk. The middle 37% are stable
— but their low adaptive capacity means any disruption could tip them into the first
group.

### What the Data Says We Should Do

1. **Target retraining to specific occupation codes** — the vulnerable group is
   identifiable. Broad programs miss them.
2. **Raise wage floors** — adaptive capacity requires income. Low-wage workers
   can't access training markets even when programs exist.
3. **Invest in healthcare careers** — the safest, fastest-growing jobs are
   concentrated in healthcare. Removing barriers to these careers is labor policy.
""")

    st.markdown("""
### A New Wrinkle: The GenAI Shift

The analysis above is grounded in Frey & Osborne's 2013 automation scores — which predicted
physical, routine, and clerical jobs were most at risk. A decade later, the ILO's 2025 GenAI
Exposure Index tells a different story.

**The risk map has flipped.**

| Sector | Traditional Automation Risk (2013) | GenAI Exposure (2025) | Shift |
|---|---|---|---|
| Computer & Math | 13% | 56% | **+43 pp** — newly exposed |
| Management | 14% | 37% | **+22 pp** — newly exposed |
| Arts & Media | 21% | 37% | **+16 pp** — newly exposed |
| Production | 82% | 20% | **−62 pp** — de-risked |
| Building & Grounds | 78% | 15% | **−62 pp** — de-risked |
| Construction | 74% | 13% | **−61 pp** — de-risked |

Writers, analysts, counselors, and mathematicians — who barely registered on the 2013 risk map —
are now among the most GenAI-exposed occupations. Sewers, brickmasons, and groundskeepers — who
Frey & Osborne flagged as near-certain automation targets — are effectively safe from GenAI.

The Automation Paradox has a sequel: **the workers we thought were safe may not be, and the
workers we feared for may be safer than expected.** Explore this fully in the **Then vs. Now** tab.
""")

    st.info("💡 **For the interactive version:** Use the Job Explorer tab to hover "
            "over any occupation and see its full profile. Use the Clusters tab to "
            "explore which occupations fall into each group. Use **Then vs. Now** to "
            "see the 2013 → 2025 risk shift in detail.", icon="💡")

# ────────────────────────────────────────────────────────────────────────────
# TAB 6 — THEN VS. NOW (ILO 2025 GenAI Exposure)
# ────────────────────────────────────────────────────────────────────────────
with tab6:
    st.subheader("⏳ Then vs. Now: How AI Risk Has Shifted (2013 → 2025)")
    st.markdown(
        "Traditional automation models (Frey & Osborne, 2013) predicted that **physical "
        "and routine manual jobs** were most at risk. A decade later, the ILO's 2025 "
        "GenAI Exposure Index tells a different story: **knowledge workers, writers, "
        "analysts, and tech roles** now face the highest exposure. The risk map flipped."
    )
    st.caption(
        "Sources: Frey & Osborne (2013) via SOC codes · "
        "Gmyrek et al. (2025) ILO Working Paper 140 · "
        "BLS ISCO-08 × SOC crosswalk. "
        "6 occupations with no ISCO-08 match excluded."
    )
    st.divider()

    # Working dataset — drop the 6 unmatched occupations
    thenow = df[df["occupation_group"].isin(grp_filter)].dropna(subset=["genai_exposure_2025"]).copy()
    thenow["risk_delta"] = thenow["genai_exposure_2025"] - thenow["automation_prob"]

    # ── KPI strip ─────────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Occupations with GenAI score", f"{len(thenow):,}")
    k2.metric(
        "Avg Traditional Risk (2013)",
        f"{thenow['automation_prob'].mean():.0%}",
        help="Frey & Osborne automation probability",
    )
    k3.metric(
        "Avg GenAI Exposure (2025)",
        f"{thenow['genai_exposure_2025'].mean():.0%}",
        help="ILO Gmyrek et al. mean exposure score",
    )
    k4.metric(
        "Avg Risk Delta",
        f"{thenow['risk_delta'].mean():+.2f}",
        help="Positive = more exposed under GenAI than traditional automation",
    )

    st.divider()

    # ── Fig 12 — Scatter: automation_prob vs genai_exposure_2025 ──────────────
    st.subheader("Occupation-Level Risk Shift")
    st.caption(
        "Each dot is one occupation. **Above the diagonal** = newly exposed by GenAI "
        "(underestimated by 2013 models). **Below the diagonal** = old automation risk "
        "that GenAI doesn't replicate (physical/manual jobs)."
    )

    fig_scatter = px.scatter(
        thenow,
        x="automation_prob",
        y="genai_exposure_2025",
        color="occupation_group",
        hover_name="occupation",
        hover_data={
            "automation_prob":      ":.0%",
            "genai_exposure_2025":  ":.0%",
            "risk_delta":           ":.2f",
            "occupation_group":     False,
        },
        labels={
            "automation_prob":     "Traditional Automation Risk — Frey & Osborne (2013)",
            "genai_exposure_2025": "GenAI Exposure — ILO (2025)",
            "occupation_group":    "Sector",
        },
        template="plotly_white",
        height=520,
        opacity=0.65,
    )
    # Diagonal: x = y means risk unchanged between 2013 and 2025
    fig_scatter.add_shape(
        type="line", x0=0, y0=0, x1=1, y1=1,
        line=dict(color="gray", dash="dash", width=1),
    )
    fig_scatter.add_annotation(
        x=0.82, y=0.93, text="Same risk then & now",
        showarrow=False, font=dict(color="gray", size=11), textangle=-38,
    )
    fig_scatter.update_layout(legend_title="Sector")
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.divider()

    # ── Fig 13 — Sector dumbbell ───────────────────────────────────────────────
    st.subheader("Sector-Level Risk Shift")
    st.caption(
        "Average traditional automation risk (2013) vs. average GenAI exposure (2025) "
        "per sector. Sorted by GenAI exposure. Sectors near the top saw risk *increase* "
        "under GenAI; sectors near the bottom are *safer* from GenAI than from traditional automation."
    )

    sector = (
        thenow.groupby("occupation_group")[["automation_prob", "genai_exposure_2025"]]
        .mean()
        .reset_index()
        .sort_values("genai_exposure_2025", ascending=False)
    )

    # Build a long-form dataframe for grouped bars
    sector_long = sector.melt(
        id_vars="occupation_group",
        value_vars=["automation_prob", "genai_exposure_2025"],
        var_name="Era",
        value_name="Score",
    )
    sector_long["Era"] = sector_long["Era"].map({
        "automation_prob":     "2013 — Traditional Automation (F&O)",
        "genai_exposure_2025": "2025 — GenAI Exposure (ILO)",
    })

    fig_sector = px.bar(
        sector_long,
        x="Score",
        y="occupation_group",
        color="Era",
        orientation="h",
        barmode="group",
        color_discrete_map={
            "2013 — Traditional Automation (F&O)": "#3498db",
            "2025 — GenAI Exposure (ILO)":         "#e74c3c",
        },
        labels={"Score": "Average Score", "occupation_group": ""},
        template="plotly_white",
        height=600,
    )
    fig_sector.add_vline(x=0.5, line_dash="dash", line_color="gray", opacity=0.5)
    fig_sector.update_layout(
        yaxis={"categoryorder": "total ascending"},
        legend_title="Era",
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
    )
    st.plotly_chart(fig_sector, use_container_width=True)

    st.divider()

    # ── Fig 14 — Biggest movers ────────────────────────────────────────────────
    st.subheader("The Biggest Movers")

    col_gain, col_lose = st.columns(2)

    with col_gain:
        st.markdown("#### Newly Exposed by GenAI")
        st.caption("Occupations where GenAI exposure far exceeds traditional automation risk")
        gainers = (
            thenow.nlargest(15, "risk_delta")
            [["occupation", "occupation_group", "automation_prob", "genai_exposure_2025", "risk_delta"]]
            .sort_values("risk_delta", ascending=True)
        )
        fig_gain = px.bar(
            gainers,
            x="risk_delta",
            y="occupation",
            orientation="h",
            color="risk_delta",
            color_continuous_scale=[[0, "#f9c6c6"], [1, "#e74c3c"]],
            hover_data={
                "automation_prob":     ":.0%",
                "genai_exposure_2025": ":.0%",
                "occupation_group":    True,
                "risk_delta":          ":.2f",
            },
            labels={"risk_delta": "Risk Delta", "occupation": ""},
            template="plotly_white",
            height=480,
        )
        fig_gain.update_layout(
            coloraxis_showscale=False,
            yaxis={"categoryorder": "total ascending"},
        )
        fig_gain.add_vline(x=0, line_color="black", line_width=0.8)
        st.plotly_chart(fig_gain, use_container_width=True)

    with col_lose:
        st.markdown("#### De-Risked by GenAI Shift")
        st.caption("High traditional automation risk — but GenAI poses little threat (physical/manual jobs)")
        losers = (
            thenow.nsmallest(15, "risk_delta")
            [["occupation", "occupation_group", "automation_prob", "genai_exposure_2025", "risk_delta"]]
            .sort_values("risk_delta", ascending=False)
        )
        fig_lose = px.bar(
            losers,
            x="risk_delta",
            y="occupation",
            orientation="h",
            color="risk_delta",
            color_continuous_scale=[[0, "#2980b9"], [1, "#d6eaf8"]],
            hover_data={
                "automation_prob":     ":.0%",
                "genai_exposure_2025": ":.0%",
                "occupation_group":    True,
                "risk_delta":          ":.2f",
            },
            labels={"risk_delta": "Risk Delta", "occupation": ""},
            template="plotly_white",
            height=480,
        )
        fig_lose.update_layout(
            coloraxis_showscale=False,
            yaxis={"categoryorder": "total descending"},
        )
        fig_lose.add_vline(x=0, line_color="black", line_width=0.8)
        st.plotly_chart(fig_lose, use_container_width=True)

    # ── Raw comparison table ───────────────────────────────────────────────────
    st.subheader("Full Then vs. Now Table")
    st.caption("Sortable. Use sidebar filters to narrow by sector or wage range.")
    display = (
        thenow[["occupation", "occupation_group", "automation_prob",
                "genai_exposure_2025", "risk_delta"]]
        .sort_values("risk_delta", ascending=False)
        .rename(columns={
            "occupation":          "Occupation",
            "occupation_group":    "Sector",
            "automation_prob":     "Traditional Risk (2013)",
            "genai_exposure_2025": "GenAI Exposure (2025)",
            "risk_delta":          "Δ Risk",
        })
    )
    st.dataframe(
        display.style.format({
            "Traditional Risk (2013)": "{:.0%}",
            "GenAI Exposure (2025)":   "{:.0%}",
            "Δ Risk":                  "{:+.2f}",
        }).background_gradient(subset=["Δ Risk"], cmap="RdBu_r", vmin=-0.9, vmax=0.6),
        use_container_width=True,
        height=380,
    )
