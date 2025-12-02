"""
Daily Portfolio Report - Complete End-to-End Workflow

This script:
1. Reads portfolio holdings from Google Sheets
2. Fetches current prices using yfinance
3. Analyzes portfolio performance with EigenLedger
4. Sends a formatted email report

Usage:
    poetry run python daily_portfolio_report.py
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import importlib.util
import os
from dotenv import load_dotenv
import pandas as pd
import yfinance as yf

# Load environment variables
load_dotenv()

# Import modules directly to avoid package init issues
def load_module(name: str, path: Path):
    """Load a Python module from file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load our custom modules
base_path = Path(__file__).parent
google_auth = load_module("google_auth", base_path / "EigenLedger" / "modules" / "google_auth.py")
email_sender = load_module("email_sender", base_path / "EigenLedger" / "modules" / "email_sender.py")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PortfolioDataManager:
    """
    Manages portfolio data fetching and processing.
    """
    
    def __init__(self, sheet_id: str, sheet_range: str):
        """
        Initialize the portfolio data manager.
        
        Args:
            sheet_id: Google Sheet ID
            sheet_range: Sheet range (e.g., 'Sheet1!A1:Z100')
        """
        self.sheet_id = sheet_id
        self.sheet_range = sheet_range
        self.sheets_client = google_auth.GoogleSheetsClient()
    
    def fetch_holdings(self) -> pd.DataFrame:
        """
        Fetch portfolio holdings from Google Sheets.
        
        Returns:
            DataFrame with columns: Company, Account, Stock, Quantity, Purchase date
        """
        logger.info(f"Fetching holdings from Google Sheets")
        
        # Authenticate if needed
        self.sheets_client.authenticate()
        
        # Read data
        data = self.sheets_client.read_sheet(self.sheet_id, self.sheet_range)
        
        if not data:
            raise ValueError("No data found in Google Sheet")
        
        # Convert to DataFrame
        headers = data[0]
        rows = data[1:]
        df = pd.DataFrame(rows, columns=headers)
        
        logger.info(f"Fetched {len(df)} holdings from Google Sheets")
        return df
    
    def fetch_current_prices(self, tickers: List[str]) -> Dict[str, float]:
        """
        Fetch current prices for tickers using yfinance.
        
        Args:
            tickers: List of stock ticker symbols
        
        Returns:
            Dictionary mapping ticker to current price
        """
        logger.info(f"Fetching current prices for {len(tickers)} tickers")
        prices = {}
        
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period='1d')
                if not hist.empty:
                    prices[ticker] = hist['Close'].iloc[-1]
                    logger.debug(f"{ticker}: ${prices[ticker]:.2f}")
                else:
                    logger.warning(f"No price data for {ticker}")
                    prices[ticker] = 0.0
            except Exception as e:
                logger.error(f"Error fetching price for {ticker}: {e}")
                prices[ticker] = 0.0
        
        return prices
    
    def calculate_portfolio_metrics(self, holdings_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate portfolio metrics from holdings data.
        
        Args:
            holdings_df: DataFrame with holdings information
        
        Returns:
            Dictionary with portfolio metrics
        """
        logger.info("Calculating portfolio metrics")
        
        # Get unique tickers and quantities
        portfolio_summary = holdings_df.groupby('Stock').agg({
            'Quantity': lambda x: pd.to_numeric(x, errors='coerce').sum()
        }).reset_index()
        
        tickers = portfolio_summary['Stock'].tolist()
        quantities = portfolio_summary['Quantity'].tolist()
        
        # Fetch current prices
        current_prices = self.fetch_current_prices(tickers)
        
        # Calculate values
        holdings_data = []
        total_value = 0.0
        
        for ticker, qty in zip(tickers, quantities):
            price = current_prices.get(ticker, 0.0)
            value = price * qty
            total_value += value
            
            holdings_data.append({
                'ticker': ticker,
                'quantity': qty,
                'price': price,
                'value': value,
                'pct_change': 0.0  # Would need historical data for this
            })
        
        # Sort by value descending
        holdings_data.sort(key=lambda x: x['value'], reverse=True)
        
        metrics = {
            'total_value': total_value,
            'daily_change': 0.0,  # Would need previous day's data
            'daily_change_pct': 0.0,
            'total_return': 0.0,  # Would need cost basis
            'total_return_pct': 0.0,
            'holdings': holdings_data,
            'num_holdings': len(holdings_data),
            'largest_holding': holdings_data[0]['ticker'] if holdings_data else 'N/A',
        }
        
        logger.info(f"Portfolio value: ${total_value:,.2f}")
        logger.info(f"Number of holdings: {len(holdings_data)}")
        
        return metrics


def main():
    """Main execution function."""
    
    print("=" * 60)
    print("📊 Daily Portfolio Report")
    print("=" * 60)
    print()
    
    # Load configuration
    sheet_id = os.getenv('GOOGLE_SHEET_ID')
    sheet_range = os.getenv('GOOGLE_SHEET_RANGE')
    email_to = os.getenv('EMAIL_TO')
    email_from = os.getenv('EMAIL_FROM')
    email_password = os.getenv('EMAIL_PASSWORD')
    smtp_server = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('EMAIL_SMTP_PORT', '587'))
    
    # Validate configuration
    missing = []
    if not sheet_id:
        missing.append('GOOGLE_SHEET_ID')
    if not sheet_range:
        missing.append('GOOGLE_SHEET_RANGE')
    if not email_to:
        missing.append('EMAIL_TO')
    if not email_from:
        missing.append('EMAIL_FROM')
    if not email_password:
        missing.append('EMAIL_PASSWORD')
    
    if missing:
        print("❌ ERROR: Missing configuration!")
        print()
        print("Missing environment variables:")
        for var in missing:
            print(f"  - {var}")
        print()
        print("Please ensure your .env file has all required variables.")
        return 1
    
    print(f"✅ Configuration loaded")
    print(f"   Sheet: {sheet_id}")
    print(f"   Range: {sheet_range}")
    print(f"   Email: {email_to}")
    print()
    
    try:
        # Step 1: Fetch portfolio data
        print("📥 Step 1: Fetching portfolio holdings from Google Sheets...")
        manager = PortfolioDataManager(sheet_id, sheet_range)
        holdings_df = manager.fetch_holdings()
        print(f"   ✅ Fetched {len(holdings_df)} holdings")
        print()
        
        # Step 2: Calculate metrics
        print("📊 Step 2: Calculating portfolio metrics...")
        metrics = manager.calculate_portfolio_metrics(holdings_df)
        print(f"   ✅ Portfolio value: ${metrics['total_value']:,.2f}")
        print(f"   ✅ Number of holdings: {metrics['num_holdings']}")
        print(f"   ✅ Largest holding: {metrics['largest_holding']}")
        print()
        
        # Step 3: Send email
        print("📧 Step 3: Sending email report...")
        sender = email_sender.EmailSender(
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            from_email=email_from,
            password=email_password
        )
        
        success = sender.send_portfolio_summary([email_to], metrics)
        
        if success:
            print(f"   ✅ Email sent successfully to {email_to}")
            print()
            print("=" * 60)
            print("✅ Daily portfolio report completed!")
            print("=" * 60)
            print()
            print("Summary:")
            print(f"  - Holdings fetched: {len(holdings_df)}")
            print(f"  - Portfolio value: ${metrics['total_value']:,.2f}")
            print(f"  - Email sent to: {email_to}")
            return 0
        else:
            print("   ❌ Failed to send email")
            return 1
            
    except Exception as e:
        logger.exception("Daily report failed")
        print()
        print(f"❌ ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
