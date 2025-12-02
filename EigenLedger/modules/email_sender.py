"""
Email Notification Module

This module handles sending portfolio summary emails via SMTP.
Supports HTML email templates with embedded images/charts.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


class EmailSender:
    """
    Email sender for portfolio notifications using SMTP.
    
    Supports:
    - HTML and plain text emails
    - Embedded images (inline attachments)
    - Multiple recipients
    - TLS encryption
    """
    
    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        from_email: str,
        password: str,
        use_tls: bool = True
    ):
        """
        Initialize the email sender.
        
        Args:
            smtp_server: SMTP server hostname (e.g., 'smtp.gmail.com')
            smtp_port: SMTP server port (e.g., 587 for TLS, 465 for SSL)
            from_email: Sender email address
            password: Email account password or app-specific password
            use_tls: Whether to use TLS encryption (default: True)
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.from_email = from_email
        self.password = password
        self.use_tls = use_tls
        
    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        images: Optional[Dict[str, Path]] = None
    ) -> bool:
        """
        Send an email with optional HTML formatting and embedded images.
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject line
            html_body: HTML version of email body
            text_body: Plain text version (optional, auto-generated if None)
            images: Dict mapping content IDs to image file paths
                   e.g., {'logo': Path('logo.png')} -> use in HTML as <img src="cid:logo">
        
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('related')
            msg['From'] = self.from_email
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
            
            # Create alternative part for HTML and text
            msg_alternative = MIMEMultipart('alternative')
            msg.attach(msg_alternative)
            
            # Add plain text version
            if text_body is None:
                # Simple HTML to text conversion
                text_body = html_body.replace('<br>', '\n').replace('</p>', '\n\n')
                # Remove all HTML tags
                import re
                text_body = re.sub('<[^<]+?>', '', text_body)
            
            msg_text = MIMEText(text_body, 'plain')
            msg_alternative.attach(msg_text)
            
            # Add HTML version
            msg_html = MIMEText(html_body, 'html')
            msg_alternative.attach(msg_html)
            
            # Attach images if provided
            if images:
                for cid, image_path in images.items():
                    if image_path.exists():
                        with open(image_path, 'rb') as f:
                            img = MIMEImage(f.read())
                            img.add_header('Content-ID', f'<{cid}>')
                            img.add_header('Content-Disposition', 'inline', filename=image_path.name)
                            msg.attach(img)
                            logger.debug(f"Attached image: {cid} -> {image_path}")
                    else:
                        logger.warning(f"Image not found: {image_path}")
            
            # Send email
            logger.info(f"Connecting to SMTP server {self.smtp_server}:{self.smtp_port}")
            
            if self.use_tls:
                # Use STARTTLS
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.ehlo()
                server.starttls()
                server.ehlo()
            else:
                # Use SSL
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            
            server.login(self.from_email, self.password)
            logger.info(f"Sending email to: {', '.join(to_emails)}")
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {len(to_emails)} recipient(s)")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error occurred: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_portfolio_summary(
        self,
        to_emails: List[str],
        portfolio_data: Dict[str, Any],
        chart_path: Optional[Path] = None
    ) -> bool:
        """
        Send a portfolio summary email with formatted data.
        
        Args:
            to_emails: List of recipient email addresses
            portfolio_data: Dictionary containing portfolio metrics
            chart_path: Optional path to performance chart image
        
        Returns:
            True if email sent successfully, False otherwise
        """
        subject = f"Daily Portfolio Summary - {datetime.now().strftime('%B %d, %Y')}"
        
        # Generate HTML body
        html_body = self._generate_portfolio_html(portfolio_data, chart_path is not None)
        
        # Attach chart if provided
        images = {}
        if chart_path and chart_path.exists():
            images['chart'] = chart_path
        
        return self.send_email(to_emails, subject, html_body, images=images)
    
    def _generate_portfolio_html(
        self,
        data: Dict[str, Any],
        include_chart: bool = False
    ) -> str:
        """
        Generate HTML email body for portfolio summary.
        
        Args:
            data: Portfolio metrics dictionary
            include_chart: Whether to include chart image placeholder
        
        Returns:
            HTML string
        """
        # Extract data with defaults
        date = datetime.now().strftime('%B %d, %Y')
        total_value = data.get('total_value', 'N/A')
        daily_change = data.get('daily_change', 'N/A')
        daily_pct = data.get('daily_change_pct', 'N/A')
        total_return = data.get('total_return', 'N/A')
        total_return_pct = data.get('total_return_pct', 'N/A')
        
        holdings = data.get('holdings', [])
        
        # Determine color for daily change
        change_color = 'green' if isinstance(daily_change, (int, float)) and daily_change >= 0 else 'red'
        
        html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    margin: 0 0 10px 0;
                    font-size: 28px;
                }}
                .header p {{
                    margin: 0;
                    opacity: 0.9;
                }}
                .metrics {{
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .metric-card {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    border-left: 4px solid #667eea;
                }}
                .metric-card h3 {{
                    margin: 0 0 10px 0;
                    font-size: 14px;
                    color: #666;
                    text-transform: uppercase;
                }}
                .metric-card .value {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #333;
                }}
                .metric-card .sub-value {{
                    font-size: 14px;
                    margin-top: 5px;
                }}
                .positive {{
                    color: #28a745;
                }}
                .negative {{
                    color: #dc3545;
                }}
                .holdings-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    background: white;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    border-radius: 8px;
                    overflow: hidden;
                }}
                .holdings-table th {{
                    background: #667eea;
                    color: white;
                    padding: 12px;
                    text-align: left;
                    font-weight: 600;
                }}
                .holdings-table td {{
                    padding: 12px;
                    border-bottom: 1px solid #eee;
                }}
                .holdings-table tr:last-child td {{
                    border-bottom: none;
                }}
                .holdings-table tr:hover {{
                    background: #f8f9fa;
                }}
                .chart {{
                    margin: 30px 0;
                    text-align: center;
                }}
                .chart img {{
                    max-width: 100%;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 2px solid #eee;
                    text-align: center;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Portfolio Summary</h1>
                <p>{date}</p>
            </div>
            
            <div class="metrics">
                <div class="metric-card">
                    <h3>Total Portfolio Value</h3>
                    <div class="value">${total_value:,.2f}</div>
                </div>
                
                <div class="metric-card">
                    <h3>Daily Change</h3>
                    <div class="value {change_color}">${daily_change:,.2f}</div>
                    <div class="sub-value {change_color}">({daily_pct:+.2f}%)</div>
                </div>
                
                <div class="metric-card">
                    <h3>Total Return</h3>
                    <div class="value">${total_return:,.2f}</div>
                    <div class="sub-value">({total_return_pct:+.2f}%)</div>
                </div>
            </div>
        """
        
        # Add holdings table if available
        if holdings:
            html += """
            <h2>Top Holdings</h2>
            <table class="holdings-table">
                <thead>
                    <tr>
                        <th>Ticker</th>
                        <th>Quantity</th>
                        <th>Value</th>
                        <th>% Change</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for holding in holdings[:10]:  # Top 10 holdings
                ticker = holding.get('ticker', 'N/A')
                qty = holding.get('quantity', 0)
                value = holding.get('value', 0)
                pct_change = holding.get('pct_change', 0)
                change_class = 'positive' if pct_change >= 0 else 'negative'
                
                html += f"""
                    <tr>
                        <td><strong>{ticker}</strong></td>
                        <td>{qty:,.0f}</td>
                        <td>${value:,.2f}</td>
                        <td class="{change_class}">{pct_change:+.2f}%</td>
                    </tr>
                """
            
            html += """
                </tbody>
            </table>
            """
        
        # Add chart if available
        if include_chart:
            html += """
            <div class="chart">
                <h2>Performance Chart</h2>
                <img src="cid:chart" alt="Portfolio Performance Chart">
            </div>
            """
        
        html += """
            <div class="footer">
                <p>This is an automated email from your Portfolio Management System.</p>
                <p>Generated by Bricks Portfolio Tracker</p>
            </div>
        </body>
        </html>
        """
        
        return html


# Convenience function
def send_test_email(
    smtp_server: str,
    smtp_port: int,
    from_email: str,
    password: str,
    to_email: str
) -> bool:
    """
    Send a test email to verify configuration.
    
    Args:
        smtp_server: SMTP server hostname
        smtp_port: SMTP port
        from_email: Sender email
        password: Email password
        to_email: Recipient email
    
    Returns:
        True if successful
    """
    sender = EmailSender(smtp_server, smtp_port, from_email, password)
    
    test_data = {
        'total_value': 125000.00,
        'daily_change': 1250.50,
        'daily_change_pct': 1.01,
        'total_return': 25000.00,
        'total_return_pct': 25.00,
        'holdings': [
            {'ticker': 'AAPL', 'quantity': 100, 'value': 18500, 'pct_change': 1.5},
            {'ticker': 'GOOGL', 'quantity': 50, 'value': 15000, 'pct_change': -0.8},
            {'ticker': 'MSFT', 'quantity': 75, 'value': 28500, 'pct_change': 2.3},
        ]
    }
    
    return sender.send_portfolio_summary([to_email], test_data)
