# Matcher - Profile-Job Matching System

Match user profiles against job requirements and generate tailored cover letters.

## Overview

Two **independent** functions:
1. **Gap Analysis** - Find missing skills/qualifications
2. **Cover Letter** - Generate tailored cover letters

Each function takes pre-parsed data and uses **1 AI call**.

---

## Installation

Uses shared dependencies from root `requirements.txt`.

---

## Function 1: Gap Analysis

Compares user profile against job requirements.

### Usage
```python
from matcher import analyze_gaps

# Assuming you have parsed data
gaps = analyze_gaps(profile_data, job_data)
```

### Input
- `profile_data`: Dict from `profile.parse_profile()`
- `job_data`: Dict from `job.sources.posting.parse_job_posting()`

### Output
```json
{
  "match_score": 78,
  "technical_skills": {
    "matched": ["Python", "AWS"],
    "missing_required": ["Kubernetes", "Go"],
    "missing_preferred": ["Terraform"]
  },
  "qualifications": {
    "required_matched": ["5+ years", "BS in CS"],
    "required_missing": ["Distributed systems"],
    "preferred_matched": [],
    "preferred_missing": ["Fintech experience"]
  },
  "soft_skills": {
    "explicit_matched": ["Communication"],
    "explicit_missing": ["Mentorship"],
    "implicit_matched": ["Leadership (from 'led team')"],
    "implicit_missing": ["Cross-functional collaboration"]
  },
  "experience_gap": "Profile: 4 years, Required: 5+",
  "recommendations": [
    "Highlight Docker experience",
    "Mention Kubernetes learning",
    "Emphasize team leadership"
  ]
}
```

### Costing
- **AI Calls**: 1 DeepSeek call
- **Cost**: ~$0.01

---

## Function 2: Cover Letter Generator

Generates tailored cover letters based on matches.

### Usage
```python
from matcher import generate_cover_letter

result = generate_cover_letter(
    profile_data,
    job_data,
    style="professional"  # or "enthusiastic", "concise"
)

print(result['letter'])
```

### Input
- `profile_data`: Dict from `profile.parse_profile()`
- `job_data`: Dict from `job.sources.posting.parse_job_posting()`
- `style`: "professional", "enthusiastic", or "concise"

### Output
```json
{
  "letter": "Dear Hiring Manager,\n\nI am excited to apply...",
  "key_points_highlighted": [
    "5 years Python experience",
    "Led team of 5 engineers",
    "AWS certification"
  ],
  "gaps_addressed": [
    "Eager to expand Kubernetes skills"
  ],
  "word_count": 280
}
```

### Costing
- **AI Calls**: 1 DeepSeek call
- **Cost**: ~$0.01

---

## Full Workflow Example

```python
import json
from profile import parse_profile
from job.sources.posting import parse_job_posting
from matcher import analyze_gaps, generate_cover_letter

# 1. Parse resume (1 AI call)
profile = json.loads(parse_profile("resume.pdf", "pdf"))

# 2. Parse job posting (1 AI call)
job_text = """
Senior Software Engineer at Stripe
Requirements: 5+ years Python, AWS...
"""
job = parse_job_posting(job_text)

# 3. Analyze gaps (1 AI call)
gaps = analyze_gaps(profile, job)
print(f"Match Score: {gaps['match_score']}%")

# 4. Generate cover letter (1 AI call)
cover = generate_cover_letter(profile, job, style="professional")
print(cover['letter'])
```

**Total: 4 AI calls, ~$0.035**

---

## Testing

```bash
# Test gap analyzer
python -m matcher.tests.test_gap_analyzer

# Test cover letter
python -m matcher.tests.test_cover_letter
```

---

## Key Features

- **Independent Functions** - Use one or both, pre-parse data once
- **Implicit Skill Matching** - AI infers skills from experience descriptions
- **Multiple Styles** - Professional, enthusiastic, or concise cover letters
- **Actionable Recommendations** - Specific advice to improve match
- **Error Resilient** - Returns error dict instead of crashing
