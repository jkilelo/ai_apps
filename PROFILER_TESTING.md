# AI-Powered Data Profiler Testing Guide

## Overview
The AI-Powered Data Profiler has been successfully integrated into the AI Apps Suite. It provides comprehensive data quality analysis with ML insights and real-time monitoring capabilities.

## How to Access

1. **Start the React Development Server** (if not already running):
   ```bash
   cd /var/www/ai_apps/ui
   npm run dev
   ```
   The UI will be available at http://localhost:3000

2. **Navigate to Data Quality App**:
   - Click on "Data Quality" in the sidebar
   - Select "AI-Powered Data Profiler" (the third sub-app)

## Features Implemented

### 1. **Data Source Selection**
   - Pre-configured synthetic datasets (Retail, Finance, Healthcare, IoT)
   - Support for database, file, streaming, and API connections
   - Custom connection configuration

### 2. **Comprehensive Profiling**
   - Column-level statistics and distributions
   - Data quality dimensions (completeness, validity, uniqueness, consistency)
   - Pattern detection and regex generation
   - Missing value analysis
   - Outlier detection

### 3. **ML-Powered Insights**
   - Anomaly detection using Isolation Forest, DBSCAN, and PCA
   - Pattern discovery and clustering
   - Correlation analysis (linear and non-linear)
   - Predictive quality insights

### 4. **Quality Rules Engine**
   - AI-generated quality rules based on profile results
   - Rule customization and management
   - SQL, PySpark, and Python code generation
   - Batch rule execution with detailed results

### 5. **Real-Time Monitoring**
   - Live quality metrics tracking
   - Configurable update intervals
   - Alert system for quality issues
   - Performance statistics

### 6. **Data Catalog**
   - Searchable data asset inventory
   - Quality scores and metadata
   - Data lineage visualization
   - Tagging and favorites

## Architecture

### Frontend Components
- `DataQualityApp.tsx` - Main application container
- `DataSourceSelector.tsx` - Data source configuration
- `ProfileResults.tsx` - Profile visualization
- `QualityRules.tsx` - Rule management
- `MLInsights.tsx` - ML analysis display
- `RealTimeMonitor.tsx` - Live monitoring
- `DataCatalog.tsx` - Data catalog interface

### Backend Components
- `enhanced_profiler.py` - ML-enhanced profiling engine
- `spark_generator.py` - Distributed profiling code generation
- `api/router.py` - FastAPI endpoints
- `useDataQualityAPI.ts` - API integration hook

### API Endpoints
- `POST /api/data-quality/profile` - Run data profiling
- `POST /api/data-quality/rules/generate` - Generate quality rules
- `POST /api/data-quality/rules/execute` - Execute quality rules
- `POST /api/data-quality/ml-insights` - Get ML insights
- `POST /api/data-quality/monitor/start` - Start monitoring
- `GET /api/data-quality/catalog` - Get catalog data
- `WS /ws/data-quality/{session_id}` - WebSocket for real-time updates

## Testing the Profiler

1. **Basic Profiling Test**:
   - Select "Retail Analytics Dataset" from data sources
   - Click "Run Profile"
   - View comprehensive results in the Profile tab

2. **ML Insights Test**:
   - After profiling, switch to "ML Insights" tab
   - Review anomaly detection results
   - Check pattern discovery and correlations

3. **Quality Rules Test**:
   - Go to "Rules" tab after profiling
   - Review auto-generated rules
   - Click "Execute Rules" to validate data

4. **Real-Time Monitoring Test**:
   - Switch to "Monitor" tab
   - Click "Start" to begin monitoring
   - Observe live metrics and alerts

## Mock Data
The system currently uses mock data generation for demonstration:
- Customer data with demographics
- Transaction records
- Product catalog
- IoT sensor readings

## Next Steps
1. Connect to real PySpark cluster for actual data processing
2. Implement data lineage tracking
3. Add automated remediation suggestions
4. Integrate with existing synthetic data in `/workspace/generated_data`

## Troubleshooting

If the API is not responding:
1. Check server is running: `ps aux | grep python | grep uvicorn`
2. Verify port 8002 is listening: `netstat -tulpn | grep 8002`
3. Check logs: `tail -f /var/www/ai_apps/logs/*.log`

## Technical Details
- Built with React, TypeScript, and Tailwind CSS
- FastAPI backend with async support
- WebSocket integration for real-time updates
- Scikit-learn for ML algorithms
- Supports PySpark code generation for big data