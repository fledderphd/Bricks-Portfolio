# Bricks Portfolio Management System

An automated portfolio tracking and reporting system that integrates with Google Sheets and sends daily email summaries.

## Features

- 📊 **Google Sheets Integration** - Read portfolio holdings from Google Sheets using OAuth 2.0
- 📧 **Email Notifications** - Beautiful HTML email reports with portfolio metrics
- 📈 **Portfolio Analysis** - Built on EigenLedger framework with QuantStats
- 🤖 **GitHub Actions Automation** - Automated daily reports (coming soon)

## Quick Start

### 1. Install Dependencies

```bash
poetry install
```

### 2. Configure Google Sheets

1. Follow the setup guide in [`cloudsetup.md`](cloudsetup.md)
2. Download OAuth credentials from Google Cloud Console
3. Place `credentials.json` in `config/` directory

### 3. Configure Email

Create a `.env` file:

```env
# Google Sheets
GOOGLE_SHEET_ID=your-sheet-id-here
GOOGLE_SHEET_RANGE=Portfolio Holdings!A1:Z100

# Email
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_FROM=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_TO=recipient@gmail.com

# Portfolio
BENCHMARK_TICKER=SPY
START_DATE=2020-01-01
```

### 4. Test Authentication

```bash
# Test Google Sheets connection
poetry run python test_google_sheets.py

# Test email sending
poetry run python test_email.py
```

## Project Structure

```
SeanPortfolio/
├── EigenLedger/           # Portfolio analysis framework
│   ├── main.py            # Core Engine and analysis functions
│   └── modules/
│       ├── google_auth.py # Google Sheets OAuth integration
│       └── email_sender.py # Email notification system
├── config/                # Configuration and credentials
│   ├── credentials.json   # Google OAuth credentials (not committed)
│   └── token.pickle       # OAuth token (auto-generated)
├── test_google_sheets.py  # Google Sheets test script
├── test_email.py          # Email sender test script
├── cloudsetup.md          # OAuth setup guide
└── .env                   # Environment variables (not committed)
```

## Documentation

- [`cloudsetup.md`](cloudsetup.md) - Complete Google Sheets OAuth setup guide
- [`GOOGLE_SHEETS_SETUP.md`](GOOGLE_SHEETS_SETUP.md) - Quick reference for Google Sheets
- [`AGENTS.md`](AGENTS.md) - Development guidelines
- [`PLAN.md`](PLAN.md) - Development roadmap

## Security

**Never commit these files:**
- `config/credentials.json` - OAuth credentials
- `config/token.pickle` - Auth tokens
- `.env` - Environment variables

All sensitive files are already in `.gitignore`.

## Next Steps

- [ ] Integrate portfolio data manager
- [ ] Create GitHub Actions workflow
- [ ] Add Service Account for automation
- [ ] Implement daily email scheduler

## License

This project builds on [EigenLedger](https://github.com/ssantoshp/EigenLedger) - An Open Source Portfolio Management Framework.

## Support

For OAuth setup issues, see [`cloudsetup.md`](cloudsetup.md).

For email configuration help, check the Gmail App Password section in [`.env.example`](.env.example).
