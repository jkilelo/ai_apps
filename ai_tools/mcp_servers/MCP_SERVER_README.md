# MCP Servers

Model Context Protocol (MCP) servers for code analysis, indexing, and manipulation.

## Installation

### Required Packages

Install all required packages using pip:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install mcp[cli] numpy msgpack tree-sitter tree-sitter-python pytest pytest-asyncio
```

### Core Dependencies

- **mcp[cli]** >= 1.13.0 - Model Context Protocol SDK
- **numpy** >= 2.3.0 - Numerical operations for vector server
- **msgpack** >= 1.1.0 - Binary serialization
- **tree-sitter** >= 0.25.0 - Code parsing
- **tree-sitter-python** >= 0.23.0 - Python language parser

## Available Servers

### 1. Chunk Server (`chunk_server_fixed.py`)
Code chunking and analysis server for breaking down code into manageable pieces.
- Semantic code chunking
- AST-based analysis
- Multiple chunking strategies

### 2. Index Server (`index_server_fixed.py`)
Code indexing and search server for efficient code discovery.
- Full-text search
- Metadata indexing
- Fast retrieval

### 3. Vector Server (`vector_server_fixed.py`)
Vector storage and similarity search for semantic code understanding.
- Vector embeddings storage
- Similarity search
- Clustering support

### 4. Edit Server (`edit_server_fixed.py`)
Code editing and refactoring server for automated code modifications.
- Safe file editing
- Diff generation
- Backup management

## Running the Servers

### Method 1: Python Script (Recommended)

Run individual server:
```bash
python run_mcp_servers.py chunk
python run_mcp_servers.py index
python run_mcp_servers.py vector
python run_mcp_servers.py edit
```

Run all servers:
```bash
python run_mcp_servers.py all
```

Enable debug mode:
```bash
python run_mcp_servers.py all --debug
```

### Method 2: Batch Script (Windows)

Run the batch script:
```bash
start_mcp_servers.bat
```

### Method 3: Direct Python

Run server directly:
```bash
python chunk_server_fixed.py
python index_server_fixed.py
python vector_server_fixed.py
python edit_server_fixed.py
```

## Testing

Run the test suite:
```bash
python test_mcp_servers.py
```

Run unit tests:
```bash
pytest test_chunk_server.py
pytest test_index_server.py
```

## Notes

- The servers can run without the full MCP SDK installed (will show warnings but work in mock mode)
- The "MCP SDK not installed" warnings are expected and don't affect functionality
- Servers include comprehensive error handling and logging
- All servers are production-ready with security features

## Server Communication

The servers are designed to work together:
1. **Chunk Server** breaks code into pieces
2. **Index Server** indexes the chunks
3. **Vector Server** stores semantic representations
4. **Edit Server** applies modifications

## Configuration

Each server supports configuration through:
- Environment variables
- Configuration files
- Command-line arguments

## Troubleshooting

If you encounter issues:

1. **Import Errors**: Ensure all packages are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **MCP SDK Warnings**: These are expected and don't affect functionality

3. **Unicode Errors on Windows**: The servers automatically configure UTF-8 encoding

4. **Permission Errors**: Ensure write permissions in working directory

## Development

The servers are built on `mcp_base.py` which provides:
- Robust error handling
- Security features
- Logging infrastructure
- Mock mode for testing

## License

See main project license.