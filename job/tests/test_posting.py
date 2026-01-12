"""
Test Job Posting Parser
"""

import json
from job.sources.posting import parse_job_posting


def test_posting_parser():
    """Test single job posting extraction."""
    print(f"\n{'='*70}")
    print("Testing Job Posting Parser")
    print(f"{'='*70}\n")
    
    # Sample job posting
    sample_posting = """
    As a Software Engineer at Hudson River Trading (HRT), the code you write is our business. Our engineers create and maintain critical technology and infrastructure that is integral to the success of our trading. In this role, you will work closely with other engineers across the firm who design trading algorithms and monitor trading in an extremely fast-paced, real-time environment! We are looking for smart programmers who love to code, enjoy being challenged, and can thrive in an open and collaborative company culture.

Profile

In your spare time you: code, tinker, read, explore, break things, and have an insatiable curiosity for all things computer-related — you'll find like-minded people here
You are capable of working both independently, as well as part of a team and can analyze and fix problems quickly
You can look at code, figure out how it works, and identify how to make it better
You can describe software designs at a high level (the abstract interface), low level (step-by-step algorithm), and anywhere in between
You really like to work with people who push you to be better at what you do
Qualifications

You are a full-time undergraduate student studying computer science or a related field who is eligible for full-time roles in 2026.

Excellent design, debugging, and problem solving skills
Working experience with C/C++ or Python is required, as are good CS fundamentals
Knowledge of UNIX operating systems (we use Linux), system/processor performance, and network communication
Interest in low-level architecture, logic design, and/or verification is a plus
Annual base salary of $300,000. Pay (base and bonus) may vary depending on job-related skills and experience. A sign-on and discretionary performance bonus will be provided as part of the total compensation package, in addition to company-paid medical and/or other benefits.
    """
    
    print("🔍 Parsing job posting...")
    result = parse_job_posting(sample_posting)
    
    # Print results
    print(f"\n{'='*70}")
    print("RESULTS")
    print(f"{'='*70}\n")
    
    if 'error' in result:
        print(f"⚠ Error: {result['error']}")
    else:
        print(f"🏢 Company: {result.get('company_name', 'N/A')}")
        print(f"💼 Title: {result.get('job_title', 'N/A')}")
        print(f"📍 Location: {result.get('location', 'N/A')}")
        print(f"🏠 Remote: {result.get('remote_policy', 'N/A')}")
        print(f"📊 Level: {result.get('experience_level', 'N/A')}")
        
        print(f"\n🔧 Technical Skills:")
        for skill in result.get('technical_skills', []):
            print(f"  • {skill}")
        
        print(f"\n📝 Required Qualifications:")
        for qual in result.get('required_qualifications', [])[:5]:
            print(f"  • {qual}")
        
        print(f"\n🎯 Soft Skills (Explicit):")
        for skill in result.get('soft_skills_explicit', []):
            print(f"  • {skill}")
        
        print(f"\n🧠 Soft Skills (Inferred):")
        for skill in result.get('soft_skills_implicit', []):
            print(f"  • {skill}")
        
        print(f"\n🎁 Benefits:")
        for benefit in result.get('benefits', []):
            print(f"  • {benefit}")
    
    # Save to JSON
    with open('posting_test.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n💾 Saved to: posting_test.json")
    print(f"\n{'='*70}\n")
    
    return result


if __name__ == "__main__":
    test_posting_parser()
