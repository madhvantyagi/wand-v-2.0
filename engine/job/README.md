# Job Intelligence Extractor

Extract comprehensive company intelligence from job postings, websites, and news.

## Overview

Multi-source intelligence system with a single entry point:

```python
from job import extract_company_intelligence

result = extract_company_intelligence("Google")
```

---

## Directory Structure

```
job/
├── extractor.py          # Main entry point
├── sources/
│   ├── jobs.py          # Job postings intelligence
│   ├── website.py       # Company website intelligence
│   ├── news.py          # News scraping
│   └── posting.py       # Single job posting parser
├── tests/
│   ├── test_extractor.py
│   ├── test_jobs.py
│   ├── test_website.py
│   ├── test_news.py
│   └── test_posting.py
└── README.md
```

---

## Main Entry Point: `extractor.py`

### `extract_company_intelligence()`

Extract intelligence from all sources for a company.

**Input:**
```python
from job import extract_company_intelligence

result = extract_company_intelligence(
    company_name="Google",      # Required
    max_jobs=50,                # Max job postings to analyze
    include_website=True,       # Scrape company website
    include_news=True,          # Scrape news
    website_url=None            # Optional: provide website URL
)
```

**Output:**
```json
{
  "company": "Google",
  "jobs": {
    "tech_stack": ["Python", "Java", "Kubernetes"],
    "salary_range": {"min": 150000, "max": 200000},
    "benefits": ["Health Insurance", "401k"],
    "hiring_tempo": "Active",
    "recruiter_contacts": ["careers@google.com"],
    "active_roles": 50
  },
  "website": {
    "mission": "Organize the world's information...",
    "values_explicit": ["Innovation"],
    "values_implicit": ["Speed", "User Focus"],
    "products": ["Search", "Cloud", "Android"],
    "culture": ["Remote-friendly"],
    "tech_stack": ["Go", "Python"],
    "company_info": {"size": "1000+", "industry": "Tech"}
  },
  "news": {
    "headlines": ["Google launches new AI..."],
    "count": 20
  },
  "metadata": {
    "sources_used": ["jobs", "website", "news"],
    "api_calls": 2,
    "errors": []
  }
}
```

**Error Handling:** Each source runs independently. If one fails, others continue. Errors are logged in `metadata.errors`.

---

### `extract_from_posting()`

Parse a single job posting text.

**Input:**
```python
from job import extract_from_posting

posting = """
Senior Software Engineer at Stripe
Requirements: 5+ years Python...
"""

result = extract_from_posting(posting)
```

**Output:**
```json
{
  "company_name": "Stripe",
  "job_title": "Senior Software Engineer",
  "about_company": "Stripe is a technology company...",
  "job_description": "Build scalable payment systems...",
  "location": "San Francisco, CA",
  "remote_policy": "Hybrid",
  "required_qualifications": ["5+ years experience", "BS/MS CS"],
  "preferred_qualifications": ["Fintech experience"],
  "technical_skills": ["Python", "Ruby", "Go", "AWS"],
  "soft_skills_explicit": ["Strong communication"],
  "soft_skills_implicit": ["Leadership", "Collaboration"],
  "salary_range": {"min": 180000, "max": 250000},
  "benefits": ["Health insurance", "401k", "Equity"],
  "experience_level": "Senior"
}
```

---

## Individual Sources

### Source 1: Jobs (`sources/jobs.py`)

**Functionality:** Scrapes job postings from LinkedIn, Indeed, Glassdoor

**Methodology:**
1. Fetches up to 50 job postings via `jobspy`
2. Filters for tech roles
3. Batch processes ALL jobs in ONE AI call
4. Aggregates tech stack, salaries, benefits

**Costing:**
- AI Calls: 1 DeepSeek call
- HTTP Calls: ~5 (job board requests)
- Cost: ~$0.01

**Libraries:** `python-jobspy`, `pandas`, `instructor`, `pydantic`

---

### Source 2: Website (`sources/website.py`)

**Functionality:** Extracts company info from official website

**Methodology:**
1. Auto-discovers website (or uses provided URL)
2. Scrapes 5 key pages (about, careers, engineering, etc.)
3. AI extracts mission, values (explicit + implicit), products, tech stack

**Costing:**
- AI Calls: 1 DeepSeek call
- HTTP Calls: ~8 (website discovery + scraping)
- Cost: ~$0.01

**Libraries:** `requests`, `beautifulsoup4`, `instructor`, `pydantic`

---

### Source 3: News (`sources/news.py`)

**Functionality:** Scrapes recent company news

**Methodology:**
1. Searches Google News
2. Extracts headlines (no AI)

**Costing:**
- AI Calls: 0
- HTTP Calls: 1
- Cost: Free

**Libraries:** `requests`, `beautifulsoup4`

---

### Source 4: Posting (`sources/posting.py`)

**Functionality:** Parses single job posting text

**Methodology:**
1. Takes raw job posting text as input
2. AI extracts all structured information
3. Infers implicit soft skills from description

**Costing:**
- AI Calls: 1 DeepSeek call
- HTTP Calls: 0
- Cost: ~$0.005

**Libraries:** `instructor`, `pydantic`

---

## Total Cost Per Company

| Source | AI Calls | HTTP Calls | Cost |
|--------|----------|------------|------|
| Jobs | 1 | ~5 | ~$0.01 |
| Website | 1 | ~8 | ~$0.01 |
| News | 0 | 1 | Free |
| **Total** | **2** | **~14** | **~$0.02** |

---

## Testing

```bash
# Test main extractor
python -m job.tests.test_extractor

# Test individual sources
python -m job.tests.test_jobs
python -m job.tests.test_website
python -m job.tests.test_news
python -m job.tests.test_posting
```

---

## Configuration

Set DeepSeek API key in `.env`:
```
DEEPSEEK_API_KEY=your_key_here
```

---

## Standardized Variable Names

All outputs use consistent naming:
- `tech_stack` - Technologies
- `salary_range` - Compensation info
- `benefits` - Perks and benefits
- `values_explicit` - Stated values
- `values_implicit` - Inferred values
- `company_info` - Size, industry, founded
