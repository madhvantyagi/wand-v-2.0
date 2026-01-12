"""
Matcher Package - Profile-Job Matching System

Functions:
- analyze_gaps: Compare all profile sources vs job
- analyze_match: NEW - Compare with source-organized context (strict schema)
- analyze_resume_gaps: Compare resume only vs job
- analyze_online_presence_gaps: Compare LinkedIn + portfolio vs job
- generate_cover_letter: Create tailored cover letters
- combine_profiles: Merge multiple profile sources
"""

from .gap_analyzer import (
    analyze_gaps,
    analyze_match,
    analyze_resume_gaps,
    analyze_online_presence_gaps,
    combine_profiles,
    optimize_resume
)
from .cover_letter import generate_cover_letter

__all__ = [
    'analyze_gaps',
    'analyze_match',
    'analyze_resume_gaps',
    'analyze_online_presence_gaps',
    'generate_cover_letter',
    'combine_profiles',
    'optimize_resume'
]
