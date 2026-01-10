# Company Intel Scraper - Phase 1

Extract salary ranges and tech stack information from job postings using **python-jobspy**.

## Features

✅ **Salary Extraction**: Automatically detects salary ranges from job descriptions  
✅ **Tech Stack Analysis**: Identifies 70+ technologies across 8 categories  
✅ **Multi-Source**: Scrapes LinkedIn, Indeed, and Glassdoor  
✅ **Zero Cost**: Uses only free/open-source tools  

## Installation

```bash
pip install -r requirements_intel.txt
```

## Usage

### Basic Usage

```python
from company_intel import get_company_intelligence, save_intelligence

# Get intelligence for a company
intel = get_company_intelligence("Shipday")

# Save to JSON file
save_intelligence("Shipday", intel)
```

### Command Line

```bash
python company_intel.py
```

## Output Structure

```json
{
  "meta": {
    "company_name": "Shipday",
    "jobs_analyzed": 15,
    "status": "Success"
  },
  "intelligence": {
    "tech_stack": {
      "confirmed_in_jd": ["Java", "Spring Boot", "React", "AWS"],
      "occurrence_count": {
        "Java": 12,
        "Spring Boot": 10,
        "React": 8
      }
    }
  },
  "compensation": {
    "source": "Job Descriptions",
    "salary_range": "$120k - $160k",
    "currency": "USD",
    "sample_size": 5
  }
}
```

## Tech Categories Detected

- **Languages**: Python, Java, JavaScript, TypeScript, Go, Rust, etc.
- **Frontend**: React, Vue, Angular, Next.js, Svelte
- **Backend**: Node.js, Django, Flask, Spring Boot, FastAPI
- **Databases**: PostgreSQL, MongoDB, Redis, MySQL
- **Cloud**: AWS, Azure, GCP, Heroku, Vercel
- **DevOps**: Docker, Kubernetes, Jenkins, Terraform
- **AI/ML**: PyTorch, TensorFlow, LangChain, RAG
- **Tools**: Git, Jira, Figma, Postman

## How It Works

1. **Fetch Jobs**: Uses `python-jobspy` to scrape job postings from LinkedIn, Indeed, and Glassdoor
2. **Extract Salary**: Regex patterns detect salary ranges in multiple formats
3. **Analyze Tech Stack**: Searches for 70+ technology keywords in job descriptions
4. **Aggregate Results**: Counts occurrences and ranks technologies by frequency
5. **Output JSON**: Saves structured data to `{company}_intel.json`

## Limitations

- Requires active job postings (won't work for companies not hiring)
- Salary data depends on transparency in job descriptions
- Tech stack limited to predefined keywords (70+ technologies)

## Next Steps (Phase 2 & 3)

- [ ] Company values/mission scraping (Playwright)
- [ ] News feed integration (RSS)
- [ ] H1B salary data fallback
