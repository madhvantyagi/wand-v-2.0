"""
Profile Discrepancy Detector
Compares resume, LinkedIn, and portfolio to find inconsistencies.
Returns UI-friendly JSON for table display.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from engine.models import get_deepseek_client


# ============================================================================
# PYDANTIC MODELS (UI-Friendly Format)
# ============================================================================

class DiscrepancyItem(BaseModel):
    """Single discrepancy between sources."""
    field: str = Field(description="What's being compared (e.g., 'Job Title', 'Dates')")
    resume: str = Field(default="", description="Value from resume")
    linkedin: str = Field(default="", description="Value from LinkedIn")
    portfolio: str = Field(default="", description="Value from portfolio")
    issue: str = Field(default="", description="Description of the discrepancy")
    severity: str = Field(default="low", description="low, medium, or high")


class SkillComparison(BaseModel):
    """Skills across all sources."""
    skill: str = Field(description="Skill name")
    in_resume: bool = Field(default=False)
    in_linkedin: bool = Field(default=False)
    in_portfolio: bool = Field(default=False)


class ProfileDiscrepancy(BaseModel):
    """Complete discrepancy analysis between profile sources."""
    discrepancies: List[DiscrepancyItem] = Field(
        default_factory=list,
        description="List of found discrepancies"
    )
    skill_comparison: List[SkillComparison] = Field(
        default_factory=list,
        description="Skills matrix across sources"
    )
    missing_in_resume: List[str] = Field(
        default_factory=list,
        description="Items in LinkedIn/portfolio but missing from resume"
    )
    missing_online: List[str] = Field(
        default_factory=list,
        description="Items in resume but missing from online presence"
    )
    consistency_score: int = Field(
        default=100,
        description="Overall consistency percentage (0-100)"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Specific fixes to improve consistency"
    )


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def compare_profile_sources(
    resume: Dict = None,
    linkedin: Dict = None,
    portfolio: Dict = None,
    api_key: str = None
) -> Dict:
    """
    Compare 3 profile sources to find discrepancies.
    
    Returns JSON formatted for UI table display.
    Uses 1 AI call.
    
    Args:
        resume: Parsed resume data
        linkedin: Parsed LinkedIn profile data
        portfolio: Parsed portfolio data
        api_key: DeepSeek API key (optional)
        
    Returns:
        Dict with discrepancies, skill matrix, and recommendations.
        Formatted for easy UI table rendering.
        
    Example:
        >>> from profile import parse_profile
        >>> from matcher import compare_profile_sources
        >>> 
        >>> resume = json.loads(parse_profile("resume.pdf", "pdf"))
        >>> linkedin = json.loads(parse_profile("linkedin.pdf", "pdf"))
        >>> portfolio = json.loads(parse_profile("index.html", "html"))
        >>> 
        >>> result = compare_profile_sources(resume, linkedin, portfolio)
        >>> # result['skill_comparison'] ready for table display
    """
    print("🔍 Comparing profile sources for discrepancies...")
    
    sources_provided = []
    if resume:
        sources_provided.append("resume")
    if linkedin:
        sources_provided.append("linkedin")
    if portfolio:
        sources_provided.append("portfolio")
    
    if len(sources_provided) < 2:
        return {"error": "Need at least 2 sources to compare"}
    
    print(f"  📄 Comparing: {', '.join(sources_provided)}")
    
    try:
        client = get_deepseek_client(api_key)
    except ValueError as e:
        print(f"  ⚠ {e}")
        return {"error": str(e)}
    
    # Build comparison context
    context = f"""
PROFILE SOURCES TO COMPARE:

=== RESUME ===
{resume if resume else "Not provided"}

=== LINKEDIN ===
{linkedin if linkedin else "Not provided"}

=== PORTFOLIO ===
{portfolio if portfolio else "Not provided"}
"""
    
    try:
        result = client.chat.completions.create(
            model="deepseek-chat",
            response_model=ProfileDiscrepancy,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are analyzing profile consistency across sources.\n\n"
                        "Compare resume, LinkedIn, and portfolio to find:\n\n"
                        "1. **discrepancies**: Conflicts between sources. For each, specify:\n"
                        "   - field: What's being compared (e.g., 'Current Title', 'Company Dates')\n"
                        "   - resume/linkedin/portfolio: Value from each source\n"
                        "   - issue: Clear description of the conflict\n"
                        "   - severity: 'high' (dates/titles mismatch), 'medium' (minor differences), 'low' (formatting)\n\n"
                        "2. **skill_comparison**: Matrix of skills across sources. Check which skills appear where.\n\n"
                        "3. **missing_in_resume**: Important items (skills, projects, roles) in LinkedIn/portfolio but NOT in resume\n\n"
                        "4. **missing_online**: Items in resume but NOT in online presence\n\n"
                        "5. **consistency_score**: 0-100 based on how consistent the sources are\n\n"
                        "6. **recommendations**: Specific fixes (e.g., 'Add Python to LinkedIn skills')\n\n"
                        "Focus on meaningful discrepancies, not minor formatting differences."
                    )
                },
                {
                    "role": "user",
                    "content": context
                }
            ],
            temperature=0.0,
        )
        
        print("✅ Discrepancy analysis complete!")
        return result.model_dump()
        
    except Exception as e:
        print(f"  ⚠ Discrepancy analysis failed: {e}")
        return {"error": str(e)}


# ============================================================================
# HELPER: FORMAT FOR UI TABLE
# ============================================================================

def format_for_table(discrepancy_result: Dict) -> Dict:
    """
    Format discrepancy results for easy UI table rendering.
    
    Returns:
        Dict with 'skill_table' and 'discrepancy_table' ready for display
    """
    skill_table = {
        "headers": ["Skill", "Resume", "LinkedIn", "Portfolio"],
        "rows": []
    }
    
    for skill in discrepancy_result.get("skill_comparison", []):
        skill_table["rows"].append([
            skill.get("skill", ""),
            "✓" if skill.get("in_resume") else "✗",
            "✓" if skill.get("in_linkedin") else "✗",
            "✓" if skill.get("in_portfolio") else "✗"
        ])
    
    discrepancy_table = {
        "headers": ["Field", "Resume", "LinkedIn", "Portfolio", "Issue", "Severity"],
        "rows": []
    }
    
    for d in discrepancy_result.get("discrepancies", []):
        discrepancy_table["rows"].append([
            d.get("field", ""),
            d.get("resume", "-"),
            d.get("linkedin", "-"),
            d.get("portfolio", "-"),
            d.get("issue", ""),
            d.get("severity", "low")
        ])
    
    return {
        "skill_table": skill_table,
        "discrepancy_table": discrepancy_table,
        "consistency_score": discrepancy_result.get("consistency_score", 100),
        "missing_in_resume": discrepancy_result.get("missing_in_resume", []),
        "missing_online": discrepancy_result.get("missing_online", []),
        "recommendations": discrepancy_result.get("recommendations", [])
    }
