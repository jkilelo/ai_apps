# Contributing to Dynamic Forms Streaming API

Thank you for your interest in contributing to this project! 🎉

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/dynamic-forms-streaming.git
   cd dynamic-forms-streaming
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the application**:
   ```bash
   python main.py
   ```

## 🔧 Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and single-purpose

### Frontend Guidelines
- Use modern ES6+ JavaScript features
- Follow CSS BEM methodology for class naming
- Ensure responsive design works on all devices
- Test WebSocket functionality thoroughly

### Adding New Forms

1. **Create Pydantic Model**:
   ```python
   class MyNewForm(BaseModel):
       field1: str = Field(..., description="Field 1")
       field2: int = Field(..., ge=1, description="Field 2")
   ```

2. **Add API Endpoint**:
   ```python
   @app.post("/api/my-new-form")
   async def create_my_data(data: MyNewForm):
       # Process data
       return {"success": True, "message": "Data created"}
   ```

3. **Update Endpoints Config** in `get_endpoints()` function

4. **Test the new form** in the browser

### Testing

- Test all form validations (client and server-side)
- Verify WebSocket real-time updates work
- Check responsive design on different screen sizes
- Test error handling and edge cases

## 📝 Pull Request Process

1. **Create a new branch** for your feature:
   ```bash
   git checkout -b feature/amazing-new-feature
   ```

2. **Make your changes** following the guidelines above

3. **Test thoroughly**:
   - Run the application locally
   - Test all form types
   - Verify WebSocket connectivity
   - Check responsive design

4. **Commit your changes**:
   ```bash
   git commit -m "Add amazing new feature"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/amazing-new-feature
   ```

6. **Create a Pull Request** on GitHub with:
   - Clear description of changes
   - Screenshots if UI changes are involved
   - Test results

## 🐛 Bug Reports

When reporting bugs, please include:

- **Environment**: OS, Python version, browser
- **Steps to reproduce** the issue
- **Expected behavior** vs **actual behavior**
- **Screenshots** if applicable
- **Console errors** (browser dev tools)

## 💡 Feature Requests

We welcome feature requests! Please:

1. **Check existing issues** first
2. **Describe the feature** clearly
3. **Explain the use case** and benefits
4. **Consider implementation complexity**

## 🎨 UI/UX Improvements

For design improvements:

- Follow the existing design system
- Maintain accessibility standards
- Ensure mobile responsiveness
- Consider dark mode compatibility

## 📚 Documentation

Help improve documentation by:

- Fixing typos and grammar
- Adding examples and use cases
- Improving API documentation
- Creating tutorials

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- GitHub contributors page

## 📞 Questions?

Feel free to:
- Open an issue for questions
- Start a discussion on GitHub
- Reach out to maintainers

Happy contributing! 🚀
