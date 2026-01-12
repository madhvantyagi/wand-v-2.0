# Wand API Documentation

> **Base URL**: `http://localhost:8000`  
> **Auth**: All endpoints require `X-User-Id` header

---

## Quick Start

```bash
# Start the API
cd wand
uvicorn api.main:app --reload

# Docs available at
http://localhost:8000/docs
```

---

## Authentication

All endpoints require the `X-User-Id` header:
```
X-User-Id: <uuid>
```

Create a user first via `POST /user/` if needed.

---

## API Endpoints Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/profile/resume` | POST | Upload and parse resume (PDF) |
| `/profile/linkedin` | POST | Upload and parse LinkedIn export (PDF) |
| `/profile/portfolio` | POST | Upload and parse portfolio (HTML) |
| `/profile/{type}` | GET | Get parsed profile by type |
| `/profile/` | GET | List all profiles |
| `/job/posting` | POST | Parse job posting text |
| `/job/company` | POST | Extract company intelligence |
| `/job/{id}` | GET | Get saved job by ID |
| `/job/` | GET | List all saved jobs |
| `/match/gaps` | POST | Analyze gaps between profile and job |
| `/match/cover-letter` | POST | Generate cover letter |

---

## Profiles

### Upload Resume
```bash
POST /profile/resume
Content-Type: multipart/form-data
```

**Request:**
```bash
curl -X POST 'http://localhost:8000/profile/resume' \
  -H 'X-User-Id: <user-id>' \
  -F 'file=@resume.pdf;type=application/pdf'
```

**Response:**
```json
{
  "id": "1642dfa7-afdf-4a73-ba97-5d72068e6272",
  "user_id": "4a9e666c-2bd9-44fc-85f1-1a72a2d331a9",
  "source_type": "resume",
  "file_name": "resume.pdf",
  "parsed_data": {
    "personal_info": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "(555) 123-4567",
      "location": "New York, NY",
      "linkedin": "linkedin.com/in/johndoe",
      "github": "github.com/johndoe"
    },
    "about": "Software engineer with 5 years experience...",
    "technical_skills": {
      "programming_languages": ["Python", "Java", "C++"],
      "web_and_backend": ["FastAPI", "Django", "Node.js"],
      "cloud_and_devops": ["AWS", "Docker", "Kubernetes"],
      "databases_and_storage": ["PostgreSQL", "MongoDB", "Redis"]
    },
    "education": [...],
    "work_experience": [...],
    "projects": [...]
  },
  "created_at": "2026-01-11T20:13:35.144990"
}
```

---

### Upload LinkedIn
```bash
POST /profile/linkedin
Content-Type: multipart/form-data
```

**Request:**
```bash
curl -X POST 'http://localhost:8000/profile/linkedin' \
  -H 'X-User-Id: <user-id>' \
  -F 'file=@Profile.pdf;type=application/pdf'
```

**Response:** Same structure as resume with LinkedIn-specific fields like `summary`, `certifications`, `languages`.

---

### Upload Portfolio
```bash
POST /profile/portfolio
Content-Type: multipart/form-data
```

**Request:**
```bash
curl -X POST 'http://localhost:8000/profile/portfolio' \
  -H 'X-User-Id: <user-id>' \
  -F 'file=@index.html;type=text/html'
```

**Response:** Same structure with portfolio-specific fields like `research`, `projects_and_publications`, `teaching_and_technical_leadership`.

---

### Get Profile by Type
```bash
GET /profile/{type}
```
Where `type` is: `resume`, `linkedin`, or `portfolio`

---

### List All Profiles
```bash
GET /profile/
```

Returns array of all uploaded profiles for the user.

---

## Jobs

### Parse Job Posting
```bash
POST /job/posting
Content-Type: application/json
```

**Request:**
```json
{
  "job_text": "As a Software Engineer at Company X...",
  "job_title": "Software Engineer",      // optional
  "company_name": "Company X"            // optional
}
```

> **Note**: `job_text` is required. The API will extract `job_title` and `company_name` from the text if not provided.

**Response:**
```json
{
  "id": "e095ffbc-554a-4c94-9e61-774a7c4b78cd",
  "user_id": "4a9e666c-2bd9-44fc-85f1-1a72a2d331a9",
  "job_title": "Software Engineer",
  "company_name": "Hudson River Trading (HRT)",
  "parsed_data": {
    "company_name": "Hudson River Trading (HRT)",
    "about_company": "...",
    "job_title": "Software Engineer",
    "job_description": "...",
    "location": "",
    "remote_policy": "",
    "required_qualifications": [...],
    "preferred_qualifications": [...],
    "technical_skills": ["C++", "Python", "Linux", ...],
    "soft_skills_explicit": [...],
    "soft_skills_implicit": [...],
    "salary_range": {
      "min": 300000,
      "max": null,
      "currency": "USD"
    },
    "benefits": [...],
    "experience_level": "Entry",
    "team_info": "..."
  },
  "created_at": "2026-01-11T20:24:37.400159"
}
```

---

### Extract Company Intelligence
```bash
POST /job/company
Content-Type: application/json
```

**Request:**
```json
{
  "company_name": "Hudson River Trading",
  "max_jobs": 50,
  "include_website": true,
  "include_news": true
}
```

**Response:**
```json
{
  "source": "fresh",
  "company": "Hudson River Trading",
  "intelligence": {
    "company": "Hudson River Trading",
    "jobs": {
      "tech_stack": ["C++", "Python", "AI"],
      "hiring_tempo": "Urgent (Posted 1 days ago)",
      "active_roles": 15,
      "raw_listings": [
        {
          "title": "Software Engineer",
          "url": "https://linkedin.com/jobs/view/...",
          "days_old": 1
        }
      ]
    },
    "website": {
      "mission": "...",
      "values_explicit": ["Kindness", "Excellence"],
      "values_implicit": ["Innovation", "Collaboration"],
      "products": [...],
      "culture": [...],
      "tech_stack": ["Python", "C++"],
      "company_info": {
        "size": "1000+",
        "industry": "Quantitative Trading",
        "founded": "2002"
      },
      "website_url": "https://www.hudsonrivertrading.com"
    },
    "news": {
      "headlines": [...],
      "count": 0
    }
  }
}
```

---

### Get Job by ID
```bash
GET /job/{job_id}
```

---

### List All Jobs
```bash
GET /job/
```

---

## Matching

### Analyze Gaps
```bash
POST /match/gaps
Content-Type: application/json
```

**Request:**
```json
{
  "profile_ids": ["1642dfa7-afdf-4a73-ba97-5d72068e6272"],
  "job_id": "e095ffbc-554a-4c94-9e61-774a7c4b78cd"
}
```

> **Note**: `profile_ids` can include 1-3 profiles (resume, linkedin, portfolio)

**Response:**
```json
{
  "id": "1cc3d1f6-05c2-47a6-b30e-6d3a71c9c6a0",
  "job_id": "e095ffbc-554a-4c94-9e61-774a7c4b78cd",
  "match_score": 45,
  "analysis_data": {
    "match_score": 45,
    "technical_skills": {
      "matched": ["Python", "UNIX/Linux"],
      "missing_required": ["C/C++", "Network communication"],
      "missing_preferred": []
    },
    "qualifications": {
      "required_matched": [...],
      "required_missing": [...],
      "preferred_matched": [...],
      "preferred_missing": [...]
    },
    "soft_skills": {
      "explicit_matched": [...],
      "explicit_missing": [...],
      "implicit_matched": [...],
      "implicit_missing": []
    },
    "experience_gap": "Candidate has strong entrepreneurial experience but lacks specific low-level systems expertise...",
    "recommendations": [
      "Develop C/C++ proficiency...",
      "Gain hands-on experience with system performance...",
      "Highlight coding passion more explicitly..."
    ]
  },
  "created_at": "2026-01-11T20:30:20.495017"
}
```

---

### Generate Cover Letter
```bash
POST /match/cover-letter
Content-Type: application/json
```

**Request:**
```json
{
  "profile_ids": ["1642dfa7-afdf-4a73-ba97-5d72068e6272"],
  "job_id": "e095ffbc-554a-4c94-9e61-774a7c4b78cd",
  "style": "professional"
}
```

**Style options:** `professional`, `enthusiastic`, `concise`

**Response:**
```json
{
  "id": "abc123",
  "job_id": "e095ffbc-554a-4c94-9e61-774a7c4b78cd",
  "style": "professional",
  "letter": "Dear Hiring Manager,\n\nI am writing to express my strong interest in...",
  "letter_metadata": {
    "key_points_highlighted": [...],
    "gaps_addressed": [...],
    "word_count": 350
  },
  "created_at": "2026-01-11T20:35:00.000000"
}
```

---

## Frontend Integration Guide

### Workflow

```
1. User uploads profiles (resume, linkedin, portfolio)
   └── POST /profile/{type}

2. User pastes job description
   └── POST /job/posting → returns job_id

3. User requests gap analysis  
   └── POST /match/gaps { profile_ids, job_id }

4. Display results:
   - Match percentage
   - Skills comparison tables
   - Recommendations

5. User generates cover letter
   └── POST /match/cover-letter { profile_ids, job_id, style }
```

### Page: Analyze (Dashboard)

**Inputs:**
- Job description textarea
- Company name input (optional)

**API Calls:**
1. `POST /job/posting` - Parse job
2. `POST /job/company` - Get company intelligence
3. `POST /match/gaps` - Analyze match

**Outputs to Display:**
- `match_score` - Percentage badge
- `technical_skills.matched` / `missing_required` - Skills table
- `soft_skills.explicit_matched` / `implicit_matched` - Soft skills table
- `recommendations` - Actionable list
- `company.intelligence.website` - Company info card
- `company.intelligence.news` - News section

---

### Page: Jobs

**API Calls:**
- `GET /job/` - List all jobs
- `GET /job/{id}` - Get specific job details
- `DELETE /job/{id}` - Delete job (if implemented)

**Display:**
- Job cards with title, company, match score, date
- Click → show full analysis

---

### Page: Cover Letter

**Inputs:**
- Theme selector (professional/enthusiastic/concise)
- Custom instructions textarea

**API Call:**
- `POST /match/cover-letter`

---

### Page: Profiles

**API Calls:**
- `GET /profile/` - List all profiles
- `POST /profile/{type}` - Upload new
- `DELETE /profile/{id}` - Delete (if implemented)

---

## Error Handling

All errors return JSON:
```json
{
  "detail": "Error message here"
}
```

| Status | Meaning |
|--------|---------|
| 400 | Bad request / validation error |
| 404 | Resource not found |
| 500 | Server error / LLM failure |

---

## Database Schema

| Table | Key Fields |
|-------|------------|
| `users` | id, email, name |
| `profiles` | id, user_id, source_type, parsed_data |
| `jobs` | id, user_id, job_title, company_name, parsed_data |
| `gap_analyses` | id, user_id, job_id, profile_ids, match_score, analysis_data |
| `cover_letters` | id, user_id, job_id, style, letter, letter_metadata |
| `companies` | id, name, website, intelligence (cached) |

---

## Environment Variables

```env
DATABASE_URL=sqlite+aiosqlite:///./wand.db  # or PostgreSQL for production
OPENAI_API_KEY=sk-...
```
