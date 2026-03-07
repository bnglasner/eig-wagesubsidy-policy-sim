"""
EIG brand style helpers for Plotly figures in the Streamlit app.

Imports color and typography tokens from INFRA/style/themes/python/eig_tokens.py
and builds a Plotly layout template. Falls back to hardcoded EIG values if the
INFRA import fails (e.g. path issues on a deployment server).

Usage
-----
    from utils.eig_style import eig_plotly_layout

    fig.update_layout(**eig_plotly_layout())          # base EIG style
    fig.update_layout(title_text="My Chart", ...)     # figure-specific overrides
"""
from __future__ import annotations

import sys
from pathlib import Path

import plotly.graph_objects as go

# ── Load tokens from INFRA ────────────────────────────────────────────────────

_INFRA_TOKENS = (
    Path(__file__).resolve()
    .parent        # utils/
    .parent        # app/
    .parent        # WORKSPACE/
    .parent        # project root
    / "INFRA" / "style" / "themes" / "python"
)

if str(_INFRA_TOKENS) not in sys.path:
    sys.path.insert(0, str(_INFRA_TOKENS))

try:
    from eig_tokens import BRAND_COLORS, EIG_DISCRETE, SEQUENTIAL, TYPOGRAPHY  # type: ignore
except ImportError:
    # Hardcoded fallback — keep in sync with eig_tokens.py
    BRAND_COLORS = {
        "eig_teal_900":  "#024140",
        "eig_green_700": "#19644D",
        "eig_green_500": "#5E9C86",
        "eig_blue_800":  "#194F8B",
        "eig_blue_200":  "#B3D6DD",
        "eig_cream_100": "#FEECD6",
        "eig_purple_800":"#39274F",
        "eig_gold_600":  "#E1AD28",
        "eig_cyan_700":  "#176F96",
        "eig_tan_500":   "#D6936F",
        "eig_tan_300":   "#F0B799",
        "eig_black":     "#000000",
        "eig_white":     "#FFFFFF",
    }
    EIG_DISCRETE = [
        "#19644D", "#E1AD28", "#176F96",
        "#D6936F", "#194F8B", "#5E9C86", "#39274F",
    ]
    SEQUENTIAL = {
        "eig_seq_red_5": ["#97310E", "#D34917", "#F97D1E", "#FBA94F", "#FDD7A8"],
    }
    TYPOGRAPHY = {
        "headline": {
            "primary_family": "Tiempos Headline",
            "fallback_stack": ["Georgia", "Times New Roman", "serif"],
        },
        "body": {
            "primary_family": "Galaxie Polaris",
            "fallback_stack": ["Arial", "Helvetica Neue", "Helvetica", "sans-serif"],
        },
    }


# ── Font stack helpers ────────────────────────────────────────────────────────

def _font_stack(role: str) -> str:
    t = TYPOGRAPHY.get(role, TYPOGRAPHY["body"])
    return ", ".join([t["primary_family"]] + t["fallback_stack"])


HEADLINE_FONT = _font_stack("headline")
BODY_FONT     = _font_stack("body")


# ── EIG Plotly layout dict ────────────────────────────────────────────────────

def eig_plotly_layout(**overrides) -> dict:
    """
    Return a dict of EIG-branded layout kwargs for fig.update_layout().

    Pass any figure-specific overrides as keyword arguments — they will
    take precedence over the base EIG defaults.

    Example
    -------
        fig.update_layout(**eig_plotly_layout(
            title_text="My Chart",
            height=480,
        ))
    """
    base = dict(
        font=dict(
            family=BODY_FONT,
            size=11,
            color=BRAND_COLORS["eig_black"],
        ),
        title=dict(
            font=dict(
                family=HEADLINE_FONT,
                size=16,
                color=BRAND_COLORS["eig_black"],
            ),
            x=0,
            xanchor="left",
            pad=dict(l=0),
        ),
        paper_bgcolor=BRAND_COLORS["eig_white"],
        plot_bgcolor=BRAND_COLORS["eig_white"],
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            linecolor="#CFCFCF",
            tickfont=dict(family=BODY_FONT, size=10),
            titlefont=dict(family=BODY_FONT, size=11),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#D9D9D9",
            gridwidth=0.6,
            zeroline=False,
            linecolor="#CFCFCF",
            tickfont=dict(family=BODY_FONT, size=10),
            titlefont=dict(family=BODY_FONT, size=11),
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            font=dict(family=BODY_FONT, size=10),
        ),
    )
    base.update(overrides)
    return base
