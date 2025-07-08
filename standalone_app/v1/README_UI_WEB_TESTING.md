# UI Web Auto Testing - Quick Start Guide

This guide will help you run the UI Web Auto Testing application with its backend API.

## Prerequisites

- Python 3.8+
- Node.js 16+
- FastAPI and related dependencies
- Playwright for web automation

## Installation

1. **Install Python dependencies:**
```bash
pip install fastapi uvicorn slowapi pydantic playwright
# Install Playwright browsers
playwright install chromium
```

2. **Install Node.js dependencies:**
```bash
cd /var/www/ai_apps
npm install
```

## Running the Application

### Step 1: Start the Backend API Server

```bash
cd /var/www/ai_apps/apps/ui_web_auto_testing
python run_api.py
```

The API server will start on http://localhost:8002

You can view the API documentation at:
- Swagger UI: http://localhost:8002/api/docs
- ReDoc: http://localhost:8002/api/redoc

### Step 2: Start the Frontend Application

In a new terminal:

```bash
cd /var/www/ai_apps
npm run dev
```

The frontend will be available at http://localhost:3001 (or another port if 3001 is in use)

## Using the Application

1. **Select "UI Web Auto Testing"** from the sidebar
2. **Step 1 - Element Extraction:**
   - Enter a web page URL (e.g., https://example.com)
   - Select a profile (default: qa_manual_tester)
   - Click "Execute Step"
   - Wait for elements to be extracted

3. **Step 2 - Test Generation:**
   - The extracted elements from Step 1 will be automatically available
   - Select test type and framework options
   - Click "Execute Step"
   - View the generated test cases

4. **Step 3 - Test Execution:**
   - The generated test cases will be automatically available
   - Select execution options (browser, timeout, etc.)
   - Click "Execute Step"
   - View the test results with pass/fail status

## API Endpoints

### Element Extraction
- `POST /api/v1/element-extraction/extract` - Start element extraction
- `GET /api/v1/element-extraction/extract/{job_id}` - Get extraction status
- `GET /api/v1/element-extraction/profiles` - List available profiles

### Test Generation
- `POST /api/v1/test-generation/generate` - Generate test cases
- `GET /api/v1/test-generation/generate/{job_id}` - Get generation status

### Test Execution
- `POST /api/v1/test-execution/execute` - Execute test cases
- `GET /api/v1/test-execution/execute/{job_id}` - Get execution status
- `GET /api/v1/test-execution/results/{job_id}/report` - Get execution report

## Configuration

The API URL is configured in `.env.development`:
```
VITE_API_URL=http://localhost:8002/api/v1
```

## Troubleshooting

1. **Port already in use:**
   - The API uses port 8002 by default
   - The frontend uses port 3001 by default
   - Update the ports in the respective configuration files if needed

2. **CORS errors:**
   - Make sure the API server is running
   - Check that the frontend is using the correct API URL

3. **Module not found errors:**
   - Ensure all Python dependencies are installed
   - Check that the Python path includes the project root

## Architecture

- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI + Python
- **Web Automation**: Playwright
- **API Communication**: REST with async job processing