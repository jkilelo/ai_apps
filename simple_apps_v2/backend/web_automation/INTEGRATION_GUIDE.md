# Web Automation Pipeline Integration Guide

## 🎯 Overview

The Web Automation Pipeline provides a 4-step process for automated web testing:

1. **Element Extraction** - Extracts testable elements from a webpage
2. **Test Generation** - Generates test scenarios from extracted elements
3. **Code Generation** - Creates executable test code
4. **Code Execution** - Runs the generated tests

## 📍 API Endpoints

### Base URL
```
http://localhost:8000/api/ui
```

### Endpoints Mapping

| Step | Frontend Component | Backend Endpoint | Method |
|------|-------------------|------------------|--------|
| 1 | ElementExtraction | `/element_extraction` | POST |
| 2 | TestGeneration | `/test_generation` | POST |
| 3 | CodeGeneration | `/code_generation` | POST |
| 4 | CodeExecution | `/code_execution` | POST |

## 🔄 Data Flow

Each step takes the output of the previous step as input:

```
URL → [Step 1] → extraction_data → [Step 2] → test_data → [Step 3] → code_data → [Step 4] → results
```

## 📝 Request/Response Examples

### Step 1: Element Extraction
**Request:**
```json
{
  "url": "https://example.com",
  "headless": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "step": "element_extraction",
    "url": "https://example.com",
    "elements": [...],
    "elements_by_category": {...},
    "statistics": {
      "total_elements": 15,
      "categories": ["buttons", "inputs", "navigation"]
    }
  },
  "timestamp": "2025-08-21T10:00:00"
}
```

### Step 2: Test Generation
**Request:**
```json
{
  "extraction_data": {/* output from Step 1 */},
  "test_categories": ["functional", "validation", "navigation"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "step": "test_generation",
    "test_scenarios": {...},
    "statistics": {
      "scenarios_count": 25,
      "features_count": 4
    }
  },
  "timestamp": "2025-08-21T10:01:00"
}
```

### Step 3: Code Generation
**Request:**
```json
{
  "test_data": {/* output from Step 2 */},
  "language": "python",
  "framework": "playwright"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "step": "code_generation",
    "generated_code": {
      "page_objects": {...},
      "test_files": {...},
      "config_files": {...}
    },
    "statistics": {
      "total_files": 6,
      "total_lines": 500
    }
  },
  "timestamp": "2025-08-21T10:02:00"
}
```

### Step 4: Code Execution
**Request:**
```json
{
  "code_data": {/* output from Step 3 */},
  "run_tests": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "step": "code_execution",
    "test_report": {
      "total_tests": 25,
      "passed": 23,
      "failed": 2,
      "success_rate": 92.0
    },
    "execution_results": {...}
  },
  "timestamp": "2025-08-21T10:03:00"
}
```

## 🔗 Frontend Integration

Update your frontend `useWebAutomation.ts` hook:

```typescript
// Step 1: Element Extraction
const response = await fetch(`${API_BASE_URL}/element_extraction`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url: targetUrl, headless: true })
});

// Step 2: Test Generation
const response = await fetch(`${API_BASE_URL}/test_generation`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ extraction_data: step1Result.data })
});

// Step 3: Code Generation
const response = await fetch(`${API_BASE_URL}/code_generation`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
        test_data: step2Result.data,
        language: "python",
        framework: "playwright"
    })
});

// Step 4: Code Execution
const response = await fetch(`${API_BASE_URL}/code_execution`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
        code_data: step3Result.data,
        run_tests: true
    })
});
```

## 🧪 Testing

### Run Standalone Functions Test
```bash
python backend/web_automation/test_pipeline.py --standalone
```

### Run API Integration Test
```bash
# Start the backend server first
python -m uvicorn backend.web_automation.main:app --host 0.0.0.0 --port 8000

# In another terminal, run the API tests
python backend/web_automation/test_pipeline.py --api
```

### Test with Custom URL
```bash
python backend/web_automation/test_pipeline.py --url https://your-site.com
```

## 🚀 Starting the Backend

```bash
cd simple_apps_v2
python -m uvicorn backend.web_automation.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📊 Features

- **Standalone Functions**: Each step can be tested independently
- **Chained Data Flow**: Output of each step feeds into the next
- **Live LLM Integration**: Uses Gemini AI for intelligent analysis
- **Error Handling**: Comprehensive error reporting at each step
- **Flexible Configuration**: Support for multiple languages and frameworks
- **Dry Run Mode**: Test without actual execution

## 🔧 Configuration

### Supported Languages
- Python
- JavaScript
- TypeScript

### Supported Frameworks
- Playwright
- Selenium
- Puppeteer

### Environment Variables
```bash
GOOGLE_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key  # Optional
ANTHROPIC_API_KEY=your_claude_api_key  # Optional
```

## 📈 Performance

Typical execution times:
- Step 1 (Element Extraction): 15-30 seconds
- Step 2 (Test Generation): 20-30 seconds
- Step 3 (Code Generation): 30-40 seconds
- Step 4 (Code Execution): Variable based on test count

## 🐛 Troubleshooting

### Common Issues

1. **Browser initialization failed**
   - Ensure Playwright is installed: `pip install playwright && playwright install chromium`

2. **LLM connection failed**
   - Check your API keys in environment variables
   - Verify internet connection

3. **Code execution timeout**
   - Use dry run mode for testing: `run_tests: false`

4. **CORS errors**
   - Ensure backend is running on correct port
   - Check CORS configuration in main.py

## 📚 Architecture

```
Backend Structure:
simple_apps_v2/
├── backend/
│   ├── web_automation/
│   │   ├── automation_pipeline.py  # Core 4 functions
│   │   ├── api_router.py          # API endpoints
│   │   ├── main.py                # FastAPI app
│   │   └── test_pipeline.py       # Test suite
│   └── shared/
│       └── llm.py                  # LLM integration
└── shared_modules/
    └── ui_web_auto_testing_v2/    # Browser automation
```

## ✅ Validation

Each function has been tested with live LLM connections and verified to:
- Extract elements correctly
- Generate meaningful test scenarios
- Create executable test code
- Execute tests successfully (in simulation mode)

## 🎉 Success Metrics

- ✅ All 4 standalone functions implemented
- ✅ All 4 API endpoints created and mapped
- ✅ Live LLM integration tested
- ✅ Chained data flow verified
- ✅ Error handling implemented
- ✅ Test suite created
- ✅ Documentation complete