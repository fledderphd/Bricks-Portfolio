"""
Google Sheets API Authentication Module

This module handles OAuth 2.0 authentication with Google Sheets API
and provides functions to read data from Google Sheets.
"""

import os
import pickle
from pathlib import Path
from typing import List, Optional, Any
import logging

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configure logging
logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.pickle
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# Default paths for credentials and token
DEFAULT_CREDENTIALS_PATH = Path('config/credentials.json')
DEFAULT_TOKEN_PATH = Path('config/token.pickle')


class GoogleSheetsClient:
    """
    Client for interacting with Google Sheets API using OAuth 2.0.
    
    This class handles authentication and provides methods to read data
    from Google Sheets.
    """
    
    def __init__(
        self,
        credentials_path: Optional[Path] = None,
        token_path: Optional[Path] = None,
        scopes: Optional[List[str]] = None
    ):
        """
        Initialize the Google Sheets client.
        
        Args:
            credentials_path: Path to OAuth credentials JSON file
            token_path: Path to save/load OAuth token pickle file
            scopes: List of OAuth scopes to request
        """
        self.credentials_path = credentials_path or DEFAULT_CREDENTIALS_PATH
        self.token_path = token_path or DEFAULT_TOKEN_PATH
        self.scopes = scopes or SCOPES
        self.service = None
        
    def authenticate(self) -> None:
        """
        Authenticate with Google Sheets API using OAuth 2.0.
        
        This method will:
        1. Check for existing valid credentials
        2. Refresh expired credentials if possible
        3. Run OAuth flow if no valid credentials exist
        4. Save credentials for future use
        
        Raises:
            FileNotFoundError: If credentials file doesn't exist
            Exception: If authentication fails
        """
        creds = None
        
        # Check for existing credentials
        if self.token_path.exists():
            logger.info(f"Loading existing credentials from {self.token_path}")
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Validate and refresh credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired credentials")
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.warning(f"Failed to refresh credentials: {e}")
                    creds = None
            
            # Run OAuth flow if needed
            if not creds:
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_path}\n"
                        f"Please download OAuth credentials from Google Cloud Console "
                        f"and save as {self.credentials_path}"
                    )
                
                logger.info("Running OAuth authentication flow")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), self.scopes
                )
                creds = flow.run_local_server(port=0)
                
                # Save credentials for future use
                logger.info(f"Saving credentials to {self.token_path}")
                self.token_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.token_path, 'wb') as token:
                    pickle.dump(creds, token)
        
        # Build the service
        self.service = build('sheets', 'v4', credentials=creds)
        logger.info("Successfully authenticated with Google Sheets API")
    
    def read_sheet(
        self,
        sheet_id: str,
        range_name: str,
        value_render_option: str = 'FORMATTED_VALUE'
    ) -> List[List[Any]]:
        """
        Read data from a Google Sheet.
        
        Args:
            sheet_id: The Google Sheet ID (from the URL)
            range_name: The A1 notation range to read (e.g., 'Sheet1!A1:Z100')
            value_render_option: How values should be rendered in the output
                - FORMATTED_VALUE (default): Values will be calculated and formatted
                - UNFORMATTED_VALUE: Values will be calculated but not formatted
                - FORMULA: Formulas will be returned
        
        Returns:
            List of rows, where each row is a list of cell values
            Returns empty list if no data found
        
        Raises:
            HttpError: If the API request fails
            ValueError: If not authenticated
        """
        if not self.service:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        try:
            logger.info(f"Reading sheet {sheet_id}, range: {range_name}")
            result = self.service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=range_name,
                valueRenderOption=value_render_option
            ).execute()
            
            values = result.get('values', [])
            logger.info(f"Retrieved {len(values)} rows from sheet")
            return values
            
        except HttpError as error:
            logger.error(f"Failed to read sheet: {error}")
            raise
    
    def get_sheet_metadata(self, sheet_id: str) -> dict:
        """
        Get metadata about a Google Sheet.
        
        Args:
            sheet_id: The Google Sheet ID
        
        Returns:
            Dictionary containing sheet metadata
        
        Raises:
            HttpError: If the API request fails
            ValueError: If not authenticated
        """
        if not self.service:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        try:
            logger.info(f"Getting metadata for sheet {sheet_id}")
            result = self.service.spreadsheets().get(
                spreadsheetId=sheet_id
            ).execute()
            
            return result
            
        except HttpError as error:
            logger.error(f"Failed to get sheet metadata: {error}")
            raise


# Convenience functions for simple usage
def get_google_sheets_service():
    """
    Get an authenticated Google Sheets API service.
    
    This is a convenience function that creates a client,
    authenticates it, and returns the service object.
    
    Returns:
        Google Sheets API service object
    """
    client = GoogleSheetsClient()
    client.authenticate()
    return client.service


def read_sheet(sheet_id: str, range_name: str) -> List[List[Any]]:
    """
    Read data from a Google Sheet (convenience function).
    
    Args:
        sheet_id: The Google Sheet ID (from the URL)
        range_name: The range to read (e.g., 'Portfolio Holdings!A1:Z100')
    
    Returns:
        List of rows from the sheet
    """
    client = GoogleSheetsClient()
    client.authenticate()
    return client.read_sheet(sheet_id, range_name)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # This will run the OAuth flow when executed directly
    client = GoogleSheetsClient()
    client.authenticate()
    
    print("Authentication successful!")
    print("You can now use this client to read Google Sheets.")
