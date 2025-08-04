# Security Setup Guide

## Environment Configuration

This project uses environment variables to manage sensitive configuration data. Follow these steps to set up your development environment securely.

### 1. Environment Variables Setup

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` and replace the placeholder values with your actual credentials:

- `OPENAI_API_KEY`: Your OpenAI API key
- `GOOGLE_API_KEY`: Your Google API key  
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `DEEPSEEK_API_KEY`: Your DeepSeek API key
- `COHERE_API_KEY`: Your Cohere API key
- `MONGODB_CONNECTION_STRING`: Your MongoDB connection string
- `MONGODB_HOST`, `MONGODB_PORT`, etc.: Individual MongoDB connection parameters

### 2. MCP Configuration Setup

Copy the MCP configuration templates:

```bash
cp claude_desktop_config.json.example claude_desktop_config.json
cp mcp-config.json.example mcp-config.json
```

Edit these files to include your actual database credentials and configuration.

### 3. MongoDB Setup

For MongoDB access, you have two options:

#### Option A: Connection String
Set `MONGODB_CONNECTION_STRING` with your full connection string:
```
MONGODB_CONNECTION_STRING=mongodb://username:password@host:port/database?authSource=admin
```

#### Option B: Individual Parameters
Set individual MongoDB parameters:
```
MONGODB_HOST=your_host
MONGODB_PORT=27017
MONGODB_USERNAME=your_username
MONGODB_PASSWORD=your_password
MONGODB_DATABASE=your_database
```

### 4. Security Notes

⚠️ **Important Security Practices:**

- Never commit `.env`, `claude_desktop_config.json`, or `mcp-config.json` files to version control
- These files are already listed in `.gitignore`
- Use strong, unique passwords for all services
- Rotate API keys regularly
- Use different credentials for development, staging, and production environments

### 5. Running Tests

The test files have been updated to use environment variables. Before running tests that require database connectivity, ensure your `.env` file is properly configured:

```bash
# Test MongoDB connection
python test_mongo_connection.py

# Test internet access
python test_internet_mongodb_access.py

# Test Compass-style connection
python test_compass_connection.py
```

### 6. Development vs Production

For production deployment:
- Use a secrets management service (AWS Secrets Manager, Azure Key Vault, etc.)
- Set environment variables through your deployment platform
- Never store production credentials in files

## File Structure

```
.env.example                          # Template environment file
claude_desktop_config.json.example    # Template MCP config
mcp-config.json.example              # Template MCP config
.gitignore                           # Ensures sensitive files are not tracked
```

## Support

If you encounter issues with database connectivity or configuration, check:
1. Your environment variables are correctly set
2. Network connectivity to your databases
3. Firewall settings allowing outbound connections
4. Database server is running and accessible
