"""
Job Intelligence Extractor
Main entry point for extracting comprehensive company intelligence.
"""

from typing import Dict, Optional
from datetime import datetime
from .sources.jobs import get_salary_and_stack
from .sources.website import get_company_info
from .sources.news import get_news_signals
from .sources.posting import parse_job_posting


def extract_company_intelligence(
    company_name: str,
    max_jobs: int = 50,
    include_website: bool = True,
    include_news: bool = True,
    website_url: Optional[str] = None
) -> Dict:
    """
    Extract comprehensive company intelligence from multiple sources.
    
    Each source is independent - if one fails, others continue.
    Errors are logged but don't stop execution.
    
    Args:
        company_name: Name of the company to research
        max_jobs: Maximum number of job postings to analyze (default: 50)
        include_website: Whether to scrape company website (default: True)
        include_news: Whether to scrape news (default: True)
        website_url: Optional company website URL (auto-discovered if not provided)
        
    Returns:
        Dict with unified company intelligence from all sources
    """
    print(f"\n{'='*60}")
    print(f"Extracting intelligence for: {company_name}")
    print(f"{'='*60}\n")
    
    # Track sources used, API calls, and errors
    sources_used = []
    api_calls = 0
    errors = []
    
    # Source 1: Job Postings (always run)
    jobs_data = {}
    print("📊 Source 1: Job Postings")
    try:
        jobs_result = get_salary_and_stack(company_name)
        sources_used.append("jobs")
        api_calls += 1
        
        # Extract job intelligence from result
        jobs_intel = jobs_result.get('phase_1_results', {}).get('derived_intelligence', {})
        
        jobs_data = {
            "tech_stack": jobs_intel.get('tech_stack', []),
            "salary_range": jobs_intel.get('salary_range'),
            "benefits": jobs_intel.get('culture_signals', {}).get('benefits', []),
            "hiring_tempo": jobs_intel.get('culture_signals', {}).get('hiring_tempo', 'Unknown'),
            "recruiter_contacts": jobs_intel.get('recruiter_contacts', []),
            "active_roles": jobs_result.get('phase_1_results', {}).get('active_role_count', 0),
            "raw_listings": jobs_result.get('phase_1_results', {}).get('raw_listings', [])
        }
    except Exception as e:
        error_msg = f"Jobs source failed: {e}"
        print(f"  ⚠ {error_msg}")
        errors.append(error_msg)
    
    # Source 2: Company Website (optional)
    website_data = {}
    if include_website:
        print("\n🌐 Source 2: Company Website")
        try:
            website_result = get_company_info(company_name, website_url)
            sources_used.append("website")
            api_calls += 1
            
            website_data = {
                "mission": website_result.get('mission', ''),
                "values_explicit": website_result.get('values_explicit', []),
                "values_implicit": website_result.get('values_implicit', []),
                "products": website_result.get('products', []),
                "culture": website_result.get('culture', []),
                "tech_stack": website_result.get('tech_stack', []),
                "company_info": {
                    "size": website_result.get('company_size', ''),
                    "industry": website_result.get('industry', ''),
                    "founded": website_result.get('founded', '')
                },
                "website_url": website_result.get('website', '')
            }
        except Exception as e:
            error_msg = f"Website source failed: {e}"
            print(f"  ⚠ {error_msg}")
            errors.append(error_msg)
    
    # Source 3: News (optional, no AI)
    news_data = {}
    if include_news:
        print("\n📰 Source 3: News")
        try:
            news_result = get_news_signals(company_name)
            sources_used.append("news")
            # No API call for news
            
            news_data = {
                "headlines": news_result.get('news', []),
                "count": news_result.get('count', 0)
            }
        except Exception as e:
            error_msg = f"News source failed: {e}"
            print(f"  ⚠ {error_msg}")
            errors.append(error_msg)
    
    # Build unified result
    print(f"\n{'='*60}")
    if errors:
        print(f"⚠ Completed with {len(errors)} error(s)")
    else:
        print("✅ Extraction complete!")
    print(f"{'='*60}\n")
    
    return {
        "company": company_name,
        "jobs": jobs_data,
        "website": website_data,
        "news": news_data,
        "metadata": {
            "sources_used": sources_used,
            "api_calls": api_calls,
            "extracted_at": datetime.now().isoformat(),
            "errors": errors,
            "config": {
                "max_jobs": max_jobs,
                "include_website": include_website,
                "include_news": include_news
            }
        }
    }


def extract_from_posting(posting_text: str) -> Dict:
    """
    Extract structured information from a single job posting.
    
    Args:
        posting_text: Raw job posting text (copy-pasted from job board)
        
    Returns:
        Dict with structured job posting information
    """
    print("🔍 Parsing job posting...")
    try:
        result = parse_job_posting(posting_text)
        print("✅ Parsing complete!")
        return result
    except Exception as e:
        error_msg = f"Posting parse failed: {e}"
        print(f"  ⚠ {error_msg}")
        return {"error": error_msg}


def extract_full_job_context(
    posting_text: str,
    company_name: Optional[str] = None,
    include_company_intel: bool = True
) -> Dict:
    """
    Extract comprehensive job context from posting + company intelligence.
    
    Combines data from multiple sources and organizes by source type:
    - job_posting: Data extracted from the job posting text
    - company_intel: Data from company website and job listings
    - news: Latest news about the company
    
    Args:
        posting_text: Raw job posting text
        company_name: Company name (extracted from posting if not provided)
        include_company_intel: Whether to gather company intelligence
        
    Returns:
        Dict organized by source with all extracted data
    """
    print(f"\n{'='*60}")
    print("Extracting Full Job Context")
    print(f"{'='*60}\n")
    
    result = {
        "job_posting": {},
        "company_intel": {},
        "news": [],
        "metadata": {
            "sources_used": [],
            "errors": []
        }
    }
    
    # Step 1: Parse job posting (always required)
    print("📋 Step 1: Parsing job posting...")
    try:
        posting_data = parse_job_posting(posting_text)
        result["job_posting"] = {
            "job_title": posting_data.get("job_title", ""),
            "company_name": posting_data.get("company_name", ""),
            "job_description": posting_data.get("job_description", ""),
            "about_company": posting_data.get("about_company", ""),
            "location": posting_data.get("location", ""),
            "remote_policy": posting_data.get("remote_policy", ""),
            "required_qualifications": posting_data.get("required_qualifications", []),
            "preferred_qualifications": posting_data.get("preferred_qualifications", []),
            "technical_skills": posting_data.get("technical_skills", []),
            "soft_skills_explicit": posting_data.get("soft_skills_explicit", []),
            "soft_skills_implicit": posting_data.get("soft_skills_implicit", []),
            "salary_range": posting_data.get("salary_range", {}),
            "benefits": posting_data.get("benefits", []),
            "experience_level": posting_data.get("experience_level", ""),
            "team_info": posting_data.get("team_info", "")
        }
        result["metadata"]["sources_used"].append("job_posting")
        
        # Use company name from posting if not provided
        if not company_name:
            company_name = posting_data.get("company_name", "")
            
    except Exception as e:
        error_msg = f"Job posting parsing failed: {e}"
        print(f"  ⚠ {error_msg}")
        result["metadata"]["errors"].append(error_msg)
        return result
    
    # Step 2: Get company intelligence (optional, continues on failure)
    if include_company_intel and company_name:
        print(f"\n🏢 Step 2: Gathering company intelligence for '{company_name}'...")
        try:
            intel = extract_company_intelligence(
                company_name=company_name,
                include_website=True,
                include_news=True
            )
            
            # Extract website data as company_intel
            website_data = intel.get("website", {})
            jobs_data = intel.get("jobs", {})
            
            result["company_intel"] = {
                "mission": website_data.get("mission", ""),
                "values_explicit": website_data.get("values_explicit", []),
                "values_implicit": website_data.get("values_implicit", []),
                "culture": website_data.get("culture", []),
                "products": website_data.get("products", []),
                "technical_skills": list(set(
                    website_data.get("tech_stack", []) + jobs_data.get("tech_stack", [])
                )),
                "soft_skills_explicit": website_data.get("values_explicit", []),
                "soft_skills_implicit": website_data.get("values_implicit", []),
                "company_info": website_data.get("company_info", {}),
                "salary_range": jobs_data.get("salary_range"),
                "benefits": jobs_data.get("benefits", []),
                "active_roles": jobs_data.get("active_roles", 0),
                "hiring_tempo": jobs_data.get("hiring_tempo", "Unknown")
            }
            result["metadata"]["sources_used"].append("company_intel")
            
            # Extract news
            news_data = intel.get("news", {})
            result["news"] = news_data.get("headlines", [])
            if result["news"]:
                result["metadata"]["sources_used"].append("news")
                
        except Exception as e:
            error_msg = f"Company intelligence failed: {e}"
            print(f"  ⚠ {error_msg}")
            result["metadata"]["errors"].append(error_msg)
    
    print(f"\n{'='*60}")
    print(f"✅ Extraction complete! Sources: {result['metadata']['sources_used']}")
    print(f"{'='*60}\n")
    
    return result
