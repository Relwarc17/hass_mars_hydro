"""ClevastEntity class"""
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.core import callback
import logging

from .const import DOMAIN
from .const import NAME

_LOGGER: logging.Logger = logging.getLogger(__package__)

class MarsHydroEntity(CoordinatorEntity):
    """An entity using CoordinatorEntity.

    The CoordinatorEntity class provides:
      should_poll
      async_update
      async_added_to_hass
      available

    """
    def __init__(self, coordinator, idx):
        super().__init__(coordinator, context=idx)
        device = coordinator.get_device_by_id(int(idx))
        self.idx = idx
        self._device_name = device["deviceName"]
        self._brightness = device["deviceLightRate"]
        self._state = not device["isClose"]
        self._coordinator = coordinator
        self._speed = device["speed"]
        self._speed_percentage = self._brightness
        self._coordinator._device_id = idx
        

    @property
    def unique_id(self):
        """Return a unique ID for the switch."""
        return self.idx
    
    @property
    def name(self):
        return self._device_name
        
    
    @property
    def available(self) -> bool:
        """Return True if roller and hub is available."""
        return self._coordinator.data[self.idx]["connectStatus"]

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self.unique_id)
            },
            name = self._device_name,
            manufacturer = NAME,
            model = self._coordinator.data[self.idx]["deviceSerialnum"],
            model_id = self._coordinator.data[self.idx]["productId"],
            sw_version = str(self._coordinator.data[self.idx]["deviceVersion"]),
        )

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {
            "attribution": "",
            "id": self.unique_id,
            "integration": DOMAIN,
        }

    async def modify_device_state(self, new_state: bool = False):
        self._state = new_state
        await self._coordinator._my_api.toggle_switch(new_state, self.unique_id)
        await self._coordinator.async_request_refresh()
    
    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = not self._coordinator.data[self.idx]["isClose"]
        self.async_write_ha_state()
