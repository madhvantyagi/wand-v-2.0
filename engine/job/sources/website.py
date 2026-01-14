"""
Phase 2: Company Website Intelligence
Extracts mission, values, products, and culture from company websites.
"""

import os
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from engine.models import get_deepseek_client


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class CompanyIntelligence(BaseModel):
    """Intelligence extracted from company website."""
    mission: str = Field(
        default="",
        description="Company mission statement"
    )
    values_explicit: List[str] = Field(
        default_factory=list,
        description="Explicitly stated company values"
    )
    values_implicit: List[str] = Field(
        default_factory=list,
        description="Implicit values inferred from content, culture, and messaging"
    )
    products: List[str] = Field(
        default_factory=list,
        description="Main products or services"
    )
    culture_signals: List[str] = Field(
        default_factory=list,
        description="Work culture insights (e.g., Remote-first, Learning culture)"
    )
    tech_stack: List[str] = Field(
        default_factory=list,
        description="Technologies mentioned in engineering blogs, careers pages"
    )
    company_size: str = Field(
        default="",
        description="Company size (e.g., 'Startup', '100-500', '1000+', 'Enterprise')"
    )
    industry: str = Field(
        default="",
        description="Primary industry or sector"
    )
    founded: str = Field(
        default="",
        description="Year founded or founding information"
    )


# ============================================================================
# WEBSITE DISCOVERY
# ============================================================================

def discover_company_website(company_name: str) -> Optional[str]:
    """
    Discover company website using Google search.
    
    Args:
        company_name: Name of the company
        
    Returns:
        Company website URL or None
    """
    try:
        # Simple heuristic: try common patterns first
        common_domains = [
            f"https://www.{company_name.lower().replace(' ', '')}.com",
            f"https://{company_name.lower().replace(' ', '')}.com",
            f"https://www.{company_name.lower().replace(' ', '')}.io",
        ]
        
        for url in common_domains:
            try:
                response = requests.head(url, timeout=3, allow_redirects=True)
                if response.status_code == 200:
                    return url
            except:
                continue
        
        # If heuristics fail, use Google search
        search_url = f"https://www.google.com/search?q={company_name}+official+website"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(search_url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract first result link
        for link in soup.find_all('a'):
            href = link.get('href', '')
            if '/url?q=' in href and 'google.com' not in href:
                url = href.split('/url?q=')[1].split('&')[0]
                if url.startswith('http'):
                    return url
        
        return None
    except Exception as e:
        print(f"  ⚠ Website discovery failed: {e}")
        return None


# ============================================================================
# WEB SCRAPING
# ============================================================================

def scrape_company_pages(base_url: str) -> str:
    """
    Scrape key pages from company website.
    
    Args:
        base_url: Company website URL
        
    Returns:
        Combined text from all pages
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Pages to scrape
    page_paths = [
        '',  # Homepage
        '/about',
        '/about-us',
        '/mission',
        '/values',
        '/products',
        '/careers',
        '/culture',
        '/company',
    ]
    
    all_text = ""
    scraped_count = 0
    
    for path in page_paths:
        try:
            url = base_url.rstrip('/') + path
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer"]):
                    script.decompose()
                
                # Get text
                text = soup.get_text(separator=' ', strip=True)
                all_text += f"\n\n--- {path or 'Homepage'} ---\n{text[:2000]}"
                scraped_count += 1
                
                if scraped_count >= 3:  # Limit to 3 pages to avoid too much data
                    break
        except:
            continue
    
    return all_text[:10000]  # Limit total text


# ============================================================================
# AI EXTRACTION
# ============================================================================

def extract_company_intelligence_ai(website_text: str, company_name: str, api_key: str = None) -> CompanyIntelligence:
    """
    Extract company intelligence using DeepSeek AI.
    
    Args:
        website_text: Text scraped from company website
        company_name: Name of the company
        api_key: DeepSeek API key (optional)
        
    Returns:
        CompanyIntelligence object
    """
    if not website_text or len(website_text) < 100:
        return CompanyIntelligence()
    
    try:
        client = get_deepseek_client(api_key)
    except ValueError as e:
        print(f"  ⚠ {e}")
        return CompanyIntelligence()
    
    try:
        result = client.chat.completions.create(
            model="deepseek-chat",
            response_model=CompanyIntelligence,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are analyzing a company website. Extract comprehensive intelligence:\n\n"
                        "1. **mission**: Company mission statement (1-2 sentences)\n"
                        "2. **values_explicit**: Values explicitly stated on the website\n"
                        "3. **values_implicit**: Values you can INFER from their culture, messaging, and content "
                        "(e.g., if they emphasize 'move fast', infer 'Speed/Agility'; if they mention 'customer obsession', infer 'Customer Focus')\n"
                        "4. **products**: Main products or services\n"
                        "5. **culture_signals**: Work culture insights (Remote-first, Learning culture, Diversity focus, etc.)\n"
                        "6. **tech_stack**: Technologies mentioned in engineering blogs, careers pages, or tech content "
                        "(languages, frameworks, tools, platforms)\n"
                        "7. **company_size**: Estimate size from content (Startup, 100-500, 1000+, Enterprise)\n"
                        "8. **industry**: Primary industry or sector\n"
                        "9. **founded**: Year founded if mentioned\n\n"
                        "Be thoughtful about implicit values - read between the lines of their messaging and culture."
                    )
                },
                {
                    "role": "user",
                    "content": f"Company: {company_name}\n\nWebsite content:\n{website_text}"
                }
            ],
            temperature=0.0,
        )
        return result
    except Exception as e:
        print(f"  ⚠ AI extraction failed: {e}")
        return CompanyIntelligence()


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def get_company_info(company_name: str, website: str = None) -> Dict:
    """
    Phase 2: Extract company intelligence from website.
    
    Args:
        company_name: Name of the company
        website: Optional company website URL (auto-discovered if not provided)
        
    Returns:
        Dict with company intelligence
    """
    print(f"  🔍 Phase 2: Discovering company website...")
    
    # Discover website if not provided
    if not website:
        website = discover_company_website(company_name)
    
    if not website:
        print(f"  ⚠ Could not discover website for {company_name}")
        return {
            'mission': '',
            'values': [],
            'products': [],
            'culture': [],
            'website': ''
        }
    
    print(f"  ✓ Found website: {website}")
    print(f"  📄 Scraping company pages...")
    
    # Scrape website
    website_text = scrape_company_pages(website)
    
    if not website_text:
        print(f"  ⚠ Could not scrape website content")
        return {
            'mission': '',
            'values': [],
            'products': [],
            'culture': [],
            'website': website
        }
    
    print(f"  🤖 Analyzing with AI...")
    
    # Extract intelligence
    intel = extract_company_intelligence_ai(website_text, company_name)
    
    print(f"  ✓ Phase 2 complete!")
    
    return {
        'mission': intel.mission,
        'values_explicit': intel.values_explicit,
        'values_implicit': intel.values_implicit,
        'products': intel.products,
        'culture': intel.culture_signals,
        'tech_stack': intel.tech_stack,
        'company_size': intel.company_size,
        'industry': intel.industry,
        'founded': intel.founded,
        'website': website
    }
