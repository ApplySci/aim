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
        
        # Country (English - preferred)
        "country": "Country",
        "country region": "Country",
        "countryregion": "Country",  # Normalized from "Country/Region"
        
        # Country (Japanese - backup)
        "国": "Country_JP",
        "国 地域": "Country_JP",
        "国地域": "Country_JP",  # Normalized from "国/地域"
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
                
                # Check if next row is actually better headers by looking for header-like keywords
                # Don't just count cells with content - check for actual header keywords
                current_header_score = sum(1 for h in headers if h and any(keyword in str(h).lower() 
                                          for keyword in ['rank', 'no', 'name', 'country', 'total', '順位', '氏名', '国']))
                next_row_header_score = sum(1 for h in next_row if h and any(keyword in str(h).lower() 
                                           for keyword in ['rank', 'no', 'name', 'country', 'total', '順位', '氏名', '国']))
                
                # Only use next row as headers if it has MORE header keywords than current row
                if next_row_header_score > current_header_score:
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

            # Prefer English country name over Japanese
            english_country = processed_row.get("Country", "").strip()
            japanese_country = processed_row.get("Country_JP", "").strip()
            
            if english_country:
                # Use English country name if available
                processed_row["Country"] = english_country
            elif japanese_country:
                # Fall back to Japanese country name if English is not available
                processed_row["Country"] = japanese_country
            else:
                # No country information available
                processed_row["Country"] = ""
            
            # Remove the Japanese country field to avoid confusion
            if "Country_JP" in processed_row:
                del processed_row["Country_JP"]

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
    """Extract round number from filename in various formats
    
    Handles:
    - Old format: 'TeamEvent_3rdRound_PlayerStandings_*.pdf'
    - New format: 'MainEvent_1stRound_Standings_*.pdf'
    
    Returns:
        int: Round number (e.g., 3 for '3rd'), or 0 if not found
    """
    # Pattern to match {nth}Round format where n can be 1st, 2nd, 3rd, 4th, etc.
    # Works for both old and new formats
    patterns = [
        r".*Event_(\d+)(?:st|nd|rd|th)Round_PlayerStandings_",  # Old format
        r".*Event_(\d+)(?:st|nd|rd|th)Round_Standings_"         # New format
    ]
    
    for pattern in patterns:
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


def download_and_convert_to_csv(pattern=None, file_list=None, html_output_path=None):
    """Main function to download PDF and convert to simple CSV
    
    Args:
        pattern: Regex pattern to match files (default: .*PlayerStandings.*\\.pdf)
        file_list: List of available files with 'name' and 'id' keys (will fetch dynamically if None)
        html_output_path: Custom path for HTML output (if None, uses default relative path)
    """
    
    # Default pattern for player standings files with round format
    # Handles both old format (TeamEvent_3rdRound_PlayerStandings_*.pdf) and new format (MainEvent_1stRound_Standings_*.pdf)
    if pattern is None:
        pattern = r".*Event_.*Round_.*Standings_.*\.pdf"
    
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
    if html_output_path:
        # Use consistent path structure when called from Flask app
        current_dir = os.getcwd()
        downloads_dir = os.path.join(current_dir, "wrc2025", "downloads")
        download_path = os.path.join(downloads_dir, target_file['name'])
    else:
        download_path = f"downloads/{target_file['name']}"
    
    print(f"🔍 PDF download path: {os.path.abspath(download_path)}")
    
    # Ensure download directory exists before checking if file exists
    download_dir = os.path.dirname(download_path)
    os.makedirs(download_dir, exist_ok=True)
    print(f"🔍 Download directory created/verified: {download_dir}")
    
    if not os.path.exists(download_path):
        print("📥 Downloading PDF...")
        # Pass the custom download directory if we're using custom paths
        if html_output_path:
            success = downloader.download_pdf_direct(target_file["id"], target_file["name"], download_dir)
        else:
            success = downloader.download_pdf_direct(target_file["id"], target_file["name"])
        
        if not success:
            print("❌ Failed to download PDF")
            return None
        
        # Verify the download was successful
        if os.path.exists(download_path):
            file_size = os.path.getsize(download_path)
            print(f"✅ PDF downloaded successfully: {download_path} ({file_size} bytes)")
        else:
            print(f"❌ PDF download claimed success but file not found: {download_path}")
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

    # Create simplified version with key columns, dynamically including all available rounds
    base_key_columns = [
        "Player_Name",
        "Country",
        "Total_Score",
    ]
    
    # Dynamically find all available round columns
    all_round_columns = set()
    for row in data_rows:
        for col in row.keys():
            if col.startswith("Round_"):
                all_round_columns.add(col)
    
    # Sort round columns numerically (Round_1, Round_2, etc.)
    sorted_round_columns = sorted(all_round_columns, key=lambda x: int(x.split('_')[1]) if x.split('_')[1].isdigit() else 999)
    
    # Combine base columns with available round columns
    key_columns = base_key_columns + sorted_round_columns
    
    print(f"📋 Available rounds detected: {sorted_round_columns}")
    
    # Filter to only include available key columns (excluding Rank since we'll calculate it)
    available_key_cols = [col for col in key_columns if any(col in row for row in data_rows)]
    
    if available_key_cols:
        # Create simplified data with only key columns
        simple_data = []
        for row in data_rows:
            simple_row = {col: row.get(col) for col in available_key_cols}
            simple_data.append(simple_row)

        # Calculate rankings based on Total_Score
        simple_data = calculate_rankings(simple_data)
        
        # Reorder columns to put Rank first
        if simple_data:
            rank_first_cols = ['Rank'] + [col for col in simple_data[0].keys() if col != 'Rank']
            simple_data = [{col: row[col] for col in rank_first_cols} for row in simple_data]

        # Display sample data
        print(f"\n📊 Sample data (first 5 rows):")
        display_sample_data(simple_data, 5)

        # Create output filename based on the source file
        base_name = os.path.splitext(target_file['name'])[0]
        
        # Determine CSV path - if we have a custom HTML path, put CSV in the same directory structure
        if html_output_path:
            # Put CSV in wrc2025/downloads/ relative to the Flask app root
            current_dir = os.getcwd()
            csv_downloads_dir = os.path.join(current_dir, "wrc2025", "downloads")
            simple_csv_filename = os.path.join(csv_downloads_dir, "latest.csv")
        else:
            simple_csv_filename = f"downloads/latest.csv"
        
        # Debug: Show CSV path info
        abs_csv_path = os.path.abspath(simple_csv_filename)
        print(f"🔍 CSV will be saved to: {abs_csv_path}")
        
        # Ensure CSV directory exists
        csv_dir = os.path.dirname(abs_csv_path)
        os.makedirs(csv_dir, exist_ok=True)
        print(f"🔍 CSV directory created/verified: {csv_dir}")
        
        if save_to_csv(simple_data, simple_csv_filename):
            if os.path.exists(abs_csv_path):
                csv_size = os.path.getsize(abs_csv_path)
                print(f"\n💾 CSV saved successfully: {abs_csv_path} ({csv_size} bytes)")
            else:
                print(f"\n⚠️ CSV save reported success but file not found: {abs_csv_path}")
        else:
            print(f"\n❌ Failed to save CSV file to: {abs_csv_path}")

        # Display data types
        print(f"\n📈 Data types:")
        type_info = get_data_types(simple_data)
        for col, dtype in type_info.items():
            print(f"   {col}: {dtype}")

        # Summary statistics for numeric columns
        display_summary_statistics(simple_data)

        # Generate HTML page
        if html_output_path:
            generate_html_page(simple_data, output_path=html_output_path, pdf_filename=target_file['name'])
        else:
            generate_html_page(simple_data, pdf_filename=target_file['name'])

        # Update calendar.html and makecalendar.js files
        round_number = determine_round_number(simple_data)
        update_calendar_html(simple_data, round_number)
        update_makecalendar_js(simple_data, round_number)
        update_calendar_display_logic(round_number)

        return simple_data

    return None


def generate_html_page(simple_data, output_path="../static/wrc.html", pdf_filename=None):
    """Generate a mobile-friendly HTML page displaying the player standings
    
    Args:
        simple_data: List of dictionaries containing player data
        output_path: Path where to save the HTML file
        pdf_filename: Original PDF filename to determine appropriate title
    """
    if not simple_data:
        print("❌ No data to generate HTML page")
        return False
    
    # Determine page title based on PDF filename
    if pdf_filename and pdf_filename.startswith("TeamEvent"):
        page_title = "WRC 2025 Team Event, Individual Scores"
        header_title = "🏆 WRC 2025 Team Event, Individual Scores"
    elif pdf_filename and pdf_filename.startswith("MainEvent"):
        page_title = "WRC 2025 Main Event"
        header_title = "🏆 WRC 2025 Main Event"
    else:
        page_title = "WRC 2025 Player Standings"
        header_title = "🏆 WRC 2025 Player Standings"
    
    # Get column names
    columns = list(simple_data[0].keys())
    
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
            color: #333;
        }}
        
        .header-images {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 20px;
            margin: 20px 0;
            padding: 15px;
        }}
        
        .qr-code {{
            height: 120px;
            width: 120px;
            object-fit: contain;
        }}
        
        .logo {{
            height: 120px;
            object-fit: contain;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        h1 {{
            text-align: center;
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: clamp(1.5rem, 4vw, 2.5rem);
        }}
        
        .search-container {{
            margin-bottom: 20px;
            position: sticky;
            top: 0;
            z-index: 100;
            background-color: #f5f5f5;
            padding: 10px 0;
        }}
        
        .search-box {{
            width: 100%;
            padding: 12px 20px;
            font-size: 16px;
            border: 2px solid #ddd;
            border-radius: 25px;
            outline: none;
            transition: border-color 0.3s;
        }}
        
        .search-box:focus {{
            border-color: #3498db;
        }}
        
        .table-container {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .table-wrapper {{
            overflow-x: auto;
            max-height: 70vh;
            overflow-y: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        
        thead {{
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        
        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: bold;
            padding: 12px 8px;
            text-align: left;
            border-right: 1px solid rgba(255,255,255,0.2);
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        th.right-align {{
            text-align: right;
        }}
        
        th:last-child {{
            border-right: none;
        }}
        
        td {{
            padding: 10px 8px;
            border-bottom: 1px solid #eee;
            border-right: 1px solid #f0f0f0;
        }}
        
        td:last-child {{
            border-right: none;
        }}
        
        tbody tr {{
            transition: background-color 0.2s;
        }}
        
        tbody tr:hover {{
            background-color: #f8f9fa;
        }}
        
        tbody tr:nth-child(even) {{
            background-color: #fafafa;
        }}
        
        .rank {{
            font-weight: bold;
            color: #2c3e50;
            text-align: center;
        }}
        
        .player-name {{
            font-weight: 600;
            color: #2980b9;
        }}
        
        .country {{
            color: #7f8c8d;
            font-size: 0.85em;
            font-weight: normal;
        }}
        
        .score {{
            font-weight: bold;
            text-align: right;
        }}
        
        .score.positive {{
            color: #27ae60;
        }}
        
        .score.negative {{
            color: #e74c3c;
        }}
        
        .no-results {{
            text-align: center;
            padding: 40px;
            color: #7f8c8d;
            font-style: italic;
        }}
        
        tbody tr.highlighted {{
            background-color: #fff3cd !important;
            border-left: 4px solid #ffc107;
            animation: highlight-pulse 1.5s ease-in-out;
        }}
        
        @keyframes highlight-pulse {{
            0% {{ background-color: #fff3cd; }}
            50% {{ background-color: #ffecb5; }}
            100% {{ background-color: #fff3cd; }}
        }}
        
        @media (max-width: 768px) {{
            .header-images {{
                gap: 15px;
            }}
            
            .qr-code {{
                height: 100px;
                width: 100px;
            }}
            
            .logo {{
                height: 60px;
            }}
            
            .container {{
                padding: 10px;
            }}
            
            table {{
                font-size: 12px;
            }}
            
            th, td {{
                padding: 8px 4px;
            }}
            
            .search-box {{
                font-size: 16px; /* Prevent zoom on iOS */
            }}
        }}
        
        @media (max-width: 480px) {{
            th, td {{
                padding: 6px 3px;
            }}
            
            .country {{
                display: block;
                margin-top: 2px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{header_title}</h1>
        
        <div class="search-container">
            <input type="text" class="search-box" id="searchBox" placeholder="🔍 Search by player name...">
        </div>
        
        <div class="table-container">
            <div class="table-wrapper" id="tableWrapper">
                <table>
                    <thead>
                        <tr>'''
    
    # Add column headers
    for col in columns:
        if col == 'Country':
            # Skip Country column as it will be combined with Player_Name
            continue
        elif col.startswith('Round_'):
            # Convert Round_1, Round_2, etc. to H#1, H#2, etc.
            round_num = col.split('_')[1]
            display_name = f'H#{round_num}'
            html_content += f'<th class="right-align">{display_name}</th>'
        elif col == 'Total_Score':
            display_name = 'Total'
            html_content += f'<th class="right-align">{display_name}</th>'
        else:
            display_name = col.replace('_', ' ').title()
            html_content += f'<th>{display_name}</th>'
    
    html_content += '''
                        </tr>
                    </thead>
                    <tbody id="tableBody">'''
    
    # Add data rows
    for i, row in enumerate(simple_data):
        html_content += f'<tr id="row-{i}">'
        
        for col in columns:
            if col == 'Country':
                # Skip Country column as it's combined with Player_Name
                continue
                
            value = row.get(col, '')
            css_class = ''
            
            # Add specific styling based on column type
            if col == 'Rank':
                css_class = 'rank'
            elif col == 'Player_Name':
                css_class = 'player-name'
                # Combine player name with country
                player_name = str(value) if value else ''
                country = row.get('Country', '')
                
                if country and country.strip():
                    display_value = f'{player_name} <span class="country">({country})</span>'
                else:
                    display_value = player_name
                html_content += f'<td class="{css_class}">{display_value}</td>'
                continue
            elif 'Score' in col or 'Round_' in col:
                css_class = 'score'
                if isinstance(value, (int, float)) and value is not None:
                    if value > 0:
                        css_class += ' positive'
                    elif value < 0:
                        css_class += ' negative'
            
            # Format the value
            if value is None or value == '':
                display_value = '-'
            elif isinstance(value, (int, float)):
                # Format numeric values with + prefix for positive scores and always 1 decimal place
                if 'Score' in col or 'Round_' in col:
                    if value > 0:
                        display_value = f'+{value:.1f}'
                    elif value < 0:
                        display_value = f'{value:.1f}'
                    else:  # value == 0
                        display_value = '0.0'
                else:
                    display_value = f'{value:.1f}'
            else:
                display_value = str(value)
            
            html_content += f'<td class="{css_class}">{display_value}</td>'
        
        html_content += '</tr>'
    
    html_content += '''
                    </tbody>
                </table>
                <div class="no-results" id="noResults" style="display: none;">
                    No players found matching your search term.
                </div>
            </div>
        </div>
    </div>

    <script>
        const searchBox = document.getElementById('searchBox');
        const tableBody = document.getElementById('tableBody');
        const tableWrapper = document.getElementById('tableWrapper');
        const noResults = document.getElementById('noResults');
        const rows = tableBody.getElementsByTagName('tr');

        searchBox.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase().trim();
            let matchCount = 0;
            let firstMatch = null;

            // Clear all highlights and keep all rows visible
            for (let i = 0; i < rows.length; i++) {
                const row = rows[i];
                row.classList.remove('highlighted');
                row.style.display = ''; // Always keep rows visible
            }

            // If search term is empty, no highlighting needed
            if (searchTerm === '') {
                noResults.style.display = 'none';
                return;
            }

            // Highlight matching rows
            for (let i = 0; i < rows.length; i++) {
                const row = rows[i];
                const playerNameCell = row.querySelector('.player-name');
                
                if (playerNameCell) {
                    const playerName = playerNameCell.textContent.toLowerCase();
                    
                    if (playerName.includes(searchTerm)) {
                        row.classList.add('highlighted');
                        matchCount++;
                        
                        // Remember first match for scrolling
                        if (firstMatch === null) {
                            firstMatch = row;
                        }
                    }
                }
            }

            // Show/hide no results message (though rows are still visible)
            if (matchCount === 0) {
                noResults.style.display = 'block';
            } else {
                noResults.style.display = 'none';
            }

            // Scroll to first match
            if (firstMatch) {
                setTimeout(() => {
                    const rect = firstMatch.getBoundingClientRect();
                    const wrapperRect = tableWrapper.getBoundingClientRect();
                    const scrollTop = tableWrapper.scrollTop + rect.top - wrapperRect.top - 60;
                    
                    tableWrapper.scrollTo({
                        top: Math.max(0, scrollTop),
                        behavior: 'smooth'
                    });
                }, 100);
            }
        });

        // Add some keyboard navigation
        searchBox.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                this.value = '';
                this.dispatchEvent(new Event('input'));
            }
        });
    </script>
        
        <div class="header-images">
            <img src="wrcqr.png" alt="WRC QR Code" class="qr-code">
            <img src="20205logo.svg" alt="2025 Logo" class="logo">
        </div>
    </div>
</body>
</html>'''
    
    try:
        # Get absolute path for clarity
        abs_output_path = os.path.abspath(output_path)
        output_dir = os.path.dirname(abs_output_path)
        
        print(f"🔍 Attempting to write HTML to: {abs_output_path}")
        print(f"🔍 Output directory: {output_dir}")
        print(f"🔍 Directory exists: {os.path.exists(output_dir)}")
        
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        print(f"🔍 Directory created/verified: {output_dir}")
        
        with open(abs_output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Verify file was created
        if os.path.exists(abs_output_path):
            file_size = os.path.getsize(abs_output_path)
            print(f"🌐 HTML page generated successfully: {abs_output_path} ({file_size} bytes)")
            return True
        else:
            print(f"❌ HTML file not found after writing: {abs_output_path}")
            return False
        
    except Exception as e:
        print(f"❌ Failed to generate HTML page: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False


def calculate_rankings(data_rows):
    """Calculate rankings based on Total_Score, handling ties with = prefix
    
    Args:
        data_rows: List of dictionaries containing player data
        
    Returns:
        List of dictionaries with Rank column added
    """
    if not data_rows:
        return data_rows
    
    # Sort by Total_Score in descending order (highest first)
    sorted_data = sorted(data_rows, key=lambda x: x.get('Total_Score', 0) if x.get('Total_Score') is not None else -float('inf'), reverse=True)
    
    # Calculate rankings
    current_rank = 1
    for i, row in enumerate(sorted_data):
        current_score = row.get('Total_Score')
        
        if i == 0:
            # First player always gets rank 1
            row['Rank'] = '1'
            last_score = current_score
        else:
            # Check if score is the same as previous player
            if current_score == last_score and current_score is not None:
                # Tie - use = prefix and same rank as previous
                prev_rank = sorted_data[i-1]['Rank']
                if prev_rank.startswith('='):
                    row['Rank'] = prev_rank  # Keep the same =rank
                else:
                    # Convert previous rank to =rank and apply to both
                    equal_rank = f'={prev_rank}'
                    sorted_data[i-1]['Rank'] = equal_rank
                    row['Rank'] = equal_rank
            else:
                # Different score - calculate new rank
                current_rank = i + 1
                row['Rank'] = str(current_rank)
                last_score = current_score
    
    return sorted_data


def get_google_drive_file_list():
    """Get list of PDF files from Google Drive folder for web interface
    
    Returns:
        List of dictionaries with file information (name, id, size, createdTime, modifiedTime)
        Returns empty list if unable to fetch files
    """
    try:
        # Initialize components with same folder ID as main function
        folder_id = "1PuSjJY5PSxXHja8xDESEhWk1kDhpX9hJ"
        downloader = GoogleDrivePDFDownloader(folder_id)
        
        # Fetch file list
        file_list = downloader.fetch_file_list("pdf")
        
        if not file_list:
            print("❌ Failed to fetch file list from Google Drive")
            return []
        
        # Sort by modified time (newest first)
        file_list.sort(key=lambda x: x.get('modifiedTime', ''), reverse=True)
        
        return file_list
        
    except Exception as e:
        print(f"❌ Error fetching file list: {e}")
        return []


def process_selected_file(file_id, file_name):
    """Process a specific file selected from the web interface
    
    Args:
        file_id: Google Drive file ID
        file_name: Name of the file
        
    Returns:
        dict: Result information with success status and message
    """
    try:
        # Create file_list with just the selected file
        selected_file_list = [{
            'id': file_id,
            'name': file_name
        }]
        
        # Determine the correct path for the HTML file
        # Assume we're running from the Flask app root (server directory)
        current_dir = os.getcwd()
        html_output_path = os.path.join(current_dir, "static", "wrc.html")
        
        # Call the main conversion function with the specific file and HTML path
        result = download_and_convert_to_csv(pattern=None, file_list=selected_file_list, html_output_path=html_output_path)
        
        if result is not None:
            # Check if HTML file was actually created
            if os.path.exists(html_output_path):
                html_size = os.path.getsize(html_output_path)
                html_info = f" HTML file created: {html_output_path} ({html_size} bytes)"
            else:
                html_info = f" ⚠️ HTML file not found at: {html_output_path}"
            
            return {
                'success': True,
                'message': f'Successfully processed {len(result)} player records from {file_name}.{html_info}',
                'record_count': len(result),
                'filename': file_name,
                'html_path': html_output_path
            }
        else:
            return {
                'success': False,
                'message': f'Failed to process {file_name}',
                'filename': file_name
            }
            
    except Exception as e:
        return {
            'success': False,
            'message': f'Error processing {file_name}: {str(e)}',
            'filename': file_name
        }


def format_score(score):
    """Format score with + prefix for positive values and 1 decimal place
    
    Args:
        score: Numeric score value
        
    Returns:
        str: Formatted score string (e.g., '+14.0', '-2.5', '0.0')
    """
    if score is None:
        return "+0.0"
    
    score_val = float(score)
    if score_val >= 0:
        return f"+{score_val:.1f}"
    else:
        return f"{score_val:.1f}"


def determine_round_number(simple_data):
    """Determine the number of rounds based on available Round_X columns with actual data
    
    Args:
        simple_data: List of dictionaries containing player data
        
    Returns:
        int: Number of rounds with actual data (not None)
    """
    if not simple_data:
        return 0
    
    # Find all Round_X columns with actual data
    max_round_with_data = 0
    for col in simple_data[0].keys():
        if col.startswith('Round_'):
            try:
                round_num = int(col.split('_')[1])
                
                # Check if this round has actual data (not None) for any player
                has_data = any(
                    row.get(col) is not None 
                    for row in simple_data
                )
                
                if has_data:
                    max_round_with_data = max(max_round_with_data, round_num)
                    
            except (ValueError, IndexError):
                continue
    
    return max_round_with_data


def update_calendar_html(simple_data, round_number):
    """Update the calendar.html file with current round information
    
    Args:
        simple_data: List of dictionaries containing player data
        round_number: Number of rounds completed
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Get the server directory based on script location (works regardless of cwd)
    script_dir = os.path.dirname(os.path.abspath(__file__))  # wrc2025/
    server_dir = os.path.dirname(script_dir)  # server/
    calendar_html_path = os.path.join(server_dir, "static", "cal", "calendar.html")
    calendar_css_path = os.path.join(server_dir, "static", "cal", "calendar.css")
    

    
    try:
        # Read the current calendar.html file
        with open(calendar_html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the h1 tag and add the round information
        round_info = f"Scores and ranks as of the end of round {round_number}"
        
        # Replace the h1 content (remove existing round-info if present)
        import re
        content = re.sub(
            r'<h1>Tournament Calendar</h1>(\s*<div class="round-info">[^<]*</div>)?',
            f'<h1>Tournament Calendar</h1>\n    <div class="round-info">{round_info}</div>',
            content
        )
        
        # Write the updated HTML content back
        with open(calendar_html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Update the CSS file to add round-info styles if not present
        try:
            with open(calendar_css_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
            
            if '.round-info' not in css_content:
                css_addition = '''
.round-info {
    text-align: center;
    font-size: 1.2em;
    color: #666;
    margin-bottom: 20px;
    font-weight: normal;
}
'''
                css_content += css_addition
                
                with open(calendar_css_path, 'w', encoding='utf-8') as f:
                    f.write(css_content)
                
                print(f"✅ Updated calendar.css with round-info styles")
        except Exception as css_e:
            print(f"⚠️ Warning: Could not update calendar.css: {css_e}")
        
        print(f"✅ Updated calendar.html with round {round_number} information")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update calendar.html: {e}")
        return False


def update_makecalendar_js(simple_data, round_number):
    """Update the makecalendar.js file with current player rankings and scores
    
    Args:
        simple_data: List of dictionaries containing player data
        round_number: Number of rounds completed
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Get the server directory based on script location (works regardless of cwd)
    script_dir = os.path.dirname(os.path.abspath(__file__))  # wrc2025/
    server_dir = os.path.dirname(script_dir)  # server/
    makecalendar_js_path = os.path.join(server_dir, "static", "cal", "makecalendar.js")
    

    
    try:
        # Read the current makecalendar.js file
        with open(makecalendar_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create a lookup map for player rankings and scores
        player_lookup = {}
        for player in simple_data:
            name = player.get('Player_Name', '')
            rank = player.get('Rank', '')
            score = player.get('Total_Score', 0)
            
            if name:
                # Clean the rank (remove = prefix if present)
                rank_clean = rank.replace('=', '') if rank else ''
                score_formatted = format_score(score)
                player_lookup[name] = {
                    'rank': rank_clean,
                    'score': score_formatted
                }
        
        import re
        
        # Update the completed rounds constant at the top of the file
        content = re.sub(
            r'(const COMPLETED_ROUNDS = )\d+;',
            f'\\g<1>{round_number};',
            content
        )
        
        # If the constant doesn't exist, add it after the TOURNAMENT_DATA definition
        if 'const COMPLETED_ROUNDS' not in content:
            content = re.sub(
                r'(const TOURNAMENT_DATA = \{[^}]*\};)',
                f'\\1\n\n// Number of completed rounds (updated by PDF converter)\nconst COMPLETED_ROUNDS = {round_number};',
                content,
                flags=re.DOTALL
            )
        
        # Add utility function to extract clean names from full names (for autocomplete)
        clean_name_function = '''
// Utility function to extract clean name from full name (removes rank and score)
function getCleanPlayerName(fullName) {
    // Extract just the player name (remove rank and score)
    const match = fullName.match(/^([^,]+)(?:, #\\\\d+, [+-]?[\\\\d.]+)?$/);
    return match ? match[1] : fullName;
}

// Utility function to create player name mapping for autocomplete
function createPlayerNameMapping() {
    const mapping = new Map();
    TOURNAMENT_DATA.players.forEach(player => {
        const cleanName = getCleanPlayerName(player.name);
        mapping.set(cleanName, player.name);
    });
    return mapping;
}

'''
        
        # Insert the utility functions after the formatPlayerName function
        if 'function getCleanPlayerName' not in content:
            content = re.sub(
                r'(function formatPlayerName\(fullName, roundNumber\) \{[\s\S]*?\}\n\n)',
                f'\\1{clean_name_function}',
                content
            )
        
        # Update the getAllPlayerNames function to return clean names
        old_get_all_player_names = r'function getAllPlayerNames\(\) \{\s*return TOURNAMENT_DATA\.players\.map\(p => p\.name\)\.sort\(\);\s*\}'
        new_get_all_player_names = '''function getAllPlayerNames() {
    return TOURNAMENT_DATA.players.map(p => getCleanPlayerName(p.name)).sort();
}'''
        
        content = re.sub(old_get_all_player_names, new_get_all_player_names, content)
        
        # Update the setupTypeahead function to handle clean names properly
        old_setup_typeahead = r'function setupTypeahead\(\) \{[\s\S]*?// Load all player names\s*allPlayerNames = getAllPlayerNames\(\);'
        new_setup_typeahead = '''function setupTypeahead() {
    const searchInput = document.getElementById('playerSearch');
    const suggestionsDiv = document.getElementById('suggestions');
    
    // Load all player names and create mapping
    allPlayerNames = getAllPlayerNames();
    const playerNameMapping = createPlayerNameMapping();'''
        
        content = re.sub(old_setup_typeahead, new_setup_typeahead, content)
        
        # Update the suggestion click handler to map clean names back to full names
        old_suggestion_click = r'// Handle suggestion clicks\s*suggestionsDiv\.addEventListener\(\'click\', function\(e\) \{\s*if \(e\.target\.classList\.contains\(\'suggestion-item\'\)\) \{\s*const playerName = e\.target\.getAttribute\(\'data-name\'\);\s*searchInput\.value = playerName;\s*suggestionsDiv\.style\.display = \'none\';\s*showPlayerSchedule\(playerName\);\s*\}\s*\}\);'
        new_suggestion_click = '''// Handle suggestion clicks
    suggestionsDiv.addEventListener('click', function(e) {
        if (e.target.classList.contains('suggestion-item')) {
            const cleanPlayerName = e.target.getAttribute('data-name');
            const fullPlayerName = playerNameMapping.get(cleanPlayerName);
            searchInput.value = cleanPlayerName;
            suggestionsDiv.style.display = 'none';
            showPlayerSchedule(fullPlayerName);
        }
    });'''
        
        content = re.sub(old_suggestion_click, new_suggestion_click, content)
        
        # Update the enter key handler to map clean names back to full names
        old_enter_key = r'// Handle enter key\s*searchInput\.addEventListener\(\'keydown\', function\(e\) \{\s*if \(e\.key === \'Enter\'\) \{\s*const suggestions = suggestionsDiv\.querySelectorAll\(\'\.suggestion-item\'\);\s*if \(suggestions\.length > 0\) \{\s*const playerName = suggestions\[0\]\.getAttribute\(\'data-name\'\);\s*searchInput\.value = playerName;\s*suggestionsDiv\.style\.display = \'none\';\s*showPlayerSchedule\(playerName\);\s*\}\s*\}\s*\}\);'
        new_enter_key = '''// Handle enter key
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            const suggestions = suggestionsDiv.querySelectorAll('.suggestion-item');
            if (suggestions.length > 0) {
                const cleanPlayerName = suggestions[0].getAttribute('data-name');
                const fullPlayerName = playerNameMapping.get(cleanPlayerName);
                searchInput.value = cleanPlayerName;
                suggestionsDiv.style.display = 'none';
                showPlayerSchedule(fullPlayerName);
            }
        }
    });'''
        
        content = re.sub(old_enter_key, new_enter_key, content)
        
        # Update player data in both getAllPlayerData and getAllTeamData functions
        # Pattern to match individual player entries in any data function
        player_pattern = r'\[(\d+),"([^"]+)","([^"]+)",([^\]]+)\]'
        
        def replace_player_entry(player_match):
            player_id = player_match.group(1)
            country = player_match.group(2)
            full_name = player_match.group(3)
            table_data = player_match.group(4)
            
            # Extract clean player name (remove existing rank and score)
            clean_name_match = re.match(r'^([^,]+)(?:, #\d+, [+-]?[\d.]+)?$', full_name)
            if clean_name_match:
                clean_name = clean_name_match.group(1).strip()
            else:
                clean_name = full_name.strip()
            
            # Update player name with current rank and score
            if clean_name in player_lookup:
                rank = player_lookup[clean_name]['rank']
                score = player_lookup[clean_name]['score']
                updated_name = f"{clean_name}, #{rank}, {score}"
            else:
                # Keep the clean name if no ranking data found
                updated_name = clean_name
            
            return f'[{player_id},"{country}","{updated_name}",{table_data}]'
        
        # Apply the update to all player entries in the file
        content = re.sub(player_pattern, replace_player_entry, content)
        
        # Write the updated content back
        with open(makecalendar_js_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Updated makecalendar.js with player rankings and scores for all events")
        print(f"✅ Updated autocomplete to show clean names while preserving functionality")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update makecalendar.js: {e}")
        return False


def update_calendar_display_logic(round_number):
    """Add JavaScript logic to conditionally display rank/score based on completed rounds
    
    Args:
        round_number: Number of rounds completed
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Get the server directory based on script location (works regardless of cwd)
    script_dir = os.path.dirname(os.path.abspath(__file__))  # wrc2025/
    server_dir = os.path.dirname(script_dir)  # server/
    makecalendar_js_path = os.path.join(server_dir, "static", "cal", "makecalendar.js")
    

    
    try:
        # Read the current makecalendar.js file
        with open(makecalendar_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add utility function to format player names based on round completion
        utility_function = '''
// Utility function to format player name based on round completion
function formatPlayerName(fullName, roundNumber) {
    // If round is completed or this is team event, show just the name
    if (roundNumber <= COMPLETED_ROUNDS) {
        // Extract just the player name (remove rank and score)
        const match = fullName.match(/^([^,]+)(?:, #\\\\d+, [+-]?[\\\\d.]+)?$/);
        return match ? match[1] : fullName;
    }
    // For future rounds, show full name with rank and score
    return fullName;
}

'''
        
        # Insert the utility function after the COMPLETED_ROUNDS constant
        import re
        
        # Find the COMPLETED_ROUNDS constant and add the function after it
        if 'function formatPlayerName' not in content:
            content = re.sub(
                r'(const COMPLETED_ROUNDS = \d+;)',
                f'\\1\n{utility_function}',
                content
            )
        
        # Update the showPlayerSchedule function to use formatPlayerName
        # Find the tablemates mapping section and update it
        tablemates_pattern = r'(\$\{roundInfo\.tablemates\.map\(mate => `[\s\S]*?<li class="tablemate">[\s\S]*?)\$\{mate\.name\}([\s\S]*?`\)\.join\(\'\'\)\})'
        
        def update_tablemates_display(match):
            before = match.group(1)
            after = match.group(2)
            return f'{before}${{formatPlayerName(mate.name, roundInfo.round)}}{after}'
        
        content = re.sub(tablemates_pattern, update_tablemates_display, content)
        
        # Also update team event tablemates display
        # The pattern is slightly different for team events
        team_tablemates_pattern = r'(\$\{roundInfo\.tablemates\.map\(mate => `[\s\S]*?<li class="tablemate">[\s\S]*?)\$\{mate\.name\}([\s\S]*?<span class="country">\(\$\{mate\.teamName\}\)</span>[\s\S]*?`\)\.join\(\'\'\)\})'
        
        def update_team_tablemates_display(match):
            before = match.group(1)
            after = match.group(2)
            # For team events, always show just the name (no rank/score)
            return f'{before}${{formatPlayerName(mate.name, 1)}}{after}'  # Use 1 to ensure name only
        
        content = re.sub(team_tablemates_pattern, update_team_tablemates_display, content)
        
        # Write the updated content back
        with open(makecalendar_js_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Updated calendar display logic for conditional rank/score display")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update calendar display logic: {e}")
        return False


if __name__ == "__main__":
    # Run the conversion with default pattern
    data = download_and_convert_to_csv()

    if data is not None:
        print(f"\n🎉 SUCCESS! Created CSV file with {len(data)} player records")
        print(f"📋 Columns: {list(data[0].keys()) if data else []}")
        print(f"🌐 HTML page also generated for web viewing")
    else:
        print(f"\n❌ Failed to create CSV file")
        
    # Example: Run with custom pattern to match specific event types
    # data = download_and_convert_to_csv(pattern=r"TeamEvent_.*Round_PlayerStandings_.*\.pdf")
    # data = download_and_convert_to_csv(pattern=r"MainEvent_.*Round_PlayerStandings_.*\.pdf")
