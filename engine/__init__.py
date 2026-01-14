"""
Engine Package - Unified Application Engine

This package consolidates all core application logic:
- job: Job intelligence and company data extraction
- matcher: Profile-job matching and gap analysis
- profile_extractor: Resume and profile parsing
- discrepancy: Profile source comparison
- models: LLM configurations
"""

from .job import (
    extract_company_intelligence,
    extract_from_posting,
    extract_full_job_context,
    get_salary_and_stack,
    get_company_info,
    get_news_signals,
    parse_job_posting
)

from .matcher import (
    analyze_gaps,
    analyze_match,
    analyze_resume_gaps,
    analyze_online_presence_gaps,
    generate_cover_letter,
    combine_profiles,
    optimize_resume
)

from .profile_extractor import parse_profile, ProfileData

from .discrepancy import compare_profile_sources, format_for_table

from .models import get_deepseek_client, get_gemini_client, LLMModels

__all__ = [
    # Job
    'extract_company_intelligence',
    'extract_from_posting',
    'extract_full_job_context',
    'get_salary_and_stack',
    'get_company_info',
    'get_news_signals',
    'parse_job_posting',
    # Matcher
    'analyze_gaps',
    'analyze_match',
    'analyze_resume_gaps',
    'analyze_online_presence_gaps',
    'generate_cover_letter',
    'combine_profiles',
    'optimize_resume',
    # Profile Extractor
    'parse_profile',
    'ProfileData',
    # Discrepancy
    'compare_profile_sources',
    'format_for_table',
    # Models
    'get_deepseek_client',
    'get_gemini_client',
    'LLMModels'
]
