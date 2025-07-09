# Project Structure

This document describes the organized structure of the AI Apps repository.

## Directory Layout

```
ai_apps/
├── apps/                           # AI Applications
│   ├── common/                     # Shared modules across all apps
│   │   ├── config/                 # Configuration modules
│   │   ├── database/               # Database connectivity
│   │   └── services/               # Shared services
│   ├── data_quality/               # Data Quality Application
│   │   ├── dq_generator/           # DQ code generation
│   │   ├── profiling/              # Data profiling modules
│   │   └── requirements.txt        # App-specific dependencies
│   └── ui_web_auto_testing/        # UI Testing Application
│       ├── api/                    # FastAPI backend
│       ├── element_extraction/     # Web element extraction
│       ├── test_generation/        # Test case generation
│       └── requirements.txt        # App-specific dependencies
│
├── bigdata/                        # Big Data Ecosystem
│   ├── docker/                     # Docker configurations
│   │   ├── Dockerfile.pyspark      # PySpark container
│   │   └── docker-compose.*.yml    # Compose configurations
│   ├── scripts/                    # Shell scripts
│   │   ├── bigdata_env.sh          # Environment setup
│   │   └── pyspark_container.sh    # Container management
│   ├── demos/                      # Demo scripts and notebooks
│   │   ├── bigdata_demo.py
│   │   ├── pyspark_demo.py
│   │   └── pyspark_demo.ipynb
│   ├── docs/                       # Big data documentation
│   └── requirements_pyspark.txt    # PySpark dependencies
│
├── ui/                             # React Frontend Application
│   ├── src/                        # Source code
│   │   ├── components/             # React components
│   │   ├── hooks/                  # Custom React hooks
│   │   ├── services/               # API service layer
│   │   ├── types/                  # TypeScript definitions
│   │   └── data/                   # Static data
│   ├── public/                     # Public assets
│   ├── dist/                       # Build output (generated)
│   ├── package.json                # Node dependencies
│   ├── tsconfig.json               # TypeScript config
│   └── vite.config.ts              # Vite bundler config
│
├── docs/                           # Project Documentation
│   ├── architecture/               # Architecture diagrams and docs
│   ├── guides/                     # User and developer guides
│   └── api/                        # API documentation
│
├── infrastructure/                 # Infrastructure & DevOps
│   ├── docker/                     # Docker configurations
│   │   └── docker-compose.core.yml # Core services
│   ├── scripts/                    # Deployment and utility scripts
│   │   ├── build_frontend.sh       # Frontend build script
│   │   ├── run_cross_platform.*    # Cross-platform runners
│   │   └── setup_*.sh              # Setup scripts
│   └── config/                     # Configuration files
│
├── tests/                          # Test Suites
│   ├── ui_tests/                   # UI testing scripts
│   ├── api_tests/                  # API testing scripts
│   └── integration/                # Integration tests
│
├── utils/                          # Utility Modules
│   ├── code_extractor.py           # Code extraction utilities
│   ├── language_prompts.py         # LLM prompt templates
│   ├── platform_utils.py           # Cross-platform utilities
│   ├── playwright_test_runner.py   # Test runner
│   └── web_testing_utils.py        # Web testing utilities
│
├── .env.example                    # Environment template
├── .gitignore                      # Git ignore rules
├── README.md                       # Main documentation
├── requirements.txt                # Python dependencies
└── run.py                          # Main entry point
```

## Key Benefits of This Structure

1. **Separation of Concerns**: Each major component (apps, frontend, bigdata) has its own directory
2. **Modularity**: Apps can be developed and deployed independently
3. **Shared Resources**: Common code is centralized in `apps/common/` and `utils/`
4. **Clear Organization**: Easy to navigate and understand the project layout
5. **Scalability**: New apps can be added to the `apps/` directory without affecting others

## Running the Application

From the root directory:

```bash
# Run the full stack
python run.py

# Or use the platform-specific scripts
./infrastructure/scripts/run_cross_platform.sh  # Linux/macOS
infrastructure\scripts\run_cross_platform.bat    # Windows
```

## Building Components

### Frontend
```bash
cd ui && npm run build
# Or use the helper script
./infrastructure/scripts/build_frontend.sh
```

### Running Tests
```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/ui_tests/
pytest tests/api_tests/
pytest tests/integration/
```

## Adding New Applications

1. Create a new directory under `apps/`
2. Include an `api/` directory with FastAPI routes
3. Add app-specific requirements.txt
4. Update `apps/apps_map.json` with the new app metadata
5. Import the app's router in the main API file

## Docker Development

Big data components can be run using Docker:

```bash
cd bigdata/docker
docker-compose -f docker-compose.pyspark.yml up
```