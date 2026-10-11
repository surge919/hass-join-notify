"""Support for Join notifications via UI Config Flow."""
import logging
import requests
from homeassistant.components.notify import BaseNotificationService
from .const import DOMAIN, CONF_API_KEY

_LOGGER = logging.getLogger(__name__)

async def async_get_service(hass, config, discovery_info=None):
    """Set up the notification service from config entries."""
    if discovery_info is None:
        return None

    api_key = discovery_info.get(CONF_API_KEY)
    return JoinNotificationService(api_key)

class JoinNotificationService(BaseNotificationService):
    """Implement the Join notification service."""

    def __init__(self, api_key):
        """Initialize the service."""
        self.api_key = api_key

    def send_message(self, message="", **kwargs):
        """Send a message through Join API."""
        target = kwargs.get("target")
        device_id = target[0] if target else "group.all"
        title = kwargs.get("title", "Home Assistant")

        url = "https://joinjoaomgcd.appspot.com/_ah/api/messaging/v1/sendPush"
        params = {
            "apikey": self.api_key,
            "deviceId": device_id,
            "text": message,
            "title": title
        }

        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            _LOGGER.error("Failed to send Join notification: %s", response.text)
