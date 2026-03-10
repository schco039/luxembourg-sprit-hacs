"""Config flow for Luxembourg Spritpreise."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_VEHICLE_NAME,
    CONF_TANK_SIZE,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_TANK_SIZE,
)


class LuxembourgSpritConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow for Luxembourg Spritpreise."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Handle the initial setup step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            vehicle_name = user_input[CONF_VEHICLE_NAME].strip()

            # Unique ID = vehicle name (lowercased, spaces→underscore)
            unique_id = f"luxembourg_sprit_{vehicle_name.lower().replace(' ', '_')}"
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=vehicle_name,
                data={
                    CONF_VEHICLE_NAME: vehicle_name,
                    CONF_TANK_SIZE: user_input[CONF_TANK_SIZE],
                },
                options={
                    CONF_SCAN_INTERVAL: user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                },
            )

        schema = vol.Schema({
            vol.Required(CONF_VEHICLE_NAME, description={"suggested_value": "Mein Auto"}): str,
            vol.Required(CONF_TANK_SIZE, default=DEFAULT_TANK_SIZE): vol.All(
                vol.Coerce(int), vol.Range(min=10, max=200)
            ),
            vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
                vol.Coerce(int), vol.Range(min=15, max=1440)
            ),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "rss_source": "lesfrontaliers.lu",
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> OptionsFlow:
        """Return the options flow."""
        return OptionsFlow(config_entry)


class OptionsFlow(config_entries.OptionsFlow):
    """Handle options (edit after setup)."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict | None = None) -> FlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema({
            vol.Required(
                CONF_TANK_SIZE,
                default=self._config_entry.data.get(CONF_TANK_SIZE, DEFAULT_TANK_SIZE),
            ): vol.All(vol.Coerce(int), vol.Range(min=10, max=200)),
            vol.Optional(
                CONF_SCAN_INTERVAL,
                default=self._config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            ): vol.All(vol.Coerce(int), vol.Range(min=15, max=1440)),
        })

        return self.async_show_form(step_id="init", data_schema=schema)
