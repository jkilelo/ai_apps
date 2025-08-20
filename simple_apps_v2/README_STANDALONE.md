# simple_apps_v2 - Standalone Version

This is a fully standalone version of simple_apps_v2 with all dependencies self-contained.

## Features

- **Web Automation Testing**: AI-powered UI element extraction and test generation
- **Data Profiling**: Comprehensive data quality analysis with automated assessment
- **Modern UI**: React-based frontend with glassmorphic design
- **AI Integration**: Powered by Gemini, OpenAI, and Anthropic LLMs
- **Browser Automation**: Playwright-based web scraping with stealth capabilities

## Project Structure

```
simple_apps_v2/
├── backend/                 # FastAPI backend
│   ├── web_automation/      # Web automation API endpoints
│   └── shared/              # Shared utilities and LLM integration
├── shared_modules/          # Shared Python modules
│   └── ui_web_auto_testing_v2/  # Browser automation and extraction
├── frontend/                # React + TypeScript frontend
│   ├── src/
│   │   ├── flows/          # Application workflows
│   │   └── pages/          # Page components
│   └── package.json
├── run_standalone.py        # Main runner script
├── requirements.txt         # Python dependencies
└── setup_standalone.bat     # One-click setup script
```

## Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- npm or yarn

## Quick Setup

### Windows

1. Run the automated setup:
```bash
setup_standalone.bat
```

This will:
- Create a Python virtual environment
- Install all Python dependencies
- Install Playwright browsers
- Install frontend dependencies

### Manual Setup

1. **Backend Setup**:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

2. **Frontend Setup**:
```bash
cd frontend
npm install
```

## Running the Application

### Option 1: Using Batch Scripts (Windows)

Open two terminals:

**Terminal 1 - Backend**:
```bash
run_backend_standalone.bat
```

**Terminal 2 - Frontend**:
```bash
run_frontend_standalone.bat
```

### Option 2: Using Python Script

**Backend**:
```bash
python run_standalone.py --service backend
```

**Frontend** (in new terminal):
```bash
python run_standalone.py --service frontend
```

### Option 3: Manual Start

**Backend**:
```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac

# Run backend
python -m uvicorn backend.web_automation.main:app --host 0.0.0.0 --port 5175
```

**Frontend** (in new terminal):
```bash
cd frontend
npm run dev
```

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# LLM API Keys (optional - for AI features)
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
ANTHROPIC_API_KEY=your_anthropic_key

# Server Configuration
BACKEND_PORT=5175
FRONTEND_PORT=3000
```

### API Endpoints

- Backend: `http://localhost:5175`
- Frontend: `http://localhost:3000`
- API Docs: `http://localhost:5175/docs`

## Features Documentation

### Web Automation Flow

1. **Extract Elements**: Enter a URL to extract all interactive elements
2. **Generate Tests**: AI generates comprehensive test scenarios
3. **Generate Code**: Creates executable test code
4. **Execute Tests**: Runs the generated tests

### Error Handling

The application includes comprehensive error handling:
- Structured error responses with type classification
- User-friendly error messages with suggestions
- Retry mechanisms for recoverable errors
- Graceful degradation when AI services are unavailable

## Troubleshooting

### Common Issues

1. **Port already in use**:
   - Change the port in `run_standalone.py` or use environment variables

2. **Playwright browser not found**:
   ```bash
   playwright install chromium
   ```

3. **Module import errors**:
   - Ensure you're running from the simple_apps_v2 directory
   - Check that the virtual environment is activated

4. **LLM features not working**:
   - Add your API keys to the .env file
   - Check your API key quotas and rate limits

## Development

### Running Tests

```bash
# Backend tests
pytest tests/

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Format Python code
black .

# Lint Python code
ruff check .

# Format/lint frontend
cd frontend
npm run lint
```

## License

This is a standalone version for development and testing purposes.

## Support

For issues or questions, please check the documentation or create an issue in the repository.