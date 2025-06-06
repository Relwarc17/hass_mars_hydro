"""Example integration using DataUpdateCoordinator."""

from datetime import timedelta
import logging


from .mars_device import MarsHydroDevice, MarsHydroDevices
from homeassistant.core import callback
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN

SCAN_INTERVAL = timedelta(seconds=60)

_LOGGER: logging.Logger = logging.getLogger(__package__)

class MarsHydroDataUpdateCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass, config_entry, my_api):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name = DOMAIN,
            config_entry = config_entry,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval = SCAN_INTERVAL,
            # Set always_update to `False` if the data returned from the
            # api can be compared via `__eq__` to avoid duplicate updates
            # being dispatched to listeners
            always_update = False
        )
        _LOGGER.info("Initializing Cordinator")
        self._platforms = []
        self._my_api = my_api
        self._devices: MarsHydroDevices | list = list
        self._prev_temp = '21'
        self._prev_humi = '50'
        self._invalid_values = ['-', '100', '0']
        
        

    async def _async_setup(self) -> None:
        """Set up the coordinator

        This is the place to set up your coordinator,
        or to load data, that only needs to be loaded once.

        This method will be called automatically during
        coordinator.async_config_entry_first_refresh.
        """
        _LOGGER.info("Cordinator _async_setup")
        self._devices = await self._my_api.async_get_devices()
        


    async def _async_update_data(self) -> ...:
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        """Update data via library."""
        _LOGGER.info("Cordinator _async_update_data")
        try:
            
            listening_idx = set(self.async_contexts())
            device_data = dict()
            for device in self._devices:
                dev_id = device["id"]
                device_data[dev_id] = await self._my_api.async_get_device_data(dev_id)
            _LOGGER.info("Device data: %s", str(device_data))
            #return await self._my_api.async_get_device_data(self._device_id)
            return device_data
        except Exception as exception:
            _LOGGER.error("Error _async_update_data: %s", str(exception))
            raise UpdateFailed() from exception

    async def async_update_device_data(self, device_id):
        """Fetch only fan data separately."""
        _LOGGER.info("Cordinator async_update_device_data")
        try:
            clima_data = await self._my_api.async_get_device_data(device_id)
            if 'productType' in clima_data and clima_data["productType"] == "WIND":
                clima_data = self.normalize_temp_humi_abnormal_values(clima_data)
            self.data[device_id] = clima_data
            self.async_set_updated_data(self.data)
        except Exception as err:
            raise UpdateFailed(f"Error fetching fan data: {err}")


    def normalize_temp_humi_abnormal_values(self, clima_data):

        if clima_data["temperature"] in self._invalid_values:
            clima_data["temperature"] = self._prev_temp
        elif clima_data["temperature"] != self._prev_temp:
            self._prev_temp = clima_data["temperature"]

        if clima_data["humidity"] in self._invalid_values:
            clima_data["humidity"] = self._prev_humi
        else:
            self._prev_humi = clima_data["humidity"]

        return clima_data

    def get_device_by_type(self, prod_type) -> MarsHydroDevice | None:
        for device in self._devices:
            if device["productType"] == prod_type:
                return device
        return None
    
    def get_device_by_id(self, device_id: int) -> MarsHydroDevice | None:
        for device in self._devices:
            if device["id"] == device_id:
                return device
        return None