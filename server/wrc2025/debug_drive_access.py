#!/usr/bin/env python3
"""
Debug script to test Google Drive access and permissions
"""

from drive_pdf_downloader import GoogleDrivePDFDownloader
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

def test_folder_access():
    """Test various aspects of Google Drive folder access"""
    folder_id = "1PuSjJY5PSxXHja8xDESEhWk1kDhpX9hJ"
    
    print("🔍 Google Drive Access Debugging")
    print("=" * 50)
    
    # Check service account file
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    service_account_file = os.path.join(parent_dir, "fcm-admin.json")
    
    print(f"📁 Service account file: {service_account_file}")
    print(f"📁 File exists: {os.path.exists(service_account_file)}")
    
    if not os.path.exists(service_account_file):
        print("❌ Service account file not found!")
        return
    
    try:
        # Initialize the service directly for debugging
        SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file, scopes=SCOPES
        )
        service = build('drive', 'v3', credentials=credentials)
        
        print("✅ Google Drive service initialized successfully")
        
        # Test 1: Try to get folder metadata
        print(f"\n🔍 Test 1: Getting folder metadata for ID: {folder_id}")
        try:
            folder_metadata = service.files().get(
                fileId=folder_id,
                fields="id, name, mimeType, parents, capabilities"
            ).execute()
            
            print("✅ Folder metadata retrieved:")
            print(f"   Name: {folder_metadata.get('name')}")
            print(f"   ID: {folder_metadata.get('id')}")
            print(f"   MIME Type: {folder_metadata.get('mimeType')}")
            print(f"   Parents: {folder_metadata.get('parents')}")
            
            capabilities = folder_metadata.get('capabilities', {})
            print(f"   Can List Children: {capabilities.get('canListChildren', 'Unknown')}")
            print(f"   Can Read: {capabilities.get('canRead', 'Unknown')}")
            
        except Exception as e:
            print(f"❌ Error getting folder metadata: {e}")
            return
        
        # Test 2: Try different query variations
        print(f"\n🔍 Test 2: Testing different query variations")
        
        queries = [
            f"'{folder_id}' in parents and trashed=false",
            f"parents in '{folder_id}' and trashed=false",
            f"'{folder_id}' in parents",
            "trashed=false"  # Get all accessible files
        ]
        
        for i, query in enumerate(queries, 1):
            try:
                print(f"\n   Query {i}: {query}")
                results = service.files().list(
                    q=query,
                    pageSize=10,
                    fields="nextPageToken, files(id, name, mimeType, size, parents)"
                ).execute()
                
                files = results.get('files', [])
                print(f"   Results: {len(files)} files found")
                
                if files:
                    for file_info in files[:3]:  # Show first 3 files
                        print(f"     - {file_info.get('name')} ({file_info.get('mimeType')})")
                        print(f"       ID: {file_info.get('id')}")
                        print(f"       Parents: {file_info.get('parents')}")
                
            except Exception as e:
                print(f"   ❌ Error with query {i}: {e}")
        
        # Test 3: Check service account email
        print(f"\n🔍 Test 3: Service account information")
        try:
            about = service.about().get(fields="user").execute()
            user_info = about.get('user', {})
            print(f"   Service account email: {user_info.get('emailAddress', 'Unknown')}")
            print(f"   Display name: {user_info.get('displayName', 'Unknown')}")
        except Exception as e:
            print(f"   ❌ Error getting service account info: {e}")
        
        # Test 4: List all files the service account can access
        print(f"\n🔍 Test 4: List all accessible files (first 10)")
        try:
            all_results = service.files().list(
                pageSize=10,
                fields="nextPageToken, files(id, name, mimeType, parents, shared)"
            ).execute()
            
            all_files = all_results.get('files', [])
            print(f"   Total accessible files: {len(all_files)}")
            
            for file_info in all_files:
                print(f"     - {file_info.get('name')} ({file_info.get('mimeType')})")
                print(f"       ID: {file_info.get('id')}")
                print(f"       Shared: {file_info.get('shared', False)}")
                if file_info.get('parents'):
                    print(f"       Parents: {file_info.get('parents')}")
                
        except Exception as e:
            print(f"   ❌ Error listing all files: {e}")
        
    except Exception as e:
        print(f"❌ Error initializing Google Drive service: {e}")

def test_with_downloader():
    """Test using the existing downloader class"""
    print(f"\n🔍 Test 5: Using GoogleDrivePDFDownloader class")
    folder_id = "1PuSjJY5PSxXHja8xDESEhWk1kDhpX9hJ"
    
    downloader = GoogleDrivePDFDownloader(folder_id)
    
    # Test with empty extension to get all files
    all_files = downloader.fetch_file_list("")
    print(f"   Files found with downloader: {len(all_files)}")
    
    if all_files:
        print("   Sample files:")
        for file_info in all_files[:3]:
            print(f"     - {file_info.get('name')}")
    
    return all_files

if __name__ == "__main__":
    test_folder_access()
    files = test_with_downloader()
    
    if files:
        print(f"\n💾 Saving debug results to downloads/debug_results.json")
        os.makedirs('downloads', exist_ok=True)
        with open('downloads/debug_results.json', 'w', encoding='utf-8') as f:
            json.dump(files, f, indent=2, ensure_ascii=False)
    
    print(f"\n💡 Troubleshooting tips:")
    print(f"   1. Make sure the service account has been granted access to the folder")
    print(f"   2. Check if the folder is shared with the service account email")
    print(f"   3. Verify the folder ID is correct")
    print(f"   4. The service account needs 'Viewer' or 'Reader' permissions") 