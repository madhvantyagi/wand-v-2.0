"""
Discrepancy Package - Profile Source Comparison

Compares resume, LinkedIn, and portfolio to find inconsistencies.
Returns UI-friendly JSON for table display.
"""

from .discrepancy import compare_profile_sources, format_for_table

__all__ = ['compare_profile_sources', 'format_for_table']
