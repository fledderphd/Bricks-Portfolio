# GitHub Actions Setup Guide

This guide explains how to set up the GitHub Secrets needed for the daily portfolio report workflow.

## Required GitHub Secrets

Go to your repository → Settings → Secrets and variables → Actions → New repository secret

Create the following secrets:

### Google Sheets Secrets

1. **`GOOGLE_CREDENTIALS`**
   - Value: Copy the entire contents of your `config/credentials.json` file
   - This is your OAuth client configuration from Google Cloud

2. **`GOOGLE_TOKEN`**
   - Value: Run this command on your local machine to get the base64-encoded token:
   ```bash
   base64 config/token.pickle
   ```
   - Copy the output and paste as the secret value
   - This is your authenticated OAuth token

3. **`GOOGLE_SHEET_ID`**
   - Value: `1YnkFAvFaRMW6zGv_c_l5w0L_8lCG8GZLqOWSQR1pfC8`
   - This is your Google Sheet ID

4. **`GOOGLE_SHEET_RANGE`**
   - Value: `bricks!A1:E21`
   - This is the range to read from your sheet

### Email Secrets

5. **`EMAIL_SMTP_SERVER`**
   - Value: `smtp.gmail.com`

6. **`EMAIL_SMTP_PORT`**
   - Value: `587`

7. **`EMAIL_FROM`**
   - Value: `fleddermaus@gmail.com`

8. **`EMAIL_PASSWORD`**
   - Value: Your Gmail App Password (from .env file)

9. **`EMAIL_TO`**
   - Value: `fleddermaus@gmail.com`

## How to Get the Base64 Token

On Windows (PowerShell):
```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("config\token.pickle"))
```

On macOS/Linux:
```bash
base64 config/token.pickle
```

Copy the entire output and paste it as the `GOOGLE_TOKEN` secret.

## Testing the Workflow

Once all secrets are set up:

1. Go to your repository on GitHub
2. Click "Actions" tab
3. Click "Daily Portfolio Report" workflow
4. Click "Run workflow" → "Run workflow"
5. Watch it execute
6. Check your email for the report!

## Schedule

The workflow runs automatically:
- **Daily at 9 AM EST** (2 PM UTC)
- Can also be triggered manually via "Run workflow" button

## Troubleshooting

If the workflow fails:
1. Check the Actions log for error messages
2. Verify all secrets are set correctly
3. Make sure the base64 token was copied completely
4. Try running manually first before relying on schedule

## Token Expiration

OAuth tokens can expire. If you get authentication errors:
1. Run `poetry run python test_google_sheets.py` locally to refresh the token
2. Re-encode the new `token.pickle` file to base64
3. Update the `GOOGLE_TOKEN` secret in GitHub
