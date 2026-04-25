"""
dashboard/app.py
Interactive Streamlit dashboard — The Automation Paradox
Run with: streamlit run dashboard/app.py

Tabs:
  1. TL;DR        — four headline findings, no charts
  2. The Story    — three-act narrative with charts
  3. At Risk      — top occupations, clusters, wage divide
  4. Then vs. Now — how the risk map has shifted (2013 → 2025)
  5. Explore      — full interactive scatter + table with inline filters
"""

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="The Automation Paradox",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }
    h1 { font-size: 2rem !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 8px 20px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    df       = pd.read_csv("data/processed/cleaned_main.csv")
    cl       = pd.read_csv("data/processed/clustered.csv")
    cl_genai = pd.read_csv("data/processed/clustered_genai.csv")
    return df, cl, cl_genai


df, clustered, clustered_genai = load_data()

# ── Derived stats — computed once, never hardcoded ─────────────────────────────
_n_total   = len(df)
_n_high    = int((df["risk_tier"] == "High").sum())
_n_vuln    = int(df["vulnerable"].sum())
_pct_vuln  = df["vulnerable"].mean()
_wage_high = int(df[df["risk_tier"] == "High"]["median_wage_2024"].median())
_wage_low  = int(df[df["risk_tier"] == "Low"]["median_wage_2024"].median())
_wage_vuln = int(df[df["vulnerable"] == True]["median_wage_2024"].median())
_wage_safe = int(df[df["vulnerable"] == False]["median_wage_2024"].median())

_thenow = df.dropna(subset=["genai_exposure_2025"]).copy()
_thenow["risk_delta"] = _thenow["genai_exposure_2025"] - _thenow["automation_prob"]
_genai_max  = _thenow["genai_exposure_2025"].max()

_comp_trad  = df[df["occupation_group"] == "Computer & Math"]["automation_prob"].mean()
_comp_genai = df[df["occupation_group"] == "Computer & Math"]["genai_exposure_2025"].mean()

_cl = clustered.dropna(subset=["cluster_label"])
_cl_total = len(_cl)

PALETTE = {"Low": "#2ecc71", "Medium": "#f39c12", "High": "#e74c3c"}
CLUSTER_COLORS = {
    "High Risk / Low Resilience": "#e74c3c",
    "Low Risk / High Skill":      "#2ecc71",
    "Low Risk / Stable":          "#3498db",
}
GENAI_CLUSTER_COLORS = {
    "High Exposure / Low Resilience": "#e74c3c",
    "High Exposure / Adaptable":      "#e67e22",
    "Low Exposure / Stable":          "#3498db",
    "Low Exposure / High Skill":      "#2ecc71",
}

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🤖 The Automation Paradox")
st.markdown(
    "**MIS502 Final Project** — Who really gets hurt when AI takes over? "
    "| BLS 2024–2034 × Frey & Osborne (2013) × ILO GenAI Index (2025)"
)
st.divider()

tab_tldr, tab_story, tab_atrisk, tab_thenow, tab_explore = st.tabs([
    "📋 TL;DR",
    "📖 The Story",
    "⚠️ At Risk",
    "⚡ Then vs. Now",
    "🔎 Explore",
])


# ────────────────────────────────────────────────────────────────────────────
# TAB 1 — TL;DR
# ────────────────────────────────────────────────────────────────────────────
with tab_tldr:
    st.subheader("Four things to know.")
    st.caption("The full analysis is in the tabs above — this is the 30-second version.")
    st.markdown("<br>", unsafe_allow_html=True)

    _cards = [
        {
            "number":  f"{_n_high} of {_n_total}",
            "label":   "jobs carry high automation risk",
            "context": "But most still show positive projected employment growth through 2034. "
                       "Automation exposure doesn't determine outcomes on its own.",
            "color":   "#e74c3c",
        },
        {
            "number":  f"{_pct_vuln:.0%} of jobs",
            "label":   "are in the vulnerable zone",
            "context": f"{_n_vuln} occupations combine high automation risk with wages and education "
                       "too low to support adaptation. For them, displacement is already happening.",
            "color":   "#e67e22",
        },
        {
            "number":  f"${_wage_high:,} vs ${_wage_low:,}",
            "label":   "median wage — high vs. low risk",
            "context": "The workers most threatened by AI earn the least — and have the fewest "
                       "resources to retrain, relocate, or wait out a job search.",
            "color":   "#f39c12",
        },
        {
            "number":  f"{_comp_trad:.0%} → {_comp_genai:.0%}",
            "label":   "Computer & Math risk, 2013 → 2025",
            "context": "The risk map has fundamentally shifted. GenAI targets knowledge work, "
                       "not physical labor. What was safe in 2013 may not be safe now.",
            "color":   "#3498db",
        },
    ]

    cols = st.columns(4)
    for col, card in zip(cols, _cards):
        col.markdown(f"""
<div style="border-left:4px solid {card['color']}; padding:18px 20px;
            background:#1a1a2e; border-radius:0 10px 10px 0; min-height:195px;">
    <div style="font-size:1.55rem; font-weight:800; color:{card['color']}; line-height:1.2;">
        {card['number']}
    </div>
    <div style="font-size:0.8rem; color:#a0aec0; margin:5px 0 10px 0; font-weight:600;
                text-transform:uppercase; letter-spacing:0.04em;">
        {card['label']}
    </div>
    <div style="font-size:0.82rem; color:#718096; line-height:1.55;">
        {card['context']}
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.info(
        "**Start with The Story** for the full argument, or jump to **At Risk** to see "
        "which specific occupations are most exposed. Use **Explore** to search and filter.",
        icon="👆",
    )


# ────────────────────────────────────────────────────────────────────────────
# TAB 2 — THE STORY
# ────────────────────────────────────────────────────────────────────────────
with tab_story:

    # ── Act 1 — The Paradox ───────────────────────────────────────────────────
    st.subheader("Act 1 — The Paradox")
    st.markdown(
        "Automation risk and job loss are correlated (r = −0.41) — but weakly. "
        "A regression model using automation risk, adaptive capacity, and sector controls "
        "explains only **16.6% of variance** in employment outcomes. "
        "Most high-risk occupations still show positive projected growth through 2034."
    )

    fig_scatter = px.scatter(
        df.dropna(subset=["emp_change_pct"]),
        x="automation_prob", y="emp_change_pct",
        trendline="ols",
        color="risk_tier", color_discrete_map=PALETTE,
        hover_name="occupation",
        hover_data={"median_wage_2024": ":$,.0f", "occupation_group": True,
                    "automation_prob": ":.0%", "emp_change_pct": ":.1f",
                    "risk_tier": False},
        labels={"automation_prob": "Automation Probability (Frey & Osborne 2013)",
                "emp_change_pct":  "Projected Employment Change 2024–34 (%)",
                "risk_tier":       "Risk Tier"},
        template="plotly_white", height=420, opacity=0.45,
    )
    fig_scatter.add_vline(x=0.5, line_dash="dash", line_color="gray",
                          annotation_text="50% threshold", annotation_position="top right")
    fig_scatter.add_hline(y=0, line_dash="dash", line_color="gray",
                          annotation_text="No net change", annotation_position="right")
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.divider()

    # ── Act 2 — The Economic Divide ───────────────────────────────────────────
    st.subheader("Act 2 — The Economic Divide")
    st.markdown(
        f"High-risk workers earn a median of **${_wage_high:,}** annually — "
        f"compared to **${_wage_low:,}** for low-risk workers. "
        f"The **{_pct_vuln:.0%}** of occupations combining high automation risk "
        "with low wages and education have no economic buffer when displacement hits."
    )

    col_wage, col_box = st.columns(2)

    with col_wage:
        wage_df = (df.groupby("risk_tier")["median_wage_2024"]
                   .median().reindex(["Low", "Medium", "High"]).reset_index())
        wage_df.columns = ["Risk Tier", "Median Wage"]
        fig_wage = px.bar(
            wage_df, x="Risk Tier", y="Median Wage",
            color="Risk Tier", color_discrete_map=PALETTE,
            template="plotly_white", text_auto="$,.0f",
        )
        fig_wage.update_traces(textposition="outside")
        fig_wage.update_yaxes(tickprefix="$", tickformat=",")
        fig_wage.update_layout(showlegend=False, height=340,
                                title="Median Wage by Automation Risk Tier")
        st.plotly_chart(fig_wage, use_container_width=True)

    with col_box:
        vul_df = df.copy()
        vul_df["Vulnerability"] = vul_df["vulnerable"].map(
            {True: "Vulnerable", False: "Not Vulnerable"}
        )
        fig_box = px.box(
            vul_df, x="Vulnerability", y="median_wage_2024",
            color="Vulnerability",
            color_discrete_map={"Vulnerable": "#e74c3c", "Not Vulnerable": "#2ecc71"},
            template="plotly_white",
            labels={"median_wage_2024": "Median Annual Wage ($)"},
        )
        fig_box.update_yaxes(tickprefix="$", tickformat=",")
        fig_box.update_layout(showlegend=False, height=340,
                               title="Wage Distribution: Vulnerable vs. Not Vulnerable")
        st.plotly_chart(fig_box, use_container_width=True)

    st.divider()

    # ── Act 3 — The GenAI Flip ────────────────────────────────────────────────
    st.subheader("Act 3 — The Risk Map Has Flipped")
    st.markdown(
        "Frey & Osborne (2013) predicted physical and routine jobs were most at risk. "
        "The ILO's 2025 GenAI Exposure Index tells a different story: GenAI targets "
        "**language, reasoning, and information synthesis** — not physical manipulation. "
        f"Computer & Math went from **{_comp_trad:.0%}** traditional risk to "
        f"**{_comp_genai:.0%}** GenAI exposure. Production went the other way."
    )
    st.info(
        "See the **⚡ Then vs. Now** tab for the full sector-by-sector comparison "
        "and individual occupation breakdowns.",
        icon="→",
    )


# ────────────────────────────────────────────────────────────────────────────
# TAB 3 — AT RISK
# ────────────────────────────────────────────────────────────────────────────
with tab_atrisk:
    st.subheader("Which occupations are most exposed?")
    st.caption(
        "High automation risk (≥70%) combined with the worst projected employment outlook. "
        "BLS projects active job losses in all of these through 2034."
    )

    at_risk = (
        df[df["emp_change_pct"].notna() & (df["automation_prob"] >= 0.7)]
        .sort_values("emp_change_pct")
        .head(15)
    )
    fig_atrisk = px.bar(
        at_risk, x="emp_change_pct", y="occupation", orientation="h",
        color="automation_prob", color_continuous_scale="Reds",
        hover_data={"median_wage_2024": ":$,.0f", "automation_prob": ":.0%"},
        labels={"emp_change_pct": "Projected Employment Change (%)",
                "occupation":     "",
                "automation_prob":"Automation Risk"},
        template="plotly_white", height=460,
    )
    fig_atrisk.update_layout(yaxis={"categoryorder": "total ascending"},
                              coloraxis_colorbar_title="Automation Risk")
    fig_atrisk.add_vline(x=0, line_dash="dash", line_color="black", line_width=0.8)
    st.plotly_chart(fig_atrisk, use_container_width=True)

    st.divider()

    col_cl, col_cards = st.columns([3, 2])

    with col_cl:
        st.subheader("Three Paths Forward")
        st.caption("K-Means clustering (k=3) on automation risk, wage, and education level.")
        cl_data = _cl.dropna(subset=["pca_1", "pca_2"])
        fig_cl = px.scatter(
            cl_data, x="pca_1", y="pca_2",
            color="cluster_label", color_discrete_map=CLUSTER_COLORS,
            hover_name="occupation",
            hover_data={"automation_prob":         ":.0%",
                        "adaptive_capacity_score":  ":.3f",
                        "emp_change_pct":            ":.1f",
                        "median_wage_2024":          ":$,.0f",
                        "pca_1": False, "pca_2": False},
            labels={"pca_1": "PC1", "pca_2": "PC2", "cluster_label": "Cluster"},
            template="plotly_white", height=380, opacity=0.65,
        )
        fig_cl.update_layout(legend=dict(
            orientation="h", yanchor="bottom", y=-0.3, xanchor="left", x=0))
        st.plotly_chart(fig_cl, use_container_width=True)

    with col_cards:
        st.subheader("Cluster Outcomes")
        profile = (
            _cl.groupby("cluster_label")
            .agg(count=("occupation",     "count"),
                 risk=("automation_prob",  "mean"),
                 growth=("emp_change_pct", "mean"),
                 wage=("median_wage_2024", "median"))
            .reset_index()
            .sort_values("risk", ascending=False)
        )
        for _, row in profile.iterrows():
            color = CLUSTER_COLORS.get(row["cluster_label"], "#888")
            pct   = row["count"] / _cl_total * 100
            st.markdown(f"""
<div style="border-left:4px solid {color}; padding:12px 16px;
            margin-bottom:10px; background:#1a1a2e; border-radius:0 8px 8px 0;">
<b style="color:{color}">{row['cluster_label']}</b><br>
<small>
{int(row['count'])} occupations ({pct:.0f}%)<br>
Avg automation: {row['risk']:.0%} &nbsp;|&nbsp; Avg growth: {row['growth']:+.1f}%<br>
Median wage: ${row['wage']:,.0f}
</small>
</div>
""", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
# TAB 4 — THEN VS. NOW
# ────────────────────────────────────────────────────────────────────────────
with tab_thenow:
    st.subheader("How AI Risk Has Shifted: 2013 → 2025")
    st.markdown(
        "Traditional automation models (Frey & Osborne, 2013) predicted that **physical "
        "and routine manual jobs** were most at risk. A decade later, the ILO's 2025 "
        "GenAI Exposure Index tells a different story: **knowledge workers, writers, "
        "analysts, and tech roles** now face the highest exposure. The risk map flipped."
    )
    st.caption(
        "Sources: Frey & Osborne (2013) · Gmyrek et al. (2025) ILO Working Paper 140 · "
        "BLS ISCO-08 × SOC crosswalk. 6 occupations with no ISCO-08 match excluded."
    )
    st.divider()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Occupations with GenAI score",  f"{len(_thenow):,}")
    k2.metric("Avg Traditional Risk (2013)",   f"{_thenow['automation_prob'].mean():.0%}")
    k3.metric("Avg GenAI Exposure (2025)",      f"{_thenow['genai_exposure_2025'].mean():.0%}")
    k4.metric("Avg Risk Delta",                 f"{_thenow['risk_delta'].mean():+.2f}")

    st.divider()

    # Sector-level shift
    st.subheader("Sector-Level Shift")
    st.caption(
        "Sorted by GenAI exposure. Lines pointing right = newly exposed by GenAI. "
        "Lines pointing left = less threatened by GenAI than by traditional automation."
    )
    sector = (
        _thenow.groupby("occupation_group")[["automation_prob", "genai_exposure_2025"]]
        .mean().reset_index()
        .sort_values("genai_exposure_2025", ascending=False)
    )
    sector_long = sector.melt(
        id_vars="occupation_group",
        value_vars=["automation_prob", "genai_exposure_2025"],
        var_name="Era", value_name="Score",
    )
    sector_long["Era"] = sector_long["Era"].map({
        "automation_prob":     "2013 — Traditional Automation (F&O)",
        "genai_exposure_2025": "2025 — GenAI Exposure (ILO)",
    })
    fig_sector = px.bar(
        sector_long, x="Score", y="occupation_group",
        color="Era", orientation="h", barmode="group",
        color_discrete_map={
            "2013 — Traditional Automation (F&O)": "#3498db",
            "2025 — GenAI Exposure (ILO)":         "#e74c3c",
        },
        labels={"Score": "Average Score", "occupation_group": ""},
        template="plotly_white", height=580,
    )
    fig_sector.add_vline(x=0.5, line_dash="dash", line_color="gray", opacity=0.5)
    fig_sector.update_layout(
        yaxis={"categoryorder": "total ascending"},
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
    )
    st.plotly_chart(fig_sector, use_container_width=True)

    st.divider()

    # Occupation-level scatter
    st.subheader("Occupation-Level Shift")
    st.caption(
        "Each dot is one occupation. Above the diagonal = more exposed under GenAI than "
        "traditional models predicted. Below = physical/manual jobs safe from GenAI."
    )
    fig_oc = px.scatter(
        _thenow, x="automation_prob", y="genai_exposure_2025",
        color="occupation_group",
        hover_name="occupation",
        hover_data={"automation_prob":     ":.0%",
                    "genai_exposure_2025":  ":.0%",
                    "risk_delta":           ":.2f",
                    "occupation_group":     False},
        labels={"automation_prob":     "Traditional Automation Risk — F&O (2013)",
                "genai_exposure_2025": "GenAI Exposure — ILO (2025)",
                "occupation_group":    "Sector"},
        template="plotly_white", height=500, opacity=0.65,
    )
    fig_oc.add_shape(
        type="line", x0=0, y0=0, x1=_genai_max, y1=_genai_max,
        line=dict(color="gray", dash="dash", width=1),
    )
    fig_oc.add_annotation(
        x=_genai_max * 0.83, y=_genai_max * 0.91, text="Same risk then & now",
        showarrow=False, font=dict(color="gray", size=11), textangle=-38,
    )
    fig_oc.update_layout(legend_title="Sector")
    st.plotly_chart(fig_oc, use_container_width=True)

    st.divider()

    # Biggest movers
    st.subheader("The Biggest Movers")
    col_gain, col_lose = st.columns(2)

    with col_gain:
        st.markdown("#### Newly Exposed by GenAI")
        st.caption("Low traditional risk, high GenAI exposure")
        gainers = (
            _thenow.nlargest(15, "risk_delta")
            [["occupation", "occupation_group", "automation_prob",
              "genai_exposure_2025", "risk_delta"]]
            .sort_values("risk_delta")
        )
        fig_gain = px.bar(
            gainers, x="risk_delta", y="occupation", orientation="h",
            color="risk_delta",
            color_continuous_scale=[[0, "#f9c6c6"], [1, "#e74c3c"]],
            hover_data={"automation_prob": ":.0%", "genai_exposure_2025": ":.0%",
                        "occupation_group": True},
            labels={"risk_delta": "Risk Delta", "occupation": ""},
            template="plotly_white", height=460,
        )
        fig_gain.update_layout(coloraxis_showscale=False,
                                yaxis={"categoryorder": "total ascending"})
        fig_gain.add_vline(x=0, line_color="black", line_width=0.8)
        st.plotly_chart(fig_gain, use_container_width=True)

    with col_lose:
        st.markdown("#### De-Risked by GenAI Shift")
        st.caption("High traditional risk, low GenAI exposure — physical/manual jobs")
        losers = (
            _thenow.nsmallest(15, "risk_delta")
            [["occupation", "occupation_group", "automation_prob",
              "genai_exposure_2025", "risk_delta"]]
            .sort_values("risk_delta", ascending=False)
        )
        fig_lose = px.bar(
            losers, x="risk_delta", y="occupation", orientation="h",
            color="risk_delta",
            color_continuous_scale=[[0, "#2980b9"], [1, "#d6eaf8"]],
            hover_data={"automation_prob": ":.0%", "genai_exposure_2025": ":.0%",
                        "occupation_group": True},
            labels={"risk_delta": "Risk Delta", "occupation": ""},
            template="plotly_white", height=460,
        )
        fig_lose.update_layout(coloraxis_showscale=False,
                                yaxis={"categoryorder": "total descending"})
        fig_lose.add_vline(x=0, line_color="black", line_width=0.8)
        st.plotly_chart(fig_lose, use_container_width=True)

    st.divider()

    st.subheader("Full Then vs. Now Table")
    thenow_display = (
        _thenow[["occupation", "occupation_group", "automation_prob",
                 "genai_exposure_2025", "risk_delta"]]
        .sort_values("risk_delta", ascending=False)
        .rename(columns={"occupation":          "Occupation",
                          "occupation_group":    "Sector",
                          "automation_prob":     "Traditional Risk (2013)",
                          "genai_exposure_2025": "GenAI Exposure (2025)",
                          "risk_delta":          "Δ Risk"})
    )
    st.dataframe(
        thenow_display.style
        .format({"Traditional Risk (2013)": "{:.0%}",
                 "GenAI Exposure (2025)":   "{:.0%}",
                 "Δ Risk":                  "{:+.2f}"})
        .background_gradient(subset=["Δ Risk"], cmap="RdBu_r", vmin=-0.9, vmax=0.6),
        use_container_width=True, height=380,
    )


# ────────────────────────────────────────────────────────────────────────────
# TAB 5 — EXPLORE
# ────────────────────────────────────────────────────────────────────────────
with tab_explore:
    st.subheader("Explore all 606 occupations")

    with st.expander("🔍 Filters", expanded=False):
        fc1, fc2 = st.columns(2)
        with fc1:
            risk_view = st.radio(
                "Risk Score",
                ["Traditional (F&O 2013)", "GenAI (ILO 2025)"],
                horizontal=True,
            )
            use_genai  = risk_view == "GenAI (ILO 2025)"
            risk_col   = "genai_exposure_2025" if use_genai else "automation_prob"
            risk_label = "GenAI Exposure — ILO (2025)" if use_genai else "Automation Risk — F&O (2013)"
            risk_short = "GenAI Exposure" if use_genai else "Automation Risk"

            if use_genai:
                st.caption("⚠️ GenAI tiers use 33rd/67th percentile cutpoints — ILO scores top out at 0.70.")

            risk_filter = st.multiselect(
                "Risk Tier", ["Low", "Medium", "High"], default=["Low", "Medium", "High"]
            )
            grp_options = sorted(df["occupation_group"].dropna().unique())
            grp_filter  = st.multiselect("Occupation Group", grp_options, default=grp_options)

        with fc2:
            wage_min    = int(df["median_wage_2024"].min())
            wage_max    = int(df["median_wage_2024"].max())
            wage_filter = st.slider("Median Annual Wage ($)", wage_min, wage_max,
                                    (wage_min, wage_max), step=1000, format="$%d")
            auto_filter = st.slider(f"{risk_short} Range", 0.0, 1.0, (0.0, 1.0), step=0.05)

    # Build filtered view
    _genai_p33 = df["genai_exposure_2025"].quantile(0.33)
    _genai_p67 = df["genai_exposure_2025"].quantile(0.67)

    df_view = df.copy()
    if use_genai:
        df_view = df_view.dropna(subset=["genai_exposure_2025"])
        df_view["_risk_tier"] = pd.cut(
            df_view["genai_exposure_2025"],
            bins=[-0.001, _genai_p33, _genai_p67,
                  df["genai_exposure_2025"].max() + 0.001],
            labels=["Low", "Medium", "High"],
        ).astype(str)
    else:
        df_view["_risk_tier"] = df_view["risk_tier"]

    filtered = df_view[
        df_view["_risk_tier"].isin(risk_filter) &
        df_view["occupation_group"].isin(grp_filter) &
        df_view["median_wage_2024"].between(wage_filter[0], wage_filter[1]) &
        df_view[risk_col].between(auto_filter[0], auto_filter[1])
    ]

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Occupations",       f"{len(filtered):,}")
    k2.metric("High-Risk",         f"{(filtered['_risk_tier']=='High').sum():,}",
              delta=f"{(filtered['_risk_tier']=='High').mean():.0%}")
    k3.metric(f"Avg {risk_short}", f"{filtered[risk_col].mean():.0%}")
    k4.metric("Vulnerable",        f"{filtered['vulnerable'].sum():,}")
    k5.metric("Avg Growth",        f"{filtered['emp_change_pct'].mean():.1f}%")

    st.divider()

    st.subheader(f"{risk_label} vs. Projected Employment Change")
    fig_exp = px.scatter(
        filtered.dropna(subset=["emp_change_pct", "annual_openings"]),
        x=risk_col, y="emp_change_pct",
        size="annual_openings", size_max=45,
        color="_risk_tier", color_discrete_map=PALETTE,
        hover_name="occupation",
        hover_data={"median_wage_2024":   ":$,.0f",
                    "education_required":  True,
                    "occupation_group":    True,
                    "annual_openings":     ":,.0f",
                    risk_col:              ":.0%",
                    "_risk_tier":          False},
        labels={risk_col:        risk_label,
                "emp_change_pct": "Projected Employment Change 2024–34 (%)",
                "_risk_tier":     "Risk Tier"},
        template="plotly_white", height=520,
    )
    fig_exp.add_vline(x=0.5, line_dash="dash", line_color="gray",
                      annotation_text="50% threshold", annotation_position="top right")
    fig_exp.add_hline(y=0, line_dash="dash", line_color="gray",
                      annotation_text="No net change", annotation_position="right")
    fig_exp.update_layout(legend_title="Risk Tier")
    st.plotly_chart(fig_exp, use_container_width=True)

    st.divider()

    st.subheader("By Sector")
    grp_stats = (
        filtered.groupby("occupation_group")
        .agg(avg_risk=(risk_col,          "mean"),
             avg_wage=("median_wage_2024", "median"),
             avg_growth=("emp_change_pct", "mean"),
             count=("occupation",          "count"))
        .reset_index()
        .sort_values("avg_risk", ascending=False)
    )
    fig_sec = px.bar(
        grp_stats, x="avg_risk", y="occupation_group", orientation="h",
        color="avg_risk",
        color_continuous_scale=["#2ecc71", "#f39c12", "#e74c3c"],
        hover_data={"avg_wage": ":$,.0f", "avg_growth": ":.1f", "count": True},
        labels={"avg_risk": f"Avg {risk_short}", "occupation_group": ""},
        template="plotly_white", height=500,
    )
    fig_sec.add_vline(x=0.5, line_dash="dash", line_color="gray")
    fig_sec.update_layout(yaxis={"categoryorder": "total ascending"},
                           coloraxis_showscale=False)
    st.plotly_chart(fig_sec, use_container_width=True)

    st.divider()

    st.subheader("Full Data Table")
    display_cols = ["occupation", "occupation_group", "_risk_tier", risk_col,
                    "emp_change_pct", "median_wage_2024", "education_required", "vulnerable"]
    st.dataframe(
        filtered[display_cols]
        .sort_values(risk_col, ascending=False)
        .rename(columns={"occupation":        "Occupation",
                          "occupation_group":  "Group",
                          "_risk_tier":        "Risk Tier",
                          risk_col:            risk_short,
                          "emp_change_pct":    "Projected Change %",
                          "median_wage_2024":  "Median Wage $",
                          "education_required":"Education",
                          "vulnerable":        "Vulnerable"}),
        use_container_width=True, height=400,
    )
