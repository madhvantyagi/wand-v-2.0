# Wand - AI-Powered Intelligence Extraction

Two powerful modules for extracting structured data from unstructured sources using AI.

---

## What We've Built

### 1. **Job Intelligence Scraper** (`job/`)

3-phase system that extracts comprehensive company intelligence:

**Phase 1: Job Postings** → Tech stack, salaries, benefits, contacts  
**Phase 2: Company Website** → Mission, values, products, culture  
**Phase 3: News** → Recent headlines and announcements

**Total Cost**: ~$0.02 per company (2 AI calls)

---

### 2. **Profile Extractor** (`profile/`)

AI-powered resume and portfolio parser:

Converts PDF/HTML documents into structured JSON with complete information extraction.

**Total Cost**: ~$0.01 per document (1 AI call)

---

## Quick Start

### Installation

```bash
# Clone or navigate to project
cd wand

# Install dependencies
pip install -r requirements.txt

# Set API key
echo "DEEPSEEK_API_KEY=your_key_here" > .env
```

### Job Intelligence

```python
from job.phases import get_salary_and_stack, get_company_info, get_news_signals

# Phase 1: Job postings
jobs = get_salary_and_stack("Google")
print(jobs['phase_1_results']['derived_intelligence']['tech_stack'])

# Phase 2: Company website
company = get_company_info("Google")
print(company['mission'])
print(company['values_implicit'])

# Phase 3: News
news = get_news_signals("Google")
print(news['news'])
```

### Profile Extraction

```python
from profile import parse_profile
import json

# Extract from resume
result = parse_profile("resume.pdf", "pdf")
data = json.loads(result)

print(data['personal_info']['name'])
print(data['work_experience'])
print(data['skills'])
```

---

## Project Structure

```
wand/
├── job/                      # Job Intelligence Scraper
│   ├── phases/
│   │   ├── phase1_jobs.py   # Job postings → Tech, salaries, benefits
│   │   ├── phase2_company.py # Website → Mission, values, products
│   │   └── phase3_news.py    # News → Headlines
│   ├── tests/
│   │   ├── test_phase1.py
│   │   ├── test_phase2.py
│   │   └── test_phase3.py
│   └── README.md             # Detailed job/ documentation
│
├── profile/                  # Profile Extractor
│   ├── extractor.py         # Main extraction logic
│   ├── tests/
│   │   ├── test_extractor.py
│   │   ├── resume.pdf
│   │   ├── linkedin.pdf
│   │   └── index.html
│   └── README.md             # Detailed profile/ documentation
│
├── models/                   # Centralized LLM clients
│   ├── llm.py               # DeepSeek & Gemini clients
│   └── __init__.py
│
├── requirements.txt          # All dependencies
├── .env                      # API keys
└── README.md                 # This file
```

---

## Cost Breakdown

### Job Intelligence (per company)
| Phase | AI Calls | HTTP Calls | Cost |
|-------|----------|------------|------|
| Phase 1: Jobs | 1 DeepSeek | ~5 | ~$0.01 |
| Phase 2: Website | 1 DeepSeek | ~8 | ~$0.01 |
| Phase 3: News | 0 | 1 | Free |
| **Total** | **2** | **~14** | **~$0.02** |

### Profile Extraction (per document)
| Task | AI Calls | Cost |
|------|----------|------|
| Parse PDF/HTML | 1 DeepSeek | ~$0.01 |

**DeepSeek Pricing**: ~$0.14 per 1M input tokens, ~$0.28 per 1M output tokens

---

## Technology Stack

### Core AI
- **DeepSeek-V3** - Primary LLM for all extraction
- **Instructor** - Structured LLM outputs
- **Pydantic** - Data validation

### Job Intelligence
- **python-jobspy** - Job board scraping (LinkedIn, Indeed, Glassdoor)
- **BeautifulSoup4** - HTML parsing (websites, news)
- **Requests** - HTTP requests
- **Pandas** - Data processing

### Profile Extraction
- **PyMuPDF** - PDF text extraction
- **Trafilatura** - HTML content extraction

---

## Key Features

### Job Intelligence
✅ **Batch Processing** - Processes 50 jobs in 1 API call  
✅ **Implicit Values** - AI infers company values from culture  
✅ **Tech Stack** - Extracted from both job descriptions AND engineering blogs  
✅ **Auto-Discovery** - Automatically finds company websites  
✅ **No Categorization Needed** - AI handles all categorization

### Profile Extraction
✅ **Comprehensive** - Extracts ALL information, not just predefined fields  
✅ **Flexible** - Adapts to any resume/portfolio format  
✅ **Multi-Format** - Supports PDF and HTML  
✅ **Structured Output** - Clean JSON output

---

## API Keys Required

**DeepSeek API Key** (Required for both modules):
1. Get free key at [platform.deepseek.com](https://platform.deepseek.com)
2. Set in `.env`: `DEEPSEEK_API_KEY=your_key`

**No other API keys needed** - Job scraping uses free sources.

---

## Testing

```bash
# Job Intelligence
python -m job.tests.test_phase1    # Test job scraping
python -m job.tests.test_phase2    # Test website extraction
python -m job.tests.test_phase3    # Test news scraping

# Profile Extraction
python -m profile.tests.test_extractor
```

---

## Use Cases

### Job Intelligence
- 🔍 Research companies before interviews
- 💰 Find salary ranges for specific companies
- 📊 Track hiring activity and tech stack trends
- 🏢 Competitive intelligence gathering
- 📰 Monitor company news and growth

### Profile Extraction
- 📄 Parse hundreds of resumes automatically
- 🔗 Convert LinkedIn profiles to structured data
- 🌐 Extract portfolio information for analysis
- 🗄️ Build candidate databases from unstructured documents
- 🤖 Automate resume screening

---

## Documentation

- **[Job Intelligence README](job/README.md)** - Detailed job/ documentation
- **[Profile Extractor README](profile/README.md)** - Detailed profile/ documentation

Each module README contains:
1. Functionality, inputs, outputs, methodology
2. Costing breakdown (AI calls, HTTP calls)
3. Libraries used for each feature

---

## License

MIT
