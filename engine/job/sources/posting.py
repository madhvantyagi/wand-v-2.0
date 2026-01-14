"""
Job Posting Parser
Extracts structured information from a single job posting text.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from engine.models import get_deepseek_client


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class JobPostingIntelligence(BaseModel):
    """Structured information extracted from a job posting."""
    
    # Company Info
    company_name: str = Field(default="", description="Company name")
    about_company: str = Field(default="", description="About the company section")
    
    # Role Info
    job_title: str = Field(default="", description="Job title")
    job_description: str = Field(default="", description="Role description and responsibilities")
    location: str = Field(default="", description="Job location")
    remote_policy: str = Field(default="", description="Remote/hybrid/onsite policy")
    
    # Qualifications
    required_qualifications: List[str] = Field(
        default_factory=list,
        description="Required qualifications and experience"
    )
    preferred_qualifications: List[str] = Field(
        default_factory=list,
        description="Preferred/nice-to-have qualifications"
    )
    
    # Skills
    technical_skills: List[str] = Field(
        default_factory=list,
        description="Technical skills required (languages, frameworks, tools)"
    )
    soft_skills_explicit: List[str] = Field(
        default_factory=list,
        description="Soft skills explicitly mentioned"
    )
    soft_skills_implicit: List[str] = Field(
        default_factory=list,
        description="Soft skills inferred from job description"
    )
    
    # Compensation & Benefits
    salary_range: Optional[Dict] = Field(
        default=None,
        description="Salary range with keys: min, max, currency, pay_type (hourly/daily/weekly/monthly/yearly)"
    )
    benefits: List[str] = Field(
        default_factory=list,
        description="Benefits and perks mentioned"
    )
    
    # Additional
    experience_level: str = Field(
        default="",
        description="Experience level (Entry, Mid, Senior, Lead, etc.)"
    )
    team_info: str = Field(
        default="",
        description="Information about the team"
    )


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def parse_job_posting(posting_text: str, api_key: str = None) -> Dict:
    """
    Parse a single job posting text into structured information.
    
    Args:
        posting_text: Raw job posting text
        api_key: DeepSeek API key (optional, uses env var)
        
    Returns:
        Dict with structured job posting information
    """
    if not posting_text or len(posting_text) < 50:
        return {"error": "Job posting text too short"}
    
    try:
        client = get_deepseek_client(api_key)
    except ValueError as e:
        return {"error": str(e)}
    
    try:
        result = client.chat.completions.create(
            model="deepseek-chat",
            response_model=JobPostingIntelligence,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are analyzing a job posting. Extract ALL relevant information with MAXIMUM thoroughness:\n\n"
                        "1. **company_name**: Company name\n"
                        "2. **about_company**: About the company section (if present)\n"
                        "3. **job_title**: Job title\n"
                        "4. **job_description**: Role description and responsibilities\n"
                        "5. **location**: Job location\n"
                        "6. **remote_policy**: Remote/hybrid/onsite policy\n\n"
                        
                        "7. **required_qualifications**: ACTUAL job requirements (NOT generic items like 'Full-time').\n"
                        "   - Extract education requirements (e.g., 'Bachelor's in CS', 'Master's degree')\n"
                        "   - Extract years of experience (e.g., '3+ years in backend development')\n"
                        "   - Extract mandatory certifications (e.g., 'AWS Certified Developer')\n"
                        "   - Extract hard requirements (e.g., 'Must have led a team of 5+')\n"
                        "   - DO NOT include generic items like 'Full-time', 'Onsite', or employment type\n"
                        "   - If no actual qualifications found, return []\n\n"
                        
                        "8. **preferred_qualifications**: Nice-to-have/bonus qualifications\n"
                        "   - Look for sections titled 'Preferred', 'Nice to Have', 'Bonus'\n"
                        "   - Extract optional education, experience, or certifications\n"
                        "   - Extract 'Ideally you have...' or similar statements\n"
                        "   - If none found, return [] (empty list, NOT null)\n\n"
                        
                        "9. **technical_skills**: Technical skills (languages, frameworks, tools, platforms)\n"
                        "   - Programming languages (Python, Java, JavaScript, etc.)\n"
                        "   - Frameworks/libraries (React, Django, TensorFlow, etc.)\n"
                        "   - Tools (Docker, Kubernetes, Git, etc.)\n"
                        "   - Platforms (AWS, GCP, Azure, etc.)\n"
                        "   - Databases (PostgreSQL, MongoDB, etc.)\n\n"
                        
                        "10. **soft_skills_explicit**: Soft skills EXPLICITLY mentioned in the posting\n"
                        "    - Look for phrases like 'strong communication', 'team player', 'leadership'\n"
                        "    - Only include if directly stated\n\n"
                        
                        "11. **soft_skills_implicit**: Soft skills INFERRED from the job description\n"
                        "    - If role requires 'coordinating across teams' → infer 'Collaboration'\n"
                        "    - If role requires 'presenting to stakeholders' → infer 'Communication', 'Presentation Skills'\n"
                        "    - If role requires 'managing projects' → infer 'Project Management', 'Organization'\n"
                        "    - If role requires 'mentoring juniors' → infer 'Mentorship', 'Leadership'\n"
                        "    - Read between the lines and extract ALL implied soft skills\n\n"
                        
                        "12. **salary_range**: Salary information if mentioned\n"
                        "    - Look for salary ranges, compensation, or pay information\n"
                        "    - Include min, max, currency, and pay_type (hourly/daily/weekly/monthly/yearly)\n"
                        "    - If only one value mentioned, set min=max\n"
                        "    - If no salary mentioned, return null (NOT empty dict)\n"
                        "    - Examples: '$120k-$150k' → {min: 120000, max: 150000, currency: 'USD', pay_type: 'yearly'}\n"
                        "              '$50/hour' → {min: 50, max: 50, currency: 'USD', pay_type: 'hourly'}\n\n"
                        
                        "13. **benefits**: Benefits and perks\n"
                        "    - Health insurance, 401k, equity, PTO, etc.\n\n"
                        
                        "14. **experience_level**: Entry/Mid/Senior/Lead/etc.\n\n"
                        
                        "15. **team_info**: Information about the team\n\n"
                        
                        "CRITICAL RULES:\n"
                        "- Be EXTREMELY thorough - extract ALL available information\n"
                        "- For required_qualifications, DO NOT include generic items like employment type\n"
                        "- For preferred_qualifications, return [] if none found (NOT null)\n"
                        "- For salary_range, return null if not mentioned (NOT empty dict or {})\n"
                        "- For implicit soft skills, read between the lines and infer ALL relevant skills\n"
                    )
                },
                {
                    "role": "user",
                    "content": f"Job Posting:\n\n{posting_text[:5000]}"
                }
            ],
            temperature=0.0,
        )
        
        return result.model_dump()
        
    except Exception as e:
        return {"error": f"AI extraction failed: {e}"}
