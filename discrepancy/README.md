# Discrepancy - Profile Source Comparison

Compare resume, LinkedIn, and portfolio to find inconsistencies between sources.

## Overview

Analyzes 3 profile sources to find:
- Conflicting information (titles, dates, skills)
- Skills missing from one source but present in others
- Recommendations to improve consistency

Returns UI-friendly JSON for table display.

---

## Usage

```python
from discrepancy import compare_profile_sources, format_for_table

# Compare all 3 sources
result = compare_profile_sources(
    resume=resume_data,
    linkedin=linkedin_data,
    portfolio=portfolio_data
)

# Format for UI table
table_data = format_for_table(result)
```

---

## Input

- `resume`: Parsed resume data from `profile.parse_profile()`
- `linkedin`: Parsed LinkedIn profile data
- `portfolio`: Parsed portfolio data

Need at least 2 sources to compare.

---

## Output

```json
{
  "consistency_score": 85,
  "discrepancies": [
    {
      "field": "Current Title",
      "resume": "Senior Engineer",
      "linkedin": "Lead Engineer",
      "portfolio": "-",
      "issue": "Title mismatch between resume and LinkedIn",
      "severity": "high"
    }
  ],
  "skill_comparison": [
    {"skill": "Python", "in_resume": true, "in_linkedin": true, "in_portfolio": true},
    {"skill": "Kubernetes", "in_resume": false, "in_linkedin": true, "in_portfolio": false}
  ],
  "missing_in_resume": ["Kubernetes", "GraphQL"],
  "missing_online": ["Docker Certification"],
  "recommendations": [
    "Add Kubernetes to resume",
    "Update LinkedIn title to match resume"
  ]
}
```

---

## UI Table Format

```python
table_data = format_for_table(result)

# table_data["skill_table"]
# {
#   "headers": ["Skill", "Resume", "LinkedIn", "Portfolio"],
#   "rows": [["Python", "✓", "✓", "✓"], ["Kubernetes", "✗", "✓", "✗"]]
# }

# table_data["discrepancy_table"]
# {
#   "headers": ["Field", "Resume", "LinkedIn", "Portfolio", "Issue", "Severity"],
#   "rows": [...]
# }
```

---

## Costing

- **AI Calls**: 1 DeepSeek call
- **Cost**: ~$0.01

---

## Testing

```bash
python -m discrepancy.tests.test_discrepancy
```
