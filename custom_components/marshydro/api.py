import aiohttp
import json
import time
import logging
import socket
import asyncio
import async_timeout

from .mars_device import MarsHydroDevice, MarsHydroDevices


TIMEOUT = 30

_LOGGER: logging.Logger = logging.getLogger(__package__)

HEADERS = {
    "Content-type": "application/json; charset=UTF-8",
    "User-Agent": "Python/3.x",
    "Accept-Encoding": "gzip",
    "Host": "api.lgledsolutions.com",
}


class MarsHydroAPI:
    def __init__(
        self, username: str, password: str, session: aiohttp.ClientSession
    ) -> None:
        """Sample API Client."""
        self._username = username
        self._password = password
        self._session = session
        self._token = None
        self._last_login_time = None
        self._login_interval = 300 
        self._base_url = "https://api.lgledsolutions.com/api/android"

    async def _ensure_token(self):
        """Ensure that the token is valid."""
        if not self._token:
            _LOGGER.error(f"Inside _ensure_token, apparently token is None token: {self._token}")
            await self.login()


    async def login(self) -> bool:
        """Authenticate and retrieve the token."""
        now = time.time()
        if self._token and (now - self._last_login_time < self._login_interval):
            _LOGGER.info("Token still valid, skipping login.")
            return True

        HEADERS["systemData"] = self._generate_system_data()

        #_LOGGER.error("Enter API login method")
        login_data = {
            "email": self._username,
            "password": self._password,
            "loginMethod": "1"
        }

        url = f"{self._base_url}/ulogin/mailLogin/v1"
        response = await self.api_wrapper("post", url, data=login_data, headers=HEADERS)
        if not response:
            return False
        #_LOGGER.error(f"Response in login: {response}")
        self._token = response["token"]
        self._last_login_time = now
        _LOGGER.info(f"Login erfolgreich, Token erhalten: {self._token}")
        return True

    async def async_get_devices(self) -> MarsHydroDevice | list:
        await self._ensure_token()

        HEADERS["systemData"] = self._generate_system_data()
        json_body = {"currentPage": 0}

        url = f"{self._base_url}/udm/getDeviceList/v1"
        response = await self.api_wrapper("post", url, data=json_body, headers=HEADERS)
        
        
        return response["list"]
        
        #device_list = {}
        #for device in response.get("list", []):
        #    prod_type = device["productType"]
        #    device_list[prod_type] = device

        #return device_list


    async def async_set_device_p(self, brightness, device_id) -> None:
        """Set the brightness of the Mars Hydro light."""
        await self._ensure_token()

        HEADERS["systemData"] = self._generate_system_data()

        url = f"{self._base_url}/udm/adjustLight/v1"

        json_body = {
            "light": brightness,
            "deviceId": device_id,
            "groupId": None,
        }

        response = await self.api_wrapper("post", url, data=json_body, headers=HEADERS)
        _LOGGER.info(response)
        

    async def toggle_switch(self, is_close: bool, device_id: str):
        """Toggle the light or fan switch (on/off)."""
        await self._ensure_token()

        HEADERS["systemData"] = self._generate_system_data()

        url = f"{self._base_url}/udm/lampSwitch/v1"

        json_body = {
            "isClose": is_close,
            "deviceId": device_id,
            "groupId": None,
        }

        response = await self.api_wrapper("post", url, data=json_body, headers=HEADERS)
        _LOGGER.info(response)

    async def async_get_device_data(self, device_id) -> MarsHydroDevice:
        """Get detailed info on the device"""
        await self._ensure_token()

        HEADERS["systemData"] = self._generate_system_data()

        url = f"{self._base_url}/udm/getDeviceDetail/v1"

        json_body = {
            "deviceId": device_id,
        }

        response = await self.api_wrapper("post", url, data=json_body, headers=HEADERS)
        _LOGGER.info(f"async_get_device_data response: {response}")
        return response

    def _generate_system_data(self, device_id=None):
        """Generate systemData payload with dynamic device_id."""
        now_time = int(time.time())
        system_data = {
            "reqId": now_time * 1000,
            "appVersion": "1.2.0",
            "osType": "android",
            "osVersion": "14",
            "deviceType": "SM-S928C",
            "netType": "wifi",
            "wifiName": "123",
            "timestamp": now_time,
            "timezone": "Europe/Berlin",
            "language": "German"
        }
        if device_id:
            system_data["deviceId"] = device_id
        if self._token:
            system_data["token"] = self._token
        return json.dumps(system_data)
    

    async def api_wrapper(
        self, method: str, url: str, data: dict = {}, headers: dict = {}
    ) -> dict:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(TIMEOUT):
                
                if method == "get":
                    response = await self._session.get(url, params=data, headers=headers)#, ssl=False, proxy="http://192.168.178.62:8080")

                elif method == "put":
                    response = await self._session.put(url, headers=headers, json=data)#, ssl=False, proxy="http://192.168.178.62:8080")

                elif method == "patch":
                    response = await self._session.patch(url, headers=headers, json=data)#, ssl=False, proxy="http://192.168.178.62:8080")

                elif method == "post":
                    response = await self._session.post(url, headers=headers, json=data)#, ssl=False, proxy="http://192.168.178.62:8080")
                json_response = await response.json()
                #_LOGGER.error("HTTP Response json: %s", json_response)

                if json_response["code"] == "000" and "data" in json_response:
                    return json_response["data"]
                
                if json_response["code"] == "100":
                    _LOGGER.error("Error logging in: %s",json_response["msg"])
                    raise aiohttp.ClientError
                
                if json_response["code"] == "102":
                    _LOGGER.error("Token expired, re-authenticating...")
                    await self.login()
                    self.api_wrapper(method, url, data, headers)
        
                _LOGGER.error("result not in esponse.")
        except asyncio.TimeoutError as exception:
            _LOGGER.error(
                "Timeout error fetching information from %s - %s",
                url,
                exception,
            )

        except (KeyError, TypeError) as exception:
            _LOGGER.error(
                "Error parsing information from %s - %s",
                url,
                exception,
            )
        except (aiohttp.ClientError, socket.gaierror) as exception:
            _LOGGER.error(
                "Error fetching information from %s - %s",
                url,
                exception,
            )
        except Exception as exception:  # pylint: disable=broad-except
            _LOGGER.error("Something really wrong happened! - %s", exception)
