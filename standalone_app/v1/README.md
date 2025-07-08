# AI Apps Standalone v1

A standalone fullstack AI application with web automation and data profiling capabilities.

## Features

- **LLM Query**: Interact with AI language models
- **Web Automation**: Extract elements, generate tests, create and execute automation scripts
- **Data Profiling**: Analyze data quality with PySpark integration

## Tech Stack

- **Backend**: FastAPI (Python 3.12)
- **Frontend**: React 19.1 with TypeScript and Tailwind CSS 3.4
- **Database**: MongoDB 6.0 (optional)
- **AI**: OpenAI GPT-4

## Quick Start

1. Start the application:
   ```bash
   ./start_app.sh
   ```

2. Access the application at: http://localhost:8004

3. Stop the application:
   ```bash
   ./stop_app.sh
   ```

## API Endpoints

### General
- `GET /api/health` - Health check

### LLM
- `POST /api/llm_query` - Query the LLM

### Web Automation
- `POST /api/web_automation/extract_elements` - Extract elements from URL
- `POST /api/web_automation/generate_gherkin_tests` - Generate test scenarios
- `POST /api/web_automation/generate_python_code` - Generate automation code
- `POST /api/web_automation/execute_python_code` - Execute automation script

### Data Profiling
- `POST /api/data_profiling/generate_profiling_suggestions` - Generate profiling suggestions
- `POST /api/data_profiling/generate_profiling_testcases` - Generate test cases
- `POST /api/data_profiling/generate_pyspark_code` - Generate PySpark code
- `POST /api/data_profiling/execute_pyspark_code` - Execute PySpark code
- `POST /api/data_profiling/generate_dq_suggestions` - Generate DQ suggestions
- `POST /api/data_profiling/generate_dq_tests` - Generate DQ tests
- `POST /api/data_profiling/generate_pyspark_dq_code` - Generate DQ PySpark code
- `POST /api/data_profiling/execute_pyspark_dq_code` - Execute DQ PySpark code

## Status

✅ Backend API is running and functional
✅ LLM endpoint tested and working
✅ Beautiful UI components created
✅ Responsive design implemented
⚠️ MongoDB authentication optional (runs without DB)
⚠️ Frontend build requires minor configuration fixes

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd standalone_app/v1
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

3. **Install dependencies**
   ```bash
   # Backend
   pip install -r requirements.txt
   playwright install chromium
   
   # Frontend
   cd frontend
   npm install
   cd ..
   ```

4. **Start the application**
   ```bash
   ./start_app.sh
   ```

5. **Access the application**
   - Frontend: http://localhost:8005
   - API: http://localhost:8004

## Environment Variables

- `OPENAI_API_KEY` - Required for LLM functionality
- `MONGODB_CONNECTION_STRING` - Optional MongoDB connection (app works without it)

## Architecture

The application follows a modular architecture:
- API endpoints handle HTTP requests
- Service modules implement business logic
- MongoDB stores session data (when available)
- React frontend provides beautiful, responsive UI