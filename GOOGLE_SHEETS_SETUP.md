# Google Sheets Integration Setup

## Quick Start

1. **Place your OAuth credentials**:
   ```bash
   # Download credentials.json from Google Cloud Console
   # Save it to: config/credentials.json
   ```

2. **Test the authentication**:
   ```bash
   poetry run python test_google_sheets.py
   ```

3. **On first run**:
   - A browser will open for OAuth consent
   - Sign in with your Google account
   - Grant access to Google Sheets
   - Token will be saved for future use

## Configuration

Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
```

Edit `.env` with your Google Sheet details:
```env
GOOGLE_SHEET_ID=your-actual-sheet-id
GOOGLE_SHEET_RANGE=Portfolio Holdings!A1:Z100
```

## Files Created

- `EigenLedger/modules/google_auth.py` - OAuth authentication module
- `config/credentials.json` - Your OAuth credentials (download from Google Cloud)
- `config/token.pickle` - Auto-generated auth token (don't commit!)
- `.env` - Your environment variables (don't commit!)
- `test_google_sheets.py` - Test script

## Next Steps

See `cloudsetup.md` for detailed OAuth setup instructions.
