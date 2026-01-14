"""
Cover Letter Generator
Generates tailored cover letters based on profile and job match.
Supports combining multiple profile sources.
"""

from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field
from engine.models import get_deepseek_client
from .gap_analyzer import combine_profiles


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class CoverLetter(BaseModel):
    """Generated cover letter with metadata."""
    letter: str = Field(
        default="",
        description="The complete cover letter text"
    )
    key_points_highlighted: List[str] = Field(
        default_factory=list,
        description="Main strengths emphasized in the letter"
    )
    gaps_addressed: List[str] = Field(
        default_factory=list,
        description="How gaps were positively addressed"
    )
    word_count: int = Field(default=0)


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def generate_cover_letter(
    job_data: Dict,
    resume: Dict = None,
    linkedin: Dict = None,
    portfolio: Dict = None,
    combined_profile: Dict = None,
    style: Literal["professional", "enthusiastic", "concise"] = "professional",
    company_name: str = None,
    api_key: str = None
) -> Dict:
    """
    Generate a tailored cover letter based on profile and job match.
    
    Accepts EITHER individual profile sources OR a pre-combined profile.
    Uses 1 AI call.
    
    Args:
        job_data: Parsed job posting from job/sources/posting.py
        resume: Parsed resume data (optional)
        linkedin: Parsed LinkedIn profile data (optional)
        portfolio: Parsed portfolio data (optional)
        combined_profile: Pre-combined profile (if using your own merge logic)
        style: "professional", "enthusiastic", or "concise"
        company_name: Optional company name (extracted from job if not provided)
        api_key: DeepSeek API key (optional)
        
    Returns:
        Dict with cover letter and metadata
        
    Example:
        >>> from profile import parse_profile
        >>> from job.sources.posting import parse_job_posting
        >>> 
        >>> resume = json.loads(parse_profile("resume.pdf", "pdf"))
        >>> linkedin = json.loads(parse_profile("linkedin.pdf", "pdf"))
        >>> job = parse_job_posting(job_text)
        >>> 
        >>> result = generate_cover_letter(job, resume=resume, linkedin=linkedin)
        >>> print(result['letter'])
    """
    print(f"📝 Generating {style} cover letter...")
    
    # Combine profiles if not pre-combined
    if combined_profile:
        profile = combined_profile
    else:
        profile = combine_profiles(resume, linkedin, portfolio)
    
    if not profile.get("sources_used") and not combined_profile:
        return {"error": "No profile data provided"}
    
    print(f"  📄 Using sources: {profile.get('sources_used', ['pre-combined'])}")
    
    try:
        client = get_deepseek_client(api_key)
    except ValueError as e:
        print(f"  ⚠ {e}")
        return {"error": str(e)}
    
    # Extract company name from job if not provided
    if not company_name:
        company_name = job_data.get('company_name', 'the company')
    
    # Get candidate name
    candidate_name = profile.get('personal_info', {}).get('name', 'Candidate')
    
    # Get most recent role
    recent_role = None
    if profile.get('work_experience'):
        recent_role = profile['work_experience'][0]
    
    # Build context
    profile_summary = f"""
CANDIDATE: {candidate_name}
Sources: {profile.get('sources_used', ['unknown'])}

Skills: {profile.get('skills', [])}

Work Experience (most recent):
{recent_role}

All Experience: {len(profile.get('work_experience', []))} positions

Education: {profile.get('education', [])}

Projects: {profile.get('projects', [])}

Certifications: {profile.get('certifications', [])}
"""
    
    job_summary = f"""
JOB DETAILS:
- Company: {company_name}
- Title: {job_data.get('job_title', '')}
- About Company: {job_data.get('about_company', '')}
- Role Description: {job_data.get('job_description', '')}
- Required Skills: {job_data.get('technical_skills', [])}
- Required Qualifications: {job_data.get('required_qualifications', [])}
"""
    
    style_instructions = {
        "professional": "Write in a formal, professional tone. Use industry-appropriate language.",
        "enthusiastic": "Write with energy and genuine excitement. Show passion for the role and company.",
        "concise": "Be brief and direct. Get to the point quickly. Maximum 200 words."
    }
    
    try:
        result = client.chat.completions.create(
            model="deepseek-chat",
            response_model=CoverLetter,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are an expert career coach writing a cover letter for {candidate_name}.\n\n"
                        f"Style: {style_instructions[style]}\n\n"
                        "The profile is combined from multiple sources (resume, LinkedIn, portfolio).\n"
                        "Use the BEST evidence from ANY source.\n\n"
                        "Guidelines:\n"
                        "1. Open with a compelling hook mentioning the specific role\n"
                        "2. Highlight 2-3 key strengths that match the job requirements\n"
                        "3. Use specific examples from their experience\n"
                        "4. Address any gaps positively (e.g., 'eager to expand my skills in...')\n"
                        "5. Show knowledge of the company\n"
                        "6. Close with a call to action\n\n"
                        "Return:\n"
                        "- **letter**: The complete cover letter\n"
                        "- **key_points_highlighted**: Main strengths emphasized\n"
                        "- **gaps_addressed**: How gaps were addressed\n"
                        "- **word_count**: Total words"
                    )
                },
                {
                    "role": "user",
                    "content": f"{profile_summary}\n\n{job_summary}"
                }
            ],
            temperature=0.7,  # Slightly creative for better writing
        )
        
        print("✅ Cover letter generated!")
        return result.model_dump()
        
    except Exception as e:
        print(f"  ⚠ Cover letter generation failed: {e}")
        return {"error": str(e)}
