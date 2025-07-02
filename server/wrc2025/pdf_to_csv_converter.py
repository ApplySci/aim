#!/usr/bin/env python3
"""
Convert PDF player standings to simple CSV with proper data types
"""

import csv
import re
import logging
from drive_pdf_downloader import GoogleDrivePDFDownloader, PDFParser
import os
from collections import defaultdict

# Suppress pdfminer font warnings
logging.getLogger("pdfminer.pdffont").setLevel(logging.ERROR)
logging.getLogger("pdfminer").setLevel(logging.ERROR)


def clean_numeric_value(value):
    """Convert string to numeric value, handling various formats"""
    if value is None or value == "":
        return None

    # Convert to string and clean
    str_val = str(value).strip()

    # Handle empty or dash values
    if str_val in ["", "-", "N/A", "n/a"]:
        return None

    # Remove any non-numeric characters except decimal point and minus
    cleaned = re.sub(r"[^\d.-]", "", str_val)

    try:
        # Try to convert to float first
        if "." in cleaned:
            return float(cleaned)
        else:
            return int(cleaned)
    except ValueError:
        return None


def clean_string_value(value):
    """Clean string values, removing extra whitespace"""
    if value is None:
        return ""
    return str(value).strip()


def display_sample_data(data_rows, num_rows=5):
    """Display sample data in a formatted way"""
    if not data_rows:
        print("No data to display")
        return
    
    # Get column names from first row
    columns = list(data_rows[0].keys())
    
    # Calculate column widths
    col_widths = {}
    for col in columns:
        col_widths[col] = max(len(str(col)), 
                             max(len(str(row.get(col, ""))) for row in data_rows[:num_rows]))
    
    # Print header
    header = " | ".join(str(col).ljust(col_widths[col]) for col in columns)
    print(header)
    print("-" * len(header))
    
    # Print data rows
    for i, row in enumerate(data_rows[:num_rows]):
        row_str = " | ".join(str(row.get(col, "")).ljust(col_widths[col]) for col in columns)
        print(row_str)


def get_data_types(data_rows):
    """Analyze data types in the dataset"""
    if not data_rows:
        return {}
    
    type_info = {}
    for col in data_rows[0].keys():
        types_found = set()
        for row in data_rows:
            value = row.get(col)
            if value is not None:
                types_found.add(type(value).__name__)
        
        if len(types_found) == 1:
            type_info[col] = list(types_found)[0]
        else:
            type_info[col] = f"mixed ({', '.join(sorted(types_found))})"
    
    return type_info


def calculate_numeric_summary(data_rows, column):
    """Calculate summary statistics for a numeric column"""
    values = []
    for row in data_rows:
        val = row.get(column)
        if val is not None and isinstance(val, (int, float)):
            values.append(val)
    
    if not values:
        return None
    
    values.sort()
    n = len(values)
    
    summary = {
        'count': n,
        'mean': sum(values) / n,
        'min': min(values),
        'max': max(values),
        'median': values[n//2] if n % 2 == 1 else (values[n//2-1] + values[n//2]) / 2
    }
    
    return summary


def display_summary_statistics(data_rows):
    """Display summary statistics for numeric columns"""
    if not data_rows:
        return
    
    numeric_columns = []
    for col in data_rows[0].keys():
        # Check if column contains numeric data
        has_numeric = any(isinstance(row.get(col), (int, float)) and row.get(col) is not None 
                         for row in data_rows)
        if has_numeric:
            numeric_columns.append(col)
    
    if not numeric_columns:
        print("No numeric columns found for summary statistics")
        return
    
    print(f"\n📊 Summary statistics for numeric columns:")
    for col in numeric_columns:
        summary = calculate_numeric_summary(data_rows, col)
        if summary:
            print(f"   {col}:")
            print(f"     count: {summary['count']}")
            print(f"     mean:  {summary['mean']:.2f}")
            print(f"     min:   {summary['min']}")
            print(f"     max:   {summary['max']}")
            print(f"     median: {summary['median']:.2f}")


def save_to_csv(data_rows, filename):
    """Save data to CSV file"""
    if not data_rows:
        print("No data to save")
        return False
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = data_rows[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(data_rows)
        
        return True
    except Exception as e:
        print(f"Error saving CSV: {e}")
        return False


def process_player_standings_table(tables):
    """Process the player standings table from PDF extraction (handles multi-page PDFs)"""
    if not tables:
        print("No tables found in PDF")
        return None

    print(f"📄 Processing {len(tables)} tables from PDF pages")
    
    # Define column mappings from possible header names to our standardized names
    column_mappings = {
        # Rank columns
        "rank": "Rank",
        "順位": "Rank",
        
        # Player number
        "no": "Player_No",
        "no.": "Player_No",
        "player no": "Player_No",
        "player no.": "Player_No",
        
        # Country
        "country": "Country",
        "国": "Country",
        "country jp": "Country_JP",
        "国名": "Country_JP",
        
        # Player name
        "player name": "Player_Name",
        "name": "Player_Name",
        "player": "Player_Name",
        "氏名": "Player_Name_JP",
        "player name jp": "Player_Name_JP",
        
        # Scores
        "total": "Total_Score",
        "total score": "Total_Score",
        "score": "Total_Score",
        "合計": "Total_Score",
        
        # Team (if present)
        "team": "Team_Name",
        "team name": "Team_Name",
        "チーム": "Team_Name",
        
        # Round scores - flexible pattern matching
        "round 1": "Round_1",
        "round 2": "Round_2",
        "round 3": "Round_3",
        "round 4": "Round_4",
        "round 5": "Round_5",
        "round 6": "Round_6",
        "round 7": "Round_7",
        "round 8": "Round_8",
        "round 9": "Round_9",
        "round 10": "Round_10",
        "1回戦": "Round_1",
        "2回戦": "Round_2",
        "3回戦": "Round_3",
        "4回戦": "Round_4",
        "5回戦": "Round_5",
        "6回戦": "Round_6",
        "7回戦": "Round_7",
        "8回戦": "Round_8",
        "9回戦": "Round_9",
        "10回戦": "Round_10",
    }

    def normalize_header(header):
        """Normalize header text for matching"""
        if header is None:
            return ""
        # Convert to lowercase, remove extra spaces and special characters
        normalized = str(header).lower().strip()
        normalized = re.sub(r'[^\w\s]', '', normalized)  # Remove punctuation
        normalized = re.sub(r'\s+', ' ', normalized)     # Normalize whitespace
        return normalized

    def find_column_mapping(headers):
        """Map actual PDF headers to our standardized column names"""
        mapping = {}  # index -> our_column_name
        
        for idx, header in enumerate(headers):
            if header is None:
                continue
                
            normalized = normalize_header(header)
            
            # Direct mapping first
            if normalized in column_mappings:
                mapping[idx] = column_mappings[normalized]
                continue
            
            # Pattern matching for round columns (e.g., "1", "2", "3" might be rounds)
            if re.match(r'^\d+$', normalized):
                round_num = int(normalized)
                if 1 <= round_num <= 10:
                    mapping[idx] = f"Round_{round_num}"
                    continue
            
            # Pattern matching for round columns with various formats
            round_match = re.search(r'(\d+)', normalized)
            if round_match and any(word in normalized for word in ['round', 'r', '回戦', '戦']):
                round_num = int(round_match.group(1))
                if 1 <= round_num <= 10:
                    mapping[idx] = f"Round_{round_num}"
                    continue
        
        return mapping

    all_data_rows = []
    column_mapping = None
    headers_found = False

    # Process each table (page) separately
    for page_idx, raw_table in enumerate(tables):
        print(f"📋 Processing page {page_idx + 1}: {len(raw_table)} rows")
        
        if not raw_table or len(raw_table) == 0:
            print(f"   ⚠️  Page {page_idx + 1} is empty, skipping")
            continue

        # Find the header row (looking for "Rank" or similar)
        header_row_idx = None
        for i, row in enumerate(raw_table):
            if any(cell and (
                "rank" in normalize_header(cell) or 
                "no" in normalize_header(cell) or
                "順位" in str(cell) or
                "氏名" in str(cell)
            ) for cell in row):
                header_row_idx = i
                break

        if header_row_idx is None:
            # No header found on this page - assume it's continuation data
            if not headers_found:
                print(f"   ⚠️  No header found on page {page_idx + 1} and no previous headers - skipping")
                continue
            else:
                print(f"   📄 Page {page_idx + 1}: No headers (continuation page)")
                start_row = 0  # Start from the beginning for continuation pages
        else:
            print(f"   📋 Page {page_idx + 1}: Header found at row {header_row_idx}")
            
            # Extract headers - try the header row and the next row
            headers = raw_table[header_row_idx]
            if header_row_idx + 1 < len(raw_table):
                # Sometimes the real column names are in the next row
                next_row = raw_table[header_row_idx + 1]
                # Use next row if it seems to have more detailed headers
                if len([h for h in next_row if h and len(str(h).strip()) > 2]) > len([h for h in headers if h and len(str(h).strip()) > 2]):
                    headers = next_row
                    start_row = header_row_idx + 2
                else:
                    start_row = header_row_idx + 1
            else:
                start_row = header_row_idx + 1
            
            # Create column mapping from headers
            if not headers_found:
                column_mapping = find_column_mapping(headers)
                print(f"   📝 Found headers: {[str(h)[:20] + '...' if h and len(str(h)) > 20 else str(h) for h in headers]}")
                print(f"   🗂️  Mapped columns: {column_mapping}")
                headers_found = True

        # Skip processing if we don't have column mapping
        if column_mapping is None:
            print(f"   ⚠️  No column mapping available for page {page_idx + 1}")
            continue

        # Process data rows
        page_data_rows = []
        
        for i, row in enumerate(raw_table[start_row:], start=start_row):
            if len(row) < 2:  # Skip rows that are too short
                continue

            # Skip empty rows
            if all(cell is None or str(cell).strip() == "" for cell in row):
                continue

            # Skip header rows that might appear on continuation pages
            if any(cell and ("rank" in normalize_header(cell) or "順位" in str(cell)) for cell in row):
                continue

            # Process each column using our mapping
            processed_row = {}

            for col_idx, our_column_name in column_mapping.items():
                if col_idx < len(row):
                    cell_value = row[col_idx]
                else:
                    cell_value = None

                # Apply appropriate data type conversion based on column type
                if our_column_name in ["Rank", "Player_No"]:
                    processed_row[our_column_name] = clean_numeric_value(cell_value)
                elif our_column_name in [
                    "Total_Score",
                    "Round_1", "Round_2", "Round_3", "Round_4", "Round_5",
                    "Round_6", "Round_7", "Round_8", "Round_9", "Round_10",
                ]:
                    processed_row[our_column_name] = clean_numeric_value(cell_value)
                else:
                    processed_row[our_column_name] = clean_string_value(cell_value)

            # Only add rows that have at least a rank or player name
            if (processed_row.get("Rank") is not None or 
                (processed_row.get("Player_Name") and processed_row.get("Player_Name").strip()) or
                (processed_row.get("Player_Name_JP") and processed_row.get("Player_Name_JP").strip())):
                page_data_rows.append(processed_row)

        print(f"   ✅ Page {page_idx + 1}: Extracted {len(page_data_rows)} player records")
        all_data_rows.extend(page_data_rows)

    print(f"🎯 Total records extracted from all pages: {len(all_data_rows)}")
    
    if not all_data_rows:
        print("❌ No player data found in any pages")
        return None
    
    # Sort by rank if available (in case pages were processed out of order)
    def sort_key(row):
        rank = row.get("Rank")
        if rank is not None:
            return (0, rank)  # Rank available - sort by rank
        else:
            return (1, 0)     # No rank - put at end
    
    all_data_rows.sort(key=sort_key)
    
    return all_data_rows


def extract_round_number(filename):
    """Extract round number from filename like 'TeamEvent_3rdRound_PlayerStandings_*.pdf'
    
    Returns:
        int: Round number (e.g., 3 for '3rd'), or 0 if not found
    """
    # Pattern to match {nth}Round format where n can be 1st, 2nd, 3rd, 4th, etc.
    pattern = r"MainEvent_(\d+)(?:st|nd|rd|th)Round_PlayerStandings_"
    
    match = re.search(pattern, filename)
    if match:
        return int(match.group(1))
    
    return 0


def select_highest_round_file(matching_files):
    """Select the file with the highest round number from matching files
    
    Args:
        matching_files: List of file dictionaries with 'name' and 'id' keys
        
    Returns:
        dict: File dictionary with highest round number, or first file if no rounds found
    """
    if not matching_files:
        return None
        
    if len(matching_files) == 1:
        return matching_files[0]
    
    # Extract round numbers and find the highest
    files_with_rounds = []
    for file_info in matching_files:
        round_num = extract_round_number(file_info['name'])
        files_with_rounds.append((round_num, file_info))
    
    # Sort by round number (descending) - highest first
    files_with_rounds.sort(key=lambda x: x[0], reverse=True)
    
    # Display selection logic
    print(f"📋 Found {len(matching_files)} matching files:")
    for round_num, file_info in files_with_rounds:
        round_str = f"Round {round_num}" if round_num > 0 else "No round detected"
        print(f"   - {file_info['name']} ({round_str})")
    
    # Return file with highest round number
    selected_round, selected_file = files_with_rounds[0]
    if selected_round > 0:
        print(f"🎯 Selected highest round: Round {selected_round}")
    else:
        print(f"🎯 No round numbers detected, using first file")
    
    return selected_file


def download_and_convert_to_csv(pattern=None, file_list=None):
    """Main function to download PDF and convert to simple CSV
    
    Args:
        pattern: Regex pattern to match files (default: .*PlayerStandings.*\\.pdf)
        file_list: List of available files with 'name' and 'id' keys (will fetch dynamically if None)
    """
    
    # Default pattern for PlayerStandings files with round format (e.g., TeamEvent_3rdRound_PlayerStandings_*.pdf)
    if pattern is None:
        pattern = r".*Event_.*Round_PlayerStandings_.*\.pdf"
    
    # Initialize components
    folder_id = "1PuSjJY5PSxXHja8xDESEhWk1kDhpX9hJ"
    downloader = GoogleDrivePDFDownloader(folder_id)
    parser = PDFParser()

    # If no file list provided, fetch dynamically
    if file_list is None:
        print("📋 Fetching file list from Google Drive...")
        file_list = downloader.fetch_file_list("pdf")
        
        if not file_list:
            print("❌ Failed to fetch file list from Google Drive")
            print("💡 Make sure you have:")
            print("   1. fcm-admin.json in the project root directory")
            print("   2. Google Drive API enabled for your service account")
            print("   3. Service account has access to the target folder")
            print("   4. Required packages: pip install -r requirements.txt")
            return None
        
        print(f"✅ Found {len(file_list)} PDF files in Google Drive folder")

    print(f"Converting Player Standings PDF to Simple CSV")
    print(f"Pattern: {pattern}")
    print("=" * 60)

    # Find matching files
    matching_files = downloader.find_matching_files(pattern, file_list)
    
    if not matching_files:
        print(f"❌ No files found matching pattern: {pattern}")
        print("📋 Available files:")
        for file_info in file_list[:10]:  # Show first 10 files
            print(f"   - {file_info['name']}")
        if len(file_list) > 10:
            print(f"   ... and {len(file_list) - 10} more files")
        return None
    
    # Select the file with the highest round number
    target_file = select_highest_round_file(matching_files)
    print(f"🎯 Selected file: {target_file['name']}")

    # Download if not already present
    download_path = f"downloads/{target_file['name']}"
    if not os.path.exists(download_path):
        print("📥 Downloading PDF...")
        success = downloader.download_pdf_direct(target_file["id"], target_file["name"])
        if not success:
            print("❌ Failed to download PDF")
            return None
    else:
        print("✅ PDF already downloaded")

    # Parse PDF
    print("🔍 Parsing PDF...")
    results = parser.parse_pdf_comprehensive(download_path)

    # Process tables
    print("📊 Processing tables...")
    tables_pdfplumber = results["tables_pdfplumber"]

    if not tables_pdfplumber:
        print("❌ No tables found in PDF")
        return None

    # Convert to list of dictionaries
    data_rows = process_player_standings_table(tables_pdfplumber)

    if data_rows is None or len(data_rows) == 0:
        print("❌ Failed to process table data")
        return None

    print(f"✅ Successfully processed {len(data_rows)} player records")

    # Create simplified version with just key columns
    key_columns = [
        "Rank",
        "Player_Name",
        "Team_Name",
        "Country",
        "Total_Score",
        "Round_1",
        "Round_2",
        "Round_3",
    ]
    
    # Filter to only include available key columns
    available_key_cols = [col for col in key_columns if any(col in row for row in data_rows)]
    
    if available_key_cols:
        # Create simplified data with only key columns
        simple_data = []
        for row in data_rows:
            simple_row = {col: row.get(col) for col in available_key_cols}
            simple_data.append(simple_row)

        # Display sample data
        print(f"\n📊 Sample data (first 5 rows):")
        display_sample_data(simple_data, 5)

        # Create output filename based on the source file
        base_name = os.path.splitext(target_file['name'])[0]
        simple_csv_filename = f"downloads/latest.csv"
        
        if save_to_csv(simple_data, simple_csv_filename):
            print(f"\n💾 CSV saved to: {simple_csv_filename}")
        else:
            print(f"\n❌ Failed to save CSV file")

        # Display data types
        print(f"\n📈 Data types:")
        type_info = get_data_types(simple_data)
        for col, dtype in type_info.items():
            print(f"   {col}: {dtype}")

        # Summary statistics for numeric columns
        display_summary_statistics(simple_data)

        return simple_data

    return None


if __name__ == "__main__":
    # Run the conversion with default pattern
    data = download_and_convert_to_csv()

    if data is not None:
        print(f"\n🎉 SUCCESS! Created CSV file with {len(data)} player records")
        print(f"📋 Columns: {list(data[0].keys()) if data else []}")
    else:
        print(f"\n❌ Failed to create CSV file")
        
    # Example: Run with custom pattern to match specific event types
    # data = download_and_convert_to_csv(pattern=r"TeamEvent_.*Round_PlayerStandings_.*\.pdf")
    # data = download_and_convert_to_csv(pattern=r"MainEvent_.*Round_PlayerStandings_.*\.pdf")
