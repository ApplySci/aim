#!/usr/bin/env python3
"""
Test script to demonstrate using Google Drive files.list API
"""

from drive_pdf_downloader import GoogleDrivePDFDownloader
import json

def main():
    """Test the files.list API functionality"""
    # Google Drive folder ID for WRC 2025
    folder_id = "1PuSjJY5PSxXHja8xDESEhWk1kDhpX9hJ"
    
    print("🔍 Testing Google Drive files.list API")
    print("=" * 50)
    
    # Initialize downloader
    downloader = GoogleDrivePDFDownloader(folder_id)
    
    # Test 1: Get all PDF files
    print("\n📋 Fetching all PDF files...")
    pdf_files = downloader.fetch_file_list("pdf")
    
    if pdf_files:
        print(f"✅ Found {len(pdf_files)} PDF files:")
        for i, file_info in enumerate(pdf_files[:10], 1):  # Show first 10
            size_mb = int(file_info.get('size', 0)) / (1024 * 1024) if file_info.get('size') else 0
            print(f"  {i:2d}. {file_info['name']}")
            print(f"      ID: {file_info['id']}")
            print(f"      Size: {size_mb:.1f} MB")
            print(f"      Modified: {file_info.get('modifiedTime', 'Unknown')}")
            print()
        
        if len(pdf_files) > 10:
            print(f"      ... and {len(pdf_files) - 10} more files")
    else:
        print("❌ No PDF files found or authentication failed")
    
    # Test 2: Get all files (no extension filter)
    print("\n📋 Fetching all files (no extension filter)...")
    all_files = downloader.fetch_file_list("")
    
    if all_files:
        print(f"✅ Found {len(all_files)} total files:")
        
        # Group by file type
        file_types = {}
        for file_info in all_files:
            ext = file_info['name'].split('.')[-1].lower() if '.' in file_info['name'] else 'no_extension'
            if ext not in file_types:
                file_types[ext] = []
            file_types[ext].append(file_info)
        
        print("\n📊 File types breakdown:")
        for ext, files in sorted(file_types.items()):
            total_size = sum(int(f.get('size', 0)) for f in files)
            size_mb = total_size / (1024 * 1024)
            print(f"  {ext.upper()}: {len(files)} files ({size_mb:.1f} MB)")
    else:
        print("❌ No files found or authentication failed")
    
    # Test 3: Search for specific pattern
    print("\n🔍 Searching for TeamEvent PlayerStandings files...")
    pattern = r"TeamEvent.*PlayerStandings.*\.pdf"
    matching_files = downloader.find_matching_files(pattern, pdf_files if pdf_files else [])
    
    if matching_files:
        print(f"✅ Found {len(matching_files)} TeamEvent PlayerStandings files:")
        for file_info in matching_files:
            print(f"  - {file_info['name']}")
    else:
        print("❌ No TeamEvent PlayerStandings files found")
        
    # Test 3b: Also search for any PlayerStandings files
    print("\n🔍 Searching for any PlayerStandings files...")
    pattern_any = r".*PlayerStandings.*\.pdf"
    matching_any = downloader.find_matching_files(pattern_any, pdf_files if pdf_files else [])
    
    if matching_any:
        print(f"✅ Found {len(matching_any)} PlayerStandings files:")
        for file_info in matching_any:
            print(f"  - {file_info['name']}")
    else:
        print("❌ No PlayerStandings files found")
    
    # Test 4: Export detailed file info to JSON
    if pdf_files:
        print("\n💾 Saving detailed file info to JSON...")
        with open('downloads/file_list.json', 'w', encoding='utf-8') as f:
            json.dump(pdf_files, f, indent=2, ensure_ascii=False)
        print("✅ File list saved to downloads/file_list.json")

if __name__ == "__main__":
    main() 