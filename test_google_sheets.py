"""
Test script for Google Sheets authentication

This script tests the OAuth authentication flow and attempts to read
data from a Google Sheet. Run this after placing your credentials.json
file in the config/ directory.

Usage:
    poetry run python test_google_sheets.py
"""

import sys
import logging
from pathlib import Path
import importlib.util

# Add EigenLedger to path
sys.path.insert(0, str(Path(__file__).parent))

# Import directly from google_auth module file to avoid package __init__.py
spec = importlib.util.spec_from_file_location(
    "google_auth",
    Path(__file__).parent / "EigenLedger" / "modules" / "google_auth.py"
)
google_auth = importlib.util.module_from_spec(spec)
spec.loader.exec_module(google_auth)
GoogleSheetsClient = google_auth.GoogleSheetsClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Test Google Sheets authentication and data reading."""
    
    print("=" * 60)
    print("Google Sheets Authentication Test")
    print("=" * 60)
    print()
    
    # Check for credentials file
    creds_path = Path('config/credentials.json')
    if not creds_path.exists():
        print("❌ ERROR: credentials.json not found!")
        print(f"   Expected location: {creds_path.absolute()}")
        print()
        print("Please follow these steps:")
        print("1. Go to Google Cloud Console")
        print("2. Download your OAuth credentials")
        print("3. Save the file as 'config/credentials.json'")
        print()
        print("See cloudsetup.md for detailed instructions.")
        return 1
    
    print(f"✅ Found credentials file: {creds_path}")
    print()
    
    # Create client and authenticate
    try:
        print("Authenticating with Google Sheets API...")
        client = GoogleSheetsClient()
        client.authenticate()
        print("✅ Authentication successful!")
        print()
        
        # Show token status
        token_path = Path('config/token.pickle')
        if token_path.exists():
            print(f"✅ Token saved to: {token_path}")
            print("   (Future runs will use this token automatically)")
        print()
        
        # Prompt for sheet ID to test reading
        print("Would you like to test reading a Google Sheet? (y/n): ", end='')
        response = input().strip().lower()
        
        if response == 'y':
            print()
            print("Enter your Google Sheet ID")
            print("(Find this in the URL: docs.google.com/spreadsheets/d/SHEET_ID/edit)")
            sheet_id = input("Sheet ID: ").strip()
            
            print("Enter the range to read (e.g., 'Sheet1!A1:Z100')")
            range_name = input("Range: ").strip()
            
            print()
            print(f"Reading data from sheet...")
            data = client.read_sheet(sheet_id, range_name)
            
            if data:
                print(f"✅ Successfully read {len(data)} rows")
                print()
                print("First few rows:")
                print("-" * 60)
                for i, row in enumerate(data[:5], 1):
                    print(f"Row {i}: {row}")
                if len(data) > 5:
                    print(f"... and {len(data) - 5} more rows")
            else:
                print("⚠️  No data found in the specified range")
        
        print()
        print("=" * 60)
        print("✅ Test completed successfully! ")
        print("=" * 60)
        return 0
        
    except FileNotFoundError as e:
        print(f"❌ ERROR: {e}")
        return 1
    except Exception as e:
        logger.exception("Test failed")
        print(f"❌ ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
