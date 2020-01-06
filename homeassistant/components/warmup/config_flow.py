"""Config flow for Warmup4IE integration."""
from collections import OrderedDict
import logging

from pywarmup import InvalidToken, PyWarmupError, get_access_token
import voluptuous as vol

from homeassistant import config_entries, core, exceptions
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_EMAIL

from .const import DOMAIN  # pylint:disable=unused-import

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: core.HomeAssistant, data):
    """Validate the user input allows us to connect."""
    return {"title": "WarmUp Thermostat"}


class DomainConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Warmup4IE."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                token = get_access_token(user_input["email"], user_input["password"])
            except InvalidToken:
                errors["base"] = "invalid_auth"
            except PyWarmupError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                config = {
                    CONF_EMAIL: user_input["email"],
                    CONF_ACCESS_TOKEN: token,
                }
                return self.async_create_entry(title=DOMAIN, data=config)

        data_schema = OrderedDict()
        data_schema[vol.Required("email")] = str
        data_schema[vol.Required("password")] = str

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(data_schema), errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""
