"""Constants for Clevast."""
# Base component constants
NAME = "Mars Hydro"
DOMAIN = "marshydro"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.0.0"

ISSUE_URL = "https://github.com/Relwarc17/hass_mars_hydro/issues"

# Icons
ICON = "mdi:format-quote-close"

# Device classes
BINARY_SENSOR_DEVICE_CLASS = "connectivity"

# Platforms
SENSOR = "sensor"
SWITCH = "switch"
LIGHT = "light"
FAN = "fan"
#PLATFORMS = [SENSOR, SWITCH, FAN, LIGHT]
PLATFORMS = [SENSOR, FAN, LIGHT]

# Configuration and options
CONF_ENABLED = "enabled"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

# Defaults
DEFAULT_NAME = DOMAIN


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""