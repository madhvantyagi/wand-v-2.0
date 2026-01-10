"""
Job Posting Parser
Extracts structured information from a single job posting text.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from models import get_deepseek_client


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
        description="Salary range if mentioned"
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
                        "You are analyzing a job posting. Extract ALL relevant information:\n\n"
                        "1. **company_name**: Company name\n"
                        "2. **about_company**: About the company section\n"
                        "3. **job_title**: Job title\n"
                        "4. **job_description**: Role description and responsibilities\n"
                        "5. **location**: Job location\n"
                        "6. **remote_policy**: Remote/hybrid/onsite policy\n"
                        "7. **required_qualifications**: Required qualifications (education, experience, certifications)\n"
                        "8. **preferred_qualifications**: Nice-to-have qualifications\n"
                        "9. **technical_skills**: Technical skills (languages, frameworks, tools, platforms)\n"
                        "10. **soft_skills_explicit**: Soft skills explicitly mentioned (e.g., 'strong communication')\n"
                        "11. **soft_skills_implicit**: Soft skills INFERRED from the description "
                        "(e.g., if role requires 'coordinating across teams', infer 'Collaboration')\n"
                        "12. **salary_range**: Salary if mentioned (min, max, currency)\n"
                        "13. **benefits**: Benefits and perks\n"
                        "14. **experience_level**: Entry/Mid/Senior/Lead/etc.\n"
                        "15. **team_info**: Information about the team\n\n"
                        "Be thorough. For implicit soft skills, read between the lines."
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
