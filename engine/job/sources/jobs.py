"""
Phase 1: JD-First Deep Dive
Comprehensive job posting analysis using AI for intelligent extraction.

Extracts: Tech Stack, Salaries, Benefits, Culture Signals, Recruiter Contacts
"""

import os
from typing import Dict, List, Optional
from collections import Counter
from datetime import datetime
from jobspy import scrape_jobs
import pandas as pd
from pydantic import BaseModel, Field
from engine.models import get_deepseek_client


# ============================================================================
# PYDANTIC MODELS - Structured Extraction Schema
# ============================================================================

class SalaryRange(BaseModel):
    """Salary information extracted from job posting."""
    min: Optional[int] = Field(None, description="Minimum salary")
    max: Optional[int] = Field(None, description="Maximum salary")
    currency: str = Field(default="USD", description="Currency code")
    source: str = Field(default="Job Description", description="Data source")


class JobIntelligence(BaseModel):
    """Complete intelligence extracted from a single job posting."""
    tech_stack: List[str] = Field(
        default_factory=list,
        description="All technologies, languages, frameworks, tools mentioned"
    )
    benefits: List[str] = Field(
        default_factory=list,
        description="Benefits and culture signals (e.g., Remote Work, Health Insurance, Equity)"
    )
    recruiter_contacts: List[str] = Field(
        default_factory=list,
        description="Email addresses for recruiters or hiring contacts"
    )
    salary_range: Optional[SalaryRange] = Field(
        None,
        description="Salary range if mentioned"
    )
    is_urgent: bool = Field(
        default=False,
        description="Whether posting indicates urgent hiring"
    )


# ============================================================================
# AI-POWERED EXTRACTION
# ============================================================================

class BatchJobIntelligence(BaseModel):
    """Intelligence extracted from multiple job postings in one batch."""
    jobs: List[JobIntelligence] = Field(
        default_factory=list,
        description="List of intelligence extracted from each job"
    )


# ============================================================================
# AI-POWERED EXTRACTION (BATCH)
# ============================================================================

def extract_jobs_batch_ai(jobs_data: List[Dict], api_key: str = None) -> List[JobIntelligence]:
    """
    Extract intelligence from multiple jobs in ONE API call (much faster).
    
    Args:
        jobs_data: List of job dictionaries
        api_key: DeepSeek API key (optional, uses env var)
        
    Returns:
        List of JobIntelligence objects
    """
    if not jobs_data:
        return []
    
    # Build batch context (all jobs in one prompt)
    jobs_text = ""
    for i, job in enumerate(jobs_data, 1):
        title = job.get('title', '')
        description = job.get('description', '')
        
        # Handle NaN/float values in description
        if not isinstance(description, str):
            description = ''
        
        description = description[:1500]  # Limit per job
        company = job.get('company', '')
        
        jobs_text += f"""
--- Job {i} ---
Title: {title}
Company: {company}
Description: {description}

"""
    
    # Get DeepSeek client
    try:
        client = get_deepseek_client(api_key)
    except ValueError as e:
        print(f"  ⚠ {e}")
        return [JobIntelligence() for _ in jobs_data]
    
    # Extract intelligence for ALL jobs in one call
    try:
        result = client.chat.completions.create(
            model="deepseek-chat",
            response_model=BatchJobIntelligence,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are analyzing multiple job postings. For EACH job, extract:\n"
                        "1. **tech_stack**: ALL technologies mentioned\n"
                        "2. **benefits**: Culture signals (Remote, Health Insurance, 401k, Equity, Visa, etc.)\n"
                        "3. **recruiter_contacts**: Email addresses\n"
                        "4. **salary_range**: Salary info if mentioned\n"
                        "5. **is_urgent**: True if urgent hiring indicated\n\n"
                        "Return a list with one entry per job, in the same order."
                    )
                },
                {
                    "role": "user",
                    "content": jobs_text
                }
            ],
            temperature=0.0,
        )
        return result.jobs
    except Exception as e:
        print(f"  ⚠ Batch AI extraction failed: {e}")
        return [JobIntelligence() for _ in jobs_data]


# ============================================================================
# JOB FETCHING
# ============================================================================

def fetch_jobs(company_name: str, max_results: int = 50) -> pd.DataFrame:
    """Fetch job postings with 30-day filter for all tech roles."""
    try:
        jobs = scrape_jobs(
            site_name=["linkedin", "indeed", "glassdoor"],
            search_term=f"{company_name}",  # Search all jobs
            location="United States",
            results_wanted=max_results,
            hours_old=720,  # 30 days
            country_indeed='USA'
        )
        
        # Enforce max_results limit (jobspy sometimes returns more)
        if len(jobs) > max_results:
            jobs = jobs.head(max_results)
        
        print(f"  ✓ Found {len(jobs)} job postings (limited to {max_results})")
        return jobs
    except Exception as e:
        print(f"  ⚠ Error fetching jobs: {e}")
        return pd.DataFrame()


def calculate_hiring_tempo(jobs_df: pd.DataFrame) -> str:
    """Calculate hiring tempo from job posting dates."""
    try:
        if jobs_df.empty:
            return "Unknown"
        
        # Get most recent posting
        dates = pd.to_datetime(jobs_df['date_posted'], errors='coerce')
        most_recent = (datetime.now() - dates.max()).days
        
        if most_recent <= 3:
            return f"Urgent (Posted {most_recent} days ago)"
        elif most_recent <= 14:
            return f"Active (Posted {most_recent} days ago)"
        else:
            return f"Moderate (Posted {most_recent} days ago)"
    except:
        return "Unknown"


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def get_salary_and_stack(company_name: str) -> Dict:
    """
    Phase 1: Extract comprehensive company intelligence using AI.
    
    Args:
        company_name: Name of the company
        
    Returns:
        Dict with complete Phase 1 intelligence
    """
    jobs_df = fetch_jobs(company_name)
    
    if jobs_df.empty:
        return {
            "phase_1_results": {
                "company": company_name,
                "active_role_count": 0,
                "primary_source": "None",
                "derived_intelligence": {
                    "tech_stack": [],
                    "salary_range": None,
                    "culture_signals": {"benefits": [], "hiring_tempo": "No data"},
                    "recruiter_contacts": []
                },
                "raw_listings": []
            }
        }
    
    # Filter for tech roles and collect jobs
    tech_role_keywords = ['engineer', 'developer', 'architect', 'devops', 'sre', 'data scientist', 
                          'ml engineer', 'software', 'backend', 'frontend', 'full stack', 'qa', 
                          'security', 'cloud', 'infrastructure', 'technical', 'programmer', 'analyst']
    
    tech_jobs = []
    raw_listings = []
    
    for _, job in jobs_df.iterrows():
        title = job.get('title', '').lower()
        
        # Filter for tech roles only
        if not any(keyword in title for keyword in tech_role_keywords):
            continue
        
        tech_jobs.append(job.to_dict())
        
        # Build raw listing
        try:
            days_old = (datetime.now() - pd.to_datetime(job.get('date_posted'))).days
        except:
            days_old = None
        
        raw_listings.append({
            "title": job.get('title', ''),
            "url": job.get('job_url', ''),
            "is_stale": days_old > 21 if days_old else False,
            "days_old": days_old
        })
    
    if not tech_jobs:
        return {
            "phase_1_results": {
                "company": company_name,
                "active_role_count": 0,
                "primary_source": "None",
                "derived_intelligence": {
                    "tech_stack": [],
                    "salary_range": None,
                    "culture_signals": {"benefits": [], "hiring_tempo": "No data"},
                    "recruiter_contacts": []
                },
                "raw_listings": []
            }
        }
    
    # Extract intelligence from ALL jobs in ONE API call
    print(f"  🤖 Analyzing {len(tech_jobs)} tech roles with AI...")
    all_intelligence = extract_jobs_batch_ai(tech_jobs)
    print(f"  ✓ Analysis complete!")
    
    
    # Aggregate results
    all_tech = []
    all_benefits = []
    all_emails = []
    all_salaries = []
    
    for intel in all_intelligence:
        all_tech.extend(intel.tech_stack)
        all_benefits.extend(intel.benefits)
        all_emails.extend(intel.recruiter_contacts)
        if intel.salary_range:
            all_salaries.append(intel.salary_range.model_dump())
    
    # Count and rank
    tech_counter = Counter(all_tech)
    top_tech = [tech for tech, _ in tech_counter.most_common(20)]
    
    benefit_counter = Counter(all_benefits)
    top_benefits = [benefit for benefit, _ in benefit_counter.most_common(10)]
    
    unique_emails = list(dict.fromkeys(all_emails))
    
    # Calculate hiring tempo
    tempo = calculate_hiring_tempo(jobs_df)
    
    return {
        "phase_1_results": {
            "company": company_name,
            "active_role_count": len(all_intelligence),
            "primary_source": "LinkedIn/Indeed",
            "derived_intelligence": {
                "tech_stack": top_tech,
                "salary_range": all_salaries[0] if all_salaries else None,
                "culture_signals": {
                    "benefits": top_benefits,
                    "hiring_tempo": tempo
                },
                "recruiter_contacts": unique_emails[:10]  # Top 10
            },
            "raw_listings": raw_listings[:5]  # Top 5 for brevity
        }
    }
