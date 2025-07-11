# 🚀 Real-time Python Console Streamer

A beautiful, responsive, and modern FastAPI application that streams Python console output to web browsers in real-time using WebSockets, HTML5, CSS3, and ES6.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)
![WebSocket](https://img.shields.io/badge/WebSocket-Real--time-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

### 🎯 Core Functionality
- **Real-time Code Execution**: Execute Python code and see output streamed live
- **WebSocket Integration**: Bidirectional real-time communication
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Modern UI**: Sleek dark theme with animated backgrounds and smooth transitions

### 🛠️ Technical Features
- **FastAPI Backend**: High-performance async Python web framework
- **WebSocket Streaming**: Real-time output streaming without page refresh
- **ES6 JavaScript**: Modern client-side functionality with classes and async/await
- **CSS3 Animations**: Smooth transitions, gradients, and hover effects
- **HTML5 Semantic**: Accessible and SEO-friendly markup

### 🎨 User Experience
- **Syntax Highlighting**: Basic Python syntax highlighting in output
- **Code Examples**: Pre-built examples for quick testing
- **Keyboard Shortcuts**: Efficient navigation and code execution
- **Performance Metrics**: Live execution stats and uptime tracking
- **Auto-scroll**: Automatic scrolling to latest output
- **Toast Notifications**: User-friendly feedback messages

### 📱 Responsive Features
- **Mobile-First Design**: Optimized for all screen sizes
- **Touch-Friendly**: Large touch targets and gesture support
- **Progressive Enhancement**: Works without JavaScript (basic functionality)
- **Accessibility**: WCAG compliant with keyboard navigation

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone or download the project files**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python realtime_console.py
   ```

4. **Open your browser and navigate to:**
   ```
   http://localhost:8001
   ```

## 📖 Usage

### Basic Usage
1. **Enter Python Code**: Type your Python code in the editor panel
2. **Execute**: Click "Execute Code" or press `Ctrl+Enter`
3. **Watch Output**: See real-time output in the console panel
4. **Clear Output**: Click "Clear Output" or press `Ctrl+K`

### Code Examples
The app includes several built-in examples:
- **Hello World Loop**: Simple iteration with delays
- **Real-time Data Generation**: Simulated data streaming
- **Progress Bar Simulation**: Visual progress indicators
- **File Processing Demo**: Batch processing simulation
- **System Monitoring**: Mock system stats display

### Keyboard Shortcuts
- `Ctrl + Enter`: Execute the current code
- `Ctrl + K`: Clear the console output
- `Ctrl + R`: Reload the page
- `Tab`: Navigate between elements

## 🏗️ Architecture

### Backend Structure
```
realtime_console.py          # Main FastAPI application
├── ConnectionManager        # WebSocket connection management
├── WebSocket Endpoints      # Real-time communication handlers
├── HTTP Endpoints          # REST API for examples and static content
└── Code Execution Engine   # Safe Python code execution
```

### Frontend Structure
```
static/
├── style.css               # Modern CSS3 styling with animations
└── app.js                  # ES6 JavaScript with WebSocket client

templates/
└── console_dashboard.html  # Main HTML5 dashboard template
```

### Key Components

#### WebSocket Communication
```javascript
// Client-side WebSocket handling
class ConsoleStreamer {
    constructor() {
        this.setupWebSocket();
        this.setupEventListeners();
    }
    
    handleMessage(message) {
        // Real-time message processing
    }
}
```

#### Python Code Execution
```python
async def execute_python_code(code: str, websocket: WebSocket):
    """Execute Python code and stream output in real-time"""
    process = subprocess.Popen(
        [sys.executable, "-c", code],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    # Stream output line by line...
```

## 🎨 Design Features

### Modern CSS3 Styling
- **CSS Custom Properties**: Consistent theming with CSS variables
- **Flexbox & Grid**: Modern layout techniques
- **Animations**: Smooth transitions and hover effects
- **Responsive Design**: Mobile-first approach with breakpoints
- **Dark Theme**: Eye-friendly color scheme

### Interactive Elements
- **Glassmorphism**: Blurred background effects
- **Gradient Animations**: Dynamic background gradients
- **Hover States**: Interactive feedback on all clickable elements
- **Loading States**: Visual feedback during code execution

## 🔧 Configuration

### Environment Variables
You can customize the application by setting these environment variables:

```bash
# Server configuration
HOST=0.0.0.0                # Server host (default: 0.0.0.0)
PORT=8001                   # Server port (default: 8001)

# WebSocket configuration
WS_TIMEOUT=30               # WebSocket timeout in seconds
MAX_CONNECTIONS=100         # Maximum concurrent connections

# Code execution limits
EXECUTION_TIMEOUT=30        # Max execution time per code block
MAX_OUTPUT_LINES=1000       # Maximum output lines to retain
```

### Customization Options

#### Adding Custom Examples
Edit the `get_examples()` function in `realtime_console.py`:

```python
@app.get("/examples")
async def get_examples():
    examples = [
        {
            "name": "Your Custom Example",
            "code": """# Your Python code here
print("Hello, Custom World!")"""
        }
        # Add more examples...
    ]
    return examples
```

#### Styling Customization
Modify CSS variables in `static/style.css`:

```css
:root {
    --primary-color: #your-color;
    --bg-primary: #your-background;
    /* Customize other variables... */
}
```

## 🛡️ Security Considerations

### Code Execution Safety
- **Subprocess Isolation**: Code runs in separate processes
- **Timeout Protection**: Execution time limits prevent infinite loops
- **Output Limiting**: Prevents memory exhaustion from excessive output

### WebSocket Security
- **Connection Limits**: Maximum concurrent connections
- **Input Validation**: Sanitized message handling
- **Error Handling**: Graceful degradation on connection issues

### Recommended Security Measures
For production deployment, consider:
1. **Sandboxing**: Use Docker containers or virtual environments
2. **Resource Limits**: Implement CPU and memory restrictions
3. **Authentication**: Add user authentication if needed
4. **Rate Limiting**: Prevent abuse with rate limiting
5. **Input Filtering**: Restrict dangerous Python modules/functions

## 📊 Performance

### Optimization Features
- **Async Operations**: Non-blocking WebSocket handling
- **Efficient Output Streaming**: Line-by-line real-time streaming
- **Memory Management**: Automatic cleanup of old output lines
- **Connection Pooling**: Efficient WebSocket connection management

### Performance Metrics
The app tracks and displays:
- **Execution Count**: Number of code executions
- **Output Lines**: Total lines of output received
- **Uptime**: Application uptime tracking
- **Connection Status**: Real-time connection health

## 🧪 Development

### Project Structure
```
beautiful_pages/
├── realtime_console.py      # Main application
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── static/
│   ├── style.css           # CSS styling
│   └── app.js              # JavaScript functionality
└── templates/
    └── console_dashboard.html  # Main template
```

### Development Setup
1. **Install development dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run in development mode:**
   ```bash
   uvicorn realtime_console:app --reload --host 0.0.0.0 --port 8001
   ```

3. **Enable debug mode** by setting `reload=True` in the `uvicorn.run()` call

### Testing
The application includes:
- **WebSocket Connection Tests**: Verify real-time communication
- **Code Execution Tests**: Test Python code execution safety
- **UI Responsiveness Tests**: Cross-browser compatibility
- **Performance Tests**: Load testing for multiple connections

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 for Python code
- Use modern ES6+ JavaScript features
- Maintain responsive design principles
- Write descriptive commit messages
- Add comments for complex functionality

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI**: Amazing async web framework
- **WebSocket**: Real-time communication protocol
- **Modern Web Technologies**: HTML5, CSS3, ES6
- **Open Source Community**: For inspiration and best practices

## 📞 Support

If you encounter any issues or have questions:

1. **Check the Issues**: Look for existing solutions
2. **Create an Issue**: Report bugs or request features
3. **Read the Code**: The codebase is well-documented
4. **Join Discussions**: Participate in community discussions

---

**Made with ❤️ and modern web technologies for real-time Python code execution and streaming.**
