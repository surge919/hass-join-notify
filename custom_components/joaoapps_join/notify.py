"""Join Notification Platform for Home Assistant."""
import logging
import requests
from homeassistant.components.notify import BaseNotificationService
from .const import DOMAIN, CONF_API_KEY

_LOGGER = logging.getLogger(__name__)

async def async_get_service(hass, config, discovery_info=None):
    """Set up the Join notification service."""
    if discovery_info is None:
        api_key = config.get(CONF_API_KEY)
        device_id = config.get("device_id", "group.all")
    else:
        api_key = discovery_info.get(CONF_API_KEY)
        device_id = discovery_info.get("device_id", "group.all")

    if not api_key:
        _LOGGER.error("Join integration missing API key")
        return None

    return JoinNotificationService(api_key, device_id)


class JoinNotificationService(BaseNotificationService):
    """Implement the Join notification service."""

    def __init__(self, api_key, device_id="group.all"):
        """Initialize the Join service."""
        self.api_key = api_key
        self.default_device_id = device_id

    def send_message(self, message="", **kwargs):
        """Send a message through the Join API."""
        targets = kwargs.get("target")
        
        # If target is specified in service call, use it; otherwise use default_device_id
        if targets:
            device_ids = targets if isinstance(targets, list) else [targets]
        else:
            device_ids = [self.default_device_id]

        title = kwargs.get("title", "Home Assistant")
        url = "https://joinjoaomgcd.appspot.com/_ah/api/messaging/v1/sendPush"

        for device_id in device_ids:
            params = {
                "apikey": self.api_key,
                "deviceId": device_id,
                "text": message,
                "title": title,
            }

            try:
                response = requests.get(url, params=params, timeout=10)
                if response.status_code != 200:
                    _LOGGER.error(
                        "Failed to send Join notification to %s: %s",
                        device_id,
                        response.text,
                    )
            except Exception as err:
                _LOGGER.error("Error sending Join notification to %s: %s", device_id, err)
