"""
Test script for Phase 1: Job Analysis

Run this to test salary and tech stack extraction.
"""

import json
from engine.job.sources.jobs import get_salary_and_stack


def test_phase1(company_name: str):
    """Test Phase 1 with a company name."""
    print(f"\n{'='*70}")
    print(f"Testing Phase 1: {company_name}")
    print(f"{'='*70}\n")
    
    # Get comprehensive intelligence
    result = get_salary_and_stack(company_name)
    
    # Print results
    print(f"\n{'='*70}")
    print("PHASE 1 RESULTS")
    print(f"{'='*70}\n")
    
    phase1 = result.get('phase_1_results', {})
    intel = phase1.get('derived_intelligence', {})
    
    print(f"📊 Company: {phase1.get('company')}")
    print(f"📊 Active Roles: {phase1.get('active_role_count')}")
    print(f"📊 Source: {phase1.get('primary_source')}\n")
    
    # Tech Stack
    tech_stack = intel.get('tech_stack', [])
    if tech_stack:
        print(f"💻 Tech Stack ({len(tech_stack)} technologies):")
        for tech in tech_stack[:10]:
            print(f"  • {tech}")
    else:
        print("💻 Tech Stack: No data")
    
    # Salary
    salary = intel.get('salary_range')
    if salary:
        print(f"\n💰 Salary Range:")
        print(f"  ${salary['min']:,} - ${salary['max']:,} {salary['currency']}")
        print(f"  Source: {salary['source']}")
    else:
        print(f"\n💰 Salary Range: No data")
    
    # Culture Signals
    culture = intel.get('culture_signals', {})
    benefits = culture.get('benefits', [])
    if benefits:
        print(f"\n🎯 Culture & Benefits:")
        for benefit in benefits:
            print(f"  • {benefit}")
    print(f"  Hiring Tempo: {culture.get('hiring_tempo', 'Unknown')}")
    
    # Recruiter Contacts
    contacts = intel.get('recruiter_contacts', [])
    if contacts:
        print(f"\n📧 Recruiter Contacts:")
        for email in contacts[:5]:
            print(f"  • {email}")
    
    # Save to JSON
    output_file = f"{company_name.lower().replace(' ', '_')}_phase1.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n💾 Saved to: {output_file}")
    print(f"\n{'='*70}\n")
    
    return result


if __name__ == "__main__":
    # Test with a company
    company = "Google"  # Change this to test different companies
    
    test_phase1(company)
