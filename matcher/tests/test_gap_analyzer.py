"""
Test Gap Analyzer
Uses actual parsed profile and job JSON files
"""

import json
import os
from matcher import analyze_gaps, analyze_resume_gaps, analyze_online_presence_gaps


def load_test_data():
    """Load actual test JSON files."""
    test_dir = os.path.dirname(__file__)
    data = {}
    
    # Load profiles
    files = {
        'resume': 'output_resume.json',
        'linkedin': 'output_linkedin.json',
        'portfolio': 'output_portfolio.json',
        'job_posting': 'posting_test.json',
        'company': 'hudson_river_trading_full.json'
    }
    
    for key, filename in files.items():
        path = os.path.join(test_dir, filename)
        if os.path.exists(path):
            with open(path, 'r') as f:
                data[key] = json.load(f)
            print(f"✓ Loaded {filename}")
    
    return data


def test_gap_analyzer():
    """Test gap analysis with actual data."""
    print(f"\n{'='*70}")
    print("Testing Gap Analyzer")
    print(f"{'='*70}\n")
    
    # Load actual test data
    data = load_test_data()
    
    if 'job_posting' not in data:
        print("⚠ No job posting data found")
        return None
    
    job_data = data['job_posting']
    
    # Test 1: All sources gap analysis
    print(f"\n{'='*70}")
    print("Test 1: Full Gap Analysis (All Sources)")
    print(f"{'='*70}\n")
    
    result = analyze_gaps(
        job_data,
        resume=data.get('resume'),
        linkedin=data.get('linkedin'),
        portfolio=data.get('portfolio')
    )
    
    print_results(result)
    
    # Save result
    with open(os.path.join(os.path.dirname(__file__), 'gap_analysis_result.json'), 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\n💾 Saved to: gap_analysis_result.json")
    
    # Test 2: Resume-only gap analysis
    if 'resume' in data:
        print(f"\n{'='*70}")
        print("Test 2: Resume-Only Gap Analysis")
        print(f"{'='*70}\n")
        
        resume_result = analyze_resume_gaps(data['resume'], job_data)
        print(f"📊 Match Score: {resume_result.get('match_score', 0)}%")
    
    return result


def print_results(result):
    """Print formatted results."""
    if 'error' in result:
        print(f"⚠ Error: {result['error']}")
        return
    
    print(f"📊 Match Score: {result.get('match_score', 0)}%\n")
    
    # Technical Skills
    tech = result.get('technical_skills', {})
    print("💻 Technical Skills:")
    matched = tech.get('matched', [])
    if matched:
        print(f"  ✅ Matched: {', '.join(matched[:8])}")
    missing_req = tech.get('missing_required', [])
    if missing_req:
        print(f"  ❌ Missing Required: {', '.join(missing_req)}")
    missing_pref = tech.get('missing_preferred', [])
    if missing_pref:
        print(f"  ⚠ Missing Preferred: {', '.join(missing_pref)}")
    
    # Qualifications
    qual = result.get('qualifications', {})
    print(f"\n📋 Qualifications:")
    req_matched = qual.get('required_matched', [])
    if req_matched:
        print(f"  ✅ Required Met: {len(req_matched)} items")
        for q in req_matched[:3]:
            print(f"     • {q[:60]}...")
    req_missing = qual.get('required_missing', [])
    if req_missing:
        print(f"  ❌ Required Missing: {len(req_missing)} items")
        for q in req_missing[:3]:
            print(f"     • {q[:60]}...")
    
    # Soft Skills
    soft = result.get('soft_skills', {})
    print(f"\n🤝 Soft Skills:")
    impl_matched = soft.get('implicit_matched', [])
    if impl_matched:
        print(f"  ✅ Implicit Matched: {', '.join(impl_matched[:5])}")
    impl_missing = soft.get('implicit_missing', [])
    if impl_missing:
        print(f"  ❌ Implicit Missing: {', '.join(impl_missing[:5])}")
    
    # Experience gap
    exp_gap = result.get('experience_gap', '')
    if exp_gap:
        print(f"\n📈 Experience Gap: {exp_gap}")
    
    # Recommendations
    recs = result.get('recommendations', [])
    if recs:
        print(f"\n💡 Recommendations:")
        for rec in recs:
            print(f"  • {rec}")


if __name__ == "__main__":
    test_gap_analyzer()
