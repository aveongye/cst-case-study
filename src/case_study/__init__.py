"""
Utilities for the CST case study analytics flow.

The package exposes high-level orchestration helpers for reading cashflow
data, computing IRRs, generating NAV schedules, and suggesting FX hedges.
"""

from .run import CaseStudyResult, run_case_study  # noqa: F401


