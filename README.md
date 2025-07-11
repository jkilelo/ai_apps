# AI Apps Suite

A modern web application suite featuring AI-powered tools with a sleek, native-app-like UI. Built with React, TypeScript, and FastAPI.

## Features

- **Modern UI/UX**: Glassmorphic design with smooth animations
- **AI-Powered Tools**: Web automation testing, data processing, and more
- **Single Port Deployment**: Frontend served by FastAPI backend
- **Responsive Design**: Works seamlessly across devices
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Platform Compatibility

✅ **Windows**: Full support (without uvloop)  
✅ **macOS**: Full support with performance optimizations  
✅ **Linux**: Full support with best performance  
✅ **Docker**: Platform-independent deployment

## Prerequisites

- Node.js 18+ and npm
- Python 3.8+
- Git

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/jkilelo/ai_apps.git
cd ai_apps
```

### 2. Backend Setup

```bash
# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install backend dependencies
# For Windows:
pip install -r requirements_platform_agnostic.txt
# For macOS/Linux:
pip install -r requirements.txt

# Install Playwright browsers (for web automation features)
playwright install
```

### 3. Frontend Setup

```bash
# Install frontend dependencies
npm install

# Build the frontend for production
npm run build
```

### 4. Environment Configuration

Create a `.env` file in the root directory:

```env
# Backend Configuration
FASTAPI_PORT=8080
ENVIRONMENT=production

# Add any other environment variables as needed
```

For development, create `.env.development`:

```env
VITE_API_URL=/api/v1
```

## Running the Application

### Quick Start (All Platforms)

**Windows:**
```cmd
run_cross_platform.bat
```

**macOS/Linux:**
```bash
chmod +x run_cross_platform.sh
./run_cross_platform.sh
```

### Manual Start

```bash
# Activate virtual environment if not already activated
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Run the application
python run.py
```

The application will be available at `http://localhost:8080`

### Development Mode (Separate Ports)

For development with hot reloading:

**Terminal 1 - Backend:**
```bash
source venv/bin/activate
cd apps/ui_web_auto_testing/api
uvicorn main:app --reload --port 8002
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8002`

## Project Structure

```
ai_apps/
├── apps/                      # Backend applications
│   └── ui_web_auto_testing/   # Web automation testing app
│       ├── api/               # FastAPI backend
│       │   ├── main.py        # Main API application
│       │   ├── routers/       # API route handlers
│       │   └── services/      # Business logic
│       └── tests/             # Backend tests
├── dynamic_forms_streaming/   # 🆕 Dynamic Forms FastAPI Application
│   ├── main.py                # FastAPI app with WebSocket support
│   ├── requirements.txt       # Python dependencies
│   ├── static/                # Frontend assets
│   │   ├── app.js             # ES6 JavaScript client
│   │   └── styles.css         # Modern CSS3 styles
│   ├── templates/             # HTML templates
│   │   └── dashboard.html     # Main dashboard
│   ├── README.md              # Comprehensive documentation
│   ├── CONTRIBUTING.md        # Development guidelines
│   ├── CHANGELOG.md           # Version history
│   └── .github/workflows/     # CI/CD pipeline
├── playground/                # 🆕 Experimental and demo applications
│   ├── beautiful_pages/       # Real-time console streaming app
│   │   ├── realtime_console.py
│   │   ├── static/
│   │   └── templates/
│   └── dynamic_forms_app/     # Alternative forms implementation
├── src/                       # Frontend React application
│   ├── components/            # React components
│   ├── hooks/                 # Custom React hooks
│   ├── services/              # API services
│   ├── types/                 # TypeScript types
│   └── index.css              # Global styles
├── dist/                      # Built frontend (generated)
├── run.py                     # Production server runner
├── package.json               # Frontend dependencies
├── requirements.txt           # Backend dependencies
├── vite.config.ts             # Vite configuration
└── tsconfig.json              # TypeScript configuration
```

## Available Scripts

### Frontend Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run typecheck` - Run TypeScript type checking

### Backend Scripts

- `python run.py` - Run production server
- `pytest` - Run backend tests

## API Documentation

When running the application, API documentation is available at:
- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

## Features Overview

### 🎯 Available Applications

#### 1. UI Web Auto Testing (`/apps/ui_web_auto_testing/`)
- Extract web elements using Playwright
- Generate test cases with AI
- Execute automated tests
- View detailed test results

#### 2. Dynamic Forms Streaming API (`/dynamic_forms_streaming/`)
- **🚀 Real-time form generation** from FastAPI endpoints
- **📡 WebSocket streaming** for live updates and notifications
- **🎨 Beautiful, responsive UI** with modern CSS3 animations
- **✅ Comprehensive validation** (client-side and server-side)
- **📱 Mobile-responsive** design that works on all devices
- **🔧 5 Built-in form types**:
  - User Profile Management
  - Product Catalog Entry
  - Contact Message System
  - Feedback & Rating System
  - Newsletter Subscription

**Quick Start for Dynamic Forms:**
```bash
cd dynamic_forms_streaming
pip install -r requirements.txt
python main.py
# Visit http://localhost:8000
```

#### 3. Real-time Console Streaming (`/playground/beautiful_pages/`)
- Stream Python console output in real-time
- WebSocket-powered live updates
- Beautiful dashboard interface
- Code execution examples

**Features of Dynamic Forms App:**
- 🎨 Modern glassmorphic design with gradient backgrounds
- 📡 Real-time WebSocket streaming for live form submissions
- 🚀 Automatic form generation from Pydantic models
- ✅ Smart validation with visual feedback
- 📱 Fully responsive design (mobile, tablet, desktop)
- 🔄 Auto-reconnecting WebSocket connections
- 🎪 Toast notifications and loading states
- 🎯 In-form response display with enhanced backend data
- ♿ Accessibility features with ARIA support

## Deployment

### Using Docker (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install Node.js
RUN apt-get update && apt-get install -y nodejs npm

# Copy and install backend dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install-deps
RUN playwright install

# Copy and install frontend dependencies
COPY package*.json ./
RUN npm install

# Copy application code
COPY . .

# Build frontend
RUN npm run build

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "run.py"]
```

Build and run:
```bash
docker build -t ai-apps .
docker run -p 8080:8080 ai-apps
```

### Manual Deployment

1. Set up a Linux server (Ubuntu recommended)
2. Install Python 3.8+, Node.js 18+
3. Clone the repository
4. Follow the installation steps above
5. Use a process manager like systemd or supervisor to run the application
6. Configure a reverse proxy (nginx/Apache) if needed

## Troubleshooting

### Common Issues

1. **Port already in use**
   - Change the port in `.env` file
   - Or kill the process using the port: `lsof -ti:8080 | xargs kill -9`

2. **Module not found errors**
   - Ensure virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

3. **Frontend build errors**
   - Clear node_modules: `rm -rf node_modules && npm install`
   - Clear build cache: `rm -rf dist`

4. **Playwright issues**
   - Install system dependencies: `playwright install-deps`
   - Reinstall browsers: `playwright install`

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open an issue on GitHub.