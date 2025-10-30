"""Config flow for Arris Router Status integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default="192.168.100.1"): str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Arris Router Status."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            try:
                await self._test_connection(user_input[CONF_HOST])
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidHost:
                errors["host"] = "invalid_host"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=f"Arris Router ({user_input[CONF_HOST]})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def _test_connection(self, host: str) -> bool:
        """Test if we can connect to the router."""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                url = f"http://{host}"
                async with session.get(url) as response:
                    if response.status != 200:
                        raise CannotConnect
                    
                    # Check if the response contains expected Arris router content
                    html = await response.text()
                    if "cable modem" not in html.lower() and "docsis" not in html.lower():
                        _LOGGER.warning("Router page doesn't contain expected Arris content")
                    
                    return True
        except aiohttp.ClientError as err:
            _LOGGER.error("Error connecting to router: %s", err)
            raise CannotConnect from err
        except Exception as err:
            _LOGGER.error("Unexpected error: %s", err)
            raise InvalidHost from err


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidHost(HomeAssistantError):
    """Error to indicate there is invalid host."""