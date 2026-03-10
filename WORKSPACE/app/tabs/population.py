"""
Tab 2: Population-level impacts.

Loads five pre-computed parquet files produced by the data pipeline and renders:
  - Four headline metric tiles
  - State choropleth map (workers or gross cost, user-selectable)
  - Wage bracket distribution bar chart
  - Program interaction table
  - Family type breakdown chart

Data files live in:
  WORKSPACE/output/data/intermediate_results/population/          (stylized)
  WORKSPACE/output/data/intermediate_results/matched_population/  (matched ASEC)
"""
from __future__ import annotations

from pathlib import Path

import streamlit as st

# â"€â"€ Paths â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€
_HERE = Path(__file__).resolve()
# population.py lives at WORKSPACE/app/tabs/, so repo root is parents[3].
_PROJECT = _HERE.parents[3]
_INTERMEDIATE_DIR = _PROJECT / "WORKSPACE" / "output" / "data" / "intermediate_results"
_POP_STYLISED_DIR = _INTERMEDIATE_DIR / "population"
_POP_MATCHED_DIR = _INTERMEDIATE_DIR / "matched_population"

_CORE_FILE_NAMES = [
    "summary",
    "by_state",
    "by_wage_bracket",
    "by_family_type",
    "program_interactions",
]
_DEMO_FILE_NAMES = [
    "by_sex",
    "by_race_ethnicity",
    "by_education",
    "by_age_bin",
]


def _build_file_map(base_dir: Path) -> dict[str, Path]:
    out = {name: base_dir / f"{name}.parquet" for name in _CORE_FILE_NAMES}
    out.update({name: base_dir / f"{name}.parquet" for name in _DEMO_FILE_NAMES})
    out["comparison"] = base_dir / "comparison.parquet"
    out["program_comparison"] = base_dir / "program_comparison.parquet"
    return out


def _core_files_present(file_map: dict[str, Path]) -> bool:
    return all(file_map[name].exists() for name in _CORE_FILE_NAMES)


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

    if metric == "Share receiving subsidy (%)":
        col, label, fmt = "pct_in_group", "Share receiving subsidy (%)", ".1f"
        color_scale = [
            [0.0, "#FEECD6"],  # eig_cream_100
            [1.0, "#39274F"],  # eig_purple_800
        ]
    elif metric == "Workers (thousands)":
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
        customdata=df["pct_of_recipients"],
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
        width='stretch',
        hide_index=True,
    )


# â"€â"€ Main render â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€

def render() -> None:
    import plotly.graph_objects as go
    import pandas as pd

    st.header("Population-Level Impacts")
    stylised_files = _build_file_map(_POP_STYLISED_DIR)
    matched_files = _build_file_map(_POP_MATCHED_DIR)
    stylised_ready = _core_files_present(stylised_files)
    matched_ready = _core_files_present(matched_files)

    if matched_ready and stylised_ready:
        method_label = st.radio(
            "Household interaction method",
            options=["Matched ASEC households", "Stylized households"],
            index=0,
            horizontal=True,
            help=(
                "Matched ASEC households use spouse income and child ages from matched ASEC records; "
                "stylized households use fixed archetypes."
            ),
        )
    elif matched_ready:
        method_label = "Matched ASEC households"
    elif stylised_ready:
        method_label = "Stylized households"
    else:
        method_label = None

    if method_label is None:
        missing = [name for name in _CORE_FILE_NAMES if not stylised_files[name].exists()]
        st.warning(
            f"Population impact data has not been generated yet "
            f"(missing stylized core files: {', '.join(missing)}). "
            "Run the data pipeline first:\n\n"
            "```powershell\n"
            "# Activate your virtualenv, then:\n"
            "cd C:\\path\\to\\eig-wagesubsidy-policy-sim\n"
            "python WORKSPACE/code/01_data_preparation/01a_data_ingest.py\n"
            "python WORKSPACE/code/02_descriptive_analysis/02a_descriptive_stats.py\n"
            "# Optional matched-household pipeline:\n"
            "python WORKSPACE/code/01_data_preparation/01e_match_org_to_asec.py\n"
            "python WORKSPACE/code/01_data_preparation/01f_precompute_matched_schedules.py\n"
            "python WORKSPACE/code/03_matched_analysis/03a_apply_matched_to_population.py\n"
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

    using_matched = method_label == "Matched ASEC households"
    active_files = matched_files if using_matched else stylised_files
    source_tag = "matched" if using_matched else "stylized"

    if using_matched:
        st.markdown(
            "Aggregate effects using CPS ORG eligibility and **matched ASEC household context** for "
            "PolicyEngine interactions (spouse income and child ages)."
        )
    else:
        st.markdown(
            "Aggregate effects using CPS ORG eligibility and **stylized household archetypes** for "
            "PolicyEngine interactions."
        )

    # Load data
    summary = pd.read_parquet(active_files["summary"]).iloc[0]
    by_state = pd.read_parquet(active_files["by_state"])
    by_wb = pd.read_parquet(active_files["by_wage_bracket"])
    by_ft = pd.read_parquet(active_files["by_family_type"])
    prog = pd.read_parquet(active_files["program_interactions"])

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

    if using_matched:
        st.caption(
            "**Methodology note (matched ASEC):** Eligibility and gross subsidy are identified from CPS ORG "
            "hourly wages and annual hours. Net-cost interactions are drawn from pre-computed PolicyEngine-US "
            "schedules keyed to matched ASEC household context (state, spouse income bucket, number of adults, "
            "and child age bands)."
        )
    else:
        st.caption(
            "**Methodology note (stylized):** Eligibility is identified from CPS ORG hourly wages (`hourly_wage_epi`) "
            "with a federal floor of $7.25 and a dynamic target wage (80% of weighted median paid-hourly wage). "
            "Workers age 65 or older are excluded as a proxy for Social Security recipient status (SS income "
            "is not directly observed in ORG microdata). Tax dependents — defined as children of the household "
            "head (`relate == 301`) under age 19 — are also excluded. Annual hours are `hours_epi x WKSTAT weeks` "
            "(fallback used only when hours are missing). Safety-net interactions are interpolated from "
            "pre-computed stylized PolicyEngine-US schedules."
        )

    if using_matched and active_files["comparison"].exists():
        comp = pd.read_parquet(active_files["comparison"])
        row_net = comp[comp["metric"] == "Net cost ($B)"]
        if not row_net.empty:
            delta_pct = float(row_net.iloc[0]["delta_pct"])
            st.info(
                f"Matched vs stylized check: net cost is {delta_pct:+.1f}% relative to stylized "
                f"(comparison source: `matched_population/comparison.parquet`)."
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
        f"This {source_tag} population simulation applies the current policy settings to CPS ORG eligible workers "
        f"and maps household-level tax and transfer interactions from pre-computed schedules. In this run, about "
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
    _gross_fmt = f"\\${summary['gross_cost_bn']:.0f}B"
    _net_fmt   = f"\\${summary['net_cost_bn']:.0f}B"
    st.markdown(
        f"**Scale in context.** "
        f"Under current parameters, the 80-80 Rule carries a gross cost of {_gross_fmt} "
        f"(net cost {_net_fmt} after tax recapture and safety-net offsets), "
        f"placing it in the same fiscal tier as the Earned Income Tax Credit "
        f"(EITC, roughly \\$70-75B per year serving about 23 million claimant households). "
        f"The two programs differ fundamentally in what they target: the EITC is assessed against "
        f"*household income*, phasing in and out based on total family earnings and strongly shaped "
        f"by household composition - married filers and families with children receive substantially "
        f"larger credits. The 80-80 Rule instead targets the *wage rate paid by the employer*, so "
        f"eligibility is a property of the job rather than the worker's household circumstances. "
        f"That distinction broadens coverage to low-wage single workers and secondary earners who "
        f"receive little or no EITC. "
        f"For broader context on the scale of public investment in workers, "
        f"[Bartik (2020)](https://research.upjohn.org/cgi/viewcontent.cgi?article=1034&context=up_policypapers) "
        f"estimates that governments already spend roughly \\$80 billion per year on job creation - "
        f"most of it in tax breaks for large businesses with limited evidence of effectiveness, "
        f"and concentrated away from the distressed communities where more than a third of Americans "
        f"live and where job-finding lags the national average most severely."
    )
    st.divider()

    # â"€â"€ Map + Wage bracket side by side â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€
    col_map, col_bracket = st.columns([3, 2])

    with col_map:
        st.subheader("Geographic Distribution")
        map_metric = st.selectbox(
            "Map color",
            ["Share receiving subsidy (%)", "Workers (thousands)", "Gross cost ($M)", "Avg. annual subsidy ($)"],
            label_visibility="collapsed",
        )
        fig_map = _make_choropleth(by_state, map_metric)
        st.plotly_chart(fig_map, width='stretch')

    with col_bracket:
        st.subheader("By Wage Bracket")
        fig_bracket = _make_bracket_chart(by_wb)
        st.plotly_chart(fig_bracket, width='stretch')

    st.divider()

    # â"€â"€ Program interactions + Family type â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€
    col_prog, col_ft = st.columns([3, 2])

    with col_prog:
        st.subheader("Program Interactions")
        st.markdown(
            "How other programs change for the average eligible worker under the subsidy. "
            "Values show the change in each program from baseline to subsidized earnings.\n\n"
            "- **Transfer programs** (SNAP, EITC, Medicaid, etc.): "
            "green = benefit increases; red = benefit reductions (fiscal savings).\n"
            "- **Tax rows** (Federal income tax, State income tax, Payroll taxes): "
            "red = *more* tax revenue collected on the higher earnings - "
            "a fiscal offset to the government, not a cost."
        )
        _render_program_table(prog)

    with col_ft:
        st.subheader("By Family Type")
        fig_ft = _make_family_chart(by_ft)
        st.plotly_chart(fig_ft, width='stretch')

        # Small table with worker shares
        st.dataframe(
            by_ft[["family_type", "pct_workers", "n_workers_k"]]
            .rename(columns={
                "family_type": "Household type",
                "pct_workers": "Share (%)",
                "n_workers_k": "Workers (k)",
            })
            .style.format({"Share (%)": "{:.1f}%", "Workers (k)": "{:,.0f}"}),
            width='stretch',
            hide_index=True,
        )

    if using_matched and active_files["program_comparison"].exists():
        with st.expander("Matched vs Stylized program deltas"):
            prog_comp = pd.read_parquet(active_files["program_comparison"])
            st.dataframe(
                prog_comp.rename(columns={
                    "program": "Program",
                    "stylised_delta_mn": "Stylized delta ($M)",
                    "matched_delta_mn": "Matched delta ($M)",
                    "diff_mn": "Difference ($M)",
                }).style.format({
                    "Stylized delta ($M)": "${:,.1f}",
                    "Matched delta ($M)": "${:,.1f}",
                    "Difference ($M)": "${:,.1f}",
                }),
                width='stretch',
                hide_index=True,
            )

    st.divider()

    # ── Demographic breakdowns ────────────────────────────────────────────────
    demo_available = all(active_files[name].exists() for name in _DEMO_FILE_NAMES)
    if demo_available:
        import pandas as pd

        st.subheader("Eligible Workers by Demographic Group")
        if using_matched:
            st.caption(
                "Matched-mode interpretation: worker counts come from ORG eligibility; "
                "net-income effects include ASEC-matched household context (spouse income and child ages)."
            )
        st.markdown(
            "Distribution of eligible workers and average annual subsidy across "
            "sex, race/ethnicity, education, and age. Worker counts are weighted "
            "CPS ORG estimates."
        )

        by_sex = pd.read_parquet(active_files["by_sex"])
        by_race = pd.read_parquet(active_files["by_race_ethnicity"])
        by_educ = pd.read_parquet(active_files["by_education"])
        by_age = pd.read_parquet(active_files["by_age_bin"])

        col_sex, col_race = st.columns(2)

        with col_sex:
            st.markdown("**By Sex**")
            fig_sex = _make_demo_chart(by_sex, "sex_label", BRAND_COLORS["eig_blue_800"])
            st.plotly_chart(fig_sex, width='stretch')
            st.dataframe(
                by_sex[["sex_label", "pct_of_recipients", "pct_in_group", "avg_annual_subsidy"]]
                .rename(columns={"sex_label": "Sex", "pct_of_recipients": "% of recipients",
                                 "pct_in_group": "% of group receiving", "avg_annual_subsidy": "Avg. subsidy ($)"})
                .style.format({"% of recipients": "{:.1f}%", "% of group receiving": "{:.1f}%", "Avg. subsidy ($)": "${:,.0f}"}),
                width='stretch', hide_index=True,
            )

        with col_race:
            st.markdown("**By Race / Ethnicity**")
            fig_race = _make_demo_chart(by_race, "race_ethnicity", BRAND_COLORS["eig_cyan_700"])
            st.plotly_chart(fig_race, width='stretch')
            st.dataframe(
                by_race[["race_ethnicity", "pct_of_recipients", "pct_in_group", "avg_annual_subsidy"]]
                .rename(columns={"race_ethnicity": "Group", "pct_of_recipients": "% of recipients",
                                 "pct_in_group": "% of group receiving", "avg_annual_subsidy": "Avg. subsidy ($)"})
                .style.format({"% of recipients": "{:.1f}%", "% of group receiving": "{:.1f}%", "Avg. subsidy ($)": "${:,.0f}"}),
                width='stretch', hide_index=True,
            )

        col_educ, col_age = st.columns(2)

        with col_educ:
            st.markdown("**By Education**")
            fig_educ = _make_demo_chart(by_educ, "educ_group", BRAND_COLORS["eig_gold_600"])
            st.plotly_chart(fig_educ, width='stretch')
            st.dataframe(
                by_educ[["educ_group", "pct_of_recipients", "pct_in_group", "avg_annual_subsidy"]]
                .rename(columns={"educ_group": "Education", "pct_of_recipients": "% of recipients",
                                 "pct_in_group": "% of group receiving", "avg_annual_subsidy": "Avg. subsidy ($)"})
                .style.format({"% of recipients": "{:.1f}%", "% of group receiving": "{:.1f}%", "Avg. subsidy ($)": "${:,.0f}"}),
                width='stretch', hide_index=True,
            )

        with col_age:
            st.markdown("**By Age**")
            fig_age = _make_demo_chart(by_age, "age_bin", BRAND_COLORS["eig_green_700"])
            st.plotly_chart(fig_age, width='stretch')
            st.dataframe(
                by_age[["age_bin", "pct_of_recipients", "pct_in_group", "avg_annual_subsidy"]]
                .rename(columns={"age_bin": "Age group", "pct_of_recipients": "% of recipients",
                                 "pct_in_group": "% of group receiving", "avg_annual_subsidy": "Avg. subsidy ($)"})
                .style.format({"% of recipients": "{:.1f}%", "% of group receiving": "{:.1f}%", "Avg. subsidy ($)": "${:,.0f}"}),
                width='stretch', hide_index=True,
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
            width='stretch',
            hide_index=True,
        )

