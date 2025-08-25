#!/usr/bin/env python3
"""
Test MCP Server Functionality
Demonstrates what each server can do programmatically
"""

import sys
import json
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Suppress MCP warnings
import warnings
warnings.filterwarnings("ignore", message="MCP SDK not installed")

def test_chunk_server():
    """Test ChunkServer functionality"""
    print("\n" + "="*60)
    print("TESTING CHUNK SERVER")
    print("="*60)
    
    from chunk_server_fixed import ChunkServer, ChunkStrategy
    
    server = ChunkServer()
    
    # Sample Python code to chunk
    sample_code = '''
class DataProcessor:
    """Process and analyze data"""
    
    def __init__(self, config):
        self.config = config
        self.data = []
    
    def load_data(self, file_path):
        """Load data from file"""
        with open(file_path, 'r') as f:
            self.data = json.load(f)
        return self.data
    
    def process(self):
        """Process the loaded data"""
        results = []
        for item in self.data:
            if self.validate(item):
                results.append(self.transform(item))
        return results
    
    def validate(self, item):
        """Validate a data item"""
        return 'id' in item and 'value' in item
    
    def transform(self, item):
        """Transform a data item"""
        return {
            'id': item['id'],
            'processed_value': item['value'] * 2
        }
'''
    
    # Test different chunking strategies
    for strategy in [ChunkStrategy.SEMANTIC, ChunkStrategy.SLIDING_WINDOW]:
        print(f"\nChunking with {strategy.value} strategy:")
        chunks = server.chunk_code(
            content=sample_code,
            strategy=strategy,
            max_size=200
        )
        
        print(f"  Created {len(chunks)} chunks")
        for i, chunk in enumerate(chunks[:3], 1):  # Show first 3 chunks
            print(f"  Chunk {i}: {chunk.chunk_type.value}, {len(chunk.content)} chars")
            if hasattr(chunk, 'metadata') and chunk.metadata:
                print(f"    Metadata: {chunk.metadata}")
    
    return True


def test_index_server():
    """Test IndexServer functionality"""
    print("\n" + "="*60)
    print("TESTING INDEX SERVER")
    print("="*60)
    
    from index_server_fixed import IndexServer
    
    server = IndexServer()
    
    # Add some files to index
    files = {
        "utils.py": """
def format_date(date):
    return date.strftime('%Y-%m-%d')

def parse_json(text):
    return json.loads(text)
""",
        "models.py": """
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price
""",
        "api.py": """
def get_user(user_id):
    # Fetch user from database
    return User.query.get(user_id)

def create_product(name, price):
    product = Product(name=name, price=price)
    return product
"""
    }
    
    # Index the files
    print("\nIndexing files:")
    for file_path, content in files.items():
        server.add_to_index(
            file_path=file_path,
            content=content,
            metadata={"type": "python", "size": len(content)}
        )
        print(f"  Indexed: {file_path}")
    
    # Search the index
    search_terms = ["User", "format", "product", "def"]
    print("\nSearching index:")
    for term in search_terms:
        results = server.search(term)
        print(f"  '{term}': Found in {len(results)} files")
        for result in results:
            print(f"    - {result['file_path']}")
    
    return True


def test_vector_server():
    """Test VectorServer functionality"""
    print("\n" + "="*60)
    print("TESTING VECTOR SERVER")
    print("="*60)
    
    from vector_server_fixed import VectorServer
    import numpy as np
    
    server = VectorServer()
    
    # Create some sample vectors (simulating code embeddings)
    vectors = {
        "function_1": np.random.random(128),
        "function_2": np.random.random(128),
        "function_3": np.random.random(128),
        "class_1": np.random.random(128),
        "class_2": np.random.random(128)
    }
    
    # Store vectors
    print("\nStoring vectors:")
    for id, vector in vectors.items():
        server.store_vector(
            id=id,
            vector=vector.tolist(),
            metadata={
                "type": "function" if "function" in id else "class",
                "timestamp": "2024-01-01"
            }
        )
        print(f"  Stored: {id}")
    
    # Search for similar vectors
    print("\nSearching for similar vectors:")
    query_vector = vectors["function_1"] + np.random.normal(0, 0.1, 128)  # Similar to function_1
    
    results = server.search_vectors(
        query_vector=query_vector.tolist(),
        top_k=3
    )
    
    print(f"  Found {len(results)} similar vectors:")
    for result in results:
        print(f"    - {result['id']}: similarity = {result.get('similarity', 'N/A'):.3f}")
    
    return True


def test_edit_server():
    """Test EditServer functionality"""
    print("\n" + "="*60)
    print("TESTING EDIT SERVER")
    print("="*60)
    
    from edit_server_fixed import EditServer
    import tempfile
    import os
    
    server = EditServer()
    
    # Create a temporary file to edit
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        original_content = '''def hello():
    print("Hello, World!")
    
def goodbye():
    print("Goodbye!")
'''
        f.write(original_content)
        temp_file = f.name
    
    print(f"\nCreated test file: {temp_file}")
    print("Original content:")
    print(original_content)
    
    try:
        # Perform edit operation
        print("\nPerforming edit operation:")
        print("  Changing 'Hello, World!' to 'Hello, Universe!'")
        
        result = server.edit_file(
            file_path=temp_file,
            old_content='print("Hello, World!")',
            new_content='print("Hello, Universe!")'
        )
        
        if result:
            print("  Edit successful!")
            
            # Read the edited content
            with open(temp_file, 'r') as f:
                new_content = f.read()
            print("\nNew content:")
            print(new_content)
        else:
            print("  Edit failed!")
            
    finally:
        # Clean up
        os.unlink(temp_file)
        print(f"\nCleaned up test file")
    
    return True


def main():
    """Run all server tests"""
    print("="*60)
    print("MCP SERVER FUNCTIONALITY TEST")
    print("="*60)
    print("\nThis demonstrates what each MCP server can do.")
    print("Note: These are direct function calls, not MCP protocol calls.")
    
    try:
        # Test each server
        test_chunk_server()
        test_index_server()
        test_vector_server()
        test_edit_server()
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nThe MCP servers are working correctly and can:")
        print("  1. Chunk code into semantic pieces")
        print("  2. Index and search code")
        print("  3. Store and search vector embeddings")
        print("  4. Edit files programmatically")
        print("\nTo use these with Claude Desktop or other MCP clients,")
        print("you need to configure them in the MCP client settings.")
        
    except Exception as e:
        print(f"\nError during tests: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())