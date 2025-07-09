#!/bin/bash

# AI Apps v3 - Comprehensive Test Runner
# Runs all tests with full evidence collection

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
TEST_DIR="/var/www/ai_apps/standalone_app/v3"
REPORT_DIR="$TEST_DIR/test_reports"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_NAME="test_report_${TIMESTAMP}"

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     AI Apps v3 - Test Suite Runner     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Change to test directory
cd "$TEST_DIR"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv .venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source .venv/bin/activate

# Install/update dependencies
echo -e "${YELLOW}Installing test dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt
pip install -q -r requirements-test.txt

# Install Playwright browsers if needed
echo -e "${YELLOW}Setting up Playwright browsers...${NC}"
playwright install chromium --with-deps

# Create report directories
echo -e "${YELLOW}Creating report directories...${NC}"
mkdir -p "$REPORT_DIR"/{screenshots,videos,traces,html_reports,evidence}

# Start the application if not running
if ! curl -s http://localhost:8004/api/health > /dev/null; then
    echo -e "${YELLOW}Starting application...${NC}"
    cd "$TEST_DIR"
    ./start_app.sh > /dev/null 2>&1 &
    APP_PID=$!
    
    # Wait for app to start
    echo -e "${YELLOW}Waiting for application to start...${NC}"
    for i in {1..30}; do
        if curl -s http://localhost:8004/api/health > /dev/null; then
            echo -e "${GREEN}Application started successfully${NC}"
            break
        fi
        sleep 1
    done
else
    echo -e "${GREEN}Application already running${NC}"
fi

# Clean old test artifacts (keep last 5 runs)
echo -e "${YELLOW}Cleaning old test artifacts...${NC}"
find "$REPORT_DIR" -name "*.png" -mtime +7 -delete
find "$REPORT_DIR" -name "*.webm" -mtime +7 -delete
find "$REPORT_DIR" -name "*.zip" -mtime +7 -delete

# Run tests with full reporting
echo ""
echo -e "${BLUE}Running comprehensive test suite...${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

# Set test environment variables
export TEST_BASE_URL="http://localhost:8004"
export TEST_HEADLESS="false"
export TEST_SLOW_MO="50"
export TEST_TIMEOUT="30000"

# Run pytest with all features enabled
pytest tests/ \
    --verbose \
    --strict-markers \
    --tb=short \
    --maxfail=10 \
    --timeout=300 \
    --asyncio-mode=auto \
    --headed \
    --video=on \
    --screenshot=on \
    --tracing=on \
    --html="$REPORT_DIR/html_reports/${REPORT_NAME}.html" \
    --self-contained-html \
    --cov=frontend \
    --cov=api \
    --cov-report=html:"$REPORT_DIR/html_reports/coverage" \
    --cov-report=term \
    --junit-xml="$REPORT_DIR/junit_${REPORT_NAME}.xml" \
    -o junit_family=xunit2 \
    --capture=no \
    2>&1 | tee "$REPORT_DIR/test_log_${TIMESTAMP}.txt"

# Capture exit code
TEST_EXIT_CODE=$?

# Generate summary report
echo ""
echo -e "${BLUE}Generating test summary...${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

# Count test evidence
SCREENSHOT_COUNT=$(find "$REPORT_DIR/screenshots" -name "*.png" -newer "$REPORT_DIR/test_log_${TIMESTAMP}.txt" | wc -l)
VIDEO_COUNT=$(find "$REPORT_DIR/videos" -name "*.webm" -newer "$REPORT_DIR/test_log_${TIMESTAMP}.txt" | wc -l)
TRACE_COUNT=$(find "$REPORT_DIR/traces" -name "*.zip" -newer "$REPORT_DIR/test_log_${TIMESTAMP}.txt" | wc -l)

# Create summary file
cat > "$REPORT_DIR/summary_${TIMESTAMP}.txt" << EOF
AI Apps v3 Test Execution Summary
================================
Timestamp: $(date)
Exit Code: $TEST_EXIT_CODE

Evidence Collected:
- Screenshots: $SCREENSHOT_COUNT
- Videos: $VIDEO_COUNT
- Traces: $TRACE_COUNT

Reports Generated:
- HTML Report: $REPORT_DIR/html_reports/${REPORT_NAME}.html
- Coverage Report: $REPORT_DIR/html_reports/coverage/index.html
- JUnit XML: $REPORT_DIR/junit_${REPORT_NAME}.xml
- Test Log: $REPORT_DIR/test_log_${TIMESTAMP}.txt

EOF

# Display summary
cat "$REPORT_DIR/summary_${TIMESTAMP}.txt"

# Generate evidence index
echo -e "${YELLOW}Creating evidence index...${NC}"
python3 - << EOF
import json
import os
from pathlib import Path
from datetime import datetime

report_dir = Path("$REPORT_DIR")
timestamp = "$TIMESTAMP"

evidence = {
    "timestamp": timestamp,
    "screenshots": [],
    "videos": [],
    "traces": []
}

# Collect screenshots
for f in (report_dir / "screenshots").glob("*.png"):
    if f.stat().st_mtime > os.path.getmtime(f"$REPORT_DIR/test_log_{timestamp}.txt"):
        evidence["screenshots"].append({
            "file": f.name,
            "size": f.stat().st_size,
            "path": str(f)
        })

# Collect videos
for f in (report_dir / "videos").glob("*.webm"):
    if f.stat().st_mtime > os.path.getmtime(f"$REPORT_DIR/test_log_{timestamp}.txt"):
        evidence["videos"].append({
            "file": f.name,
            "size": f.stat().st_size,
            "path": str(f)
        })

# Collect traces
for f in (report_dir / "traces").glob("*.zip"):
    if f.stat().st_mtime > os.path.getmtime(f"$REPORT_DIR/test_log_{timestamp}.txt"):
        evidence["traces"].append({
            "file": f.name,
            "size": f.stat().st_size,
            "path": str(f)
        })

# Save evidence index
with open(report_dir / f"evidence_index_{timestamp}.json", "w") as f:
    json.dump(evidence, f, indent=2)

print(f"Evidence index created: evidence_index_{timestamp}.json")
EOF

# Display results based on exit code
echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║         All Tests Passed! ✅           ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
else
    echo -e "${RED}╔════════════════════════════════════════╗${NC}"
    echo -e "${RED}║        Some Tests Failed! ❌           ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════╝${NC}"
fi

# Open HTML report if not in CI
if [ -z "$CI" ] && [ -f "$REPORT_DIR/html_reports/${REPORT_NAME}.html" ]; then
    echo ""
    echo -e "${YELLOW}Opening test report in browser...${NC}"
    if command -v xdg-open &> /dev/null; then
        xdg-open "$REPORT_DIR/html_reports/${REPORT_NAME}.html"
    elif command -v open &> /dev/null; then
        open "$REPORT_DIR/html_reports/${REPORT_NAME}.html"
    fi
fi

# Cleanup if we started the app
if [ ! -z "$APP_PID" ]; then
    echo ""
    echo -e "${YELLOW}Stopping application...${NC}"
    kill $APP_PID 2>/dev/null || true
fi

echo ""
echo -e "${BLUE}Test execution completed at $(date)${NC}"

# Exit with test exit code
exit $TEST_EXIT_CODE