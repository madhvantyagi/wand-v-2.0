"""
Test Extractor - Main entry point for company intelligence
"""

import json
from job.extractor import extract_company_intelligence, extract_from_posting


def test_company_extraction(company_name: str):
    """Test full company extraction."""
    print(f"\n{'='*70}")
    print(f"Testing Company Extraction: {company_name}")
    print(f"{'='*70}\n")
    
    # Extract with all sources
    result = extract_company_intelligence(
        company_name,
        max_jobs=50,
        include_website=True,
        include_news=True
    )
    
    # Print results
    print(f"\n{'='*70}")
    print("EXTRACTION RESULTS")
    print(f"{'='*70}\n")
    
    # Jobs
    jobs = result.get('jobs', {})
    if jobs:
        print(f"💼 JOBS:")
        print(f"  Active Roles: {jobs.get('active_roles', 0)}")
        tech = jobs.get('tech_stack', [])
        if tech:
            print(f"  Tech Stack: {', '.join(tech[:10])}")
        salary = jobs.get('salary_range')
        if salary:
            print(f"  Salary: ${salary.get('min', 0):,} - ${salary.get('max', 0):,}")
        print()
    
    # Website
    website = result.get('website', {})
    if website:
        print(f"🌐 WEBSITE:")
        if website.get('mission'):
            print(f"  Mission: {website['mission'][:100]}...")
        values = website.get('values_implicit', [])
        if values:
            print(f"  Values (Inferred): {', '.join(values[:5])}")
        company_info = website.get('company_info', {})
        if company_info.get('size'):
            print(f"  Size: {company_info['size']}")
            print(f"  Industry: {company_info.get('industry', 'N/A')}")
        print()
    
    # News
    news = result.get('news', {})
    if news:
        headlines = news.get('headlines', [])
        print(f"📰 NEWS ({len(headlines)} articles):")
        for headline in headlines[:3]:
            print(f"  • {headline[:80]}...")
        print()
    
    # Metadata
    meta = result.get('metadata', {})
    print(f"📊 METADATA:")
    print(f"  Sources: {', '.join(meta.get('sources_used', []))}")
    print(f"  API Calls: {meta.get('api_calls', 0)}")
    errors = meta.get('errors', [])
    if errors:
        print(f"  Errors: {len(errors)}")
        for err in errors:
            print(f"    ⚠ {err}")
    
    # Save to JSON
    output_file = f"{company_name.lower().replace(' ', '_')}_full.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n💾 Saved to: {output_file}")
    print(f"\n{'='*70}\n")
    
    return result


def test_posting_extraction():
    """Test single job posting extraction."""
    print(f"\n{'='*70}")
    print("Testing Job Posting Extraction")
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
    
    result = extract_from_posting(sample_posting)
    
    # Print results
    print(f"\n{'='*70}")
    print("POSTING EXTRACTION RESULTS")
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
    # Test company extraction
    test_company_extraction("Hudson River Trading")
    
    # Test posting extraction
    # test_posting_extraction()
