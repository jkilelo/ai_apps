# Simple Apps v2 - Clean Architecture

A clean, modular web automation testing application with consolidated dependencies.

## Project Structure

```
simple_apps_v2/
├── backend/                 # FastAPI backend
│   ├── web_automation/      # Web automation API endpoints
│   ├── shared/              # Shared utilities and LLM integration
│   └── requirements.txt     # Python dependencies
├── frontend/                # React frontend
│   ├── src/                 # Source code
│   ├── package.json         # Node dependencies
│   └── vite.config.ts       # Vite configuration
├── shared_modules/          # Shared Python modules
│   └── ui_web_auto_testing_v2/
├── scripts/                 # Setup and run scripts
└── README.md               # This file
```

## Prerequisites

- Python 3.10+
- Node.js 22.16.0+
- npm or yarn

## Installation

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
```

## Running the Application

### Backend Server

```bash
cd backend
python -m uvicorn web_automation.main:app --host 0.0.0.0 --port 5175 --reload
```

### Frontend Development Server

```bash
cd frontend
npm run dev
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5175
- API Documentation: http://localhost:5175/docs

## Features

- **Web URL Input**: Enter any website URL for testing
- **Element Extraction**: Automatically extract testable elements
- **Test Generation**: Generate test scenarios using LLM
- **Code Generation**: Generate executable test code
- **Test Execution**: Run tests in real-time with live results

## API Endpoints

- `POST /api/extract-elements` - Extract elements from a webpage
- `POST /api/generate-tests` - Generate test scenarios
- `POST /api/generate-code` - Generate test code
- `POST /api/execute-tests` - Execute generated tests

## Environment Variables

Create a `.env` file in the backend directory:

```env
# LLM API Keys (optional - will use defaults if not set)
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
```

## Development

### Linting

```bash
# Frontend
cd frontend
npm run lint

# Backend (using ruff)
cd backend
ruff check .
```

### Building for Production

```bash
# Frontend
cd frontend
npm run build

# The built files will be in frontend/dist
```

## Troubleshooting

1. **Port Already in Use**: Kill any processes using ports 3000 or 5175
2. **Playwright Issues**: Run `playwright install chromium` to install browser
3. **Module Import Errors**: Ensure you're running from the correct directory with proper Python path

## License

MIT