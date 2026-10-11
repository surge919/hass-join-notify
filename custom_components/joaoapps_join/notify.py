"""Support for Join notifications via UI Config Flow."""
import logging
import requests
from homeassistant.components.notify import (
    BaseNotificationService,
    NotifyEntity,
)
from .const import DOMAIN, CONF_API_KEY

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Join notification entities from a config entry."""
    api_key = config_entry.data.get(CONF_API_KEY)

    # Fetch devices from Join API
    url = f"https://joinjoaomgcd.appspot.com/_ah/api/registration/v1/listDevices?apikey={api_key}"
    try:
        response = await hass.async_add_executor_job(lambda: requests.get(url, timeout=10))
        if response.status_code == 200:
            devices = response.json().get("records", [])
        else:
            devices = []
    except Exception as err:
        _LOGGER.error("Failed to fetch Join devices: %s", err)
        devices = []

    entities = []
    # Create an entity for 'All Devices' group
    entities.append(JoinNotificationEntity(api_key, "group.all", "Join All"))

    # Create an entity for each individual Join device found
    for device in devices:
        device_id = device.get("deviceId")
        device_name = device.get("deviceName", device_id)
        if device_id:
            entities.append(JoinNotificationEntity(api_key, device_id, f"Join {device_name}"))

    async_add_entities(entities)


class JoinNotificationEntity(NotifyEntity):
    """Implement a Join notification entity."""

    def __init__(self, api_key, device_id, name):
        """Initialize the entity."""
        self.api_key = api_key
        self.device_id = device_id
        self._attr_name = name
        self._attr_unique_id = f"join_{device_id}"

    def send_message(self, message: str, title: str = None) -> None:
        """Send a notification message via Join."""
        url = "https://joinjoaomgcd.appspot.com/_ah/api/messaging/v1/sendPush"
        params = {
            "apikey": self.api_key,
            "deviceId": self.device_id,
            "text": message,
            "title": title or "Home Assistant",
        }
        try:
            res = requests.get(url, params=params, timeout=10)
            if res.status_code != 200:
                _LOGGER.error("Join push failed for %s: %s", self.device_id, res.text)
        except Exception as err:
            _LOGGER.error("Error sending Join notification: %s", err)
