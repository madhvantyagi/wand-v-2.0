# Job Intelligence Scraper

Extract comprehensive company intelligence from job postings, websites, and news.

## Overview

3-phase system that gathers company data from multiple sources:
- **Phase 1**: Job postings (tech stack, salaries, benefits)
- **Phase 2**: Company website (mission, values, products)
- **Phase 3**: Recent news (headlines, announcements)

---

## Phase 1: Job Postings Intelligence

### Functionality
Scrapes job postings from LinkedIn, Indeed, and Glassdoor to extract company intelligence.

### Input
```python
from job.phases import get_salary_and_stack

result = get_salary_and_stack("Google")
```

**Parameters**:
- `company_name` (string): Company to research

### Output
```json
{
  "phase_1_results": {
    "company": "Google",
    "active_role_count": 50,
    "primary_source": "LinkedIn/Indeed",
    "derived_intelligence": {
      "tech_stack": ["Python", "Java", "Kubernetes", "AWS"],
      "salary_range": {
        "min": 150000,
        "max": 200000,
        "currency": "USD",
        "source": "Job Board Data"
      },
      "culture_signals": {
        "benefits": ["Health Insurance", "401k", "Remote Culture"],
        "hiring_tempo": "Active (Posted 5 days ago)"
      },
      "recruiter_contacts": ["careers@google.com"]
    },
    "raw_listings": [...]
  }
}
```

### Methodology
1. **Job Fetching**: Uses `jobspy` to scrape 50 job postings (30-day filter)
2. **Tech Role Filtering**: Filters for tech roles (engineer, developer, architect, etc.)
3. **Batch AI Extraction**: Sends all jobs to DeepSeek in ONE API call
4. **Aggregation**: Combines results, ranks by frequency

### Costing
- **AI API Calls**: 1 DeepSeek call (batch processing all jobs)
- **Other API Calls**: ~3-5 HTTP requests to job boards (via jobspy)
- **Estimated Cost**: ~$0.01 per company (DeepSeek pricing)

### Libraries Used
- `python-jobspy` - Job board scraping
- `pandas` - Data processing
- `instructor` - LLM structured outputs
- `openai` - DeepSeek API client
- `pydantic` - Data validation
- `models.get_deepseek_client()` - Centralized LLM client

---

## Phase 2: Company Website Intelligence

### Functionality
Extracts mission, values, products, and tech stack from company websites.

### Input
```python
from job.phases import get_company_info

result = get_company_info("Stripe")
# Or with explicit website:
result = get_company_info("Stripe", website="https://stripe.com")
```

**Parameters**:
- `company_name` (string): Company to research
- `website` (string, optional): Company website URL (auto-discovered if not provided)

### Output
```json
{
  "mission": "Build financial infrastructure for the internet",
  "values_explicit": ["User-first", "Move fast"],
  "values_implicit": ["Innovation", "Technical Excellence", "Customer Focus"],
  "products": ["Payments", "Billing", "Connect", "Radar"],
  "culture": ["Remote-first", "Learning culture"],
  "tech_stack": ["Ruby", "Go", "React", "PostgreSQL"],
  "company_size": "1000+",
  "industry": "FinTech",
  "founded": "2010",
  "website": "https://stripe.com"
}
```

### Methodology
1. **Website Discovery**: Auto-discovers company website via heuristics + Google search
2. **Page Scraping**: Scrapes 5 key pages (homepage, about, careers, engineering, etc.)
3. **AI Extraction**: Sends all content to DeepSeek for structured extraction
4. **Implicit Values**: AI infers values from culture/messaging (not just explicit statements)

### Costing
- **AI API Calls**: 1 DeepSeek call
- **Other API Calls**: ~6-8 HTTP requests (website discovery + page scraping)
- **Estimated Cost**: ~$0.01 per company

### Libraries Used
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `instructor` - LLM structured outputs
- `openai` - DeepSeek API client
- `pydantic` - Data validation
- `models.get_deepseek_client()` - Centralized LLM client

---

## Phase 3: News & Social Signals

### Functionality
Scrapes recent company news from Google News.

### Input
```python
from job.phases import get_news_signals

result = get_news_signals("Stripe")
```

**Parameters**:
- `company_name` (string): Company to research

### Output
```json
{
  "news": [
    "Stripe launches new payment platform in Asia",
    "Stripe raises $600M in Series H funding",
    "Stripe partners with Amazon for checkout integration"
  ],
  "count": 20
}
```

### Methodology
1. **Google News Search**: Searches Google News for company
2. **Headline Extraction**: Extracts up to 20 recent headlines
3. **No AI Processing**: Returns raw headlines (no categorization)

### Costing
- **AI API Calls**: 0 (no AI used)
- **Other API Calls**: 1 HTTP request to Google News
- **Estimated Cost**: Free

### Libraries Used
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing

---

## Total Cost Per Company

**AI API Calls**: 2 DeepSeek calls (Phase 1 + Phase 2)  
**HTTP Requests**: ~10-15 total  
**Estimated Cost**: ~$0.02 per company

---

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from job.phases import get_salary_and_stack, get_company_info, get_news_signals

# Phase 1: Job intelligence
jobs = get_salary_and_stack("Google")

# Phase 2: Website intelligence
company = get_company_info("Google")

# Phase 3: News
news = get_news_signals("Google")
```

## Testing

```bash
# Test individual phases
python -m job.tests.test_phase1
python -m job.tests.test_phase2
python -m job.tests.test_phase3
```

## Configuration

Set DeepSeek API key in `.env`:
```
DEEPSEEK_API_KEY=your_key_here
```
