"""
Wage subsidy formula logic — EIG 80-80 Rule.

Formula:
    subsidy_per_hour = subsidy_pct * max(0, target_wage - employer_wage)
    where:
        target_wage  = target_pct * median_hourly_wage
        subsidy_pct  = 0.80
        target_pct   = 0.80
        base_wage    = federal minimum wage (employer must pay >= base_wage to qualify)

Reference: Glasner & Ozimek (EIG), "How to End Low-Wage Work Forever"
"""

from __future__ import annotations


# Default policy parameters (2024 calibration)
DEFAULT_PARAMS = {
    "median_hourly_wage": 20.00,
    "target_pct":         0.80,
    "subsidy_pct":        0.80,
    "base_wage":          7.25,
    "hours_per_year":     2000,  # 40 hrs/wk * 50 wks
}


def target_wage(median_hourly_wage: float, target_pct: float = 0.80) -> float:
    """Return the target wage (80% of median by default)."""
    return median_hourly_wage * target_pct


def hourly_subsidy(
    employer_wage: float,
    median_hourly_wage: float = DEFAULT_PARAMS["median_hourly_wage"],
    target_pct: float = DEFAULT_PARAMS["target_pct"],
    subsidy_pct: float = DEFAULT_PARAMS["subsidy_pct"],
    base_wage: float = DEFAULT_PARAMS["base_wage"],
) -> float:
    """
    Return the hourly subsidy for a worker earning employer_wage.

    Returns 0 if employer_wage < base_wage (ineligible) or >= target_wage (no gap).
    """
    if employer_wage < base_wage:
        return 0.0
    t = target_wage(median_hourly_wage, target_pct)
    return subsidy_pct * max(0.0, t - employer_wage)


def take_home_wage(
    employer_wage: float,
    **params,
) -> float:
    """Return total take-home hourly wage after subsidy."""
    return employer_wage + hourly_subsidy(employer_wage, **params)


def annual_subsidy(
    employer_wage: float,
    hours_per_year: float = DEFAULT_PARAMS["hours_per_year"],
    **params,
) -> float:
    """Return total annual subsidy for a worker."""
    return hourly_subsidy(employer_wage, **params) * hours_per_year


def pct_raise(employer_wage: float, **params) -> float:
    """Return the percentage raise from the subsidy."""
    if employer_wage <= 0:
        return 0.0
    return hourly_subsidy(employer_wage, **params) / employer_wage
