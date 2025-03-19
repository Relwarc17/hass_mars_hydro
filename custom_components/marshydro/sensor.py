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
    
    _LOGGER.info('Devices in coordinator: %s', str(coordinator._devices))
    _LOGGER.info('Data in coordinator: %s', str(coordinator.data))

    fan_temperature_celsius_sensor = MarsHydroFanTemperatureCelsiusSensor(coordinator, "WIND")
    fan_temperature_sensor = MarsHydroFanTemperatureSensor(coordinator, "WIND")
    fan_humidity_sensor = MarsHydroFanHumiditySensor(coordinator, "WIND")
    #fan_speed_sensor = MarsHydroFanSpeedSensor(coordinator, "WIND")
    async_add_entities(
        [
                fan_temperature_sensor,
                fan_temperature_celsius_sensor,
                fan_humidity_sensor
                #fan_speed_sensor
        ], 
        update_before_add=True
    )


PARALLEL_UPDATES = 0
SCAN_INTERVAL = timedelta(seconds=5)

class MarsHydroSensor(MarsHydroEntity, SensorEntity):
    def __init__(self, coordinator, prod_type):
        super().__init__(coordinator, prod_type)

    async def async_update(self):
        """Update the fan temperature sensor state."""
        await self._coordinator.async_update_device_data(self._device_id)
        self.async_write_ha_state()

    @property
    def state_class(self):
        return SensorStateClass.MEASUREMENT


class MarsHydroFanTemperatureSensor(MarsHydroSensor):
    """Representation of the Mars Hydro fan temperature sensor."""

    @property
    def device_class(self):
        return SensorDeviceClass.TEMPERATURE

    @property
    def name(self):
        """Return the name of the fan temperature sensor."""
        if self._device_id:
            return f"Temperature Sensor ({self._device_id})"
        return "Mars Hydro Fan Temperature Sensor"

    @property
    def native_value(self):
        """Return the fan's temperature."""
        return self._coordinator.data.get(self._device_id).get("temperature", self.native_value)


    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        dev_info = super().device_info
        dev_info["name"] = f"iFresh Fan - ({self.name})"
        #dev_info["sw_version"] = str(self._coordinator.data.get("deviceVersion"))
        return dev_info

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return UnitOfTemperature.FAHRENHEIT

    @property
    def unique_id(self):
        """Return a unique ID for the fan temperature sensor."""
        return (
            f"{self._entry_id}_fan_temperature_sensor_{self._device_id}"
            if self._device_id
            else f"{self._entry_id}_fan_temperature_sensor"
        )


class MarsHydroFanTemperatureCelsiusSensor(MarsHydroFanTemperatureSensor):
    """Representation of the Mars Hydro fan temperature sensor in Celsius."""

    @property
    def name(self):
        """Return the name of the fan temperature sensor (Celsius)."""
        if self._device_name and self._device_id:
            return f"Temperature Sensor (Celsius) ({self._device_id})"
        return "Mars Hydro Fan Temperature Sensor (Celsius)"
    
    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return UnitOfTemperature.CELSIUS

    @property
    def unique_id(self):
        """Return a unique ID for the fan temperature sensor in Celsius."""
        return (
            f"{self._entry_id}_fan_temperature_celsius_sensor_{self._device_id}"
            if self._device_id
            else f"{self._entry_id}_fan_temperature_celsius_sensor"
        )
    
    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        dev_info = super().device_info
        dev_info["name"] = f"iFresh Fan - ({self.name})"
        #dev_info["sw_version"] = str(self._coordinator.data.get("deviceVersion"))
        return dev_info


class MarsHydroFanHumiditySensor(MarsHydroSensor):
    """Representation of the Mars Hydro fan humidity sensor."""

    @property
    def device_class(self):
        return SensorDeviceClass.HUMIDITY
    
    @property
    def name(self):
        """Return the name of the fan humidity sensor."""
        if self._device_id:
            return f"Humidity Sensor ({self._device_id})"
        return "Mars Hydro Fan Humidity Sensor"

    @property
    def native_value(self):
        """Return the fan's humidity."""
        return self._coordinator.data.get(self._device_id).get("humidity", self.native_value)

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return PERCENTAGE

    @property
    def unique_id(self):
        """Return a unique ID for the fan humidity sensor."""
        return (
            f"{self._entry_id}_fan_humidity_sensor_{self._device_id}"
            if self._device_id
            else f"{self._entry_id}_fan_humidity_sensor"
        )
    
    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        dev_info = super().device_info
        dev_info["name"] = f"iFresh Fan - ({self.name})"
        #dev_info["sw_version"] = str(self._coordinator.data.get("deviceVersion"))
        return dev_info


class MarsHydroFanSpeedSensor(MarsHydroSensor):
    """Representation of the Mars Hydro fan speed sensor."""


    @property
    def name(self):
        """Return the name of the fan speed sensor."""
        if self._device_id:
            return f"Speed Sensor ({self._device_id})"
        return "Mars Hydro Fan Speed Sensor"

    @property
    def native_value(self):
        """Return the fan's speed."""
        return self._coordinator.data.get(self._device_id).get("speed", self.native_value)

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return str(REVOLUTIONS_PER_MINUTE).upper()

    @property
    def unique_id(self):
        """Return a unique ID for the fan speed sensor."""
        return (
            f"{self._entry_id}_fan_speed_sensor_{self._device_id}"
            if self._device_id
            else f"{self._entry_id}_fan_speed_sensor"
        )

    
    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        dev_info = super().device_info
        dev_info["name"] = f"iFresh Fan - ({self.name})"
        #dev_info["sw_version"] = str(self._coordinator.data.get("deviceVersion"))
        return dev_info
