"""
Test Phase 2: Company Website Intelligence
"""

import json
from job.sources.website import get_company_info


def test_phase2(company_name: str, website: str = None):
    """Test Phase 2 with a company."""
    print(f"\n{'='*70}")
    print(f"Testing Phase 2: {company_name}")
    print(f"{'='*70}\n")
    
    # Get company intelligence
    result = get_company_info(company_name, website)
    
    # Print results
    print(f"\n{'='*70}")
    print("PHASE 2 RESULTS")
    print(f"{'='*70}\n")
    
    print(f"🌐 Website: {result.get('website', 'N/A')}\n")
    
    # Mission
    mission = result.get('mission', '')
    if mission:
        print(f"🎯 Mission:")
        print(f"  {mission}\n")
    
    # Explicit Values
    values_explicit = result.get('values_explicit', [])
    if values_explicit:
        print(f"💎 Values (Explicit) ({len(values_explicit)}):")
        for value in values_explicit:
            print(f"  • {value}")
        print()
    
    # Implicit Values
    values_implicit = result.get('values_implicit', [])
    if values_implicit:
        print(f"🧠 Values (Inferred) ({len(values_implicit)}):")
        for value in values_implicit:
            print(f"  • {value}")
        print()
    
    # Products
    products = result.get('products', [])
    if products:
        print(f"📦 Products ({len(products)}):")
        for product in products[:7]:
            print(f"  • {product}")
        print()
    
    # Tech Stack
    tech_stack = result.get('tech_stack', [])
    if tech_stack:
        print(f"💻 Tech Stack ({len(tech_stack)}):")
        for tech in tech_stack[:10]:
            print(f"  • {tech}")
        print()
    
    # Company Info
    company_size = result.get('company_size', '')
    industry = result.get('industry', '')
    founded = result.get('founded', '')
    
    if company_size or industry or founded:
        print(f"🏢 Company Info:")
        if company_size:
            print(f"  Size: {company_size}")
        if industry:
            print(f"  Industry: {industry}")
        if founded:
            print(f"  Founded: {founded}")
        print()
    
    # Culture
    culture = result.get('culture', [])
    if culture:
        print(f"🌟 Culture:")
        for signal in culture:
            print(f"  • {signal}")
    
    # Save to JSON
    output_file = f"{company_name.lower().replace(' ', '_')}_phase2.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n💾 Saved to: {output_file}")
    print(f"\n{'='*70}\n")
    
    return result


if __name__ == "__main__":
    # Test with a company
    company = "Stripe"
    
    # Optional: provide website directly
    # website = "https://shipday.com"
    
    test_phase2(company)
