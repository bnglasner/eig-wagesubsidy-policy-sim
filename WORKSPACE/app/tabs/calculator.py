"""
Tab 1: Individual wage calculator.
Section 1: quick subsidy metrics and wage-sweep chart.
Section 2: budget constraint figure (continuous hours axis) + difference table.
"""

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from utils.subsidy import (
    DEFAULT_PARAMS,
    annual_subsidy,
    hourly_subsidy,
    pct_raise,
    take_home_wage,
    target_wage,
)
from utils.states import DEFAULT_STATE_OPTION, STATE_OPTIONS, parse_state_code
from utils.household_sim import (
    COMPONENTS,
    FAMILY_TYPES,
    TABLE_HOURS,
    TRANSFER_KEYS,
    run_from_precomputed,
    schedules_available,
)
from utils.eig_style import eig_plotly_layout


# â”€â”€ Cached PolicyEngine wrapper â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@st.cache_data(show_spinner="Running PolicyEngine simulation (first load only)...")
def _cached_sim(
    employer_wage: float,
    family_type: str,
    state_code: str,
    subsidy_params_tuple: tuple,
) -> "pd.DataFrame":
    subsidy_params = dict(subsidy_params_tuple)
    return run_from_precomputed(employer_wage, family_type, state_code, subsidy_params)


# â”€â”€ Budget constraint figure â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _make_budget_figure(df: "pd.DataFrame", scenario: str, active_keys: "set[str]") -> go.Figure:
    """Single-panel stacked bar chart: annual hours on x-axis, income components on y-axis."""
    import numpy as np

    panel = df[df["scenario"] == scenario].sort_values("annual_hours")

    # Compute y-axis bounds using only active components so toggling scenarios doesn't rescale.
    # Group by (annual_hours, scenario) so the two scenarios don't get summed together.
    pos_cols = [k for k, _, _, is_pos in COMPONENTS if is_pos and k in active_keys]
    neg_cols = [k for k, _, _, is_pos in COMPONENTS if not is_pos and k in active_keys]

    grouped = df.groupby(["annual_hours", "scenario"])
    y_max_pos = float(grouped[pos_cols].sum().sum(axis=1).max()) if pos_cols else 0.0
    y_min_neg = float(grouped[neg_cols].sum().sum(axis=1).min()) if neg_cols else 0.0
    y_max_net = float(grouped["net_income"].sum().max())

    y_max = max(y_max_pos, y_max_net, 0.0)
    y_min = min(y_min_neg, 0.0)

    # Add 5% padding
    y_range_pad = (y_max - y_min) * 0.05
    y_axis_min = y_min - y_range_pad
    y_axis_max = y_max + y_range_pad

    fig = go.Figure()

    for key, label, color, _ in COMPONENTS:
        if key not in active_keys:
            continue
        fig.add_trace(go.Bar(
            name=label,
            x=panel["annual_hours"],
            y=panel[key],
            marker_color=color,
            marker_line_width=0,
        ))

    fig.add_trace(go.Scatter(
        name="Net income",
        x=panel["annual_hours"],
        y=panel["net_income"],
        mode="lines",
        line=dict(color="#111111", width=2, dash="dash"),
        showlegend=True,
    ))

    fig.add_hline(
        y=0,
        line=dict(color="#000000", width=1.5),
    )

    fig.update_layout(**eig_plotly_layout(
        barmode="relative",
        bargap=0,
        height=500,
        xaxis=dict(
            title="Annual hours worked",
            showgrid=False,
            tickvals=[0, 520, 1040, 1560, 2080, 2600, 3120],
            ticktext=["0\n(0/wk)", "520\n(10/wk)", "1,040\n(20/wk)",
                      "1,560\n(30/wk)", "2,080\n(40/wk)", "2,600\n(50/wk)", "3,120\n(60/wk)"],
        ),
        yaxis=dict(
            title="Annual dollars ($)",
            showgrid=True,
            gridcolor="#D9D9D9",
            tickprefix="$",
            tickformat=",.0f",
            range=[y_axis_min, y_axis_max],
        ),
        legend=dict(orientation="h", yanchor="top", y=-0.25, x=0),
        margin=dict(t=30, b=140),
    ))

    # Reference lines for standard part-time and full-time annual hours.
    ref_line_color = "#111111"
    for x_val, label in [(1040, "Part-time (20 hrs/wk)"), (2080, "Full-time (40 hrs/wk)")]:
        fig.add_vline(
            x=x_val,
            line=dict(color=ref_line_color, width=2),
        )
        fig.add_annotation(
            x=x_val,
            y=y_axis_max,
            text=label,
            showarrow=False,
            xanchor="right",
            yanchor="bottom",
            xshift=-6,
            font=dict(size=11, color=ref_line_color),
            bgcolor="rgba(255,255,255,0.85)",
        )

    return fig


# â”€â”€ Difference table â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _make_diff_table(df: "pd.DataFrame", active_keys: "set[str]") -> "pd.DataFrame":
    """
    Difference table: (With Subsidy) - (Baseline) at the 4 reference hour bins.
    Rows = active income/tax components + net income + total transfer spending change.
    Columns = 0 hrs/wk, 20 hrs/wk, 40 hrs/wk, 60 hrs/wk.
    """
    import pandas as pd

    col_data: dict[str, dict] = {}

    for annual_hours, col_label in TABLE_HOURS.items():
        base = df[(df["annual_hours"] == annual_hours) & (df["scenario"] == "Baseline")].iloc[0]
        sub  = df[(df["annual_hours"] == annual_hours) & (df["scenario"] == "With Subsidy")].iloc[0]

        col: dict[str, float] = {}
        for key, label, _, _ in COMPONENTS:
            if key not in active_keys:
                continue
            col[label] = sub[key] - base[key]

        col["Net income change"] = sub["net_income"] - base["net_income"]

        # Total transfer spending: sum only active government-funded transfers
        active_transfer_keys = [k for k in TRANSFER_KEYS if k in active_keys]
        col["Delta Total transfer spending"] = sum(sub[k] - base[k] for k in active_transfer_keys)

        col_data[col_label] = col

    return pd.DataFrame(col_data)


def _fmt_dollar(v: float) -> str:
    return f"${v:,.0f}"


def _sign_dollar(v: float) -> str:
    return f"${v:+,.0f}"


def _tax_impact_text(v: float) -> str:
    if v < 0:
        return f"`{_fmt_dollar(abs(v))}` loss in income from taxes paid"
    if v > 0:
        return f"`{_fmt_dollar(v)}` gain in income from lower taxes"
    return "`$0` change from taxes"


# â”€â”€ Main render â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def render() -> None:
    st.header("Individual Wage Calculator")
    st.markdown(
        "Adjust the sliders below to see how the wage subsidy would affect a "
        "worker's take-home pay."
    )

    col_inputs, col_results = st.columns([1, 2])

    with col_inputs:
        st.subheader("Your Situation")
        employer_wage = st.slider(
            "Employer-paid hourly wage ($)",
            min_value=7.25,
            max_value=20.00,
            value=10.00,
            step=0.25,
            format="$%.2f",
        )
        hours_per_week = st.slider(
            "Hours worked per week",
            min_value=10,
            max_value=40,
            value=40,
            step=5,
        )
        weeks_per_year = st.slider(
            "Weeks worked per year",
            min_value=10,
            max_value=52,
            value=50,
            step=1,
        )

        st.subheader("Policy Parameters")
        with st.expander("Adjust the 80-80 Rule"):
            median_wage = st.number_input(
                "National median hourly wage ($)",
                min_value=15.0,
                max_value=40.0,
                value=DEFAULT_PARAMS["median_hourly_wage"],
                step=0.50,
            )
            target_pct = st.slider(
                "Target wage (% of median)",
                min_value=50,
                max_value=100,
                value=int(DEFAULT_PARAMS["target_pct"] * 100),
                step=5,
                format="%d%%",
            ) / 100
            subsidy_pct = st.slider(
                "Subsidy (% of gap covered)",
                min_value=50,
                max_value=100,
                value=int(DEFAULT_PARAMS["subsidy_pct"] * 100),
                step=5,
                format="%d%%",
            ) / 100
            base_wage = st.number_input(
                "Base wage / minimum employer wage ($)",
                min_value=5.0,
                max_value=12.0,
                value=DEFAULT_PARAMS["base_wage"],
                step=0.25,
            )

        st.subheader("Budget Constraint Options")
        family_type = st.selectbox(
            "Family composition",
            options=list(FAMILY_TYPES.keys()),
            index=0,
        )
        state_option = st.selectbox(
            "State",
            options=STATE_OPTIONS,
            index=STATE_OPTIONS.index(DEFAULT_STATE_OPTION),
        )
        state_code = parse_state_code(state_option)

        # â”€â”€ Program selection â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        # employer_wages and wage_subsidy are always shown; everything else
        # is selectable. Selection is shared with the population tab.
        _ALWAYS_ON = {"employer_wages", "wage_subsidy"}
        _SELECTABLE = [(key, label) for key, label, _, _ in COMPONENTS
                       if key not in _ALWAYS_ON]
        _label_to_key = {label: key for key, label, _, _ in COMPONENTS}

        if "budget_active_keys" not in st.session_state:
            st.session_state["budget_active_keys"] = (
                _ALWAYS_ON | {key for key, _ in _SELECTABLE}
            )

        with st.expander("Programs shown in figure & table"):
            selected_labels = st.multiselect(
                "Include programs",
                options=[label for _, label in _SELECTABLE],
                default=[label for key, label in _SELECTABLE
                         if key in st.session_state["budget_active_keys"]],
                label_visibility="collapsed",
            )
            active_keys: set[str] = _ALWAYS_ON | {
                _label_to_key[lbl] for lbl in selected_labels
            }
            st.session_state["budget_active_keys"] = active_keys

    params = dict(
        median_hourly_wage=median_wage,
        target_pct=target_pct,
        subsidy_pct=subsidy_pct,
        base_wage=base_wage,
    )
    hours_per_year = hours_per_week * weeks_per_year

    subsidy_hr   = hourly_subsidy(employer_wage, **params)
    takehome_hr  = take_home_wage(employer_wage, **params)
    pct_boost    = pct_raise(employer_wage, **params)
    ann_sub      = annual_subsidy(employer_wage, hours_per_year=hours_per_year, **params)
    ann_employer = employer_wage * hours_per_year
    ann_total    = ann_employer + ann_sub
    t_wage       = target_wage(median_wage, target_pct)

    with col_results:
        st.subheader("Your Results")

        m1, m2, m3 = st.columns(3)
        m1.metric("Employer-paid wage", f"${employer_wage:.2f}/hr")
        m2.metric("Wage subsidy", f"+${subsidy_hr:.2f}/hr", f"+{pct_boost:.1%}")
        m3.metric("Take-home wage", f"${takehome_hr:.2f}/hr")

        m4, m5, m6 = st.columns(3)
        m4.metric("Annual employer pay", f"${ann_employer:,.0f}")
        m5.metric("Annual subsidy", f"+${ann_sub:,.0f}")
        m6.metric("Annual take-home", f"${ann_total:,.0f}")

        # â”€â”€ Wage sweep chart â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        wages     = np.arange(base_wage, t_wage + 0.05, 0.25)
        subsidies = [hourly_subsidy(w, **params) for w in wages]
        takehouses = [take_home_wage(w, **params) for w in wages]

        fig_sweep = go.Figure()
        fig_sweep.add_trace(go.Bar(
            x=wages, y=subsidies,
            name="Wage subsidy", marker_color="#19644D",  # eig_green_700
        ))
        fig_sweep.add_trace(go.Scatter(
            x=wages, y=takehouses,
            name="Take-home wage", mode="lines+markers",
            line=dict(color="#194F8B", width=2),          # eig_blue_800
        ))
        fig_sweep.add_vline(
            x=employer_wage, line_dash="dash", line_color="#D34917",  # eig_seq_red
            annotation_text=f"Your wage: ${employer_wage:.2f}",
            annotation_position="top right",
        )
        fig_sweep.update_layout(**eig_plotly_layout(
            title_text="Subsidy and Take-Home Wage by Employer-Paid Wage",
            xaxis_title="Employer-paid hourly wage ($)",
            yaxis_title="Dollars per hour ($)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            height=380,
        ))
        st.plotly_chart(fig_sweep, width='stretch')

    # â”€â”€ Section 2: Budget Constraint Figure â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    st.divider()
    st.subheader("Budget Constraint: Income by Hours Worked")

    if not schedules_available(family_type, state_code):
        st.info(
            "Pre-computed schedules not found - running PolicyEngine live. "
            "First load takes 1-3 minutes; subsequent loads are instant. "
            "Run `python WORKSPACE/code/01_data_preparation/01b_precompute_individual.py` "
            "to generate schedules for instant loading.",
            icon=":hourglass_flowing_sand:",
        )

    scenario = st.radio(
        "Scenario",
        options=["Baseline", "With Subsidy"],
        horizontal=True,
    )

    subsidy_params_tuple = tuple(sorted(params.items()))
    df_sim = _cached_sim(employer_wage, family_type, state_code, subsidy_params_tuple)

    hours_20 = 20 * 52
    hours_40 = 40 * 52
    annual_subsidy_20 = subsidy_hr * hours_20
    annual_subsidy_40 = subsidy_hr * hours_40

    labels_by_key = {key: label for key, label, _, _ in COMPONENTS}
    selected_program_labels = [
        labels_by_key[k]
        for k in labels_by_key
        if k in active_keys and k not in {"employer_wages", "wage_subsidy"}
    ]
    selected_programs_txt = ", ".join(selected_program_labels) if selected_program_labels else "no additional programs selected"

    def _point_deltas(annual_hours: int) -> dict[str, float]:
        base = df_sim[(df_sim["annual_hours"] == annual_hours) & (df_sim["scenario"] == "Baseline")].iloc[0]
        sub = df_sim[(df_sim["annual_hours"] == annual_hours) & (df_sim["scenario"] == "With Subsidy")].iloc[0]
        tax_change = (
            (sub["federal_tax"] - base["federal_tax"]) +
            (sub["state_tax"] - base["state_tax"]) +
            (sub["payroll_tax"] - base["payroll_tax"])
        )
        transfer_keys = [k for k in TRANSFER_KEYS if k in active_keys]
        transfer_change = sum(sub[k] - base[k] for k in transfer_keys)
        net_income_change = sub["net_income"] - base["net_income"]
        return {
            "tax_change": float(tax_change),
            "transfer_change": float(transfer_change),
            "net_income_change": float(net_income_change),
        }

    p20 = _point_deltas(hours_20)
    p40 = _point_deltas(hours_40)

    st.markdown(
        f"The proposed wage subsidy uses a national median hourly wage of `{median_wage:.2f}`. "
        f"With a target set at `{target_pct * 100:.0f}%`, the target wage is `{t_wage:.2f}`; "
        f"with a subsidy rate of `{subsidy_pct * 100:.0f}%` and a base wage floor of `{base_wage:.2f}`, "
        f"a worker paid `{employer_wage:.2f}` by their employer qualifies for an hourly subsidy of "
        f"`{subsidy_hr:.2f}`. That equals about `{_fmt_dollar(annual_subsidy_20)}` per year at 20 hours per week "
        f"(52 weeks) and `{_fmt_dollar(annual_subsidy_40)}` per year at 40 hours per week (52 weeks)."
    )
    st.markdown(
        f"Because this subsidy is treated as earnings in the household simulation, it also changes taxes and "
        f"means-tested supports. For the currently selected programs (`{selected_programs_txt}`), the model estimates "
        f"at 20 hours per week: {_tax_impact_text(p20['tax_change'])}, net transfer change "
        f"`{_sign_dollar(p20['transfer_change'])}`, and net income change `{_sign_dollar(p20['net_income_change'])}`. "
        f"At 40 hours per week: {_tax_impact_text(p40['tax_change'])}, net transfer change "
        f"`{_sign_dollar(p40['transfer_change'])}`, and net income change `{_sign_dollar(p40['net_income_change'])}`."
    )
    st.markdown(
        "Annual income is decomposed by source as hours worked increase. Taxes are shown as negative bars, "
        "and net income is the dashed line. Use the scenario toggle to compare baseline and subsidy outcomes."
    )

    fig_budget = _make_budget_figure(df_sim, scenario, active_keys)
    st.plotly_chart(fig_budget, width='stretch')

    # â”€â”€ Difference table â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    with st.expander("Difference table: With Subsidy vs. Baseline"):
        st.markdown(
            "Each cell shows **(With Subsidy) - (Baseline)** at four hours-worked levels. "
            "Positive = gain for worker or increase in program spending. "
            "Negative = reduction. "
            "The **Delta Total transfer spending** row sums all selected government-funded transfers "
            "(including the wage subsidy itself, less any reductions in existing programs).\n\n"
            "- **Transfer programs** (SNAP, EITC, Medicaid, etc.): "
            "green = benefit increases; red = benefit reductions (fiscal savings).\n"
            "- **Tax rows** (Federal income tax, State income tax, Payroll taxes): "
            "red = more tax revenue collected on the higher earnings - "
            "a fiscal offset to the government, not a cost."
        )
        diff_df = _make_diff_table(df_sim, active_keys)

        # Separate summary rows from component rows for styling
        component_labels = [label for key, label, _, _ in COMPONENTS if key in active_keys]
        summary_labels   = ["Net income change", "Delta Total transfer spending"]

        st.dataframe(
            diff_df.loc[component_labels + summary_labels]
                   .style
                   .format("${:+,.0f}")
                   .apply(
                       lambda col: [
                           "color: #2E8B57" if v > 0
                           else "color: #C0392B" if v < 0
                           else ""
                           for v in col
                       ],
                       axis=0,
                   ),
            width='stretch',
        )
