"""Adds config flow for Mars Hydro."""
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow, CONN_CLASS_CLOUD_POLL
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.exceptions import ConfigEntryAuthFailed
import voluptuous as vol

from .api import MarsHydroAPI
import logging
from .const import CONF_PASSWORD
from .const import CONF_USERNAME
from .const import DOMAIN
from .const import NAME
from .const import PLATFORMS

_LOGGER = logging.getLogger(__name__)


class MarsHydroFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Mars Hydro."""

    VERSION = 1
    CONNECTION_CLASS = CONN_CLASS_CLOUD_POLL

    @property
    def errors(self) -> dict:
        return dict()

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        self._errors = {}

        # Uncomment the next 2 lines if only a single instance of the integration is allowed:
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        
        if user_input is None:
            return await self._show_config_form(user_input)

        valid = await self._test_credentials(
            user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
        )
        if valid:
            return self.async_create_entry(
                title=NAME, data=user_input
            )
        
        self._errors["base"] = "auth"
        return await self._show_config_form(user_input)

    async def _test_credentials(self, username: str, password: str) -> bool:
        """Test the API login."""
        #_LOGGER.error("Enter _test_credentials")

        session = async_create_clientsession(self.hass)
        api = MarsHydroAPI(username, password, session)
        #_LOGGER.error("Inside _test_credentials before login")
        
        try:
            return await api.login()
        except ConfigEntryAuthFailed:
            return False
        #try:
        #    _LOGGER.error("Inside _test_credentials before login")
        #    await api.login()
        #    return True
        #except ConfigEntryAuthFailed as e:
        #    _LOGGER.error("Error testing login credentials: %s", e)
        #    return False

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry):
        """Get the options flow."""
        return MarsHydroOptionsFlowHandler()
    
    async def _show_config_form(self, user_input):  # pylint: disable=unused-argument
        """Show the configuration form to edit location data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_USERNAME): str, vol.Required(CONF_PASSWORD): str}
            ),
            errors = self._errors,
        )


class MarsHydroOptionsFlowHandler(OptionsFlow):
    """Handle an options flow for Mars Hydro."""

    @property
    def options(self) -> dict:
        return dict(self.config_entry.options)
    
    @property
    def config_entry(self):
        return self.hass.config_entries.async_get_entry(self.handler)


    async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self.options.update(user_input)
            return await self._update_options()

        return self.async_show_form(
            step_id = "user",
            data_schema = vol.Schema(
                {
                    vol.Required(x, default=self.options.get(x, True)): bool
                    for x in sorted(PLATFORMS)
                }
            ),
        )

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(
            title=NAME, data=self.options
        )