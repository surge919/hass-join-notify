"""The Join integration."""
import logging

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_API_KEY

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["notify"]

SEND_PUSH_URL = "https://joinjoaomgcd.appspot.com/_ah/api/messaging/v1/sendPush"

# service name -> {HA field: Join API param}
SERVICES = {
    "ring": {},
    "send_sms": {"number": "smsnumber", "message": "smstext"},
    "send_tasker": {"command": "text"},
    "send_url": {"url": "url"},
    "send_wallpaper": {"url": "wallpaper"},
    "send_file": {"url": "file"},
}


def _register_services(hass: HomeAssistant) -> None:
    """Register the legacy-style Join services (once)."""
    session = async_get_clientsession(hass)

    def make_handler(name: str, fields: dict):
        async def handler(call: ServiceCall) -> None:
            entries = hass.data.get(DOMAIN)
            if not entries:
                raise HomeAssistantError("Join is not configured")
            api_key = next(iter(entries.values()))[CONF_API_KEY]

            params = {
                "apikey": api_key,
                "deviceId": call.data.get("device_id", "group.all"),
            }
            if name == "ring":
                params["find"] = "true"
            for ha_key, api_param in fields.items():
                params[api_param] = call.data[ha_key]

            try:
                async with session.get(SEND_PUSH_URL, params=params) as resp:
                    if resp.status != 200:
                        _LOGGER.error(
                            "Join %s failed (%s): %s", name, resp.status, await resp.text()
                        )
            except Exception as err:  # noqa: BLE001
                _LOGGER.error("Error calling Join %s: %s", name, err)

        return handler

    for name, fields in SERVICES.items():
        if hass.services.has_service(DOMAIN, name):
            continue
        schema = vol.Schema(
            {
                vol.Optional("device_id"): str,
                **{vol.Required(key): str for key in fields},
            }
        )
        hass.services.async_register(
            DOMAIN, name, make_handler(name, fields), schema=schema
        )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Join from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    _register_services(hass)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:
            for name in SERVICES:
                hass.services.async_remove(DOMAIN, name)
    return unload_ok
