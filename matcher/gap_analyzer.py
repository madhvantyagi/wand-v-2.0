"""
Gap Analyzer
Compares user profile against job requirements to find gaps.
Supports combining multiple profile sources (resume, linkedin, portfolio).
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from models import get_deepseek_client


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class TechnicalSkillsBySource(BaseModel):
    """Technical skills categorized by source."""
    job_posting: List[str] = Field(default_factory=list, description="Skills from job posting")
    company_intel: List[str] = Field(default_factory=list, description="Skills from company website/intel")


class SoftSkillsBySource(BaseModel):
    """Soft skills categorized by source and type."""
    job_posting_explicit: List[str] = Field(default_factory=list, description="Explicit soft skills from job posting")
    job_posting_implicit: List[str] = Field(default_factory=list, description="Implicit soft skills from job posting")
    company_intel_explicit: List[str] = Field(default_factory=list, description="Explicit soft skills from company intel")
    company_intel_implicit: List[str] = Field(default_factory=list, description="Implicit soft skills from company intel")


class CompensationBenefits(BaseModel):
    """Compensation and benefits info."""
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    currency: str = "USD"
    pay_type: str = Field(default="yearly", description="hourly/daily/weekly/monthly/yearly")
    benefits: List[str] = Field(default_factory=list)


class QualificationComparison(BaseModel):
    """Comparison of candidate qualifications vs requirements."""
    qualification: str = Field(default="", description="The qualification requirement")
    type: str = Field(default="required", description="'required' or 'preferred'")
    status: str = Field(default="uncertain", description="'met', 'not_met', or 'uncertain'")
    evidence: str = Field(default="", description="Evidence from candidate's profile, or reason for uncertainty")
    importance: str = Field(default="medium", description="'high', 'medium', 'low'")


class SkillComparison(BaseModel):
    """Detailed skill comparison."""
    skill: str = Field(default="")
    type: str = Field(default="hard", description="'hard' or 'soft'")
    status: str = Field(default="uncertain", description="'matched', 'missing', or 'uncertain'")
    importance: str = Field(default="medium", description="'high', 'medium', 'low'")
    source: str = Field(default="job_posting", description="'job_posting', 'company_intel', or 'both'")
    in_profile: str = Field(default="?", description="'yes', 'no', or '?' if uncertain")


class GapAnalysis(BaseModel):
    """Complete gap analysis between profile and job."""
    
    # Job Metadata (Mandatory)
    job_title: str = Field(default="", description="Job title")
    company_name: str = Field(default="", description="Company name")
    job_description: str = Field(default="", description="Job description summary")
    about_company: str = Field(default="", description="About the company")
    
    # Compensation
    compensation: CompensationBenefits = Field(default_factory=CompensationBenefits)
    
    # Qualifications
    required_qualifications: List[str] = Field(default_factory=list)
    preferred_qualifications: List[str] = Field(default_factory=list)
    
    # Technical Skills by Source
    technical_skills: TechnicalSkillsBySource = Field(default_factory=TechnicalSkillsBySource)
    
    # Soft Skills by Source (all 4 categories)
    soft_skills: SoftSkillsBySource = Field(default_factory=SoftSkillsBySource)
    
    # Match Analysis
    match_score: int = Field(default=0, description="Overall match percentage (0-100)")
    qualification_comparison: List[QualificationComparison] = Field(
        default_factory=list,
        description="Detailed comparison of required and preferred qualifications"
    )
    skill_comparison: List[SkillComparison] = Field(
        default_factory=list,
        description="Detailed technical and soft skill comparison"
    )
    
    # Recommendations
    recommendations: List[str] = Field(default_factory=list)
    experience_gap: str = Field(default="", description="Experience level comparison")


class MatchResult(BaseModel):
    """Analysis-only result from LLM (lighter payload)."""
    match_score: int = Field(default=0, description="Overall match percentage (0-100)")
    qualification_comparison: List[QualificationComparison] = Field(
        default_factory=list,
        description="Detailed comparison of required and preferred qualifications"
    )
    skill_comparison: List[SkillComparison] = Field(
        default_factory=list,
        description="Detailed technical and soft skill comparison"
    )
    recommendations: List[str] = Field(default_factory=list)
    experience_gap: str = Field(default="", description="Experience level comparison")


# ============================================================================
# HELPER: COMBINE PROFILE SOURCES
# ============================================================================

def combine_profiles(
    resume: Dict = None,
    linkedin: Dict = None,
    portfolio: Dict = None
) -> Dict:
    """
    Combine data from multiple profile sources into unified profile.
    
    Args:
        resume: Parsed resume data
        linkedin: Parsed LinkedIn profile data
        portfolio: Parsed portfolio/website data
        
    Returns:
        Unified profile combining all sources
    """
    combined = {
        "personal_info": {},
        "skills": [],
        "work_experience": [],
        "education": [],
        "projects": [],
        "certifications": [],
        "publications": [],
        "languages": [],
        "sources_used": []
    }
    
    # Process each source
    for source_name, source_data in [("resume", resume), ("linkedin", linkedin), ("portfolio", portfolio)]:
        if not source_data:
            continue
            
        combined["sources_used"].append(source_name)
        
        # Merge personal info (later sources override)
        if source_data.get("personal_info"):
            combined["personal_info"].update(source_data["personal_info"])
        
        # Merge skills (dedupe)
        skills = source_data.get("skills", [])
        if isinstance(skills, list):
            for skill in skills:
                if skill and skill not in combined["skills"]:
                    combined["skills"].append(skill)
        
        # Merge work experience
        exp = source_data.get("work_experience", [])
        if isinstance(exp, list):
            combined["work_experience"].extend(exp)
        
        # Merge education
        edu = source_data.get("education", [])
        if isinstance(edu, list):
            combined["education"].extend(edu)
        
        # Merge projects
        proj = source_data.get("projects", [])
        if isinstance(proj, list):
            combined["projects"].extend(proj)
        
        # Merge certifications
        certs = source_data.get("certifications", [])
        if isinstance(certs, list):
            for cert in certs:
                if cert and cert not in combined["certifications"]:
                    combined["certifications"].append(cert)
        
        # Merge publications
        pubs = source_data.get("publications", [])
        if isinstance(pubs, list):
            combined["publications"].extend(pubs)
        
        # Merge languages
        langs = source_data.get("languages", [])
        if isinstance(langs, list):
            for lang in langs:
                if lang and lang not in combined["languages"]:
                    combined["languages"].append(lang)
    
    return combined


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def analyze_gaps(
    job_data: Dict,
    resume: Dict = None,
    linkedin: Dict = None,
    portfolio: Dict = None,
    combined_profile: Dict = None,
    api_key: str = None
) -> Dict:
    """
    Analyze gaps between user profile(s) and job requirements.
    
    Accepts EITHER individual profile sources OR a pre-combined profile.
    Uses 1 AI call.
    
    Args:
        job_data: Parsed job posting from job/sources/posting.py
        resume: Parsed resume data (optional)
        linkedin: Parsed LinkedIn profile data (optional)
        portfolio: Parsed portfolio data (optional)
        combined_profile: Pre-combined profile (if using your own merge logic)
        api_key: DeepSeek API key (optional)
        
    Returns:
        Dict with gap analysis results
        
    Example:
        >>> from profile import parse_profile
        >>> from job.sources.posting import parse_job_posting
        >>> 
        >>> resume = json.loads(parse_profile("resume.pdf", "pdf"))
        >>> linkedin = json.loads(parse_profile("linkedin.pdf", "pdf"))
        >>> job = parse_job_posting(job_text)
        >>> 
        >>> gaps = analyze_gaps(job, resume=resume, linkedin=linkedin)
    """
    print("🔍 Analyzing gaps...")
    
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
    
    # Build context for AI
    profile_summary = f"""
CANDIDATE PROFILE (Combined from: {profile.get('sources_used', ['unknown'])})

Personal Info: {profile.get('personal_info', {})}

Skills: {profile.get('skills', [])}

Work Experience:
{profile.get('work_experience', [])}

Education: {profile.get('education', [])}

Projects: {profile.get('projects', [])}

Certifications: {profile.get('certifications', [])}

Languages: {profile.get('languages', [])}
"""
    
    job_summary = f"""
JOB REQUIREMENTS:
- Title: {job_data.get('job_title', '')}
- Company: {job_data.get('company_name', '')}
- Technical Skills Required: {job_data.get('technical_skills', [])}
- Required Qualifications: {job_data.get('required_qualifications', [])}
- Preferred Qualifications: {job_data.get('preferred_qualifications', [])}
- Soft Skills (Explicit): {job_data.get('soft_skills_explicit', [])}
- Soft Skills (Implicit): {job_data.get('soft_skills_implicit', [])}
- Experience Level: {job_data.get('experience_level', '')}
"""
    
    try:
        # Optimization: Use simplified MatchResult model to reduce LLM load
        # We manually populate the rest from job_data
        result = client.chat.completions.create(
            model="deepseek-chat",
            response_model=MatchResult,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a career advisor analyzing a candidate's fit for a job.\n\n"
                        "The profile may be combined from multiple sources (resume, LinkedIn, portfolio).\n"
                        "Consider ALL information across sources.\n\n"
                        
                        "═══════════════════════════════════════════════════════════════\n"
                        "⚠️  CRITICAL REQUIREMENT - MATCH SCORE ⚠️\n"
                        "═══════════════════════════════════════════════════════════════\n"
                        "The match_score field is MANDATORY and MUST be an integer 0-100.\n"
                        "This represents the PROFILE MATCH PERCENTAGE.\n"
                        "Calculate by evaluating:\n"
                        "  • Technical skills match (40%)\n"
                        "  • Soft skills alignment (20%)\n"
                        "  • Experience level fit (25%)\n"
                        "  • Qualifications match (15%)\n"
                        "Example: If candidate has 75% of tech skills, good soft skills,\n"
                        "matching experience, but missing some qualifications → ~70-75 score\n"
                        "═══════════════════════════════════════════════════════════════\n\n"
                        
                        "GENERATE THE FOLLOWING MANDATORY STRUCTURED OUTPUT:\n\n"
                        
                        "## 1. match_score (integer 0-100) ⭐ MANDATORY - DO NOT SKIP ⭐\n"
                        "This is the PROFILE MATCH PERCENTAGE - how well the candidate matches this job.\n"
                        "YOU MUST CALCULATE THIS. It is NOT optional.\n"
                        "Step-by-step calculation:\n"
                        "1. Count how many technical skills the candidate has vs required (40 points max)\n"
                        "2. Evaluate soft skills alignment (20 points max)\n"
                        "3. Compare experience level (25 points max)\n"
                        "4. Check qualifications match (15 points max)\n"
                        "5. Sum the points = final score (0-100)\n"
                        "This MUST be a number between 0-100. Example: 75 means 75% match.\n"
                        "DO NOT RETURN 0 UNLESS THE CANDIDATE IS COMPLETELY UNQUALIFIED.\n\n"
                        
                        "## 2. qualification_comparison (list) ⭐ ANALYZE EACH QUALIFICATION ⭐\n"
                        "For EACH required and preferred qualification, provide:\n"
                        "- qualification: The exact qualification text\n"
                        "- type: 'required' or 'preferred'\n"
                        "- status: 'met', 'not_met', or 'uncertain'\n"
                        "- evidence: Suggest where it was met or why uncertain\n"
                        "- importance: 'high', 'medium', 'low'\n\n"
                        
                        "## 3. skill_comparison (list) ⭐ ANALYZE ALL SKILLS ⭐\n"
                        "Compare ALL technical and soft skills required:\n"
                        "- skill: The skill name\n"
                        "- type: 'hard' or 'soft'\n"
                        "- status: 'matched', 'missing', or 'uncertain'\n"
                        "- importance: 'high', 'medium', 'low'\n"
                        "- source: 'job_posting' (default)\n"
                        "- in_profile: 'yes', 'no', or '?'\n\n"
                        
                        "## 4. recommendations (3-5 items)\n"
                        "Actionable advice to improve match.\n\n"
                        
                        "## 5. experience_gap\n"
                        "Brief comparison of experience levels.\n"
                    )
                },
                {
                    "role": "user",
                    "content": f"{job_summary}\n\n{profile_summary}"
                }
            ],
            temperature=0.0,
        )
        
        # Convert to dict
        match_data = result.model_dump()
        
        # Manually construct full GapAnalysis from job_data + match_data
        analysis = {
            "job_title": job_data.get("job_title", ""),
            "company_name": job_data.get("company_name", ""),
            "job_description": job_data.get("job_description", ""),
            "about_company": job_data.get("about_company", ""),
            
            "compensation": job_data.get("salary_range") or {},
            
            "required_qualifications": job_data.get("required_qualifications", []),
            "preferred_qualifications": job_data.get("preferred_qualifications", []),
            
            "technical_skills": {
                "job_posting": job_data.get("technical_skills", []),
                "company_intel": []
            },
            
            "soft_skills": {
                "job_posting_explicit": job_data.get("soft_skills_explicit", []),
                "job_posting_implicit": job_data.get("soft_skills_implicit", []),
                "company_intel_explicit": [],
                "company_intel_implicit": []
            },
            
            # Analysis fields from LLM
            "match_score": match_data.get("match_score", 0),
            "qualification_comparison": match_data.get("qualification_comparison", []),
            "skill_comparison": match_data.get("skill_comparison", []),
            "recommendations": match_data.get("recommendations", []),
            "experience_gap": match_data.get("experience_gap", ""),
            
            # Ensure news is handled gracefully if available in job_data or context
            "news": [] 
        }
        
        print("✅ Gap analysis complete (Optimized)!")
        return analysis
        
    except Exception as e:
        print(f"  ⚠ Gap analysis failed: {e}")
        return {"error": str(e)}


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def analyze_resume_gaps(resume: Dict, job_data: Dict, api_key: str = None) -> Dict:
    """
    Analyze gaps between RESUME ONLY and job requirements.
    
    Use this when you only have a resume to compare.
    Uses 1 AI call.
    
    Args:
        resume: Parsed resume data
        job_data: Parsed job posting
        api_key: DeepSeek API key (optional)
        
    Returns:
        Dict with gap analysis results
    """
    return analyze_gaps(job_data, resume=resume, api_key=api_key)


def analyze_online_presence_gaps(
    linkedin: Dict = None,
    portfolio: Dict = None,
    job_data: Dict = None,
    api_key: str = None
) -> Dict:
    """
    Analyze gaps between LINKEDIN + PORTFOLIO and job requirements.
    
    Use this when comparing online presence only (no resume).
    Uses 1 AI call.
    
    Args:
        linkedin: Parsed LinkedIn profile data
        portfolio: Parsed portfolio data
        job_data: Parsed job posting
        api_key: DeepSeek API key (optional)
        
    Returns:
        Dict with gap analysis results
    """
    return analyze_gaps(job_data, linkedin=linkedin, portfolio=portfolio, api_key=api_key)


def analyze_match(
    job_context: Dict,
    profile_data: Dict,
    api_key: str = None
) -> Dict:
    """
    Analyze match between profile and job with source-organized context.
    
    NEW FUNCTION: Accepts data organized by source (job_posting, company_intel, news)
    and returns strict schema for frontend display.
    
    Args:
        job_context: Dict from extract_full_job_context() with keys:
            - job_posting: Data from job posting
            - company_intel: Data from company website/jobs
            - news: Latest company news
        profile_data: Combined profile JSON with skills, experience, etc.
        api_key: DeepSeek API key (optional)
        
    Returns:
        Dict with strict schema matching frontend requirements
    """
    print("🎯 Analyzing job match...")
    
    try:
        client = get_deepseek_client(api_key)
    except ValueError as e:
        print(f"  ⚠ {e}")
        return {"error": str(e)}
    
    # Extract source data
    job_posting = job_context.get("job_posting", {})
    company_intel = job_context.get("company_intel", {})
    news = job_context.get("news", [])
    
    # Build comprehensive context
    job_summary = f"""
JOB POSTING DATA:
- Title: {job_posting.get('job_title', '')}
- Company: {job_posting.get('company_name', '')}
- Description: {job_posting.get('job_description', '')}
- About Company: {job_posting.get('about_company', '')}
- Location: {job_posting.get('location', '')}
- Remote Policy: {job_posting.get('remote_policy', '')}
- Required Qualifications: {job_posting.get('required_qualifications', [])}
- Preferred Qualifications: {job_posting.get('preferred_qualifications', [])}
- Technical Skills: {job_posting.get('technical_skills', [])}
- Soft Skills (Explicit): {job_posting.get('soft_skills_explicit', [])}
- Soft Skills (Implicit): {job_posting.get('soft_skills_implicit', [])}
- Salary Range: {job_posting.get('salary_range', {})}
- Benefits: {job_posting.get('benefits', [])}
- Experience Level: {job_posting.get('experience_level', '')}

COMPANY INTELLIGENCE DATA:
- Mission: {company_intel.get('mission', '')}
- Values (Explicit): {company_intel.get('values_explicit', [])}
- Values (Implicit): {company_intel.get('values_implicit', [])}
- Culture: {company_intel.get('culture', [])}
- Products: {company_intel.get('products', [])}
- Tech Stack: {company_intel.get('technical_skills', [])}
- Company Info: {company_intel.get('company_info', {})}
- Hiring Tempo: {company_intel.get('hiring_tempo', '')}

RECENT NEWS:
{news[:5] if news else 'No news available'}
"""
    
    profile_summary = f"""
CANDIDATE PROFILE:
- Skills: {profile_data.get('skills', [])}
- Work Experience: {profile_data.get('work_experience', [])}
- Education: {profile_data.get('education', [])}
- Projects: {profile_data.get('projects', [])}
- Certifications: {profile_data.get('certifications', [])}
- Languages: {profile_data.get('languages', [])}
"""
    
    try:
        result = client.chat.completions.create(
            model="deepseek-chat",
            response_model=GapAnalysis,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a career advisor analyzing a candidate's fit for a job.\n\n"
                        "You have data from TWO SOURCES:\n"
                        "1. JOB POSTING - Direct from the job listing\n"
                        "2. COMPANY INTEL - From company website and other job postings\n\n"
                        
                        "═══════════════════════════════════════════════════════════════\n"
                        "⚠️  CRITICAL REQUIREMENT - MATCH SCORE ⚠️\n"
                        "═══════════════════════════════════════════════════════════════\n"
                        "The match_score field is MANDATORY and MUST be an integer 0-100.\n"
                        "This represents the PROFILE MATCH PERCENTAGE.\n"
                        "Calculate by evaluating:\n"
                        "  • Technical skills match (40%)\n"
                        "  • Soft skills alignment (20%)\n"
                        "  • Experience level fit (25%)\n"
                        "  • Qualifications match (15%)\n"
                        "Example: If candidate has 75% of tech skills, good soft skills,\n"
                        "matching experience, but missing some qualifications → ~70-75 score\n"
                        "═══════════════════════════════════════════════════════════════\n\n"
                        
                        "GENERATE THE FOLLOWING MANDATORY OUTPUT:\n\n"
                        
                        "## 1. job_title, company_name, job_description, about_company\n"
                        "Extract from job posting data.\n\n"
                        
                        "## 2. compensation\n"
                        "- salary_min, salary_max (integers or null)\n"
                        "- currency (default 'USD')\n"
                        "- pay_type: 'hourly', 'daily', 'weekly', 'monthly', or 'yearly'\n"
                        "- benefits: List of benefits\n\n"
                        
                        "## 3. required_qualifications, preferred_qualifications\n"
                        "Lists from job posting.\n\n"
                        
                        "## 4. technical_skills (BY SOURCE - IMPORTANT!)\n"
                        "- job_posting: Technical skills from JOB POSTING only\n"
                        "- company_intel: Technical skills from COMPANY INTEL only\n\n"
                        
                        "## 5. soft_skills (ALL 4 CATEGORIES - IMPORTANT!)\n"
                        "- job_posting_explicit: Soft skills EXPLICITLY stated in job posting\n"
                        "- job_posting_implicit: Soft skills IMPLIED by job posting\n"
                        "- company_intel_explicit: Soft skills from company values/culture\n"
                        "- company_intel_implicit: Soft skills IMPLIED by company culture\n\n"
                        
                        "## 6. match_score ⭐ MANDATORY - DO NOT SKIP ⭐\n"
                        "Integer 0-100. YOU MUST CALCULATE THIS.\n"
                        "Step-by-step calculation:\n"
                        "1. Technical skills match: How many required skills does candidate have? (40 pts)\n"
                        "2. Soft skills alignment: Does candidate demonstrate needed soft skills? (20 pts)\n"
                        "3. Experience level: Does candidate's experience match the role level? (25 pts)\n"
                        "4. Qualifications: Does candidate meet required qualifications? (15 pts)\n"
                        "5. Sum = final score (0-100)\n"
                        "This MUST be provided. DO NOT return 0 unless completely unqualified.\n\n"
                        
                        "## 7. qualification_comparison (list) ⭐ ANALYZE EACH QUALIFICATION ⭐\n"
                        "For EACH required and preferred qualification:\n"
                        "- qualification: Exact text\n"
                        "- type: 'required' or 'preferred'\n"
                        "- status: 'met', 'not_met', or 'uncertain'\n"
                        "- evidence: Specific evidence from profile or reason for uncertainty\n"
                        "- importance: 'high', 'medium', or 'low'\n\n"
                        
                        "## 8. skill_comparison (list) ⭐ ANALYZE EACH SKILL ⭐\n"
                        "For EACH skill found in job/company data:\n"
                        "- skill: name\n"
                        "- type: 'hard' or 'soft'\n"
                        "- source: 'job_posting', 'company_intel', or 'both'\n"
                        "- in_profile: 'yes', 'no', or '?'\n"
                        "- importance: 'high', 'medium', 'low'\n"
                        "- status: 'matched', 'missing', or 'uncertain'\n\n"
                        
                        "## 9. recommendations (3-5 items)\n"
                        "Actionable advice to improve match.\n\n"
                        
                        "## 10. experience_gap\n"
                        "Brief comparison of experience levels.\n\n"
                        
                        "═══════════════════════════════════════════════════════════════\n"
                        "⚠️  CRITICAL REMINDERS ⚠️\n"
                        "1. match_score MUST be integer 0-100\n"
                        "2. qualification_comparison MUST analyze ALL qualifications\n"
                        "3. skill_comparison MUST analyze ALL skills\n"
                        "4. Use 'uncertain' or '?' when not sure - DON'T GUESS\n"
                        "BE THOROUGH. All fields are MANDATORY.\n"
                        "═══════════════════════════════════════════════════════════════"
                    )
                },
                {
                    "role": "user",
                    "content": f"{job_summary}\n\n{profile_summary}"
                }
            ],
            temperature=0.0,
        )
        
        # Convert to dict and add news
        analysis = result.model_dump()
        analysis["news"] = [{"title": n, "url": ""} if isinstance(n, str) else n for n in news[:5]]
        
        print("✅ Match analysis complete!")
        return analysis
        
    except Exception as e:
        print(f"  ⚠ Analysis failed: {e}")
        return {"error": str(e)}


# ============================================================================
# RESUME OPTIMIZATION
# ============================================================================

class SectionComparison(BaseModel):
    """Comparison of original vs optimized resume section."""
    section_name: str = Field(description="Name of the resume section (e.g. 'Summary', 'Work Experience')")
    original_content: str = Field(description="Original text from resume")
    optimized_content: str = Field(description="Rewritten text optimized for the job")
    explanation: str = Field(description="Explanation of why changes were made")


class ResumeOptimization(BaseModel):
    """Resume optimization result."""
    job_id: str = Field(default="")
    optimizations: List[SectionComparison] = Field(default_factory=list)


def optimize_resume(
    resume_data: Dict,
    job_context: Dict,
    api_key: str = None
) -> Dict:
    """
    Optimize resume content specifically for a job.
    
    STRICTLY uses RESUME data only (no LinkedIn/Portfolio).
    
    Args:
        resume_data: Parsed resume JSON
        job_context: Job context with posting and company intel
        api_key: DeepSeek API key (optional)
        
    Returns:
        Dict with optimization results
    """
    print("✨ Optimizing resume...")
    
    try:
        client = get_deepseek_client(api_key)
    except ValueError as e:
        print(f"  ⚠ {e}")
        return {"error": str(e)}
        
    # Extract job data
    job_posting = job_context.get("job_posting", {})
    company_intel = job_context.get("company_intel", {})
    
    job_summary = f"""
TARGET JOB:
- Title: {job_posting.get('job_title', '')}
- Company: {job_posting.get('company_name', '')}
- Description: {job_posting.get('job_description', '')}
- Key Tech Skills: {job_posting.get('technical_skills', [])}
- Key Soft Skills: {job_posting.get('soft_skills_explicit', [])}
- Company Values: {company_intel.get('values_explicit', [])}
"""

    resume_summary = f"""
CURRENT RESUME CONTENT:
{resume_data}
"""

    try:
        result = client.chat.completions.create(
            model="deepseek-chat",
            response_model=ResumeOptimization,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert resume writer tailoring a candidate's resume for a specific job.\n\n"
                        "INPUT DATA:\n"
                        "1. TARGET JOB: Job description and company values.\n"
                        "2. CURRENT RESUME: The candidate's actual resume data.\n\n"
                        
                        "TASK:\n"
                        "Rewrite 3-5 key sections of the resume to better align with the job requirements.\n"
                        "Do NOT invent experiences. Only rephrase existing experience using job keywords.\n\n"
                        
                        "OUTPUT REQUIREMENTS:\n"
                        "Generate a list of SectionComparison objects, each containing:\n"
                        "- section_name: e.g. 'Professional Summary', 'Experience: Software Engineer at X'\n"
                        "- original_content: Collection of points/text from original resume\n"
                        "- optimized_content: The REWRITTEN version, optimized for keywords and impact\n"
                        "- explanation: Brief reason for the changes\n\n"
                        
                        "CRITICAL RULES:\n"
                        "1. maintain truthfulness - do not hallucinate skills they don't have\n"
                        "2. focus on impact and metrics\n"
                        "3. use keywords from the job description\n"
                        "4. ensure optimized_content is complete and ready to paste\n"
                    )
                },
                {
                    "role": "user",
                    "content": f"{job_summary}\n\n{resume_summary}"
                }
            ],
            temperature=0.0
        )
        
        print("✅ Resume optimization complete!")
        return result.model_dump()
        
    except Exception as e:
        print(f"  ⚠ Optimization failed: {e}")
        return {"error": str(e)}
