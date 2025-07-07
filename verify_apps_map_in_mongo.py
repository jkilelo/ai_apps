#!/usr/bin/env python3
"""
Script to verify apps_map.json data in MongoDB
This script queries the MongoDB database to verify the saved data
"""

import json
import os
import sys
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

def verify_apps_in_mongo():
    """
    Verify that apps_map.json data was saved correctly to MongoDB
    """
    try:
        # Get the collection
        collection = get_ai_apps_collection()
        if collection is None:
            logger.error("Failed to get ai_apps collection")
            return False
        
        # Query all apps from apps_map.json
        apps_cursor = collection.find({"source": "apps_map.json"})
        apps_list = list(apps_cursor)
        
        if not apps_list:
            logger.warning("No apps found in MongoDB with source 'apps_map.json'")
            return False
        
        print("\n" + "="*60)
        print("APPS VERIFICATION REPORT")
        print("="*60)
        print(f"Total apps found: {len(apps_list)}")
        print("\nApps Summary:")
        print("-" * 60)
        
        for app in apps_list:
            print(f"App: {app['name']} (v{app['version']})")
            print(f"  Description: {app.get('Description', 'N/A')}")
            print(f"  Status: {app.get('status', 'N/A')}")
            print(f"  Created: {app.get('created_at', 'N/A')}")
            
            # Count steps or sub_apps
            if 'steps' in app:
                print(f"  Steps: {len(app['steps'])}")
            elif 'sub_apps' in app:
                print(f"  Sub-apps: {len(app['sub_apps'])}")
                for sub_app in app['sub_apps']:
                    print(f"    - {sub_app['name']} ({len(sub_app.get('steps', []))} steps)")
            
            print("-" * 60)
        
        # Additional statistics
        print("\nDetailed Statistics:")
        print(f"- Apps with steps: {len([app for app in apps_list if 'steps' in app])}")
        print(f"- Apps with sub-apps: {len([app for app in apps_list if 'sub_apps' in app])}")
        
        # Count total steps across all apps
        total_steps = 0
        for app in apps_list:
            if 'steps' in app:
                total_steps += len(app['steps'])
            elif 'sub_apps' in app:
                for sub_app in app['sub_apps']:
                    total_steps += len(sub_app.get('steps', []))
        
        print(f"- Total steps across all apps: {total_steps}")
        
        print("="*60)
        print("VERIFICATION COMPLETED SUCCESSFULLY")
        print("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"Error verifying apps in MongoDB: {e}")
        return False

def main():
    """
    Main function to execute the verification
    """
    try:
        logger.info("Starting MongoDB verification for apps_map.json data")
        
        if verify_apps_in_mongo():
            logger.info("Verification completed successfully")
        else:
            logger.error("Verification failed")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        sys.exit(1)
    
    finally:
        # Ensure database connection is closed
        db_connection.disconnect()

if __name__ == "__main__":
    main()
