from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.const import (
    PERCENTAGE,
    REVOLUTIONS_PER_MINUTE,
    UnitOfTemperature,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass
)
from .entity import MarsHydroEntity
from . import _LOGGER, DOMAIN
from datetime import timedelta


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Mars Hydro sensors."""
    _LOGGER.debug("Mars Hydro fan sensor async_setup_entry called")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    device = coordinator.get_device_by_type("WIND")
    dev_id = device["id"]
    fan_temperature_celsius_sensor = MarsHydroFanTemperatureCelsiusSensor(coordinator, dev_id)
    fan_temperature_sensor = MarsHydroFanTemperatureSensor(coordinator, dev_id)
    fan_humidity_sensor = MarsHydroFanHumiditySensor(coordinator, dev_id)
    fan_speed_sensor = MarsHydroFanSpeedSensor(coordinator, dev_id)
    async_add_entities(
        [
                fan_temperature_sensor,
                fan_temperature_celsius_sensor,
                fan_humidity_sensor,
                fan_speed_sensor
        ], 
        update_before_add=True
    )


PARALLEL_UPDATES = 0
SCAN_INTERVAL = timedelta(seconds=5)

class MarsHydroSensor(MarsHydroEntity, SensorEntity):
    def __init__(self, coordinator, idx):
        super().__init__(coordinator, idx)
        #_LOGGER.debug(f"MarshydroSensor data in coordinator: {str(coordinator.data)}")
        self._parent_name = self._coordinator.data[idx]["deviceName"]

    async def async_update(self):
        """Update the fan temperature sensor state."""
        await self._coordinator.async_update_device_data(self.idx)
        self.async_write_ha_state()

    @property
    def unique_id(self):
        """Return a unique ID for the fan temperature sensor."""
        return f"{self._parent_name}_fan_sensor_{self.idx}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        dev_info = super().device_info
        _LOGGER.debug(f"MarshydroSensor device info: {str(dev_info)}")
        dev_info["sw_version"] = str(self._coordinator.data[self.idx]["deviceVersion"])
        return dev_info

    @property
    def state_class(self):
        return SensorStateClass.MEASUREMENT


class MarsHydroFanTemperatureSensor(MarsHydroSensor):
    """Representation of the Mars Hydro fan temperature sensor."""
    def __init__(self, coordinator, idx):
        super().__init__(coordinator, idx)

    @property
    def device_class(self):
        return SensorDeviceClass.TEMPERATURE

    @property
    def name(self):
        """Return the name of the fan temperature sensor."""
        if self.idx:
            return f"Temperature Sensor ({self.idx})"
        return "Mars Hydro Fan Temperature Sensor"

    @property
    def native_value(self):
        """Return the fan's temperature."""
        return self._coordinator.data[self.idx]["temperature"]


    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        dev_info = super().device_info
        dev_info["name"] = f"iFresh Fan - ({self.name})"
        return dev_info

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return UnitOfTemperature.FAHRENHEIT

    @property
    def unique_id(self):
        """Return a unique ID for the fan temperature sensor."""
        return f"{self._parent_name}_fan_temperature_sensor_{self.idx}"


class MarsHydroFanTemperatureCelsiusSensor(MarsHydroFanTemperatureSensor):
    """Representation of the Mars Hydro fan temperature sensor in Celsius."""
    def __init__(self, coordinator, idx):
        super().__init__(coordinator, idx)

    @property
    def name(self):
        """Return the name of the fan temperature sensor (Celsius)."""
        if self._device_name and self.idx:
            return f"Temperature Sensor (Celsius) ({self.idx})"
        return "Mars Hydro Fan Temperature Sensor (Celsius)"
    
    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return UnitOfTemperature.CELSIUS

    @property
    def unique_id(self):
        """Return a unique ID for the fan temperature sensor in Celsius."""
        return f"{self._parent_name}_fan_temperature_celsius_sensor_{self.idx}"
    
    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        dev_info = super().device_info
        dev_info["name"] = f"iFresh Fan - ({self.name})"
        return dev_info


class MarsHydroFanHumiditySensor(MarsHydroSensor):
    """Representation of the Mars Hydro fan humidity sensor."""
    def __init__(self, coordinator, idx):
        super().__init__(coordinator, idx)

    @property
    def device_class(self):
        return SensorDeviceClass.HUMIDITY
    
    @property
    def name(self):
        """Return the name of the fan humidity sensor."""
        if self.idx:
            return f"Humidity Sensor ({self.idx})"
        return "Mars Hydro Fan Humidity Sensor"

    @property
    def native_value(self):
        """Return the fan's humidity."""
        return self._coordinator.data[self.idx]["humidity"]

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return PERCENTAGE

    @property
    def unique_id(self):
        """Return a unique ID for the fan humidity sensor."""
        return f"{self._parent_name}_fan_humidity_sensor_{self.idx}"
    
    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        dev_info = super().device_info
        dev_info["name"] = f"iFresh Fan - ({self.name})"
        return dev_info


class MarsHydroFanSpeedSensor(MarsHydroSensor):
    """Representation of the Mars Hydro fan speed sensor."""
    def __init__(self, coordinator, idx):
        super().__init__(coordinator, idx)
        self.entity_id = f"sensor.ifresh_fan_speed_sensor_{self.idx}"

    @property
    def name(self):
        """Return the name of the fan speed sensor."""
        if self.idx:
            return f"Speed Sensor ({self.idx})"
        return "Mars Hydro Fan Speed Sensor"

    @property
    def native_value(self):
        """Return the fan's speed."""
        return self._coordinator.data[self.idx]["speed"]

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return str(REVOLUTIONS_PER_MINUTE).upper()

    @property
    def unique_id(self):
        """Return a unique ID for the fan speed sensor."""
        return f"{self._parent_name}_fan_speed_sensor_{self.idx}"
    
    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        dev_info = super().device_info
        dev_info["name"] = f"iFresh Fan - ({self.name})"
        return dev_info
