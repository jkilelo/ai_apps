# Dynamic Forms Streaming API

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![WebSocket](https://img.shields.io/badge/WebSocket-FF6B6B?style=for-the-badge&logo=websocket)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

A beautiful, responsive FastAPI application that automatically generates modern HTML5/CSS3/ES6 forms for interacting with API endpoints, featuring real-time WebSocket streaming and comprehensive form validation.

## 🚀 Live Demo

```bash
git clone https://github.com/yourusername/dynamic-forms-streaming.git
cd dynamic-forms-streaming
pip install -r requirements.txt
python main.py
```

Visit `http://localhost:8000` to see the application in action!

## ✨ Screenshots

![Dashboard](https://via.placeholder.com/800x400/667eea/ffffff?text=Dynamic+Forms+Dashboard)
*Modern dashboard with real-time form generation*

![Form Example](https://via.placeholder.com/800x400/764ba2/ffffff?text=Dynamic+Form+Example)
*Auto-generated form with real-time validation*

## Features

### 🎨 **Modern UI/UX**
- Beautiful, responsive design with CSS Grid and Flexbox
- Modern color palette with gradient backgrounds
- Smooth animations and transitions
- Dark sidebar with elegant typography
- Toast notifications for user feedback

### 🚀 **Dynamic Form Generation**
- Automatically generates forms from Pydantic models
- Supports all HTML5 input types (text, email, number, date, etc.)
- Smart field type detection based on model annotations
- Custom components for tags, ranges, and complex inputs
- Real-time client-side validation

### 📡 **Real-time Features**
- WebSocket connection for live updates
- Real-time form submission notifications
- Live activity feed showing all user interactions
- Connection status indicator
- Automatic reconnection on connection loss

### 🔧 **Technical Features**
- FastAPI backend with Pydantic models
- ES6 JavaScript client with modern async/await
- RESTful API endpoints with OpenAPI documentation
- Comprehensive error handling and validation
- Responsive design for mobile and desktop
- Accessibility features and ARIA support

## Included Form Types

1. **User Profile** - Personal information with validation
2. **Product Catalog** - Product creation with categories and ratings
3. **Contact Messages** - Customer support and inquiries
4. **Feedback & Ratings** - Multi-dimensional rating system
5. **Newsletter Subscription** - Email preferences and consent management

## Technology Stack

- **Backend**: FastAPI, Pydantic, WebSockets
- **Frontend**: HTML5, CSS3, ES6 JavaScript
- **UI**: Feather Icons, Inter Font, Custom CSS Grid
- **Real-time**: WebSocket streaming
- **Validation**: Client-side and server-side validation

## Installation & Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python main.py
   ```
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Access the Application**:
   - Open your browser and navigate to: http://localhost:8000
   - The API documentation is available at: http://localhost:8000/docs

## Usage

### Basic Workflow

1. **Select an Endpoint**: Choose from the sidebar to load a form
2. **Fill the Form**: Complete the automatically generated form fields
3. **Real-time Validation**: See validation feedback as you type
4. **Submit**: Send data to the API endpoint
5. **Live Updates**: Watch real-time notifications from other users

### Form Features

- **Smart Validation**: Real-time client-side validation with visual feedback
- **Rich Input Types**: Support for text, email, numbers, dates, selections, and more
- **Tags Input**: Dynamic tag management with keyboard shortcuts
- **Range Sliders**: Interactive sliders for ratings and numeric ranges
- **File Uploads**: Support for file upload fields (configurable)
- **Conditional Fields**: Show/hide fields based on other field values

### WebSocket Features

- **Live Notifications**: Real-time updates when forms are submitted
- **Activity Feed**: Live stream of all user interactions
- **Connection Status**: Visual indicator of WebSocket connection
- **Auto-reconnect**: Automatic reconnection on connection loss

## API Endpoints

### Core Endpoints

- `GET /` - Main dashboard interface
- `GET /api/endpoints` - Get available endpoints and their schemas
- `WebSocket /ws` - Real-time updates connection

### Form Endpoints

- `POST /api/user-profile` - Create user profile
- `POST /api/product` - Add new product
- `POST /api/contact` - Send contact message
- `POST /api/feedback` - Submit feedback and ratings
- `POST /api/newsletter` - Newsletter subscription

### Data Endpoints

- `GET /api/data/{data_type}` - Retrieve stored data

## Customization

### Adding New Forms

1. **Create Pydantic Model**:
   ```python
   class MyModel(BaseModel):
       field1: str = Field(..., description="Field 1")
       field2: int = Field(..., ge=1, le=100, description="Field 2")
   ```

2. **Add Form Endpoint**:
   ```python
   @app.post("/api/my-endpoint")
   async def create_my_data(data: MyModel):
       # Process data
       return {"success": True, "message": "Data created"}
   ```

3. **Update Endpoints Config**:
   ```python
   # Add to get_endpoints() function
   '/api/my-endpoint': {
       'method': 'POST',
       'title': 'My Form',
       'description': 'Description of my form',
       'icon': 'icon-name',
       'schema': FormGenerator.pydantic_to_form_schema(MyModel)
   }
   ```

### Styling Customization

The CSS uses CSS custom properties (variables) for easy theming:

```css
:root {
    --primary-color: #667eea;
    --secondary-color: #764ba2;
    --accent-color: #f093fb;
    /* ... more variables ... */
}
```

### Field Type Mapping

The form generator automatically maps Pydantic types to HTML input types:

- `str` → `text` input
- `EmailStr` → `email` input
- `int`/`float` → `number` input
- `bool` → `checkbox` input
- `date` → `date` input
- `Enum` → `select` dropdown
- `List[str]` → `tags` input

## Browser Support

- Chrome 88+
- Firefox 85+
- Safari 14+
- Edge 88+

## Performance Features

- **Efficient DOM Updates**: Minimal DOM manipulation for better performance
- **Debounced Validation**: Prevents excessive validation calls
- **Lazy Loading**: Components load as needed
- **Memory Management**: Proper cleanup of event listeners and WebSocket connections
- **Responsive Images**: Optimized for different screen sizes

## Security Features

- **Input Validation**: Comprehensive client and server-side validation
- **XSS Protection**: Proper HTML escaping and sanitization
- **CSRF Protection**: Token-based protection (configurable)
- **WebSocket Security**: Secure WebSocket connections with proper error handling

## Development

### Project Structure

```
dynamic_forms_streaming/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── static/
│   ├── styles.css         # Modern CSS styles
│   └── app.js            # ES6 JavaScript client
└── templates/
    └── dashboard.html     # Main dashboard template
```

### Adding Features

1. **New Field Types**: Extend the `FormGenerator` class
2. **Custom Validation**: Add validation rules in Pydantic models
3. **UI Components**: Create new CSS classes and JavaScript handlers
4. **WebSocket Events**: Add new message types and handlers

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

---

**Built with ❤️ using FastAPI, modern web technologies, and attention to user experience.**
