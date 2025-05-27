# -*- coding: utf-8 -*-
"""
Firebase Firestore backup and restore functionality.

This module provides functions to backup the entire Firestore database to a JSON file
and restore the database from a JSON backup file. The backup includes all collections
and documents with their complete data structure.
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, Any, List
import logging

from firebase_admin import firestore
from oauth_setup import firestore_client
from config import BASEDIR

# Directory for storing backups
BACKUP_DIR = os.path.join(os.path.dirname(BASEDIR), "backups")

def ensure_backup_directory():
    """Ensure the backup directory exists"""
    os.makedirs(BACKUP_DIR, exist_ok=True)

def serialize_firestore_value(value):
    """Convert Firestore values to JSON-serializable format"""
    if isinstance(value, datetime):
        return {"_type": "datetime", "value": value.isoformat()}
    elif hasattr(value, 'timestamp'):  # Firestore timestamp
        return {"_type": "timestamp", "value": value.timestamp()}
    elif isinstance(value, dict):
        return {k: serialize_firestore_value(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [serialize_firestore_value(item) for item in value]
    else:
        return value

def deserialize_firestore_value(value):
    """Convert JSON values back to Firestore format"""
    if isinstance(value, dict):
        if value.get("_type") == "datetime":
            return datetime.fromisoformat(value["value"])
        elif value.get("_type") == "timestamp":
            return firestore.SERVER_TIMESTAMP if value["value"] is None else datetime.fromtimestamp(value["value"], tz=timezone.utc)
        else:
            return {k: deserialize_firestore_value(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [deserialize_firestore_value(item) for item in value]
    else:
        return value

def backup_collection(collection_ref, collection_name: str) -> Dict[str, Any]:
    """Backup a single collection and all its documents"""
    collection_data = {}
    
    try:
        docs = collection_ref.stream()
        for doc in docs:
            doc_data = doc.to_dict()
            if doc_data:
                # Serialize the document data
                serialized_data = serialize_firestore_value(doc_data)
                collection_data[doc.id] = serialized_data
                
                # Check for subcollections
                subcollections = doc.reference.collections()
                if subcollections:
                    collection_data[doc.id]["_subcollections"] = {}
                    for subcol in subcollections:
                        subcol_data = backup_collection(subcol, f"{collection_name}/{doc.id}/{subcol.id}")
                        if subcol_data:
                            collection_data[doc.id]["_subcollections"][subcol.id] = subcol_data
                            
        logging.info(f"Backed up collection '{collection_name}' with {len(collection_data)} documents")
        
    except Exception as e:
        logging.error(f"Error backing up collection '{collection_name}': {str(e)}")
        raise
    
    return collection_data

def create_firebase_backup() -> str:
    """Create a complete backup of the Firebase Firestore database"""
    ensure_backup_directory()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"firebase_backup_{timestamp}.json"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    
    try:
        backup_data = {
            "backup_info": {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "version": "1.0",
                "description": "Complete Firebase Firestore backup"
            },
            "collections": {}
        }
        
        # Get all root collections
        collections = firestore_client.collections()
        
        for collection in collections:
            collection_name = collection.id
            logging.info(f"Starting backup of collection: {collection_name}")
            
            collection_data = backup_collection(collection, collection_name)
            if collection_data:
                backup_data["collections"][collection_name] = collection_data
        
        # Write backup to file
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        logging.info(f"Firebase backup completed successfully: {backup_path}")
        return backup_path
        
    except Exception as e:
        logging.error(f"Error creating Firebase backup: {str(e)}")
        raise

def restore_collection(collection_ref, collection_data: Dict[str, Any], collection_name: str):
    """Restore a collection from backup data"""
    restored_count = 0
    
    try:
        for doc_id, doc_data in collection_data.items():
            # Extract subcollections if they exist
            subcollections_data = doc_data.pop("_subcollections", {})
            
            # Deserialize the document data
            deserialized_data = deserialize_firestore_value(doc_data)
            
            # Set the document
            doc_ref = collection_ref.document(doc_id)
            doc_ref.set(deserialized_data)
            restored_count += 1
            
            # Restore subcollections
            for subcol_name, subcol_data in subcollections_data.items():
                subcol_ref = doc_ref.collection(subcol_name)
                restore_collection(subcol_ref, subcol_data, f"{collection_name}/{doc_id}/{subcol_name}")
        
        logging.info(f"Restored collection '{collection_name}' with {restored_count} documents")
        
    except Exception as e:
        logging.error(f"Error restoring collection '{collection_name}': {str(e)}")
        raise

def restore_firebase_backup(backup_path: str, confirm_restore: bool = False) -> bool:
    """Restore Firebase Firestore database from a backup file"""
    if not confirm_restore:
        raise ValueError("Restore operation requires explicit confirmation")
    
    if not os.path.exists(backup_path):
        raise FileNotFoundError(f"Backup file not found: {backup_path}")
    
    try:
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        if "collections" not in backup_data:
            raise ValueError("Invalid backup file format")
        
        logging.info(f"Starting Firebase restore from: {backup_path}")
        
        # Restore each collection
        for collection_name, collection_data in backup_data["collections"].items():
            logging.info(f"Restoring collection: {collection_name}")
            
            collection_ref = firestore_client.collection(collection_name)
            restore_collection(collection_ref, collection_data, collection_name)
        
        logging.info("Firebase restore completed successfully")
        return True
        
    except Exception as e:
        logging.error(f"Error restoring Firebase backup: {str(e)}")
        raise

def list_backup_files() -> List[Dict[str, Any]]:
    """List all available backup files with their metadata"""
    ensure_backup_directory()
    
    backup_files = []
    
    try:
        for filename in os.listdir(BACKUP_DIR):
            if filename.startswith("firebase_backup_") and filename.endswith(".json"):
                file_path = os.path.join(BACKUP_DIR, filename)
                file_stats = os.stat(file_path)
                
                # Try to read backup info from the file
                backup_info = {}
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        backup_info = data.get("backup_info", {})
                except:
                    pass
                
                backup_files.append({
                    "filename": filename,
                    "path": file_path,
                    "size": file_stats.st_size,
                    "created_at": datetime.fromtimestamp(file_stats.st_mtime),
                    "backup_info": backup_info
                })
        
        # Sort by creation time, newest first
        backup_files.sort(key=lambda x: x["created_at"], reverse=True)
        
    except Exception as e:
        logging.error(f"Error listing backup files: {str(e)}")
    
    return backup_files

def delete_backup_file(filename: str) -> bool:
    """Delete a backup file"""
    file_path = os.path.join(BACKUP_DIR, filename)
    
    if not os.path.exists(file_path):
        return False
    
    try:
        os.remove(file_path)
        logging.info(f"Deleted backup file: {filename}")
        return True
    except Exception as e:
        logging.error(f"Error deleting backup file {filename}: {str(e)}")
        return False 