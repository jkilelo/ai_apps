#!/usr/bin/env python3
"""
Test script for MongoDB connection and ai_apps collection
Run this script to verify your database setup is working correctly
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import (
    initialize_database, 
    get_database_stats, 
    insert_ai_app, 
    find_ai_apps,
    get_ai_apps_collection
)

def test_database_connection():
    """Test the database connection and basic operations"""
    print("🔌 Testing MongoDB connection...")
    
    # Initialize database
    if not initialize_database():
        print("❌ Failed to initialize database connection")
        return False
    
    print("✅ Database connection successful!")
    
    # Get database stats
    print("\n📊 Database Statistics:")
    stats = get_database_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Test collection access
    print("\n📁 Testing ai_apps collection...")
    collection = get_ai_apps_collection()
    if collection is None:
        print("❌ Could not access ai_apps collection")
        return False
    
    print("✅ ai_apps collection is accessible!")
    
    # Test insert operation
    print("\n📝 Testing insert operation...")
    test_app = {
        "name": "test_database_app",
        "version": "1.0.0",
        "description": "Test application for database verification",
        "status": "testing",
        "metadata": {
            "test": True,
            "framework": "python",
            "purpose": "database_testing"
        }
    }
    
    app_id = insert_ai_app(test_app)
    if app_id:
        print(f"✅ Successfully inserted test app with ID: {app_id}")
    else:
        print("❌ Failed to insert test app")
        return False
    
    # Test find operation
    print("\n🔍 Testing find operation...")
    apps = find_ai_apps({"name": "test_database_app"})
    if apps:
        print(f"✅ Found {len(apps)} test app(s)")
        for app in apps:
            print(f"   - {app['name']} (v{app['version']})")
    else:
        print("❌ Could not find test apps")
    
    # Test find all apps
    print("\n📋 All apps in collection:")
    all_apps = find_ai_apps()
    if all_apps:
        print(f"   Total apps: {len(all_apps)}")
        for app in all_apps:
            print(f"   - {app['name']} (v{app.get('version', 'unknown')})")
    else:
        print("   No apps found in collection")
    
    print("\n🎉 All database tests completed successfully!")
    return True

def cleanup_test_data():
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")
    collection = get_ai_apps_collection()
    if collection:
        result = collection.delete_many({"metadata.test": True})
        print(f"   Removed {result.deleted_count} test document(s)")

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 AI Apps Database Connection Test")
    print("=" * 50)
    
    try:
        success = test_database_connection()
        
        if success:
            # Ask if user wants to clean up test data
            response = input("\n❓ Do you want to remove test data? (y/N): ").strip().lower()
            if response == 'y':
                cleanup_test_data()
            
            print("\n✨ Database setup is ready for use!")
        else:
            print("\n💥 Database setup needs attention")
            print("\n🔧 Troubleshooting tips:")
            print("   1. Make sure MongoDB is running")
            print("   2. Check your .env file configuration")
            print("   3. Verify network connectivity")
            print("   4. Install required dependencies: pip install -r requirements.txt")
            
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        print("\n🔧 Please check your MongoDB installation and configuration")
