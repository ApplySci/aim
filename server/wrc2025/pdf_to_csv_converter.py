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
        "Player_Name",
        "Team_Name",
        "Country",
        "Total_Score",
        "Round_1",
        "Round_2",
        "Round_3",
    ]
    
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

        # Generate HTML page
        generate_html_page(simple_data)

        return simple_data

    return None


def generate_html_page(simple_data, output_path="../static/wrc.html"):
    """Generate a mobile-friendly HTML page displaying the player standings
    
    Args:
        simple_data: List of dictionaries containing player data
        output_path: Path where to save the HTML file
    """
    if not simple_data:
        print("❌ No data to generate HTML page")
        return False
    
    # Get column names
    columns = list(simple_data[0].keys())
    
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WRC 2025 Player Standings</title>
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
        
        .team-name {{
            color: #7f8c8d;
            font-size: 0.9em;
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
        
        @media (max-width: 768px) {{
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
            
            .team-name {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏆 WRC 2025 Player Standings</h1>
        
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
            value = row.get(col, '')
            css_class = ''
            
            # Add specific styling based on column type
            if col == 'Rank':
                css_class = 'rank'
            elif col == 'Player_Name':
                css_class = 'player-name'
            elif col == 'Team_Name':
                css_class = 'team-name'
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
            elif isinstance(value, float):
                display_value = f'{value:.1f}' if value != int(value) else str(int(value))
            else:
                display_value = str(value)
            
            html_content += f'<td class="{css_class}">{display_value}</td>'
        
        html_content += '</tr>'
    
    html_content += '''
                    </tbody>
                </table>
                <div class="no-results" id="noResults" style="display: none;">
                    No players found matching your search.
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
            let visibleCount = 0;
            let firstMatch = null;

            // Show/hide rows based on search
            for (let i = 0; i < rows.length; i++) {
                const row = rows[i];
                const playerNameCell = row.querySelector('.player-name');
                
                if (playerNameCell) {
                    const playerName = playerNameCell.textContent.toLowerCase();
                    
                    if (searchTerm === '' || playerName.includes(searchTerm)) {
                        row.style.display = '';
                        visibleCount++;
                        
                        // Remember first match for scrolling
                        if (firstMatch === null && searchTerm !== '') {
                            firstMatch = row;
                        }
                    } else {
                        row.style.display = 'none';
                    }
                }
            }

            // Show/hide no results message
            if (visibleCount === 0 && searchTerm !== '') {
                noResults.style.display = 'block';
            } else {
                noResults.style.display = 'none';
            }

            // Scroll to first match
            if (firstMatch && searchTerm !== '') {
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
</body>
</html>'''
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"🌐 HTML page generated: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to generate HTML page: {e}")
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
