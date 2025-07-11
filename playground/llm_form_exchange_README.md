# LLM Form Exchange System

A pure ES6, HTML5, CSS3, Python 3.12, and Pydantic v2 implementation of an interactive form exchange system between a user and an LLM.

## Features

- **Dynamic Form Generation**: LLM generates forms based on user responses
- **Multi-step Conversation**: Progressive form flow with context awareness
- **Modern Tech Stack**:
  - Pure ES6 JavaScript (no frameworks)
  - HTML5 semantic markup
  - CSS3 with modern styling (animations, gradients, flexbox)
  - Python 3.12 with FastAPI
  - Pydantic v2 for data validation
- **Form Types Supported**:
  - Text inputs
  - Textareas
  - Select dropdowns
  - Radio buttons
  - Checkboxes
  - Email inputs
- **Responsive Design**: Works on desktop and mobile
- **Session Management**: Maintains conversation context

## Architecture

### Backend (Python/FastAPI)
- RESTful API endpoints
- Session-based conversation tracking
- Dynamic form template system
- Pydantic models for request/response validation

### Frontend (Pure JavaScript)
- ES6 class-based architecture
- Async/await for API calls
- Dynamic form rendering
- No external dependencies

## Flow

1. User clicks "Start Conversation"
2. Backend sends initial form asking about interests
3. User fills form and submits
4. Backend processes response and generates contextual follow-up form
5. Process continues for multiple steps
6. Final completion message with personalized content

## Running the Application

```bash
python llm_form_exchange.py
```

Visit http://localhost:8000 to start the conversation.

## API Endpoints

- `POST /api/start` - Start a new conversation
- `POST /api/submit` - Submit form data and get next form
- `GET /api/session/{session_id}` - Debug endpoint to view session data

## Example Conversation Flow

1. **Initial Form**: Name, interests, experience
2. **Follow-up Form**: Based on interest (e.g., Technology → programming languages)
3. **Recommendation Form**: Feedback and final thoughts
4. **Completion**: Personalized thank you message

## Customization

Forms can be customized by modifying the `FORM_TEMPLATES` dictionary in the backend. The system supports branching logic based on user responses.