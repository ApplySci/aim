#!/usr/bin/env python3
"""
Google Drive PDF Downloader and Parser
"""

import os
import re
import requests
from typing import List, Dict, Optional, Any
from urllib.parse import urlparse, parse_qs
import logging

# PDF parsing libraries
try:
    import PyPDF2
    import pdfplumber
except ImportError as e:
    print(f"Warning: Some PDF libraries not available: {e}")
    print("Run: pip install -r requirements.txt")

# Google API libraries
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    print("Warning: Google API libraries not available. File listing will be limited.")
    print("Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    GOOGLE_API_AVAILABLE = False

class GoogleDrivePDFDownloader:
    def __init__(self, folder_id: str, service_account_file: str = None):
        """Initialize with Google Drive folder ID and service account credentials
        
        Args:
            folder_id: Google Drive folder ID
            service_account_file: Path to service account JSON file (default: looks for fcm-admin.json)
        """
        self.folder_id = folder_id
        self.base_url = "https://drive.google.com"
        self.service = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Scopes needed for Google Drive API
        self.SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
        
        # Determine service account file path
        if service_account_file is None:
            # Look for fcm-admin.json in parent directory (same as oauth_setup.py)
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            service_account_file = os.path.join(parent_dir, "fcm-admin.json")
        
        self.service_account_file = service_account_file
        
    def _authenticate_google_drive(self) -> bool:
        """Authenticate with Google Drive API using service account"""
        if not GOOGLE_API_AVAILABLE:
            self.logger.error("Google API libraries not available. Cannot authenticate.")
            return False
            
        try:
            # Check if service account file exists
            if not os.path.exists(self.service_account_file):
                self.logger.error(f"Service account file not found: {self.service_account_file}")
                self.logger.error("Make sure fcm-admin.json exists in the project root directory")
                return False
            
            # Load service account credentials
            credentials = service_account.Credentials.from_service_account_file(
                self.service_account_file, 
                scopes=self.SCOPES
            )
            
            # Build the Drive service
            self.service = build('drive', 'v3', credentials=credentials)
            self.logger.info("Successfully authenticated with Google Drive API using service account")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to authenticate with Google Drive API: {e}")
            self.logger.error("Make sure the service account has Google Drive API access enabled")
            return False
    
    def fetch_file_list(self, file_extension: str = "pdf") -> List[Dict[str, str]]:
        """Dynamically fetch file list from Google Drive folder
        
        Args:
            file_extension: File extension to filter by (default: "pdf")
            
        Returns:
            List of dictionaries with file information (name, id, mimeType, size)
        """
        if not self._authenticate_google_drive():
            self.logger.error("Failed to authenticate with Google Drive")
            return []
        
        try:
            # Query to get all files in the folder
            query = f"'{self.folder_id}' in parents and trashed=false"
            if file_extension:
                query += f" and name contains '.{file_extension}'"
            
            self.logger.info(f"Fetching files from folder: {self.folder_id}")
            self.logger.info(f"Query: {query}")
            
            results = self.service.files().list(
                q=query,
                pageSize=100,  # Adjust as needed
                fields="nextPageToken, files(id, name, mimeType, size, createdTime, modifiedTime)"
            ).execute()
            
            files = results.get('files', [])
            
            # Format the results
            file_list = []
            for file_info in files:
                file_dict = {
                    'id': file_info.get('id'),
                    'name': file_info.get('name'),
                    'mimeType': file_info.get('mimeType'),
                    'size': file_info.get('size'),
                    'createdTime': file_info.get('createdTime'),
                    'modifiedTime': file_info.get('modifiedTime')
                }
                file_list.append(file_dict)
            
            self.logger.info(f"Found {len(file_list)} files")
            return file_list
            
        except Exception as e:
            self.logger.error(f"Error fetching file list: {e}")
            return []
    
    def list_files_by_pattern(self, pattern: str) -> List[Dict[str, str]]:
        """Get files matching a specific pattern
        
        Args:
            pattern: Regex pattern to match filenames
            
        Returns:
            List of matching files
        """
        all_files = self.fetch_file_list()
        return self.find_matching_files(pattern, all_files)
    
    def extract_folder_id(self, url: str) -> str:
        """Extract folder ID from Google Drive URL"""
        if '/folders/' in url:
            return url.split('/folders/')[1].split('?')[0]
        return url
    
    def download_pdf_direct(self, file_id: str, filename: str, custom_download_dir: str = None) -> bool:
        """Download PDF directly using file ID
        
        Args:
            file_id: Google Drive file ID
            filename: Name of the file to save
            custom_download_dir: Custom directory to save the file (if None, uses 'downloads/')
        """
        try:
            # Direct download URL for Google Drive files
            download_url = f"https://drive.google.com/uc?id={file_id}&export=download"
            
            response = requests.get(download_url, stream=True)
            
            # Handle potential redirect for large files
            if 'download_warning' in response.url:
                # Extract confirmation token
                confirm_token = None
                for key, value in parse_qs(urlparse(response.url).query).items():
                    if key == 'confirm':
                        confirm_token = value[0]
                        break
                
                if confirm_token:
                    download_url = f"https://drive.google.com/uc?export=download&confirm={confirm_token}&id={file_id}"
                    response = requests.get(download_url, stream=True)
            
            if response.status_code == 200:
                # Use custom directory if provided, otherwise default to 'downloads'
                if custom_download_dir:
                    download_dir = custom_download_dir
                    filepath = os.path.join(download_dir, filename)
                else:
                    download_dir = 'downloads'
                    filepath = f"downloads/{filename}"
                
                os.makedirs(download_dir, exist_ok=True)
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                self.logger.info(f"Downloaded: {filename}")
                return True
            else:
                self.logger.error(f"Failed to download {filename}: Status {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error downloading {filename}: {e}")
            return False
    
    def find_matching_files(self, pattern: str, file_list: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Find files matching a specific pattern"""
        matching_files = []
        regex_pattern = re.compile(pattern, re.IGNORECASE)
        
        for file_info in file_list:
            if regex_pattern.search(file_info.get('name', '')):
                matching_files.append(file_info)
                
        return matching_files

class PDFParser:
    """PDF parsing utilities"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_text_pypdf2(self, pdf_path: str) -> str:
        """Extract text using PyPDF2"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            self.logger.error(f"Error extracting text with PyPDF2: {e}")
            return ""
    
    def extract_text_pdfplumber(self, pdf_path: str) -> str:
        """Extract text using pdfplumber (better for complex layouts)"""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            self.logger.error(f"Error extracting text with pdfplumber: {e}")
            return ""
    
    def extract_tables_pdfplumber(self, pdf_path: str) -> List[List[List[str]]]:
        """Extract tables using pdfplumber"""
        try:
            tables = []
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_tables = page.extract_tables()
                    if page_tables:
                        tables.extend(page_tables)
            return tables
        except Exception as e:
            self.logger.error(f"Error extracting tables with pdfplumber: {e}")
            return []
    
    def parse_pdf_comprehensive(self, pdf_path: str) -> Dict[str, Any]:
        """Comprehensive PDF parsing returning text and tables"""
        results = {
            'filename': os.path.basename(pdf_path),
            'text_pypdf2': self.extract_text_pypdf2(pdf_path),
            'text_pdfplumber': self.extract_text_pdfplumber(pdf_path),
            'tables_pdfplumber': self.extract_tables_pdfplumber(pdf_path)
        }
        return results

def main():
    """Example usage"""
    # Your Google Drive folder ID
    folder_id = "1PuSjJY5PSxXHja8xDESEhWk1kDhpX9hJ"
    
    # Initialize downloader
    downloader = GoogleDrivePDFDownloader(folder_id)
    parser = PDFParser()
    
    # Example: Find files matching "TeamStandings" pattern
    pattern = r"PlayerStandings"
    matching_files = downloader.list_files_by_pattern(pattern)
    
    print(f"Found {len(matching_files)} files matching pattern '{pattern}':")
    for file_info in matching_files:
        print(f"- {file_info['name']}")
    
    # Example parsing (assuming you have a downloaded PDF)
    # Uncomment and modify as needed:
    # if os.path.exists('downloads/some_file.pdf'):
    #     results = parser.parse_pdf_comprehensive('downloads/some_file.pdf')
    #     print("\nPDF Content Summary:")
    #     print(f"Text length: {len(results['text_pdfplumber'])} characters")
    #     print(f"Number of tables found: {len(results['tables_pdfplumber'])}")

if __name__ == "__main__":
    main() 