# Theming System - Developer vs Executive Views

## Overview

The Data Profiling & Quality Analysis application now supports two distinct viewing modes to cater to different audiences:

### 🔧 Developer Mode (Technical View)
- **Audience**: Technical teams, data engineers, developers
- **Features**: 
  - Raw JSON data display with syntax highlighting
  - Complete technical details and code outputs
  - Full PySpark code visibility
  - Detailed error messages and stack traces
  - Technical step-by-step progression

### 📊 Executive Mode (Business View)
- **Audience**: Senior management, business stakeholders, executives
- **Features**:
  - Clean, business-friendly summaries
  - Key insights and outcomes in plain language
  - Color-coded results with visual indicators
  - Strategic recommendations and actionable items
  - No technical jargon or raw code

## How to Use

### Switching Between Views
1. Look for the **View Mode Toggle** in the top-right corner of the screen
2. Click **Developer** for technical details
3. Click **Executive** for business-friendly summaries
4. The view persists throughout your session

### View Mode Features

#### Developer Mode
```
✅ Current Design (Preserved)
- JSON code display with formatting
- Technical error messages
- Raw API responses
- PySpark code generation output
- Database schema details
```

#### Executive Mode
```
✅ New Business-Friendly Design
- "Database Schema Analysis" instead of raw metadata
- "Data Optimization Recommendations" with clear bullet points
- "Quality Assurance Framework" with business language
- Color-coded insights with visual icons
- Strategic summaries and outcomes
```

## Benefits

### For Development Teams
- Keep the detailed technical view they love
- Debug issues with full context
- Access complete code and configurations
- Technical precision maintained

### For Management
- Quick understanding of analysis outcomes
- Strategic insights without technical noise
- Professional presentation format
- Focus on business value and recommendations

## Technical Implementation

The theming system uses React Context API:
- `ThemeContext` manages view mode state
- `ViewModeToggle` provides UI switching
- `ExecutiveResultsDisplay` formats data for business view
- Conditional rendering preserves existing developer experience

## Example Transformations

### Step: "Profiling Suggestions"

**Developer Mode:**
```json
{
  "suggestions": [
    {
      "suggestion_id": 1,
      "description": "Add index on primary key"
    }
  ]
}
```

**Executive Mode:**
```
📈 Data Optimization Recommendations
3 strategic recommendations identified for database optimization

Key Outcomes:
• Add index on primary key
• Normalize data structure  
• Implement foreign key constraints
```

This dual-mode approach ensures technical teams get the detail they need while executives get the strategic insights they want, all from the same powerful analysis engine.
