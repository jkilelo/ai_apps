#!/bin/bash

# AI Apps v3 - Smoke Test Runner
# Quick tests for CI/CD pipeline

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Running smoke tests...${NC}"

# Change to test directory
cd /var/www/ai_apps/standalone_app/v3

# Activate virtual environment
source .venv/bin/activate

# Set headless mode for CI
export TEST_BASE_URL="http://localhost:8004"
export TEST_HEADLESS="true"
export TEST_SLOW_MO="0"
export TEST_TIMEOUT="10000"

# Run only smoke tests
pytest tests/ \
    -m smoke \
    --verbose \
    --tb=short \
    --maxfail=1 \
    --timeout=60 \
    --asyncio-mode=auto \
    --headless \
    --screenshot=only-on-failure \
    -n auto \
    --json-report \
    --json-report-file=test_reports/smoke_test_results.json

echo -e "${GREEN}Smoke tests completed${NC}"