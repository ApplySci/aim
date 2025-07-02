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
    """Process the player standings table from PDF extraction"""
    if not tables:
        print("No tables found in PDF")
        return None

    # Get the first table (player standings)
    raw_table = tables[0]
    print(f"Raw table has {len(raw_table)} rows")

    # Find the header row (looking for "Rank" or similar)
    header_row_idx = None
    for i, row in enumerate(raw_table):
        if any(cell and ("Rank" in str(cell) or "No" in str(cell)) for cell in row):
            header_row_idx = i
            break

    if header_row_idx is None:
        print("Could not find header row")
        return None

    # Extract headers from the next row (which has more detailed column names)
    if header_row_idx + 1 < len(raw_table):
        headers = raw_table[header_row_idx + 1]
    else:
        headers = raw_table[header_row_idx]

    print(f"Headers found: {headers}")

    # Define our expected columns based on the data structure
    expected_columns = [
        "Rank",  # 0
        "Player_No",  # 2
        "Country",  # 5
        "Country_JP",  # 6
        "Player_Name",  # 7
        "Player_Name_JP",  # 8
        "Total_Score",  # 9
        "Round_1",  # 10
        "Round_2",  # 11
        "Round_3",  # 12
        "Round_4",  # 12
        "Round_5",  # 12
        "Round_6",  # 12
        "Round_7",  # 12
        "Round_8",  # 12
        "Round_9",  # 12
        "Round_10",  # 12
    ]

    # Process data rows (skip header rows)
    data_rows = []
    start_row = header_row_idx + 2  # Skip header rows

    for i, row in enumerate(raw_table[start_row:], start=start_row):
        if len(row) < 7:  # Skip rows that are too short
            continue

        # Skip empty rows
        if all(cell is None or str(cell).strip() == "" for cell in row):
            continue

        # Process each column
        processed_row = {}

        # Handle variable column lengths
        for col_idx, col_name in enumerate(expected_columns):
            if col_idx < len(row):
                cell_value = row[col_idx]
            else:
                cell_value = None

            # Apply appropriate data type conversion
            if col_name in ["Rank", "Player_No"]:
                processed_row[col_name] = clean_numeric_value(cell_value)
            elif col_name in [
                "Total_Score",
                "Round_1",
                "Round_2",
                "Round_3",
                "Round_4",
                "Round_5",
                "Round_6",
                "Round_7",
                "Round_8",
                "Round_9",
                "Round_10",
            ]:
                processed_row[col_name] = clean_numeric_value(cell_value)
            else:
                processed_row[col_name] = clean_string_value(cell_value)

        # Only add rows that have at least a rank
        if processed_row["Rank"] is not None:
            data_rows.append(processed_row)

    return data_rows


def download_and_convert_to_csv(pattern=None, file_list=None):
    """Main function to download PDF and convert to simple CSV
    
    Args:
        pattern: Regex pattern to match files (default: .*PlayerStandings.*\\.pdf)
        file_list: List of available files with 'name' and 'id' keys (will fetch dynamically if None)
    """
    
    # Default pattern for PlayerStandings files (works with both MainEvent and TeamEvent)
    if pattern is None:
        pattern = r".*PlayerStandings.*\.pdf"
    
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
    
    if len(matching_files) > 1:
        print(f"📋 Found {len(matching_files)} matching files:")
        for i, file_info in enumerate(matching_files):
            print(f"  {i+1}. {file_info['name']}")
        print("Using the first match...")
    
    # Use the first matching file
    target_file = matching_files[0]
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
        simple_csv_filename = f"downloads/{base_name}_processed.csv"
        
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
        
    # Example: Run with custom pattern
    # data = download_and_convert_to_csv(pattern=r"TeamEvent.*PlayerStandings.*\.pdf")
