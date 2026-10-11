"""Config flow for Join integration."""
import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_API_KEY

class JoinConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Join."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title="Join", data=user_input)

        data_schema = vol.Schema({
            vol.Required(CONF_API_KEY): str,
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
