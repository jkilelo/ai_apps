"""
MongoDB Database Connection and Configuration
Handles connection to MongoDB and provides access to collections
"""

import os
import logging
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    """
    MongoDB database connection manager
    """
    
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None
        self._connection_string = self._get_connection_string()
        self._database_name = os.getenv('MONGODB_DATABASE', 'ai_apps_db')
        
    def _get_connection_string(self) -> str:
        """
        Build MongoDB connection string from environment variables
        """
        # Try to get full connection string first
        connection_string = os.getenv('MONGODB_CONNECTION_STRING')
        if connection_string:
            return connection_string
            
        # Build connection string from individual components
        username = os.getenv('MONGODB_USERNAME', '')
        password = os.getenv('MONGODB_PASSWORD', '')
        host = os.getenv('MONGODB_HOST', 'localhost')
        port = os.getenv('MONGODB_PORT', '27017')
        auth_source = os.getenv('MONGODB_AUTH_SOURCE', 'admin')
        
        if username and password:
            return f"mongodb://{username}:{password}@{host}:{port}/?authSource={auth_source}"
        else:
            return f"mongodb://{host}:{port}/"
    
    def connect(self) -> bool:
        """
        Establish connection to MongoDB
        Returns True if successful, False otherwise
        """
        try:
            self.client = MongoClient(
                self._connection_string,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=10000,         # 10 second connection timeout
                socketTimeoutMS=10000,          # 10 second socket timeout
                maxPoolSize=10,                 # Maximum number of connections
                retryWrites=True
            )
            
            # Test the connection
            self.client.admin.command('ping')
            self.database = self.client[self._database_name]
            
            logger.info(f"Successfully connected to MongoDB database: {self._database_name}")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            return False
    
    def disconnect(self):
        """
        Close MongoDB connection
        """
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    def get_database(self) -> Optional[Database]:
        """
        Get the database instance
        """
        return self.database
    
    def get_collection(self, collection_name: str) -> Optional[Collection]:
        """
        Get a specific collection from the database
        """
        if self.database is None:
            logger.error("Database not connected")
            return None
        return self.database[collection_name]

# Global database connection instance
db_connection = DatabaseConnection()

def get_ai_apps_collection() -> Optional[Collection]:
    """
    Get the ai_apps collection
    Returns the collection if connected, None otherwise
    """
    if db_connection.database is None:
        if not db_connection.connect():
            return None
    
    collection = db_connection.get_collection('ai_apps')
    
    # Create indexes for better performance
    try:
        # Create index on commonly queried fields
        collection.create_index("name")
        collection.create_index("created_at")
        collection.create_index("status")
        collection.create_index([("name", 1), ("version", 1)], unique=True)
        
        logger.info("Created indexes for ai_apps collection")
    except Exception as e:
        logger.warning(f"Could not create indexes: {e}")
    
    return collection

def initialize_database():
    """
    Initialize database connection and create necessary collections
    """
    logger.info("Initializing database connection...")
    
    if not db_connection.connect():
        logger.error("Failed to initialize database connection")
        return False
    
    # Create ai_apps collection and verify it exists
    ai_apps_collection = get_ai_apps_collection()
    if ai_apps_collection is not None:
        logger.info("ai_apps collection is ready")
        
        # Insert a sample document if collection is empty (for testing)
        if ai_apps_collection.count_documents({}) == 0:
            sample_doc = {
                "name": "sample_ai_app",
                "version": "1.0.0",
                "description": "Sample AI application",
                "status": "active",
                "created_at": "2025-07-07T00:00:00Z",
                "updated_at": "2025-07-07T00:00:00Z",
                "metadata": {
                    "framework": "react",
                    "ai_model": "gpt-4",
                    "deployment_status": "development"
                }
            }
            
            try:
                ai_apps_collection.insert_one(sample_doc)
                logger.info("Inserted sample document into ai_apps collection")
            except Exception as e:
                logger.warning(f"Could not insert sample document: {e}")
        
        return True
    else:
        logger.error("Failed to create ai_apps collection")
        return False

def get_database_stats():
    """
    Get database statistics
    """
    if db_connection.database is None:
        return {"error": "Database not connected"}
    
    try:
        stats = db_connection.database.command("dbStats")
        collections = db_connection.database.list_collection_names()
        
        return {
            "database_name": db_connection._database_name,
            "collections": collections,
            "storage_size": stats.get("storageSize", 0),
            "data_size": stats.get("dataSize", 0),
            "index_size": stats.get("indexSize", 0),
            "objects": stats.get("objects", 0)
        }
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return {"error": str(e)}

# Utility functions for common operations
def insert_ai_app(app_data: dict) -> Optional[str]:
    """
    Insert a new AI app into the collection
    Returns the inserted document ID or None if failed
    """
    collection = get_ai_apps_collection()
    if not collection:
        return None
    
    try:
        from datetime import datetime
        app_data['created_at'] = datetime.utcnow().isoformat() + 'Z'
        app_data['updated_at'] = app_data['created_at']
        
        result = collection.insert_one(app_data)
        logger.info(f"Inserted AI app: {app_data.get('name', 'Unknown')}")
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error inserting AI app: {e}")
        return None

def find_ai_apps(query: dict = None, limit: int = 50) -> list:
    """
    Find AI apps based on query
    """
    collection = get_ai_apps_collection()
    if not collection:
        return []
    
    try:
        query = query or {}
        return list(collection.find(query).limit(limit))
    except Exception as e:
        logger.error(f"Error finding AI apps: {e}")
        return []

def update_ai_app(app_id: str, update_data: dict) -> bool:
    """
    Update an AI app by ID
    """
    collection = get_ai_apps_collection()
    if not collection:
        return False
    
    try:
        from datetime import datetime
        from bson import ObjectId
        
        update_data['updated_at'] = datetime.utcnow().isoformat() + 'Z'
        
        result = collection.update_one(
            {"_id": ObjectId(app_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
    except Exception as e:
        logger.error(f"Error updating AI app: {e}")
        return False

def delete_ai_app(app_id: str) -> bool:
    """
    Delete an AI app by ID
    """
    collection = get_ai_apps_collection()
    if not collection:
        return False
    
    try:
        from bson import ObjectId
        result = collection.delete_one({"_id": ObjectId(app_id)})
        return result.deleted_count > 0
    except Exception as e:
        logger.error(f"Error deleting AI app: {e}")
        return False

# Initialize database when module is imported
if __name__ == "__main__":
    # This runs when the script is executed directly
    initialize_database()
    stats = get_database_stats()
    print("Database Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")