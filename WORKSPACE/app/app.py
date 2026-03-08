"""
EIG Wage Subsidy Interactive Simulation
"How to End Low-Wage Work Forever" — Glasner & Ozimek (EIG)

Launch: streamlit run WORKSPACE/app/app.py
"""

import streamlit as st

# Page config — must be first Streamlit call
st.set_page_config(
    page_title="EIG Wage Subsidy Simulator",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Tabs (imported after page config)
from tabs import calculator, methods, population  # noqa: E402

# ── Header ──────────────────────────────────────────────────────────────────
st.title("EIG Wage Subsidy Simulator")
st.markdown(
    "Explore the effects of the **80-80 Rule** wage subsidy proposed by "
    "Ben Glasner and Adam Ozimek at the Economic Innovation Group."
)

# ── Tab navigation ───────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(
    ["📊 Individual Calculator", "🗺️ Population Impacts", "📚 Methods"]
)

with tab1:
    calculator.render()

with tab2:
    population.render()

with tab3:
    methods.render()
