from typing import Any, cast
from homeassistant.exceptions import ConfigEntryNotReady
from .entity import MarsHydroEntity
from homeassistant.components.light import LightEntity, ATTR_BRIGHTNESS
from homeassistant.helpers.device_registry import DeviceInfo
from . import _LOGGER, DOMAIN
from datetime import timedelta

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Mars Hydro Light entity."""
    
    _LOGGER.debug("Mars Hydro Light async_setup_entry called")

    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    _LOGGER.info('Devices in coordinator: %s', str(coordinator._devices))
    _LOGGER.info('Data in coordinator: %s', str(coordinator.data))
    device = coordinator.get_device_by_type("LIGHT")
    light = MarsHydroBrightnessLight(coordinator, device["id"])
    async_add_entities([light], update_before_add=False)

SCAN_INTERVAL = timedelta(seconds=60)

class MarsHydroBrightnessLight(MarsHydroEntity, LightEntity):
    """Representation of the Mars Hydro Light with brightness control only."""

    def __init__(self, coordinator, idx):
        super().__init__(coordinator, idx)

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        dev_info = super().device_info
        dev_info["model"] = "FC 1500-EVO"
        dev_info["name"] = f"EVO light - ({self.name})"
        dev_info["sw_version"] = str(self._coordinator.data[self.idx]["deviceVersion"])
        return dev_info
    
    @property
    def name(self):
        return f"FC 1500-EVO - ({super().name})"
    
    @property
    def brightness(self):
        """Return the brightness of the light (0-255)."""
        #return self._brightness
        brigtness_p = self._coordinator.data[self.idx]["deviceLightRate"]
        return int((brigtness_p * 255) / 100)

    @property
    def is_on(self):
        """Return True if the light is on."""
        #return self._state
        return not self._coordinator.data[self.idx]["isClose"]

    @property
    def supported_color_modes(self):
        """Return the list of supported color modes."""
        return {"brightness"}

    @property
    def color_mode(self):
        """Return the current color mode."""
        return "brightness"

    async def async_turn_on(self, **kwargs):
        """Turn on the light by setting the brightness."""
        brightness = kwargs.get(ATTR_BRIGHTNESS, self.brightness)
        if brightness != self.brightness:
            await self.async_set_brightness(brightness)
            return
        await self.modify_device_state(False)

    async def async_turn_off(self, **kwargs):
        """Turn off the light by setting brightness to 0."""
        #await self.async_set_brightness(0)
        await self.modify_device_state(True)


    async def async_set_brightness(self, brightness: int):
        """Set the brightness of the light."""

        _LOGGER.info(f"Brightness to bet to {brightness}")
        brightness_percentage = round((brightness / 255) * 100)
        
        await self._coordinator._my_api.async_set_device_p(brightness_percentage, self.unique_id)

        _LOGGER.info(f"Brightness set to {brightness_percentage}%")
        await self._coordinator.async_request_refresh()

