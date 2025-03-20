from typing import TypedDict

class MarsHydroDevices():
    list: list


class MarsHydroDevice(TypedDict, total=False):
    deviceName: str
    deviceImg: str
    deviceBluetooth: str
    isClose: bool
    isNetDevice: bool
    productId: int
    id: int
    connectStatus: int
    deviceLightRate: int
    localLight: int
    controlMode: str
    productType: str
    humidity: str
    temperature: str
    old_humidity: str = "0"
    old_temperature: str = "0"
    speed: str
    deviceVersion: str