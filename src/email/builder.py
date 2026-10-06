"""
Email builder module.
"""
import os
import logging
from jinja2 import Environment, FileSystemLoader
from src.config import TEMPLATES_DIR

logger = logging.getLogger(__name__)

def build_subject(report_data: dict) -> str:
    """
    Builds the email subject based on report data.
    """
    date = report_data.get('date', '')
    time_label = report_data.get('time_label', '')
    return f"📰 Günlük Bülten | {date} {time_label}"

def build_email(report_data: dict) -> str:
    """
    Builds the HTML email content using Jinja2 templates.
    """
    try:
        env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
        daily_template = env.get_template('daily_report.html')
        
        weekly_html = ""
        weekly_summary = report_data.get('weekly_summary')
        if weekly_summary:
            weekly_template = env.get_template('weekly_report.html')
            weekly_html = weekly_template.render(weekly_summary=weekly_summary)
            
        # The daily_report.html template should inject {{ weekly_html | safe }} 
        # where the weekly section goes.
        rendered_html = daily_template.render(
            report_data=report_data, 
            weekly_html=weekly_html
        )
        return rendered_html
    except Exception as e:
        logger.error(f"Error building HTML email content: {e}")
        raise
