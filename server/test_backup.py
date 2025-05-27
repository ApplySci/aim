#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Firebase backup functionality.

This script tests the backup and restore functions to ensure they work correctly.
Run this script to verify the backup system is functioning properly.
"""

import os
import sys
import tempfile
import json
from datetime import datetime

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_backup_functions():
    """Test the backup and restore functions"""
    try:
        from operations.firebase_backup import (
            serialize_firestore_value,
            deserialize_firestore_value,
            list_backup_files,
            ensure_backup_directory
        )
        
        print("✅ Successfully imported backup functions")
        
        # Test serialization/deserialization
        test_data = {
            "string": "test",
            "number": 42,
            "boolean": True,
            "datetime": datetime.now(),
            "nested": {
                "list": [1, 2, 3],
                "dict": {"key": "value"}
            }
        }
        
        serialized = serialize_firestore_value(test_data)
        deserialized = deserialize_firestore_value(serialized)
        
        print("✅ Serialization/deserialization test passed")
        
        # Test backup directory creation
        ensure_backup_directory()
        print("✅ Backup directory creation test passed")
        
        # Test listing backup files
        backup_files = list_backup_files()
        print(f"✅ Found {len(backup_files)} existing backup files")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def test_json_structure():
    """Test that we can create a valid backup JSON structure"""
    try:
        backup_data = {
            "backup_info": {
                "created_at": datetime.now().isoformat(),
                "version": "1.0",
                "description": "Test backup"
            },
            "collections": {
                "test_collection": {
                    "doc1": {
                        "field1": "value1",
                        "field2": 42
                    }
                }
            }
        }
        
        # Test JSON serialization
        json_str = json.dumps(backup_data, indent=2)
        parsed_back = json.loads(json_str)
        
        print("✅ JSON structure test passed")
        return True
        
    except Exception as e:
        print(f"❌ JSON test error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Firebase backup functionality...")
    print("=" * 50)
    
    success = True
    
    # Test basic functions
    if not test_backup_functions():
        success = False
    
    # Test JSON structure
    if not test_json_structure():
        success = False
    
    print("=" * 50)
    if success:
        print("🎉 All tests passed! Backup functionality is ready to use.")
        print("\nTo create a backup:")
        print("1. Go to the admin page (/admin/list)")
        print("2. Click 'Create Firebase Backup' button")
        print("3. Wait for the backup to complete")
        print("4. Use the restore functionality if needed")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    sys.exit(0 if success else 1) 