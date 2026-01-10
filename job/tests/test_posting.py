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
    Senior Software Engineer at Stripe
    
    About Stripe:
    Stripe is a technology company that builds economic infrastructure for the internet.
    Millions of companies use our software to accept payments and manage their businesses online.
    
    About the Role:
    We're looking for a Senior Software Engineer to join our Payments team. You'll be building
    scalable systems that process billions of dollars in transactions.
    
    Location: San Francisco, CA (Hybrid - 3 days in office)
    
    What you'll do:
    - Design and build high-performance payment processing systems
    - Lead technical projects from conception to deployment
    - Mentor junior engineers and contribute to team culture
    - Collaborate with product and design teams
    
    Requirements:
    - 5+ years of software engineering experience
    - Strong proficiency in one or more: Ruby, Go, Java, Python
    - Experience with distributed systems at scale
    - BS/MS in Computer Science or equivalent
    
    Nice to have:
    - Experience with payment systems or fintech
    - Contributions to open source projects
    - Experience with Kubernetes and AWS
    
    Benefits:
    - Competitive salary ($180k - $250k)
    - Equity compensation
    - Health, dental, and vision insurance
    - 401(k) with matching
    - Unlimited PTO
    - Learning and development budget
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
