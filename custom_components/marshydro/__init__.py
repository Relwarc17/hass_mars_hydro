"""
Custom integration to integrate Clevast with Home Assistant.

For more details about this integration, please refer to
https://github.com/Relwarc17/hass_mars_hydro
"""

from .coordinator import MarsHydroDataUpdateCoordinator
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.core_config import Config
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .const import CONF_PASSWORD
from .const import CONF_USERNAME
from .const import DOMAIN
from .const import PLATFORMS
from .const import STARTUP_MESSAGE

import asyncio
import logging
from .api import MarsHydroAPI

_LOGGER = logging.getLogger(__name__)


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
    my_api = MarsHydroAPI(username, password, session)
    
    # _LOGGER.info("Creating cordinator")
    coordinator = MarsHydroDataUpdateCoordinator(hass, entry, my_api)
    # _LOGGER.info("Sync coordinator")

    await coordinator.async_config_entry_first_refresh()
    # await coordinator.async_refresh()

    _LOGGER.info('Devices in coordinator: %s', str(coordinator._devices))
    _LOGGER.info('Data in coordinator: %s', str(coordinator.data))

    if not coordinator.last_update_success:
        _LOGGER.error("Error synchronizing coordinator")
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator

    _LOGGER.info("Setting entries up")
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    #entry.add_update_listener(async_reload_entry)
    return True

    devices = await api.get_devices()
    for device in devices:
        if device.get('productType', "") == "WIND":
            continue

        if device.get('productType', "") == "LIGHT":
            continue

    # Plattformen laden
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.add_update_listener(async_reload_entry)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    #coordinator = hass.data[DOMAIN][entry.entry_id]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                #if platform in coordinator._platforms
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

async def async_remove_config_entry_device(
    hass: HomeAssistant, config_entry: ConfigEntry, device_entry: DeviceEntry
) -> bool:
    """Remove a config entry from a device."""

