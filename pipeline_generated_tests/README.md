# Dynamic Generated Test Suite

Generated for: https://github.com
Generated on: 2025-08-15T07:01:00.591134

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```

2. Configure environment:
```bash
cp .env.test .env
# Edit .env with your credentials
```

## Running Tests

```bash
pytest                    # Run all tests
pytest -m critical       # Run critical tests
pytest -n 4             # Run in parallel
pytest --html=report.html # Generate HTML report
```

## Structure

- `pages/` - Page Object Model classes
- `tests/` - Test files
- `conftest.py` - Pytest configuration
- `requirements.txt` - Dependencies
- `.env.test` - Environment template
