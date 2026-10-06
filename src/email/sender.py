"""
Email sender module.
"""
import smtplib
import logging
import time
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from src.config import GMAIL_ADDRESS, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL, SMTP_SERVER, SMTP_PORT

logger = logging.getLogger(__name__)

def send_email(subject: str, html_content: str) -> bool:
    """
    Sends an HTML email using Gmail SMTP with exponential backoff retries.
    """
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = GMAIL_ADDRESS
    msg['To'] = RECIPIENT_EMAIL
    
    # Generate plain text version by removing HTML tags
    text_content = re.sub(r'<[^>]+>', '', html_content)
    text_content = re.sub(r'\s+', ' ', text_content).strip()
    
    part1 = MIMEText(text_content, 'plain', 'utf-8')
    part2 = MIMEText(html_content, 'html', 'utf-8')
    
    msg.attach(part1)
    msg.attach(part2)
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to send email (Attempt {attempt+1}/{max_retries})")
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
                server.send_message(msg)
            logger.info("Email sent successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to send email on attempt {attempt+1}: {e}")
            if attempt < max_retries - 1:
                sleep_time = 2 ** attempt
                logger.info(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                logger.error("Max retries reached. Email sending failed.")
                return False
    return False
