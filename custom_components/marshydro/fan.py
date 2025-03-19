from typing import Any, cast, Optional
from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.device_registry import DeviceInfo
from .entity import MarsHydroEntity
from . import _LOGGER, DOMAIN
from datetime import timedelta


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Mars Hydro fan entity."""
    _LOGGER.debug("Mars Hydro fan async_setup_entry called")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    _LOGGER.info('Devices in coordinator: %s', str(coordinator._devices))
    _LOGGER.info('Data in coordinator: %s', str(coordinator.data))

    fan = MarsHydroFanEntity(coordinator, "WIND")
    async_add_entities([fan], update_before_add=True)

SCAN_INTERVAL = timedelta(seconds=60)

class MarsHydroFanEntity(MarsHydroEntity, FanEntity):
    """Representation of a Mars Hydro fan."""

    def __init__(self, coordinator, prod_type):
        super().__init__(coordinator, prod_type)

    @property
    def name(self):
        return f"iFresh Fan - ({super().name})"
    
    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        dev_info = super().device_info
        dev_info["model"] = "DF100-M"
        dev_info["name"] = f"iFresh Fan - ({self.name})"
        #dev_info["sw_version"] = str(self._coordinator.data.get("deviceVersion"))
        return dev_info

    @property
    def is_on(self):
        """Return True if the light is on."""
        return not self._coordinator.data.get(self._device_id).get("isClose", True)
        #return self._state

    @property
    def percentage(self):
        """Return the current speed percentage of the fan."""
        #return self._speed_percentage
        return cast("int", self._coordinator.data.get(self._device_id).get("deviceLightRate", 0))
    
    @property
    def speed_count(self):
        """Return the current speed of the fan."""
        #return self._speed
        return cast("int", self._coordinator.data.get(self._device_id).get("speed", 0))

    @property
    def supported_features(self):
        """Return supported features of the fan."""
        return [FanEntityFeature.SET_SPEED, FanEntityFeature.TURN_ON, FanEntityFeature.TURN_OFF]  # Support speed adjustment only

    async def async_turn_on(self, percentage: Optional[int] = None, preset_mode: Optional[str] = None, **kwargs: Any) -> None:
        """Turn on the fan."""
        await self.modify_device_state(False)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the fan off."""
        await self.modify_device_state(True)

    async def async_toggle(self, **kwargs: Any) -> None:
        #new_state = not self.is_on
        await self.modify_device_state(self.is_on)

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the fan speed percentage."""
        if percentage < 25 or percentage > 100:
            _LOGGER.error(f"Fan speed percentage {percentage} not in range, aborting.")
            return
        
        await self._api.async_set_device_p(round(percentage), self.unique_id)
        await self._coordinator.async_request_refresh()
        

    
