"""Support for Warmup thermostats."""
import logging
from typing import List, Optional

from pywarmup import LocationMode, ProgramMode

from homeassistant.components.climate import ClimateDevice
from homeassistant.components.climate.const import (
    HVAC_MODE_AUTO,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.components.warmup import DOMAIN
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS

SUPPORT_FLAGS = SUPPORT_TARGET_TEMPERATURE

OPERATION_LIST = [HVAC_MODE_OFF, HVAC_MODE_AUTO, HVAC_MODE_HEAT]

PROGRAM_HVAC_MAP = {
    ProgramMode.PROGRAM: HVAC_MODE_AUTO,
    ProgramMode.FIXED: HVAC_MODE_HEAT,
}

_LOGGER = logging.getLogger(__name__)


class Thermostat(ClimateDevice):
    """A Warmup thermostat."""

    def __init__(self, *, hass, room_id, location_id, api):
        """Create new Thermostat instance."""
        self.hass = hass
        self.room_id = room_id
        self.location_id = location_id
        self.api = api
        self.room_data = self.api.get_room(self.room_id)

    async def async_update(self):
        """Get latest status from device."""
        _LOGGER.debug("Updating Warmup room data")
        self.room_data = await self.hass.async_add_executor_job(
            self.api.get_room, self.room_id
        )
        _LOGGER.debug("Received data: %s", self.room_data)

    @property
    def name(self):
        """Get the name of the Thermostat."""
        return self.room_data.name

    @property
    def supported_features(self) -> int:
        """Get supported features."""
        _LOGGER.debug("supported_features")
        return SUPPORT_FLAGS

    @property
    def current_temperature(self) -> Optional[float]:
        """Get current temperaturte."""
        _LOGGER.debug("curent_temperature: %f", self.room_data.current_temp)
        return self.room_data.current_temp

    @property
    def target_temperature(self) -> Optional[float]:
        """Get target temperature."""
        _LOGGER.debug("target temp: %f", self.room_data.target_temp)
        return self.room_data.target_temp

    @property
    def max_temp(self) -> Optional[float]:
        """Get maximum temperature."""
        _LOGGER.debug("target_temperature_high: %f", self.room_data.target_temp_high)
        return self.room_data.target_temp_high

    @property
    def min_temp(self) -> Optional[float]:
        """Get minimum temperature."""
        _LOGGER.debug("target_temperature_low: %f", self.room_data.target_temp_low)
        return self.room_data.target_temp_low

    @property
    def temperature_unit(self) -> str:
        """Get temperature unit. This is hard coded to Celsius at the moment."""
        _LOGGER.debug("temperature_unit")
        return TEMP_CELSIUS

    @property
    def hvac_action(self):
        """Return current HVAC action.

        FIXME
        """
        pass

    @property
    def hvac_modes(self) -> List[str]:
        """List of available operation modes."""
        _LOGGER.debug("hvac_modes")
        return OPERATION_LIST

    @property
    def hvac_mode(self) -> str:
        """Return current operation ie. heat, auto, off."""
        if self.room_data.location.mode == LocationMode.OFF:
            mode = HVAC_MODE_OFF
        else:
            mode = PROGRAM_HVAC_MAP.get(self.room_data.mode)
        _LOGGER.debug("hvac_mode: %s - %s", self.room_data.mode, mode)
        return mode

    def set_hvac_mode(self, hvac_mode: str) -> None:
        """Set HVAC mode (eg. auto, heat, off)."""
        _LOGGER.debug("set HVAC mode")
        if hvac_mode == HVAC_MODE_AUTO:
            self.api.set_temperature_to_auto(self.room_id)
        elif hvac_mode == HVAC_MODE_HEAT:
            self.api.set_temperature_to_manual(self.room_id)
        elif hvac_mode == HVAC_MODE_OFF:
            self.api.set_location_to_off(location_id=self.location_id)

    @property
    def preset_mode(self) -> Optional[str]:
        """Get the current preset mode.

        FIXME
        """
        _LOGGER.debug("preset_mode")
        pass

    @property
    def preset_modes(self) -> Optional[List[str]]:
        """Get all available preset modes.

        FIXME
        """
        _LOGGER.debug("preset_modes")
        pass

    def set_temperature(self, **kwargs) -> None:
        """Set temperature."""
        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp is not None:
            _LOGGER.debug("Setting temperature to %f in room %d", temp, self.room_id)
            self.api.set_temperature(self.room_id, temp)

    def set_preset_mode(self, preset_mode: str) -> None:
        """Change preset mode.

        FIXME
        """
        _LOGGER.debug("set preset mode")
        raise NotImplementedError

    @property
    def device_info(self):
        """Retrieve device information."""
        _LOGGER.debug("device_info")
        return {
            "manufacturer": "Warmup",
            "model": "Warmup 4iE",
        }


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Initialise devices."""
    data = hass.data[DOMAIN]
    api = data.api
    devices = [
        Thermostat(hass=hass, room_id=room.id, api=api, location_id=room.location.id)
        for room in data.rooms
    ]
    async_add_entities(devices, True)
