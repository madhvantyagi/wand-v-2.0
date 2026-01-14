# Testing Phase 1

## How to Run

```bash
# From the wand directory
python -m job.tests.test_phase1
```

## What It Does

- Fetches job postings for "Shipday" (configurable in the script)
- Extracts tech stack and salary information
- Prints results to console
- Saves output to `{company}_phase1.json`

## Requirements

Make sure you have installed:
```bash
pip install python-jobspy pandas
```

## Customize

Edit `job/tests/test_phase1.py` and change the company name on line 57:
```python
company = "YourCompanyName"
```
