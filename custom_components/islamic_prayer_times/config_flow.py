from typing import Any
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import callback
from .const import DOMAIN

class IslamicPrayerTimesFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Islamic Prayer Times."""
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step setup."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(title="Dynamic Islamic Prayer Times", data=user_input)

        return self.show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_LATITUDE, default=self.hass.config.latitude): float,
                    vol.Required(CONF_LONGITUDE, default=self.hass.config.longitude): float,
                }
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return IslamicPrayerTimesOptionsFlowHandler()

class IslamicPrayerTimesOptionsFlowHandler(config_entries.OptionsFlow):
    """Option workflow handler."""
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        return self.show_form(step_id="init", data_schema=vol.Schema({}))
