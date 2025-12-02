"""
Test script for email sending functionality

This script tests the email sender module and verifies SMTP configuration.

Usage:
    poetry run python test_email.py
"""

import sys
import logging
from pathlib import Path
import importlib.util
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import email_sender module directly
spec = importlib.util.spec_from_file_location(
    "email_sender",
    Path(__file__).parent / "EigenLedger" / "modules" / "email_sender.py"
)
email_sender = importlib.util.module_from_spec(spec)
spec.loader.exec_module(email_sender)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Test email sending functionality."""
    
    print("=" * 60)
    print("Email Sender Test")
    print("=" * 60)
    print()
    
    # Get email configuration
    smtp_server = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('EMAIL_SMTP_PORT', '587'))
    from_email = os.getenv('EMAIL_FROM', '')
    password = os.getenv('EMAIL_PASSWORD', '')
    to_email = os.getenv('EMAIL_TO', '')
    
    # Check if configuration is complete
    missing_config = []
    if not from_email:
        missing_config.append('EMAIL_FROM')
    if not password:
        missing_config.append('EMAIL_PASSWORD')
    if not to_email:
        missing_config.append('EMAIL_TO')
    
    if missing_config:
        print("❌ ERROR: Missing email configuration!")
        print()
        print("Missing environment variables:")
        for var in missing_config:
            print(f"  - {var}")
        print()
        print("Please create a .env file with the following:")
        print()
        print("EMAIL_SMTP_SERVER=smtp.gmail.com")
        print("EMAIL_SMTP_PORT=587")
        print("EMAIL_FROM=your-email@gmail.com")
        print("EMAIL_PASSWORD=your-app-password")
        print("EMAIL_TO=recipient@gmail.com")
        print()
        print("For Gmail, you need to create an 'App Password':")
        print("1. Go to Google Account settings")
        print("2. Security → 2-Step Verification")
        print("3. App passwords → Generate new password")
        print("4. Use that password in EMAIL_PASSWORD")
        return 1
    
    print(f"✅ Email configuration found")
    print(f"   SMTP Server: {smtp_server}:{smtp_port}")
    print(f"   From: {from_email}")
    print(f"   To: {to_email}")
    print()
    
    # Create test portfolio data
    test_data = {
        'total_value': 125789.50,
        'daily_change': 1250.75,
        'daily_change_pct': 1.01,
        'total_return': 25789.50,
        'total_return_pct': 25.80,
        'holdings': [
            {'ticker': 'VRT', 'quantity': 100, 'value': 15000, 'pct_change': 2.5},
            {'ticker': 'QQQI', 'quantity': 300, 'value': 24000, 'pct_change': 1.2},
            {'ticker': 'NVDA', 'quantity': 20, 'value': 28000, 'pct_change': 3.8},
            {'ticker': 'GOOGL', 'quantity': 200, 'value': 35000, 'pct_change': -0.5},
            {'ticker': 'AAPL', 'quantity': 150, 'value': 23789.50, 'pct_change': 0.8},
        ]
    }
    
    try:
        print("Sending test email...")
        print()
        
        # Create email sender
        sender = email_sender.EmailSender(
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            from_email=from_email,
            password=password
        )
        
        # Send portfolio summary
        success = sender.send_portfolio_summary([to_email], test_data)
        
        if success:
            print()
            print("=" * 60)
            print("✅ Test email sent successfully!")
            print("=" * 60)
            print()
            print(f"Check your inbox at: {to_email}")
            print("The email includes:")
            print("  - Portfolio value: $125,789.50")
            print("  - Daily change: +$1,250.75 (+1.01%)")
            print("  - Total return: +$25,789.50 (+25.80%)")
            print("  - Top 5 holdings table")
            return 0
        else:
            print()
            print("❌ Failed to send email")
            print("Check the logs above for error details")
            return 1
            
    except Exception as e:
        logger.exception("Test failed")
        print(f"❌ ERROR: {e}")
        print()
        print("Common issues:")
        print("  - Gmail: Use an 'App Password', not your regular password")
        print("  - Check SMTP server and port are correct")
        print("  - Ensure firewall allows outbound SMTP connections")
        return 1


if __name__ == "__main__":
    sys.exit(main())
