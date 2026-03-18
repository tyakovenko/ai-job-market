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
st.markdown("**MIS502 Final Project** — Who really gets hurt when AI takes over? | BLS 2024–2034 × Frey & Osborne (2013)")
st.divider()

# ── Sidebar filters ───────────────────────────────────────────────────────────
st.sidebar.header("🔍 Filters")
st.sidebar.caption("Filters apply to all tabs except Clusters.")

risk_filter = st.sidebar.multiselect(
    "Automation Risk Tier",
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
    "Automation Probability Range",
    min_value=0.0, max_value=1.0,
    value=(0.0, 1.0), step=0.05,
    format="%.2f",
)

filtered = df[
    df["risk_tier"].isin(risk_filter) &
    df["occupation_group"].isin(grp_filter) &
    df["median_wage_2024"].between(wage_filter[0], wage_filter[1]) &
    df["automation_prob"].between(auto_filter[0], auto_filter[1])
]

# ── KPI strip ─────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Occupations", f"{len(filtered):,}", help="Matching current filters")
c2.metric("High-Risk Jobs", f"{(filtered['risk_tier']=='High').sum():,}",
          delta=f"{(filtered['risk_tier']=='High').mean():.0%} of filtered")
c3.metric("Avg Automation Risk", f"{filtered['automation_prob'].mean():.0%}")
c4.metric("Vulnerable Jobs",
          f"{filtered['vulnerable'].sum():,}",
          help="High automation + low adaptive capacity")
c5.metric("Avg Projected Growth", f"{filtered['emp_change_pct'].mean():.1f}%")

st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "🔎 Job Explorer",
    "🏭 By Sector",
    "🧩 Clusters",
    "📖 The Paradox",
])

# ────────────────────────────────────────────────────────────────────────────
# TAB 1 — OVERVIEW
# ────────────────────────────────────────────────────────────────────────────
with tab1:
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Automation Risk Distribution")
        counts = filtered["risk_tier"].value_counts().reindex(["Low", "Medium", "High"]).reset_index()
        counts.columns = ["Risk Tier", "Count"]
        fig = px.bar(counts, x="Risk Tier", y="Count",
                     color="Risk Tier", color_discrete_map=PALETTE,
                     text="Count", template="plotly_white")
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False, height=340)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("Median Wage by Risk Tier")
        wage_df = (filtered.groupby("risk_tier")["median_wage_2024"]
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
        st.subheader("Education Level vs. Risk Tier")
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
                    .groupby(["education_required", "risk_tier"])
                    .size().reset_index(name="count"))
        fig = px.bar(edu_risk, x="education_required", y="count",
                     color="risk_tier", color_discrete_map=PALETTE,
                     category_orders={"education_required": edu_order,
                                      "risk_tier": ["Low", "Medium", "High"]},
                     labels={"education_required": "", "count": "Occupations",
                             "risk_tier": "Risk Tier"},
                     template="plotly_white", barmode="stack")
        fig.update_xaxes(tickangle=35)
        fig.update_layout(height=360, legend_title="Risk Tier")
        st.plotly_chart(fig, use_container_width=True)

    with col_d:
        st.subheader("Wage Gap: Vulnerable vs. Not Vulnerable")
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
    st.subheader("Automation Risk vs. Projected Employment Change")
    st.caption("Each dot is one occupation. Hover for details. Use sidebar filters to focus.")

    bubble_df = filtered.dropna(subset=["emp_change_pct", "annual_openings"])
    fig = px.scatter(
        bubble_df,
        x="automation_prob", y="emp_change_pct",
        size="annual_openings", size_max=45,
        color="risk_tier", color_discrete_map=PALETTE,
        hover_name="occupation",
        hover_data={
            "median_wage_2024":    ":$,.0f",
            "education_required":  True,
            "occupation_group":    True,
            "annual_openings":     ":,.0f",
            "automation_prob":     ":.0%",
            "emp_change_pct":      ":.1f",
            "risk_tier":           False,
        },
        labels={
            "automation_prob":  "Automation Probability (Frey & Osborne)",
            "emp_change_pct":   "Projected Employment Change 2024–34 (%)",
            "risk_tier":        "Risk Tier",
            "annual_openings":  "Annual Openings",
        },
        template="plotly_white", height=560,
    )
    fig.add_vline(x=0.5, line_dash="dash", line_color="gray",
                  annotation_text="50% automation threshold",
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
                   .sort_values(["automation_prob", "emp_change_pct"])
                   .head(15))
        fig = px.bar(at_risk, x="emp_change_pct", y="occupation",
                     orientation="h", color="automation_prob",
                     color_continuous_scale="Reds",
                     hover_data={"median_wage_2024": ":$,.0f"},
                     labels={"emp_change_pct": "Projected Change (%)",
                             "occupation": "",
                             "automation_prob": "Automation Prob"},
                     template="plotly_white")
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=440,
                          coloraxis_colorbar_title="Automation<br>Prob")
        fig.add_vline(x=0, line_dash="dash", line_color="black", line_width=0.8)
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.subheader("✅ Safest Growing Occupations")
        safe = (filtered[filtered["emp_change_pct"].notna() &
                         (filtered["automation_prob"] < 0.3)]
                .sort_values("emp_change_pct", ascending=False)
                .head(15))
        fig = px.bar(safe, x="emp_change_pct", y="occupation",
                     orientation="h", color="automation_prob",
                     color_continuous_scale="Greens_r",
                     hover_data={"median_wage_2024": ":$,.0f"},
                     labels={"emp_change_pct": "Projected Change (%)",
                             "occupation": "",
                             "automation_prob": "Automation Prob"},
                     template="plotly_white")
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=440,
                          coloraxis_colorbar_title="Automation<br>Prob")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Full Data Table")
    display_cols = ["occupation", "occupation_group", "risk_tier",
                    "automation_prob", "emp_change_pct",
                    "median_wage_2024", "education_required", "vulnerable"]
    st.dataframe(
        filtered[display_cols].sort_values("automation_prob", ascending=False)
        .rename(columns={
            "occupation":        "Occupation",
            "occupation_group":  "Group",
            "risk_tier":         "Risk Tier",
            "automation_prob":   "Automation Prob",
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
    st.subheader("Average Automation Risk by Occupation Group")

    grp_stats = (filtered.groupby("occupation_group")
                 .agg(avg_automation=("automation_prob", "mean"),
                      avg_wage=("median_wage_2024", "median"),
                      avg_growth=("emp_change_pct", "mean"),
                      count=("occupation", "count"))
                 .reset_index()
                 .sort_values("avg_automation", ascending=False))

    fig = px.bar(grp_stats, x="avg_automation", y="occupation_group",
                 orientation="h",
                 color="avg_automation",
                 color_continuous_scale=["#2ecc71", "#f39c12", "#e74c3c"],
                 hover_data={"avg_wage": ":$,.0f",
                             "avg_growth": ":.1f",
                             "count": True},
                 labels={"avg_automation":    "Avg Automation Probability",
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
        "avg_automation":   "Avg Automation",
        "avg_wage":         "Median Wage ($)",
        "avg_growth":       "Avg Growth %",
        "count":            "# Occupations",
    }).style.format({
        "Avg Automation": "{:.0%}",
        "Median Wage ($)": "${:,.0f}",
        "Avg Growth %": "{:.1f}%",
    }).background_gradient(subset=["Avg Automation"], cmap="RdYlGn_r")
    st.dataframe(grp_stats_display, use_container_width=True)

# ────────────────────────────────────────────────────────────────────────────
# TAB 4 — CLUSTERS
# ────────────────────────────────────────────────────────────────────────────
with tab4:
    st.subheader("K-Means Cluster Analysis")
    st.caption("4 clusters fitted on automation probability, adaptive capacity, wage, and education. "
               "Visualized using PCA (2 components). Sidebar filters do NOT apply here.")

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

    # Scatter with trend
    fig = px.scatter(
        filtered.dropna(subset=["emp_change_pct"]),
        x="automation_prob", y="emp_change_pct",
        trendline="ols",
        color="risk_tier", color_discrete_map=PALETTE,
        hover_name="occupation",
        labels={"automation_prob": "Automation Probability",
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

    st.info("💡 **For the interactive version:** Use the Job Explorer tab to hover "
            "over any occupation and see its full profile. Use the Clusters tab to "
            "explore which occupations fall into each group.", icon="💡")
