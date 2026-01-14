"""
Sources package - Company intelligence extraction modules.
"""

from .jobs import get_salary_and_stack
from .website import get_company_info
from .news import get_news_signals

__all__ = ['get_salary_and_stack', 'get_company_info', 'get_news_signals']
