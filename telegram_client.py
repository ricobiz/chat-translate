import os
import httpx
import logging

logger = logging.getLogger(__name__)


def send_message(chat_id: int, text: str) -> bool:
    """
    Send a message to a Telegram chat.
    
    Args:
        chat_id: The Telegram chat ID to send the message to.
        text: The message text to send.
    
    Returns:
        True if the message was sent successfully, False otherwise.
    """
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set")
        return False
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    
    try:
        with httpx.Client() as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            return True
    except httpx.HTTPError as e:
        logger.error(f"Failed to send Telegram message: {e}")
        return False
