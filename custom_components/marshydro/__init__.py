from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import device_registry as dr
from .const import DOMAIN
import logging
from .api import MarsHydroAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "light", "switch", "fan"]  # Sensor hinzugefügt


async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    username = entry.data.get(CONF_USERNAME)
    password = entry.data.get(CONF_PASSWORD)


    _LOGGER.info("Creating session")
    session = async_get_clientsession(hass)
    api = MarsHydroAPI(username, password, session)
    
    coordinator = ClevastDataUpdateCoordinator(hass, entry, my_api)
    # _LOGGER.info("Sync coordinator")

    await coordinator.async_config_entry_first_refresh()

    if not coordinator.last_update_success:
        _LOGGER.error("Error synchronizing coordinator")
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Gerät registrieren
    device_registry = dr.async_get(hass)

    # Light-Gerät registrieren
    light_data = await api.get_lightdata()
    if light_data:
        device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, light_data["id"])},
            manufacturer="Mars Hydro",
            name=light_data["deviceName"],
            model="Mars Hydro Light",
        )
        _LOGGER.info(
            f"Light Device {light_data['deviceName']} wurde erfolgreich registriert."
        )
    else:
        _LOGGER.warning("Kein Light-Gerät gefunden, Registrierung übersprungen.")

    # Fan-Gerät registrieren
    fan_data = await api.get_fandata()
    if fan_data:
        device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, fan_data["id"])},
            manufacturer="Mars Hydro",
            name=fan_data["deviceName"],
            model="Mars Hydro Fan",
        )
        _LOGGER.info(
            f"Fan Device {fan_data['deviceName']} wurde erfolgreich registriert."
        )
    else:
        _LOGGER.warning("Kein Fan-Gerät gefunden, Registrierung übersprungen.")

    # Plattformen laden
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Entferne eine Konfigurationsinstanz."""
    _LOGGER.debug("Mars Hydro async_unload_entry wird aufgerufen")

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def create_api_instance(hass: HomeAssistant, email: str, password: str):
    """Erstelle eine API-Instanz und führe den Login durch."""
    try:
        api_instance = MarsHydroAPI(email, password)
        await api_instance.login()
        return api_instance
    except Exception as e:
        _LOGGER.error(f"Fehler beim Erstellen der API-Instanz: {e}")
        return None
