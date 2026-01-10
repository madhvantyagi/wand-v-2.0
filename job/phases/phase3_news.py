"""
Phase 3: News & Social Signals
Scrapes recent company news from Google News.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List


# ============================================================================
# NEWS SCRAPING
# ============================================================================

def scrape_google_news(company_name: str) -> List[str]:
    """
    Scrape recent news from Google News.
    
    Args:
        company_name: Name of the company
        
    Returns:
        List of news headlines
    """
    try:
        # Google News search URL
        search_query = f"{company_name} company news"
        url = f"https://www.google.com/search?q={search_query}&tbm=nws"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"  ⚠ Google News returned status {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract news headlines
        headlines = []
        
        # Try multiple selectors for Google News
        news_items = soup.find_all('div', class_='SoaBEf')
        
        if not news_items:
            # Fallback: try different selectors
            news_items = soup.find_all('div', {'role': 'heading'})
        
        for item in news_items[:20]:  # Limit to 20 articles
            text = item.get_text(strip=True)
            if text and len(text) > 20:  # Filter out short snippets
                headlines.append(text)
        
        if not headlines:
            print(f"  ⚠ No news found for {company_name}")
        
        return headlines
        
    except Exception as e:
        print(f"  ⚠ News scraping failed: {e}")
        return []


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def get_news_signals(company_name: str) -> Dict:
    """
    Phase 3: Scrape recent company news.
    
    Args:
        company_name: Name of the company
        
    Returns:
        Dict with news headlines
    """
    print(f"  📰 Phase 3: Gathering recent news...")
    
    # Scrape news
    headlines = scrape_google_news(company_name)
    
    if not headlines:
        print(f"  ⚠ No news data available")
        return {
            'news': [],
            'count': 0
        }
    
    print(f"  ✓ Phase 3 complete! Found {len(headlines)} articles")
    
    return {
        'news': headlines,
        'count': len(headlines)
    }
