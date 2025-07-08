#!/usr/bin/env python3
"""
Script to save apps_map.json to MongoDB
This script loads the apps_map.json file and saves it to MongoDB database
"""

import json
import os
import sys
from datetime import datetime, timezone
from typing import List, Dict, Any
import logging

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_connection, get_ai_apps_collection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_apps_map_json(file_path: str) -> List[Dict[str, Any]]:
    """
    Load the apps_map.json file
    
    Args:
        file_path: Path to the apps_map.json file
        
    Returns:
        List of app configurations
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        logger.info(f"Successfully loaded apps_map.json from {file_path}")
        logger.info(f"Found {len(data)} apps in the configuration")
        
        return data
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in file {file_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading file {file_path}: {e}")
        raise

def prepare_apps_for_mongo(apps_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Prepare apps data for MongoDB insertion by adding metadata
    
    Args:
        apps_data: List of app configurations
        
    Returns:
        List of app configurations with added metadata
    """
    prepared_apps = []
    
    for app in apps_data:
        # Create a copy of the app data
        app_document = app.copy()
        
        # Add metadata fields
        app_document['created_at'] = datetime.now(timezone.utc)
        app_document['updated_at'] = datetime.now(timezone.utc)
        app_document['status'] = 'active'
        app_document['source'] = 'apps_map.json'
        
        # Add a unique identifier combining name and version
        app_document['app_key'] = f"{app['name']}_{app['version']}"
        
        prepared_apps.append(app_document)
        
        logger.info(f"Prepared app: {app['name']} (version: {app['version']})")
    
    return prepared_apps

def save_apps_to_mongo(apps_data: List[Dict[str, Any]]) -> bool:
    """
    Save apps data to MongoDB
    
    Args:
        apps_data: List of app configurations to save
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get the collection
        collection = get_ai_apps_collection()
        if collection is None:
            logger.error("Failed to get ai_apps collection")
            return False
        
        # Clear existing data (optional - remove this if you want to keep existing data)
        logger.info("Clearing existing apps data...")
        delete_result = collection.delete_many({"source": "apps_map.json"})
        logger.info(f"Deleted {delete_result.deleted_count} existing documents")
        
        # Insert new data
        logger.info(f"Inserting {len(apps_data)} apps into MongoDB...")
        insert_result = collection.insert_many(apps_data)
        
        logger.info(f"Successfully inserted {len(insert_result.inserted_ids)} apps")
        
        # Verify the insertion
        count = collection.count_documents({"source": "apps_map.json"})
        logger.info(f"Total apps from apps_map.json in database: {count}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error saving apps to MongoDB: {e}")
        return False

def main():
    """
    Main function to execute the save operation
    """
    try:
        # Define the path to the apps_map.json file
        apps_map_file = os.path.join(os.path.dirname(__file__), 'apps', 'apps_map.json')
        
        logger.info("Starting apps_map.json to MongoDB save operation")
        
        # Load the JSON file
        apps_data = load_apps_map_json(apps_map_file)
        
        # Prepare data for MongoDB
        prepared_apps = prepare_apps_for_mongo(apps_data)
        
        # Save to MongoDB
        if save_apps_to_mongo(prepared_apps):
            logger.info("Successfully saved apps_map.json to MongoDB")
            
            # Print summary
            print("\n" + "="*50)
            print("SAVE OPERATION COMPLETED SUCCESSFULLY")
            print("="*50)
            print(f"Apps saved: {len(prepared_apps)}")
            for app in prepared_apps:
                print(f"- {app['name']} (v{app['version']})")
            print("="*50)
            
        else:
            logger.error("Failed to save apps_map.json to MongoDB")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        sys.exit(1)
    
    finally:
        # Ensure database connection is closed
        db_connection.disconnect()

if __name__ == "__main__":
    main()
