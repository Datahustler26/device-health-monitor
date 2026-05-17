"""Slack notification helper."""

import requests
import logging
from app.config import settings

logger = logging.getLogger(__name__)


def send_slack_alert(message: str, level: str = "INFO"):
    """Send a message to Slack."""
    
    if not settings.slack_enabled or not settings.slack_webhook_url:
        logger.debug("Slack notifications disabled")
        return False
    
    try:
        color_map = {
            "INFO": "#36a64f",
            "WARNING": "#ffa500",
            "CRITICAL": "#ff0000"
        }
        
        payload = {
            "attachments": [
                {
                    "color": color_map.get(level, "#808080"),
                    "text": message,
                    "footer": "Device Health Monitoring"
                }
            ]
        }
        
        response = requests.post(
            settings.slack_webhook_url,
            json=payload,
            timeout=10
        )
        
        return response.status_code == 200
        
    except Exception as e:
        logger.error(f"Error sending Slack message: {e}")
        return False
