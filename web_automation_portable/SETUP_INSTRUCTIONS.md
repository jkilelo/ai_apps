# Web Automation Portable - Setup Instructions

## Prerequisites

- Python 3.9+
- Node.js 18+ (preferably 22.16.0)
- Chrome browser (for Selenium)
- Git

## Quick Setup

### 1. Clone the Repository

```bash
git clone https://github.com/jkilelo/ai_apps.git
cd ai_apps/web_automation_portable
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd ../frontend

# Install Node dependencies
npm install
```

## Running the Application

### Start Backend (Terminal 1)

```bash
cd backend
# Activate virtual environment if not already active
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Start the API server
python -m uvicorn unified_web_automation_api:app --host 0.0.0.0 --port 8001 --reload
```

The backend API will be available at:
- API: http://localhost:8001
- API Documentation: http://localhost:8001/docs

### Start Frontend (Terminal 2)

```bash
cd frontend

# Start the development server
npm run dev
```

The frontend will be available at:
- Web UI: http://localhost:3000

## Using the Application

1. Open your browser and navigate to http://localhost:3000
2. The Web Automation Flow has 4 steps:
   - **Step 1:** Enter a URL to extract elements from the webpage
   - **Step 2:** Review extracted elements and select which ones to test
   - **Step 3:** Generate test code in Python (Selenium) or JavaScript (Playwright)
   - **Step 4:** Execute the generated code (simulated)

## Troubleshooting

### Backend Issues

If the backend doesn't start:
```bash
# Make sure you're in the backend directory
cd backend

# Check Python version (should be 3.9+)
python --version

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Frontend Issues

If the frontend doesn't start:
```bash
# Make sure you're in the frontend directory
cd frontend

# Check Node version (should be 18+)
node --version

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Port Conflicts

If ports are already in use:
- Backend: Change port in the uvicorn command (e.g., `--port 8002`)
- Frontend: Change port in package.json or use `npm run dev -- --port 3001`

## Features

- **Element Extraction:** Extracts interactive elements from any webpage
- **Test Generation:** Creates test scenarios based on extracted elements
- **Code Generation:** Produces runnable Selenium or Playwright code
- **DRY Architecture:** All modules follow strict DRY principles with zero code duplication

## API Endpoints

- `POST /api/web-automation/extract` - Extract elements from a URL
- `POST /api/web-automation/generate-tests` - Generate test cases
- `POST /api/web-automation/generate-code` - Generate automation code
- `POST /api/web-automation/execute` - Execute generated code
- `GET /health` - Health check endpoint

## Technology Stack

- **Backend:** Python, FastAPI, Selenium, Playwright
- **Frontend:** React 19.1, TypeScript, Vite, Tailwind CSS 4.1
- **Architecture:** DRY-compliant modular design

## Support

For issues or questions, please open an issue on the GitHub repository.