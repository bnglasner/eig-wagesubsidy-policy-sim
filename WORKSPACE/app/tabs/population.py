"""
Tab 2: Population-level impacts.

Loads five pre-computed parquet files produced by the data pipeline and renders:
  - Four headline metric tiles
  - State choropleth map (workers or gross cost, user-selectable)
  - Wage bracket distribution bar chart
  - Program interaction table
  - Family type breakdown chart

All data files live in:
  WORKSPACE/output/data/intermediate_results/population/
"""
from __future__ import annotations

from pathlib import Path

import streamlit as st

# â"€â"€ Paths â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€
_HERE       = Path(__file__).resolve()
# population.py lives at WORKSPACE/app/tabs/, so repo root is parents[3].
_PROJECT    = _HERE.parents[3]
_POP_DIR    = (
    _PROJECT
    / "WORKSPACE" / "output" / "data" / "intermediate_results" / "population"
)

_FILES = {
    "summary":              _POP_DIR / "summary.parquet",
    "by_state":             _POP_DIR / "by_state.parquet",
    "by_wage_bracket":      _POP_DIR / "by_wage_bracket.parquet",
    "by_family_type":       _POP_DIR / "by_family_type.parquet",
    "program_interactions": _POP_DIR / "program_interactions.parquet",
}

# Demographic breakdown files (optional — present only if pipeline ran with demographic columns)
_DEMO_FILES = {
    "by_sex":            _POP_DIR / "by_sex.parquet",
    "by_race_ethnicity": _POP_DIR / "by_race_ethnicity.parquet",
    "by_education":      _POP_DIR / "by_education.parquet",
    "by_age_bin":        _POP_DIR / "by_age_bin.parquet",
}


def _all_files_present() -> bool:
    return all(p.exists() for p in _FILES.values())


# â"€â"€ EIG style â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€
import sys
_APP = _HERE.parents[1]
if str(_APP) not in sys.path:
    sys.path.insert(0, str(_APP))

from utils.eig_style import eig_plotly_layout, BRAND_COLORS
from utils.household_sim import COMPONENTS


# â"€â"€ Chart builders â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€

def _make_choropleth(by_state: "pd.DataFrame", metric: str) -> "go.Figure":
    import plotly.graph_objects as go

    if metric == "Workers (thousands)":
        col, label, fmt = "n_workers_k", "Workers (thousands)", ",.0f"
        color_scale = [
            [0.0, "#FEECD6"],  # eig_cream_100
            [1.0, "#19644D"],  # eig_green_700
        ]
    elif metric == "Gross cost ($M)":
        col, label, fmt = "gross_cost_mn", "Gross cost ($M)", ",.0f"
        color_scale = [
            [0.0, "#FEECD6"],
            [1.0, "#194F8B"],  # eig_blue_800
        ]
    else:
        col, label, fmt = "avg_annual_subsidy", "Avg. annual subsidy ($)", ",.0f"
        color_scale = [
            [0.0, "#FEECD6"],
            [1.0, "#E1AD28"],  # eig_gold_600
        ]

    fig = go.Figure(go.Choropleth(
        locations=by_state["state_code"],
        z=by_state[col],
        locationmode="USA-states",
        colorscale=color_scale,
        colorbar=dict(
            title=dict(text=label, font=dict(size=11)),
            tickformat=fmt,
            thickness=14,
            len=0.7,
        ),
        marker_line_color="white",
        marker_line_width=0.5,
        hovertemplate=(
            "<b>%{location}</b><br>"
            f"{label}: %{{z:{fmt}}}<extra></extra>"
        ),
    ))

    fig.update_layout(**eig_plotly_layout(
        geo=dict(
            scope="usa",
            showlakes=False,
            bgcolor="white",
            landcolor="#F5F5F5",
        ),
        height=380,
        margin=dict(t=10, b=10, l=0, r=0),
    ))
    return fig


def _make_bracket_chart(by_wb: "pd.DataFrame") -> "go.Figure":
    import plotly.graph_objects as go

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=by_wb["wage_bracket"],
        y=by_wb["n_workers_k"],
        name="Workers (thousands)",
        marker_color=BRAND_COLORS["eig_green_700"],
        yaxis="y",
    ))
    fig.add_trace(go.Scatter(
        x=by_wb["wage_bracket"],
        y=by_wb["avg_annual_subsidy"],
        name="Avg. annual subsidy ($)",
        mode="lines+markers",
        line=dict(color=BRAND_COLORS["eig_gold_600"], width=2.5),
        marker=dict(size=8),
        yaxis="y2",
    ))
    fig.update_layout(**eig_plotly_layout(
        barmode="group",
        height=340,
        xaxis=dict(title="Employer-paid hourly wage", showgrid=False),
        yaxis=dict(
            title="Workers (thousands)",
            showgrid=True,
            gridcolor="#D9D9D9",
            tickformat=",.0f",
        ),
        yaxis2=dict(
            title="Avg. annual subsidy ($)",
            overlaying="y",
            side="right",
            showgrid=False,
            tickprefix="$",
            tickformat=",.0f",
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        margin=dict(t=60, b=40),
    ))
    return fig


def _make_demo_chart(df: pd.DataFrame, group_col: str, color: str) -> "go.Figure":
    import plotly.graph_objects as go

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["n_workers_k"],
        y=df[group_col],
        orientation="h",
        name="Workers (k)",
        marker_color=color,
        yaxis="y",
        xaxis="x",
        text=[f"{v:,.0f}k" for v in df["n_workers_k"]],
        textposition="outside",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Workers: %{x:,.0f}k (%{customdata:.1f}%)<extra></extra>"
        ),
        customdata=df["pct_workers"],
    ))
    fig.update_layout(**eig_plotly_layout(
        height=max(200, len(df) * 40),
        xaxis=dict(title="Workers (thousands)", tickformat=",.0f", showgrid=True, gridcolor="#D9D9D9"),
        yaxis=dict(showgrid=False, automargin=True),
        margin=dict(t=20, b=40, r=130),
        showlegend=False,
    ))
    return fig


def _make_family_chart(by_ft: "pd.DataFrame") -> "go.Figure":
    import plotly.graph_objects as go

    fig = go.Figure(go.Bar(
        x=by_ft["avg_annual_subsidy"],
        y=by_ft["family_type"],
        orientation="h",
        marker_color=[
            BRAND_COLORS["eig_green_700"],
            BRAND_COLORS["eig_cyan_700"],
            BRAND_COLORS["eig_blue_800"],
            BRAND_COLORS["eig_gold_600"],
        ][:len(by_ft)],
        text=[f"${v:,.0f}" for v in by_ft["avg_annual_subsidy"]],
        textposition="outside",
        customdata=by_ft["pct_workers"],
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Avg. annual subsidy: $%{x:,.0f}<br>"
            "Share of workers: %{customdata:.1f}%<extra></extra>"
        ),
    ))
    fig.update_layout(**eig_plotly_layout(
        height=240,
        xaxis=dict(title="Avg. annual subsidy ($)", tickprefix="$", tickformat=",.0f"),
        yaxis=dict(showgrid=False, automargin=True),
        margin=dict(t=10, b=40, r=120),
    ))
    return fig


def _render_program_table(prog: "pd.DataFrame") -> None:
    import pandas as pd

    # Exclude wage_subsidy row (shown in metrics) and net_income
    display = prog[~prog["key"].isin(["wage_subsidy", "net_income"])].copy()

    # Apply the same program selection used in the calculator tab (if set)
    active_keys = st.session_state.get("budget_active_keys")
    if active_keys is not None:
        display = display[display["key"].isin(active_keys)]
        if len(display) < len(prog) - 2:  # -2 for the always-excluded rows
            st.caption("Showing selected programs only - adjust the selection in the Individual Calculator tab.")

    # Format columns
    display["Avg. change / worker"] = display["avg_delta_per_worker"].apply(
        lambda v: f"${v:+,.0f}"
    )
    display["Total change"] = display["total_delta_mn"].apply(
        lambda v: f"${v:+,.0f}M"
    )
    display["% of gross cost"] = display["pct_of_gross_cost"].apply(
        lambda v: f"{v:+.1f}%"
    )
    display = display.rename(columns={"program": "Program"})
    display = display[["Program", "Avg. change / worker", "Total change", "% of gross cost"]]

    st.dataframe(
        display.style.apply(
            lambda col: [
                "color: #2E8B57" if "+" in str(v) and v != "+$0"
                else "color: #C0392B" if "-" in str(v)
                else ""
                for v in col
            ],
            subset=["Avg. change / worker", "Total change", "% of gross cost"],
            axis=0,
        ),
        use_container_width=True,
        hide_index=True,
    )


# â"€â"€ Main render â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€

def render() -> None:
    import plotly.graph_objects as go
    import pandas as pd

    st.header("Population-Level Impacts")
    st.markdown(
        "Aggregate effects of the EIG 80-80 Rule wage subsidy, estimated using "
        "[PolicyEngine-US](https://policyengine.org) microdata (Current Population Survey) "
        "and pre-computed income schedules. Wage subsidy amounts are computed analytically; "
        "safety net interactions are interpolated from household-level simulations."
    )

    if not _all_files_present():
        missing = [name for name, p in _FILES.items() if not p.exists()]
        st.warning(
            f"Population impact data has not been generated yet "
            f"(missing: {', '.join(missing)}). "
            "Run the data pipeline first:\n\n"
            "```powershell\n"
            "# Activate your virtualenv, then:\n"
            "cd C:\\path\\to\\eig-wagesubsidy-policy-sim\n"
            "python WORKSPACE/code/01_data_preparation/01a_data_ingest.py\n"
            "python WORKSPACE/code/02_descriptive_analysis/02a_descriptive_stats.py\n"
            "```"
        )
        with st.expander("What this tab will show once the pipeline runs"):
            st.markdown(
                "- **Headline metrics**: gross program cost, net cost (after safety net "
                "adjustments), number of eligible workers, average annual subsidy\n"
                "- **State map**: workers and cost by state\n"
                "- **Wage bracket chart**: distribution of workers and avg subsidy\n"
                "- **Program interaction table**: how EITC, SNAP, Medicaid, and taxes "
                "offset or amplify the gross subsidy cost\n"
                "- **Family type breakdown**: how impacts vary by household composition"
            )
        return

    # Load data
    summary = pd.read_parquet(_FILES["summary"]).iloc[0]
    by_state = pd.read_parquet(_FILES["by_state"])
    by_wb    = pd.read_parquet(_FILES["by_wage_bracket"])
    by_ft    = pd.read_parquet(_FILES["by_family_type"])
    prog     = pd.read_parquet(_FILES["program_interactions"])

    # â"€â"€ Headline metrics â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€
    st.subheader("Headline Estimates")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(
        "Gross annual cost",
        f"${summary['gross_cost_bn']:.1f}B",
        help="Total wage subsidy payments before accounting for changes in taxes or other benefit programs.",
    )
    m2.metric(
        "Net annual cost",
        f"${summary['net_cost_bn']:.1f}B",
        delta=f"{(summary['net_cost_bn'] - summary['gross_cost_bn']):.1f}B vs. gross",
        delta_color="inverse",
        help="Gross cost adjusted for reductions in other safety net programs and increases in tax revenue.",
    )
    m3.metric(
        "Eligible workers",
        f"{summary['n_workers_mn']:.1f}M",
        help="Workers earning $7.25-$16.80/hr who would receive the subsidy.",
    )
    m4.metric(
        "Avg. annual subsidy",
        f"${summary['avg_annual_subsidy']:,.0f}",
        help="Weighted average annual subsidy per eligible worker.",
    )

    st.caption(
        "**Methodology note:** Eligibility is identified from CPS ORG hourly wages (`hourly_wage_epi`) "
        "with a federal floor of $7.25 and a dynamic target wage (80% of weighted median paid-hourly wage). "
        "Workers age 65 or older are excluded as a proxy for Social Security recipient status (SS income "
        "is not directly observed in ORG microdata). Tax dependents — defined as children of the household "
        "head (`relate == 301`) under age 19 — are also excluded. "
        "Annual hours are `hours_epi x WKSTAT weeks` (fallback used only when hours are missing). "
        "Family type is derived from `MARST` and `NCHILD`, and safety net interactions are interpolated from "
        "pre-computed PolicyEngine-US 2026 household schedules."
    )


    labels_by_key = {key: label for key, label, _, _ in COMPONENTS}
    active_keys = st.session_state.get("budget_active_keys")
    if active_keys is None:
        selected_program_keys = [
            k for k in prog["key"].tolist() if k not in {"wage_subsidy", "net_income"}
        ]
    else:
        selected_program_keys = [
            k for k in active_keys if k not in {"employer_wages", "wage_subsidy", "net_income"}
        ]
    selected_program_labels = [labels_by_key[k] for k in selected_program_keys if k in labels_by_key]
    selected_programs_txt = ", ".join(sorted(selected_program_labels)) if selected_program_labels else "no additional programs selected"

    by_state_ranked = by_state.sort_values("n_workers_k", ascending=False)
    top3 = by_state_ranked.head(3)
    top3_states_txt = ", ".join(top3["state_code"].tolist())
    total_workers_k = by_state["n_workers_k"].sum()
    top3_share = (top3["n_workers_k"].sum() / total_workers_k) * 100.0 if total_workers_k > 0 else 0.0
    offset_bn = summary["gross_cost_bn"] - summary["net_cost_bn"]

    st.markdown(
        f"This population simulation applies the current policy settings to CPS ORG eligible workers and then maps "
        f"household-level tax and transfer interactions from pre-computed schedules. In this run, about "
        f"`{summary['n_workers_mn']:.2f} million` workers are eligible, the average annual subsidy is "
        f"`${summary['avg_annual_subsidy']:,.0f}`, gross program cost is `{summary['gross_cost_bn']:.2f}B`, "
        f"and net cost is `{summary['net_cost_bn']:.2f}B`."
    )
    st.markdown(
        f"Under the currently selected policy components (`{selected_programs_txt}`), interactions with taxes and "
        f"means-tested programs offset roughly `${offset_bn:,.2f}B` of gross subsidy spending. Eligibility is "
        f"geographically concentrated: the top three states by eligible workers are `{top3_states_txt}`, accounting "
        f"for about `{top3_share:.1f}%` of eligible workers in this run."
    )
    st.divider()

    # â"€â"€ Map + Wage bracket side by side â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€
    col_map, col_bracket = st.columns([3, 2])

    with col_map:
        st.subheader("Geographic Distribution")
        map_metric = st.selectbox(
            "Map color",
            ["Workers (thousands)", "Gross cost ($M)", "Avg. annual subsidy ($)"],
            label_visibility="collapsed",
        )
        fig_map = _make_choropleth(by_state, map_metric)
        st.plotly_chart(fig_map, use_container_width=True)

    with col_bracket:
        st.subheader("By Wage Bracket")
        fig_bracket = _make_bracket_chart(by_wb)
        st.plotly_chart(fig_bracket, use_container_width=True)

    st.divider()

    # â"€â"€ Program interactions + Family type â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€
    col_prog, col_ft = st.columns([3, 2])

    with col_prog:
        st.subheader("Program Interactions")
        st.markdown(
            "How other programs change for the average eligible worker under the subsidy. "
            "Negative values (red) indicate reductions in program benefits or increases "
            "in taxes - these offset the gross subsidy cost to the government."
        )
        _render_program_table(prog)

    with col_ft:
        st.subheader("By Family Type")
        fig_ft = _make_family_chart(by_ft)
        st.plotly_chart(fig_ft, use_container_width=True)

        # Small table with worker shares
        st.dataframe(
            by_ft[["family_type", "pct_workers", "n_workers_k"]]
            .rename(columns={
                "family_type": "Household type",
                "pct_workers": "Share (%)",
                "n_workers_k": "Workers (k)",
            })
            .style.format({"Share (%)": "{:.1f}%", "Workers (k)": "{:,.0f}"}),
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    # ── Demographic breakdowns ────────────────────────────────────────────────
    demo_available = all(p.exists() for p in _DEMO_FILES.values())
    if demo_available:
        import pandas as pd

        st.subheader("Eligible Workers by Demographic Group")
        st.markdown(
            "Distribution of eligible workers and average annual subsidy across "
            "sex, race/ethnicity, education, and age. Worker counts are weighted "
            "CPS ORG estimates."
        )

        by_sex   = pd.read_parquet(_DEMO_FILES["by_sex"])
        by_race  = pd.read_parquet(_DEMO_FILES["by_race_ethnicity"])
        by_educ  = pd.read_parquet(_DEMO_FILES["by_education"])
        by_age   = pd.read_parquet(_DEMO_FILES["by_age_bin"])

        col_sex, col_race = st.columns(2)

        with col_sex:
            st.markdown("**By Sex**")
            fig_sex = _make_demo_chart(by_sex, "sex_label", BRAND_COLORS["eig_blue_800"])
            st.plotly_chart(fig_sex, use_container_width=True)
            st.dataframe(
                by_sex[["sex_label", "pct_workers", "avg_annual_subsidy"]]
                .rename(columns={"sex_label": "Sex", "pct_workers": "Share (%)", "avg_annual_subsidy": "Avg. subsidy ($)"})
                .style.format({"Share (%)": "{:.1f}%", "Avg. subsidy ($)": "${:,.0f}"}),
                use_container_width=True, hide_index=True,
            )

        with col_race:
            st.markdown("**By Race / Ethnicity**")
            fig_race = _make_demo_chart(by_race, "race_ethnicity", BRAND_COLORS["eig_cyan_700"])
            st.plotly_chart(fig_race, use_container_width=True)
            st.dataframe(
                by_race[["race_ethnicity", "pct_workers", "avg_annual_subsidy"]]
                .rename(columns={"race_ethnicity": "Group", "pct_workers": "Share (%)", "avg_annual_subsidy": "Avg. subsidy ($)"})
                .style.format({"Share (%)": "{:.1f}%", "Avg. subsidy ($)": "${:,.0f}"}),
                use_container_width=True, hide_index=True,
            )

        col_educ, col_age = st.columns(2)

        with col_educ:
            st.markdown("**By Education**")
            fig_educ = _make_demo_chart(by_educ, "educ_group", BRAND_COLORS["eig_gold_600"])
            st.plotly_chart(fig_educ, use_container_width=True)
            st.dataframe(
                by_educ[["educ_group", "pct_workers", "avg_annual_subsidy"]]
                .rename(columns={"educ_group": "Education", "pct_workers": "Share (%)", "avg_annual_subsidy": "Avg. subsidy ($)"})
                .style.format({"Share (%)": "{:.1f}%", "Avg. subsidy ($)": "${:,.0f}"}),
                use_container_width=True, hide_index=True,
            )

        with col_age:
            st.markdown("**By Age**")
            fig_age = _make_demo_chart(by_age, "age_bin", BRAND_COLORS["eig_green_700"])
            st.plotly_chart(fig_age, use_container_width=True)
            st.dataframe(
                by_age[["age_bin", "pct_workers", "avg_annual_subsidy"]]
                .rename(columns={"age_bin": "Age group", "pct_workers": "Share (%)", "avg_annual_subsidy": "Avg. subsidy ($)"})
                .style.format({"Share (%)": "{:.1f}%", "Avg. subsidy ($)": "${:,.0f}"}),
                use_container_width=True, hide_index=True,
            )

        st.divider()

    # ── State detail table (collapsed) ───────────────────────────────────────
    with st.expander("State-by-state detail table"):
        st.dataframe(
            by_state.rename(columns={
                "state_code":        "State",
                "n_workers_k":       "Workers (k)",
                "gross_cost_mn":     "Gross cost ($M)",
                "net_cost_mn":       "Net cost ($M)",
                "avg_annual_subsidy":"Avg. subsidy ($)",
            }).style.format({
                "Workers (k)":       "{:,.0f}",
                "Gross cost ($M)":   "${:,.0f}",
                "Net cost ($M)":     "${:,.0f}",
                "Avg. subsidy ($)":  "${:,.0f}",
            }),
            use_container_width=True,
            hide_index=True,
        )

