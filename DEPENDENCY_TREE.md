# Dependency Tree Analysis for simple_apps

## Backend Dependencies (Python)

### Core Framework
- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **pydantic** - Data validation

### Browser Automation
- **playwright** - Browser automation
- **playwright-async** - Async playwright support

### Testing
- **pytest** - Testing framework
- **pytest-asyncio** - Async test support
- **pytest-json-report** - JSON test reporting

### External Modules (from parent directories)
- `apps/ui_web_auto_testing_v2/element_extractor.py`
- `apps/ui_web_auto_testing_v2/browser.py`
- `apps/ui_web_auto_testing_v2/element_structure.py`
- `apps/ui_web_auto_testing_v2/llm_test_generation.py`
- `utils/code_extractor.py`
- `llm.py` - LLM integration module

## Frontend Dependencies (Node.js/React)

### Core
- **react** ^19.1.0
- **react-dom** ^19.1.0
- **react-router-dom** ^7.6.3
- **typescript** ^5.7.2

### Build Tools
- **vite** ^6.0.2
- **@vitejs/plugin-react** ^4.3.4

### Styling
- **tailwindcss** ^4.1.11
- **@tailwindcss/vite** ^4.1.11
- **autoprefixer** ^10.4.20

### UI Components
- **lucide-react** ^0.525.0 - Icons
- **@headlessui/react** ^2.2.4
- **@heroicons/react** ^2.2.0
- **framer-motion** ^12.23.3

### Utilities
- **axios** ^1.10.0 - HTTP client
- **react-syntax-highlighter** ^15.6.1 - Code highlighting
- **uuid** ^11.1.0
- **zustand** ^5.0.6 - State management

### Development Tools
- **eslint** and related plugins
- **prettier** and tailwind formatter

## Files to Copy

### Backend Structure
```
simple_apps_v2/
├── backend/
│   ├── web_automation/
│   │   ├── main.py
│   │   └── __init__.py
│   ├── requirements.txt (to be created)
│   └── shared/
│       ├── llm.py
│       └── utils/
│           └── code_extractor.py
```

### Frontend Structure
```
simple_apps_v2/
├── frontend/
│   ├── src/
│   │   ├── flows/
│   │   │   └── web-automation/
│   │   │       ├── WebAutomationFlowVertical.tsx
│   │   │       └── testUrls.json
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── tailwind.config.js
```

### Shared Dependencies
```
simple_apps_v2/
├── shared_modules/
│   └── ui_web_auto_testing_v2/
│       ├── browser.py
│       ├── element_extractor.py
│       ├── element_structure.py
│       └── llm_test_generation.py
```