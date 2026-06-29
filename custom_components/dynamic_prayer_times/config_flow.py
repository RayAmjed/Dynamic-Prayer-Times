"""Config flow for Dynamic Islamic Prayer Times."""
from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.selector import selector

from .const import (
    CALC_METHODS,
    CONF_CALC_METHOD,
    CONF_LAT_ADJ_METHOD,
    CONF_METHOD_TYPE,
    CONF_MIDNIGHT_MODE,
    CONF_SCHOOL,
    CONF_TRACKING_ENTITY,
    DEFAULT_CALC_METHOD,
    DEFAULT_LAT_ADJ_METHOD,
    DEFAULT_MIDNIGHT_MODE,
    DEFAULT_SCHOOL,
    DOMAIN,
    METHOD_FIXED,
    METHOD_TRACKER,
)

class DynamicPrayerFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""
    VERSION = 1

    def __init__(self) -> None:
        """Initialize flow."""
        self.entry_data: dict[str, Any] = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Step 1: Choose Location Mode."""
        if user_input is not None:
            self.entry_data.update(user_input)
            if user_input[CONF_METHOD_TYPE] == METHOD_TRACKER:
                return await self.async_step_tracker()
            return self.async_create_entry(title="Dynamic Prayer Times (Fixed)", data=self.entry_data)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_METHOD_TYPE, default=METHOD_FIXED): selector(
                        {
                            "select": {
                                "options": [
                                    {"label": "Use Fixed System Coordinates", "value": METHOD_FIXED},
                                    {"label": "Follow a Person or Device Tracker", "value": METHOD_TRACKER},
                                ]
                            }
                        }
                    )
                }
            ),
        )

    async def async_step_tracker(self, user_input: dict[str, Any] | None = None):
        """Step 2 (Optional): Select entity to track."""
        if user_input is not None:
            self.entry_data.update(user_input)
            name = user_input[CONF_TRACKING_ENTITY].split(".")[-1].title().replace("_", " ")
            return self.async_create_entry(title=f"Dynamic Prayer Times ({name})", data=self.entry_data)

        return self.async_show_form(
            step_id="tracker",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_TRACKING_ENTITY): selector(
                        {"entity": {"domain": ["person", "device_tracker"]}}
                    )
                }
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Get the options flow for adjustments."""
        # FIX: Modern HA handles entry injection automatically, do not pass config_entry
        return DynamicPrayerOptionsFlowHandler()


class DynamicPrayerOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle native adjustments (Calculation Methods, School, etc.)."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Manage configuration options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # self.config_entry is automatically provided by the base class
        options = self.config_entry.options
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_CALC_METHOD, default=options.get(CONF_CALC_METHOD, DEFAULT_CALC_METHOD)): selector(
                        {"select": {"options": CALC_METHODS, "mode": "dropdown"}}
                    ),
                    vol.Optional(CONF_SCHOOL, default=options.get(CONF_SCHOOL, DEFAULT_SCHOOL)): selector(
                        {"select": {"options": ["shafi", "hanafi"], "mode": "dropdown"}}
                    ),
                    vol.Optional(CONF_MIDNIGHT_MODE, default=options.get(CONF_MIDNIGHT_MODE, DEFAULT_MIDNIGHT_MODE)): selector(
                        {"select": {"options": ["standard", "jafari"], "mode": "dropdown"}}
                    ),
                    vol.Optional(CONF_LAT_ADJ_METHOD, default=options.get(CONF_LAT_ADJ_METHOD, DEFAULT_LAT_ADJ_METHOD)): selector(
                        {"select": {"options": ["none", "middle of the night", "one seventh", "angle based"], "mode": "dropdown"}}
                    ),
                }
            ),
        )
