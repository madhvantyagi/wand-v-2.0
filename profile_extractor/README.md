# Profile Extractor

AI-powered extraction of structured data from resumes, LinkedIn profiles, and portfolios.

## Overview

Converts unstructured documents (PDF/HTML) into comprehensive structured JSON using DeepSeek AI.

---

## Functionality

Extracts ALL information from profile documents:
- Personal information (name, contact, links)
- Work experience (positions, dates, responsibilities)
- Education (degrees, institutions, dates)
- Skills (technical and soft skills)
- Projects (descriptions, links, technologies)
- Certifications, awards, publications
- Languages, volunteer work, hobbies

---

## Input

```python
from profile import parse_profile

result = parse_profile("resume.pdf", "pdf")
# Or for HTML:
result = parse_profile("portfolio.html", "html")
```

**Parameters**:
- `file_path` (string): Path to the file (PDF or HTML)
- `file_type` (string): Either `"pdf"` or `"html"`
- `api_key` (string, optional): DeepSeek API key (or set `DEEPSEEK_API_KEY` env var)

---

## Output

```json
{
  "personal_info": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1-234-567-8900",
    "location": "New York, NY",
    "linkedin": "linkedin.com/in/johndoe",
    "github": "github.com/johndoe"
  },
  "work_experience": [
    {
      "title": "Senior Engineer",
      "organization": "Tech Corp",
      "location": "NY, USA",
      "dates": "2020-01 - Present",
      "responsibilities": ["Led team of 5", "Built scalable systems"]
    }
  ],
  "education": [
    {
      "institution": "MIT",
      "degree": "BS Computer Science",
      "year": "2019"
    }
  ],
  "skills": ["Python", "AWS", "React", "Leadership"],
  "projects": [
    {
      "name": "E-commerce Platform",
      "description": "Built scalable platform",
      "technologies": ["Node.js", "MongoDB"]
    }
  ],
  "certifications": ["AWS Certified Solutions Architect"],
  "languages": ["English (Native)", "Spanish (Fluent)"]
}
```

---

## Methodology

1. **Content Extraction**:
   - **PDF**: Uses `PyMuPDF` to extract text while preserving structure
   - **HTML**: Uses `Trafilatura` for clean content extraction

2. **AI Processing**:
   - Sends extracted text to DeepSeek-V3
   - AI organizes information into logical sections
   - Extracts ALL information comprehensively (not limited to predefined fields)

3. **Validation**:
   - `Pydantic` ensures valid JSON output
   - `Instructor` enforces structured responses

4. **Return**:
   - Complete structured data as JSON string

---

## Costing

**AI API Calls**: 1 DeepSeek call per document  
**Other API Calls**: 0 (local file processing)  
**Estimated Cost**: ~$0.005-0.01 per document (depending on length)

---

## Libraries Used

- `pymupdf` (fitz) - PDF text extraction
- `trafilatura` - HTML content extraction
- `instructor` - LLM structured outputs
- `openai` - DeepSeek API client
- `pydantic` - Data validation
- `python-dotenv` - Environment variables
- `models.get_deepseek_client()` - Centralized LLM client

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Setup

1. Get DeepSeek API key from [platform.deepseek.com](https://platform.deepseek.com)

2. Set environment variable:
```bash
export DEEPSEEK_API_KEY=your_api_key_here
```

Or create `.env` file:
```
DEEPSEEK_API_KEY=your_api_key_here
```

---

## Usage

```python
from profile import parse_profile
import json

# Extract from PDF resume
result = parse_profile("resume.pdf", "pdf")
data = json.loads(result)

# Extract from HTML portfolio
result = parse_profile("portfolio.html", "html")
data = json.loads(result)

# Access the data
print(data['personal_info']['name'])
print(data['work_experience'])
print(data['skills'])
```

---

## Testing

```bash
python -m profile.tests.test_extractor
```

Test files included:
- `resume.pdf` - Sample resume
- `linkedin.pdf` - LinkedIn profile export
- `index.html` - Portfolio website

---

## What Gets Extracted

The AI extracts **everything** from the document:
- ✅ Personal information (name, contact, links)
- ✅ Work experience (all positions, dates, responsibilities)
- ✅ Education (degrees, institutions, dates)
- ✅ Skills (technical and soft skills)
- ✅ Projects (descriptions, links, technologies)
- ✅ Certifications, awards, publications
- ✅ Languages, volunteer work, hobbies
- ✅ Any other information present

**No predefined fields** - the AI adapts to whatever is in the document.

---

## Error Handling

- Returns empty/partial data if extraction fails
- Handles malformed PDFs gracefully
- Validates all output with Pydantic schemas
