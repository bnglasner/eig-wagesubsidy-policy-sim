"""
Tab 1: Individual wage calculator.
Users adjust their hourly wage and policy parameters; sees subsidy and take-home.
"""

import numpy as np
import pandas as pd
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

    params = dict(
        median_hourly_wage=median_wage,
        target_pct=target_pct,
        subsidy_pct=subsidy_pct,
        base_wage=base_wage,
    )
    hours_per_year = hours_per_week * weeks_per_year

    subsidy_hr  = hourly_subsidy(employer_wage, **params)
    takehome_hr = take_home_wage(employer_wage, **params)
    pct_boost   = pct_raise(employer_wage, **params)
    ann_sub     = annual_subsidy(employer_wage, hours_per_year=hours_per_year, **params)
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

        # ── Wage sweep chart ──────────────────────────────────────────────
        wages = np.arange(base_wage, t_wage + 0.05, 0.25)
        subsidies = [hourly_subsidy(w, **params) for w in wages]
        takehouses = [take_home_wage(w, **params) for w in wages]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=wages, y=subsidies,
            name="Wage subsidy", marker_color="#00857A",
        ))
        fig.add_trace(go.Scatter(
            x=wages, y=takehouses,
            name="Take-home wage", mode="lines+markers",
            line=dict(color="#1A4D8F", width=2),
        ))
        fig.add_vline(
            x=employer_wage, line_dash="dash", line_color="#CC4400",
            annotation_text=f"Your wage: ${employer_wage:.2f}",
            annotation_position="top right",
        )
        fig.update_layout(
            title="Subsidy and Take-Home Wage by Employer-Paid Wage",
            xaxis_title="Employer-paid hourly wage ($)",
            yaxis_title="Dollars per hour ($)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            height=380,
        )
        st.plotly_chart(fig, use_container_width=True)
