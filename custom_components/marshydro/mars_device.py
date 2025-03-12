class MarsHydroDevice(TypedDict, total=False):
    deviceName: str
    deviceImage: str
    isClose: bool
    id: str
    deviceLightRate: str
    
    
class MarsHydroLight(MarsHydroDevice):


class MarsHydroFan(MarsHydroDevice):
    humidity: int
    temperature: float
    speed: int