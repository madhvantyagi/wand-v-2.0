"""
Test Profile Discrepancy Detector
Uses actual parsed profile JSON files from profile_extractor/tests/
"""

import json
import os
from engine.discrepancy import compare_profile_sources, format_for_table


def load_test_profiles():
    """Load the actual test profile JSON files."""
    test_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'profile_extractor', 'tests')
    
    profiles = {}
    
    # Load resume
    resume_path = os.path.join(test_dir, 'output_resume.json')
    if os.path.exists(resume_path):
        with open(resume_path, 'r') as f:
            profiles['resume'] = json.load(f)
        print(f"✓ Loaded resume from {resume_path}")
    
    # Load LinkedIn
    linkedin_path = os.path.join(test_dir, 'output_linkedin.json')
    if os.path.exists(linkedin_path):
        with open(linkedin_path, 'r') as f:
            profiles['linkedin'] = json.load(f)
        print(f"✓ Loaded LinkedIn from {linkedin_path}")
    
    # Load portfolio
    portfolio_path = os.path.join(test_dir, 'output_portfolio.json')
    if os.path.exists(portfolio_path):
        with open(portfolio_path, 'r') as f:
            profiles['portfolio'] = json.load(f)
        print(f"✓ Loaded portfolio from {portfolio_path}")
    
    return profiles


def test_discrepancy():
    """Test discrepancy detection with actual profile data."""
    print(f"\n{'='*70}")
    print("Testing Profile Discrepancy Detector")
    print(f"{'='*70}\n")
    
    # Load actual test profiles
    profiles = load_test_profiles()
    
    if len(profiles) < 2:
        print("⚠ Need at least 2 profile files. Available:", list(profiles.keys()))
        return None
    
    print(f"\n📄 Comparing {len(profiles)} profiles: {list(profiles.keys())}")
    
    # Analyze discrepancies
    result = compare_profile_sources(
        resume=profiles.get('resume'),
        linkedin=profiles.get('linkedin'),
        portfolio=profiles.get('portfolio')
    )
    
    # Print results
    print(f"\n{'='*70}")
    print("DISCREPANCY RESULTS")
    print(f"{'='*70}\n")
    
    if 'error' in result:
        print(f"⚠ Error: {result['error']}")
        return result
    
    print(f"📊 Consistency Score: {result.get('consistency_score', 0)}%\n")
    
    # Discrepancies
    discrepancies = result.get('discrepancies', [])
    if discrepancies:
        print(f"⚠ Discrepancies Found ({len(discrepancies)}):")
        for d in discrepancies:
            print(f"\n  📌 {d.get('field', 'Unknown')} [{d.get('severity', 'low').upper()}]")
            print(f"     Resume: {d.get('resume', '-')}")
            print(f"     LinkedIn: {d.get('linkedin', '-')}")
            print(f"     Portfolio: {d.get('portfolio', '-')}")
            print(f"     Issue: {d.get('issue', '')}")
    else:
        print("✅ No major discrepancies found!")
    
    # Skill comparison
    skills = result.get('skill_comparison', [])
    if skills:
        print(f"\n\n💡 Skill Comparison:")
        print(f"{'Skill':<25} {'Resume':<10} {'LinkedIn':<10} {'Portfolio':<10}")
        print("-" * 55)
        for s in skills[:15]:
            r = "✓" if s.get('in_resume') else "✗"
            l = "✓" if s.get('in_linkedin') else "✗"
            p = "✓" if s.get('in_portfolio') else "✗"
            print(f"{s.get('skill', ''):<25} {r:<10} {l:<10} {p:<10}")
    
    # Missing items
    missing_resume = result.get('missing_in_resume', [])
    if missing_resume:
        print(f"\n📝 Missing in Resume (consider adding):")
        for item in missing_resume:
            print(f"  • {item}")
    
    missing_online = result.get('missing_online', [])
    if missing_online:
        print(f"\n🌐 Missing from Online Presence:")
        for item in missing_online:
            print(f"  • {item}")
    
    # Recommendations
    recs = result.get('recommendations', [])
    if recs:
        print(f"\n💡 Recommendations:")
        for rec in recs:
            print(f"  • {rec}")
    
    # Format for table (UI)
    table_data = format_for_table(result)
    
    # Save outputs
    output_dir = os.path.dirname(__file__)
    
    with open(os.path.join(output_dir, 'discrepancy_result.json'), 'w') as f:
        json.dump(result, f, indent=2)
    
    with open(os.path.join(output_dir, 'discrepancy_table.json'), 'w') as f:
        json.dump(table_data, f, indent=2)
    
    print(f"\n💾 Saved to: discrepancy_result.json, discrepancy_table.json")
    print(f"\n{'='*70}\n")
    
    return result


if __name__ == "__main__":
    test_discrepancy()
