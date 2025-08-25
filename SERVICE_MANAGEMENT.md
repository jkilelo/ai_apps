# Web Automation Pipeline - Service Management

## Overview
Idempotent batch scripts for managing the Web Automation Pipeline services (Backend on port 5175, Frontend on port 3000).

## Scripts

### 1. `start_web_automation.bat`
**Purpose**: Starts both backend and frontend services with idempotency checks.

**Features**:
- ✅ Checks if services are already running before starting
- ✅ Verifies service health using HTTP health checks
- ✅ Creates log directory automatically
- ✅ Waits for services to be ready before completing
- ✅ Opens browser automatically when services start
- ✅ Color-coded console output for better readability

**Usage**:
```batch
start_web_automation.bat
```

**What it does**:
1. Checks if backend (port 5175) is already running
2. Checks if frontend (port 3000) is already running
3. Only starts services that are not running
4. Waits for services to be healthy
5. Opens browser to http://localhost:3000/flows/web-automation

### 2. `stop_web_automation.bat`
**Purpose**: Gracefully stops both services.

**Features**:
- ✅ Finds processes by port number
- ✅ Verifies process type before stopping (Python/Node.js)
- ✅ Closes console windows
- ✅ Verifies services are stopped

**Usage**:
```batch
stop_web_automation.bat
```

### 3. `restart_web_automation.bat`
**Purpose**: Restarts both services (stop then start).

**Usage**:
```batch
restart_web_automation.bat
```

### 4. `status_web_automation.bat`
**Purpose**: Shows detailed status of both services.

**Features**:
- ✅ Port status checking
- ✅ Process information
- ✅ API health checks
- ✅ Endpoint availability
- ✅ System resource usage
- ✅ Auto-refresh option

**Usage**:
```batch
status_web_automation.bat
```

**Information displayed**:
- Backend service status and PID
- Frontend service status and PID
- API endpoint health checks
- Memory usage
- Process counts
- Overall system status

## Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | React application |
| Web Automation UI | http://localhost:3000/flows/web-automation | Main pipeline interface |
| Backend API | http://localhost:5175/api/ui | REST API endpoints |
| API Health | http://localhost:5175/api/ui/health | Backend health check |
| API Docs | http://localhost:5175/docs | Swagger documentation |

## Logs

Logs are automatically created in the `logs/` directory:
- `logs/backend.log` - Backend server logs
- `logs/frontend.log` - Frontend development server logs

## Troubleshooting

### Port Already in Use
If you see "Port X is in use but service is not responding":
1. Another application is using the port
2. Run `stop_web_automation.bat` to stop any lingering processes
3. Check Task Manager for orphaned python.exe or node.exe processes

### Service Won't Start
1. Check Python virtual environment exists: `.venv\Scripts\python.exe`
2. Check frontend dependencies: `simple_apps_original\frontend\node_modules`
3. Review logs in `logs/` directory

### Service Starts but Immediately Stops
1. Check for missing dependencies
2. Verify `.env` file exists with required API keys
3. Check logs for specific error messages

## Requirements

- Windows 10/11
- Python 3.8+ with virtual environment at `.venv`
- Node.js 16+ with npm
- curl command (for health checks)
- netstat command (for port checks)

## Environment Variables

Backend reads from `.env` file:
```env
GEMINI_API_KEY=your_api_key_here
API_PORT=5175
LLM_MODEL=gemini-2.5-flash
```

## Architecture

```
┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│   Backend    │
│  Port 3000   │     │  Port 5175   │
│   (React)    │     │  (FastAPI)   │
└──────────────┘     └──────────────┘
        │                    │
        ▼                    ▼
  [Browser UI]         [API Endpoints]
                            │
                            ▼
                    [Gemini 2.5 Flash]
```

## Senior DevOps Patterns Used

1. **Idempotency**: Scripts check current state before making changes
2. **Health Checks**: Verify services are actually responding, not just running
3. **Graceful Shutdown**: Stop services cleanly without data loss
4. **Resource Monitoring**: Track memory and process usage
5. **Logging**: Centralized log management
6. **Color Coding**: Visual feedback for quick status assessment
7. **Error Recovery**: Retry logic with exponential backoff
8. **Process Isolation**: Services run in separate console windows

## Quick Commands

```batch
# Start everything
start_web_automation.bat

# Check status
status_web_automation.bat

# Restart services
restart_web_automation.bat

# Stop everything
stop_web_automation.bat
```