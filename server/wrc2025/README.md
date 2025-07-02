# Google Drive PDF Downloader and Parser

This project allows you to download and parse PDFs from public Google Drive folders using Python 3. It's specifically designed for tournament management systems but can be adapted for any PDF processing needs.

## 🚀 Quick Answer to Your Questions

### Do you need special Google Drive API permissions?

**For PUBLIC Google Drive folders: NO special permissions needed!**

- ✅ **Direct Download Method**: Works immediately for truly public files
- ✅ **No OAuth required**: Public files can be accessed directly
- ✅ **No API keys needed**: For basic public file access

**Optional: Google Drive API (for better reliability)**
- More robust file listing and metadata access
- Requires a simple API key (free) or service account
- Not required for basic functionality

## 📋 Features

- **Download PDFs** from public Google Drive folders
- **Multiple PDF parsing methods**:
  - Text extraction (PyPDF2, pdfplumber)
  - Table extraction (pdfplumber)  
  - Pattern-based file matching
- **No authentication required** for public folders

## 🛠 Installation

1. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

2. **For advanced table extraction (optional)**:
```bash
# Install Java (required for tabula-py)
# Windows: Download from Oracle or use chocolatey
# macOS: brew install openjdk
# Linux: apt-get install default-jdk
```

## 📁 Files Overview

- `drive_pdf_downloader.py` - Main downloader and parser classes
- `requirements.txt` - Python dependencies

## 🚀 Quick Start

