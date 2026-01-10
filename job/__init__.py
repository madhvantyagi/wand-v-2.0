"""
Job Intelligence Package
Main entry point for company intelligence extraction.
"""

from .extractor import extract_company_intelligence, extract_from_posting
from .sources.jobs import get_salary_and_stack
from .sources.website import get_company_info
from .sources.news import get_news_signals
from .sources.posting import parse_job_posting

__all__ = [
    'extract_company_intelligence',
    'extract_from_posting',
    'get_salary_and_stack',
    'get_company_info',
    'get_news_signals',
    'parse_job_posting'
]
