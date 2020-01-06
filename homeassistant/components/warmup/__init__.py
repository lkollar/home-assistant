"""The Warmup4IE integration."""
import asyncio

from pywarmup import API
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_EMAIL
from homeassistant.core import HomeAssistant

from .const import DOMAIN

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

PLATFORMS = ["climate"]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up device.

    FIXME
    """
    return True


class WarmupData:
    """Bridge between Warmup API and Home Assistant."""

    def __init__(self, hass: HomeAssistant, email: str, token: str) -> None:
        """Create new instance and connect to API."""
        self.hass = hass
        self.email = email
        self.token = token
        self.api = API(email=email, access_token=token)
        self.rooms = None

    async def update(self):
        """Fetch the current values through the API."""
        self.rooms = await self.hass.async_add_executor_job(self.api.get_rooms)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Warmup thermostats from a config entry."""
    email = entry.data[CONF_EMAIL]
    token = entry.data[CONF_ACCESS_TOKEN]
    data = WarmupData(hass, email, token)

    await data.update()

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    hass.data[DOMAIN] = data
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
