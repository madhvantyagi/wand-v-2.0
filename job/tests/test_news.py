"""
Test Phase 3: News & Social Signals
"""

import json
from job.sources.news import get_news_signals


def test_phase3(company_name: str):
    """Test Phase 3 with a company."""
    print(f"\n{'='*70}")
    print(f"Testing Phase 3: {company_name}")
    print(f"{'='*70}\n")
    
    # Get news
    result = get_news_signals(company_name)
    
    # Print results
    print(f"\n{'='*70}")
    print("PHASE 3 RESULTS")
    print(f"{'='*70}\n")
    
    # News Headlines
    news = result.get('news', [])
    count = result.get('count', 0)
    
    if news:
        print(f"📰 Recent News ({count} articles):\n")
        for i, headline in enumerate(news, 1):
            print(f"{i}. {headline}")
    else:
        print("📰 No recent news found")
    
    # Save to JSON
    output_file = f"{company_name.lower().replace(' ', '_')}_phase3.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n💾 Saved to: {output_file}")
    print(f"\n{'='*70}\n")
    
    return result


if __name__ == "__main__":
    # Test with a company
    company = "Stripe"
    
    test_phase3(company)
