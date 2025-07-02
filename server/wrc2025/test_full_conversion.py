#!/usr/bin/env python3
"""
Comprehensive test for the full PDF-to-CSV conversion pipeline
"""

import os
import json
from pdf_to_csv_converter import download_and_convert_to_csv
from drive_pdf_downloader import GoogleDrivePDFDownloader
import time

def test_full_conversion_pipeline():
    """Test the complete PDF to CSV conversion pipeline"""
    print("🚀 Full PDF-to-CSV Conversion Pipeline Test")
    print("=" * 60)
    
    # Test 1: Default pattern (any PlayerStandings files)
    print("\n📋 Test 1: Default Pattern (.*PlayerStandings.*\\.pdf)")
    print("-" * 40)
    
    start_time = time.time()
    try:
        result1 = download_and_convert_to_csv()
        end_time = time.time()
        
        if result1 is not None:
            print(f"✅ SUCCESS: Converted {len(result1)} records")
            print(f"⏱️  Time taken: {end_time - start_time:.2f} seconds")
            print(f"📊 Sample data from result:")
            if result1:
                print(f"   Columns: {list(result1[0].keys())}")
                print(f"   First record: {result1[0]}")
        else:
            print(f"❌ FAILED: No data returned")
            print(f"⏱️  Time taken: {end_time - start_time:.2f} seconds")
            
    except Exception as e:
        print(f"❌ ERROR in Test 1: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Specific TeamEvent PlayerStandings pattern
    print(f"\n📋 Test 2: TeamEvent PlayerStandings Pattern")
    print("-" * 40)
    
    start_time = time.time()
    try:
        pattern = r"TeamEvent.*PlayerStandings.*\.pdf"
        result2 = download_and_convert_to_csv(pattern=pattern)
        end_time = time.time()
        
        if result2 is not None:
            print(f"✅ SUCCESS: Converted {len(result2)} records")
            print(f"⏱️  Time taken: {end_time - start_time:.2f} seconds")
            print(f"📊 Sample data from result:")
            if result2:
                print(f"   Columns: {list(result2[0].keys())}")
                for i, record in enumerate(result2[:3]):  # Show first 3 records
                    print(f"   Record {i+1}: {record}")
        else:
            print(f"❌ FAILED: No data returned")
            print(f"⏱️  Time taken: {end_time - start_time:.2f} seconds")
            
    except Exception as e:
        print(f"❌ ERROR in Test 2: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Check what files are actually available
    print(f"\n📋 Test 3: Available Files Analysis")
    print("-" * 40)
    
    try:
        folder_id = "1PuSjJY5PSxXHja8xDESEhWk1kDhpX9hJ"
        downloader = GoogleDrivePDFDownloader(folder_id)
        
        # Get all PDF files
        all_pdfs = downloader.fetch_file_list("pdf")
        print(f"📄 Total PDF files found: {len(all_pdfs)}")
        
        # Analyze patterns
        player_standings = [f for f in all_pdfs if "PlayerStandings" in f.get('name', '')]
        team_standings = [f for f in all_pdfs if "TeamStandings" in f.get('name', '')]
        table_assignments = [f for f in all_pdfs if "TableAssignment" in f.get('name', '')]
        other_files = [f for f in all_pdfs if not any(keyword in f.get('name', '') 
                      for keyword in ["PlayerStandings", "TeamStandings", "TableAssignment"])]
        
        print(f"📊 File breakdown:")
        print(f"   PlayerStandings: {len(player_standings)} files")
        for f in player_standings:
            print(f"     - {f['name']}")
        
        print(f"   TeamStandings: {len(team_standings)} files")  
        for f in team_standings:
            print(f"     - {f['name']}")
            
        print(f"   TableAssignment: {len(table_assignments)} files")
        for f in table_assignments:
            print(f"     - {f['name']}")
            
        print(f"   Other: {len(other_files)} files")
        for f in other_files:
            print(f"     - {f['name']}")
            
    except Exception as e:
        print(f"❌ ERROR in Test 3: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Test with wrong pattern (should fail gracefully)
    print(f"\n📋 Test 4: Non-existent Pattern Test")
    print("-" * 40)
    
    try:
        pattern = r"NonExistentFile.*\.pdf"
        result4 = download_and_convert_to_csv(pattern=pattern)
        
        if result4 is None:
            print(f"✅ SUCCESS: Correctly handled non-existent pattern")
        else:
            print(f"⚠️  UNEXPECTED: Got result for non-existent pattern: {len(result4)} records")
            
    except Exception as e:
        print(f"❌ ERROR in Test 4: {e}")
    
    # Test 5: Check downloaded files
    print(f"\n📋 Test 5: Downloaded Files Check")
    print("-" * 40)
    
    downloads_dir = "downloads"
    if os.path.exists(downloads_dir):
        files = os.listdir(downloads_dir)
        print(f"📁 Files in downloads directory: {len(files)}")
        
        pdf_files = [f for f in files if f.endswith('.pdf')]
        csv_files = [f for f in files if f.endswith('.csv')]
        json_files = [f for f in files if f.endswith('.json')]
        
        print(f"   📄 PDF files: {len(pdf_files)}")
        for f in pdf_files:
            file_path = os.path.join(downloads_dir, f)
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            print(f"     - {f} ({size_mb:.2f} MB)")
        
        print(f"   📊 CSV files: {len(csv_files)}")
        for f in csv_files:
            file_path = os.path.join(downloads_dir, f)
            size_kb = os.path.getsize(file_path) / 1024
            print(f"     - {f} ({size_kb:.1f} KB)")
        
        print(f"   📋 JSON files: {len(json_files)}")
        for f in json_files:
            file_path = os.path.join(downloads_dir, f)
            size_kb = os.path.getsize(file_path) / 1024
            print(f"     - {f} ({size_kb:.1f} KB)")
    else:
        print(f"❌ Downloads directory not found")
    
    print(f"\n🎯 Test Summary")
    print("=" * 60)
    print(f"✅ Pipeline components tested:")
    print(f"   - Google Drive authentication")
    print(f"   - File listing and pattern matching")
    print(f"   - PDF downloading")
    print(f"   - PDF table extraction")
    print(f"   - CSV conversion (without pandas)")
    print(f"   - Error handling")
    print(f"\n📋 Next steps:")
    print(f"   1. Check the generated CSV files for data quality")
    print(f"   2. Verify the table parsing worked correctly")
    print(f"   3. Test with different file patterns as needed")

def test_specific_file_conversion():
    """Test conversion of the specific PlayerStandings file we found"""
    print(f"\n🎯 Specific File Test: TeamEvent PlayerStandings")
    print("=" * 60)
    
    # We know this file exists from our earlier test
    target_file_pattern = r"TeamEvent_3rdRound_PlayerStandings.*\.pdf"
    
    try:
        result = download_and_convert_to_csv(pattern=target_file_pattern)
        
        if result:
            print(f"✅ Successfully converted specific file!")
            print(f"📊 Records: {len(result)}")
            print(f"📋 Columns: {list(result[0].keys())}")
            
            # Show detailed sample
            print(f"\n📋 Sample records:")
            for i, record in enumerate(result[:5]):
                print(f"  Record {i+1}:")
                for key, value in record.items():
                    print(f"    {key}: {value}")
                print()
                
            return result
        else:
            print(f"❌ Failed to convert specific file")
            return None
            
    except Exception as e:
        print(f"❌ ERROR in specific file test: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Run comprehensive tests
    test_full_conversion_pipeline()
    
    # Test specific file
    specific_result = test_specific_file_conversion()
    
    print(f"\n🏁 All tests completed!")
    print(f"Check the downloads/ directory for generated files.") 