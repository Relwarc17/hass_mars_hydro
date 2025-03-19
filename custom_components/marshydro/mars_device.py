from typing import TypedDict

class MarsHydroDevices():
    list: list


class MarsHydroDevice(TypedDict, total=False):
    deviceName: str
    deviceImg: str
    deviceBluetooth: str
    isClose: bool
    isNetDevice: bool
    id: str
    connectionStatus: str
    deviceLightRate: str
    localLight: int
    controlMode: str
    productType: str
    humidity: str
    temperature: str
    speed: str