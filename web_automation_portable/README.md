# Web Automation Portable System

A complete web automation system with React frontend and FastAPI backend that extracts elements from websites, generates tests, creates automation code, and executes it.

## Features

- **Real Element Extraction**: Extracts actual elements from any website using stealth browser automation
- **Intelligent Test Generation**: Creates meaningful test scenarios based on element types
- **Code Generation**: Produces runnable Selenium (Python) or Playwright (JavaScript) code
- **Beautiful UI**: Modern React interface with glassmorphism effects and smooth animations
- **Production Ready**: Follows DRY principles with centralized data types and modular architecture

## Project Structure

```
web_automation_portable/
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── App.tsx          # Main app component with routing
│   │   └── flows/
│   │       └── web-automation/
│   │           └── WebAutomationFlowSimplified.tsx  # Main UI component
│   └── package.json         # Frontend dependencies
│
├── backend/                 # Python FastAPI backend
│   ├── unified_web_automation_api.py  # Main API server
│   ├── data_types.py        # Shared data models (DRY principle)
│   ├── browser.py           # Stealth browser automation
│   └── elements_extractor_no_llm.py   # Element extraction logic
│
└── README.md               # This file
```

## Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.9+
- **Chrome** browser installed

## Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows: `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

4. Install Python dependencies:
```bash
pip install -r requirements.txt
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node dependencies:
```bash
npm install
```

## Running the Application

### Start the Backend (Terminal 1)

```bash
cd backend
python -m uvicorn unified_web_automation_api:app --reload --port 8001
```

The API will be available at http://localhost:8001
API documentation at http://localhost:8001/docs

### Start the Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

The frontend will be available at http://localhost:3000

## Usage

1. Open http://localhost:3000/web-automation in your browser
2. Enter any website URL (e.g., https://example.com)
3. Click "Extract Elements" to extract interactive elements from the page
4. Select elements and click "Generate Tests" to create test scenarios
5. Choose Python or JavaScript and click "Generate Code" to create automation scripts
6. Click "Execute Code" to run the generated automation (simulated)

## API Endpoints

- `POST /api/web-automation/extract` - Extract elements from a URL
- `POST /api/web-automation/generate-tests` - Generate test cases from elements
- `POST /api/web-automation/generate-code` - Generate automation code from tests
- `POST /api/web-automation/execute` - Execute generated code (simulated)
- `GET /health` - Health check endpoint

## Architecture

### Frontend
- **React 19.1** with TypeScript
- **Framer Motion** for animations
- **Tailwind CSS 4.1** for styling
- **Axios** for API calls
- **Lucide React** for icons

### Backend
- **FastAPI** for REST API
- **Playwright** for browser automation
- **Pydantic** for data validation
- **Asyncio** for async operations

### Key Design Principles
- **DRY (Don't Repeat Yourself)**: All data types centralized in `data_types.py`
- **Modular Architecture**: Separate modules for browser, extraction, and API
- **Type Safety**: Full TypeScript in frontend, Pydantic models in backend
- **Production Ready**: Error handling, logging, and validation throughout

## Configuration

### Change API Port
Edit `backend/unified_web_automation_api.py` line at bottom:
```python
uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
```

### Change Frontend API URL
Edit `frontend/src/flows/web-automation/WebAutomationFlowSimplified.tsx` line 21:
```typescript
const API_BASE = 'http://localhost:8001/api/web-automation';
```

## Troubleshooting

### Backend Issues
- Ensure Chrome is installed
- Check Python version: `python --version` (should be 3.9+)
- Install Playwright browsers: `playwright install chromium`

### Frontend Issues
- Clear npm cache: `npm cache clean --force`
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`

### CORS Issues
- Backend already configured for CORS with frontend URL
- Check that frontend is running on port 3000

## Development

### Adding New Element Types
1. Add to `backend/data_types.py` ElementType enum
2. Update extraction logic in `backend/elements_extractor_no_llm.py`
3. Update UI display in frontend component

### Modifying Test Generation
Edit `backend/unified_web_automation_api.py` `generate_tests()` function

### Changing UI Theme
Modify Tailwind classes in `frontend/src/flows/web-automation/WebAutomationFlowSimplified.tsx`

## License

MIT

## Support

For issues or questions, please create an issue in the repository.