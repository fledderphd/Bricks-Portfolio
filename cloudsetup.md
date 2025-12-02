# Google Sheets API Setup with OAuth 2.0 (Personal Account)

This guide walks you through setting up Google Sheets API access using OAuth 2.0 for a personal Google account. This approach allows your application to access your private Google Sheets with proper user authorization.

## Overview

**OAuth 2.0** is recommended for personal accounts because:
- ✅ More secure than service accounts for personal data
- ✅ Allows explicit user consent
- ✅ No need to share sheets with a service account email
- ✅ Access tokens can be refreshed automatically
- ✅ Can be revoked at any time from Google Account settings

## Prerequisites

- A Google Account
- Access to [Google Cloud Console](https://console.cloud.google.com/)
- Python environment with Poetry set up

## Step 1: Create a Google Cloud Project

1. **Navigate to Google Cloud Console**
   - Go to: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create a New Project**
   - Click the project dropdown at the top
   - Click **"New Project"**
   - Enter project name: `Portfolio Management` (or your preferred name)
   - Leave organization as "No organization"
   - Click **"Create"**
   - Wait for the project to be created (usually takes a few seconds)

3. **Select Your Project**
   - Click the project dropdown again
   - Select your newly created project

## Step 2: Enable Google Sheets API

1. **Navigate to APIs & Services**
   - In the left sidebar, go to **"APIs & Services"** → **"Library"**
   - Or use direct link: https://console.cloud.google.com/apis/library

2. **Search for Google Sheets API**
   - In the search bar, type: `Google Sheets API`
   - Click on **"Google Sheets API"** from the results

3. **Enable the API**
   - Click the blue **"Enable"** button
   - Wait for confirmation that the API is enabled

## Step 3: Configure OAuth Consent Screen

1. **Navigate to OAuth Consent Screen**
   - Go to **"APIs & Services"** → **"OAuth consent screen"**
   - Or use: https://console.cloud.google.com/apis/credentials/consent

2. **Choose User Type**
   - Select **"External"** (for personal account)
   - Click **"Create"**

3. **Fill in App Information**
   - **App name**: `Portfolio Management Dashboard`
   - **User support email**: Your email address
   - **App logo**: (Optional - can skip)
   - **App domain**: (Optional - can skip for personal use)
   - **Developer contact information**: Your email address
   - Click **"Save and Continue"**

4. **Configure Scopes**
   - Click **"Add or Remove Scopes"**
   - Search for: `Google Sheets API`
   - Select the following scope:
     - `.../auth/spreadsheets.readonly` (if you only need read access)
     - OR `.../auth/spreadsheets` (if you need read/write access)
   - Click **"Update"**
   - Click **"Save and Continue"**

5. **Add Test Users** (Important for External apps)
   - Click **"Add Users"**
   - Enter your email address (the one you'll use to access sheets)
   - Click **"Add"**
   - Click **"Save and Continue"**

6. **Review and Finish**
   - Review the summary
   - Click **"Back to Dashboard"**

## Step 4: Create OAuth 2.0 Credentials

1. **Navigate to Credentials**
   - Go to **"APIs & Services"** → **"Credentials"**
   - Or use: https://console.cloud.google.com/apis/credentials

2. **Create OAuth Client ID**
   - Click **"+ Create Credentials"** at the top
   - Select **"OAuth client ID"**

3. **Configure OAuth Client**
   - **Application type**: Select **"Desktop app"**
   - **Name**: `Portfolio Management Desktop Client`
   - Click **"Create"**

4. **Download Credentials**
   - A dialog will appear with your Client ID and Client Secret
   - Click **"Download JSON"**
   - Save the file as `credentials.json` in a secure location
   - Click **"OK"**

> [!WARNING]
> **Keep your `credentials.json` file secure!** Never commit it to version control or share it publicly.

## Step 5: Set Up Your Local Environment

### Install Required Dependencies

Add these to your `pyproject.toml`:

```toml
[tool.poetry.dependencies]
google-auth-oauthlib = "^1.1.0"
google-auth-httplib2 = "^0.1.1"
google-api-python-client = "^2.108.0"
```

Then run:
```bash
poetry add google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Create Configuration Directory

```bash
mkdir -p config
mv ~/Downloads/credentials.json config/
```

### Update `.gitignore`

Add these lines to ensure credentials aren't committed:

```gitignore
# Google API Credentials
config/credentials.json
config/token.json
*.json
```

## Step 6: Create Authentication Module

Create a new file: `EigenLedger/modules/google_auth.py`

```python
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from pathlib import Path

# If modifying these scopes, delete the file token.pickle
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def get_google_sheets_service():
    """
    Authenticate with Google Sheets API using OAuth 2.0
    
    Returns:
        Google Sheets API service object
    """
    creds = None
    token_path = Path('config/token.pickle')
    credentials_path = Path('config/credentials.json')
    
    # Check if we have previously saved credentials
    if token_path.exists():
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials available, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh expired credentials
            creds.refresh(Request())
        else:
            # Run OAuth flow for first-time authentication
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for future runs
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    
    # Build and return the service
    service = build('sheets', 'v4', credentials=creds)
    return service

def read_sheet(sheet_id, range_name):
    """
    Read data from a Google Sheet
    
    Args:
        sheet_id: The Google Sheet ID (from the URL)
        range_name: The range to read (e.g., 'Portfolio Holdings!A1:Z100')
    
    Returns:
        List of rows from the sheet
    """
    service = get_google_sheets_service()
    sheet = service.spreadsheets()
    result = sheet.values().get(
        spreadsheetId=sheet_id,
        range=range_name
    ).execute()
    
    return result.get('values', [])
```

## Step 7: First-Time Authorization Flow

When you run your script for the first time:

1. **Run Your Script**
   ```bash
   poetry run python daily_portfolio_report.py
   ```

2. **Browser Opens Automatically**
   - A browser window will open
   - You may see a warning: "Google hasn't verified this app"

3. **Grant Access**
   - Click **"Advanced"** → **"Go to Portfolio Management Dashboard (unsafe)"**
   - Click **"Allow"** to grant access to your Google Sheets
   - The browser will show: "The authentication flow has completed"

4. **Token Saved**
   - A `token.pickle` file is created in the `config/` directory
   - Future runs will use this token (no need to re-authenticate)
   - Token auto-refreshes when expired

> [!NOTE]
> The "unsafe" warning appears because your app is in testing mode and not verified by Google. This is normal for personal projects.

## Step 8: Find Your Google Sheet ID

Your Sheet ID is in the URL:

```
https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit#gid=0
                                        ↑↑↑↑↑↑↑↑↑↑↑↑↑
                                   This is your Sheet ID
```

Example:
```
https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
                                        ↑ Sheet ID starts here ↑
```

## Step 9: Usage Example

Create `test_google_sheets.py`:

```python
from EigenLedger.modules.google_auth import read_sheet
import pandas as pd

# Your Google Sheet ID
SHEET_ID = "YOUR_SHEET_ID_HERE"

# The range to read (adjust to your sheet structure)
RANGE_NAME = "Portfolio Holdings!A1:Z100"

# Read the data
data = read_sheet(SHEET_ID, RANGE_NAME)

# Convert to DataFrame
if data:
    headers = data[0]  # First row as headers
    rows = data[1:]    # Remaining rows as data
    df = pd.DataFrame(rows, columns=headers)
    print(df)
else:
    print("No data found in sheet")
```

Run it:
```bash
poetry run python test_google_sheets.py
```

## Step 10: Environment Variables (Optional)

For better security, store your Sheet ID in environment variables:

### Create `.env` file:
```bash
GOOGLE_SHEET_ID=your-sheet-id-here
GOOGLE_SHEET_RANGE=Portfolio Holdings!A1:Z100
```

### Update `.env.example`:
```bash
# Google Sheets Configuration
GOOGLE_SHEET_ID=your-sheet-id-here
GOOGLE_SHEET_RANGE=Portfolio Holdings!A1:Z100
```

### Load in your script:
```python
from dotenv import load_dotenv
import os

load_dotenv()

SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
RANGE_NAME = os.getenv('GOOGLE_SHEET_RANGE')
```

## GitHub Actions Configuration

For automated GitHub Actions, you need to use **Service Account** instead of OAuth (OAuth requires interactive browser login). See `cloudsetup_service_account.md` for that setup.

Alternatively, you can:
1. Run the script locally to generate `token.pickle`
2. Store the token as a GitHub Secret (not recommended - tokens expire)

## Troubleshooting

### "File not found: config/credentials.json"
- Ensure you downloaded the credentials JSON from Google Cloud Console
- Place it in the `config/` directory
- Rename it to `credentials.json`

### "Invalid grant: account not found"
- Make sure the Google account you're using is added as a test user in the OAuth consent screen

### "Access blocked: This app's request is invalid"
- Verify the OAuth consent screen is properly configured
- Check that scopes are correctly set

### Token Expired Errors
- Delete `config/token.pickle`
- Re-run the script to re-authenticate

### "The caller does not have permission"
- Ensure you're signed in to the correct Google account
- Verify the Google Sheet is accessible by your account
- Check that the API is enabled in your project

## Security Best Practices

1. ✅ **Never commit credentials**: Always add to `.gitignore`
2. ✅ **Use minimal scopes**: Only request `readonly` if you don't need write access
3. ✅ **Store tokens securely**: Keep `token.pickle` in `config/` directory
4. ✅ **Regularly review access**: Check authorized apps at https://myaccount.google.com/permissions
5. ✅ **Revoke when needed**: You can revoke access anytime from Google Account settings

## Next Steps

- ✅ Test authentication with the example script
- ✅ Verify you can read data from your Google Sheet
- ✅ Integrate with your portfolio management workflow
- ✅ Set up Service Account for GitHub Actions automation (see separate guide)

## Additional Resources

- [Google Sheets API Documentation](https://developers.google.com/sheets/api)
- [Google OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)
- [Python Quickstart](https://developers.google.com/sheets/api/quickstart/python)
