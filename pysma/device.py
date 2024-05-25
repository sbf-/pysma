"""
abstract base class on which all device implementations are based
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from dataclasses import dataclass
from .sensor import Sensor, Sensors

@dataclass
class DiscoveryInformation():
    tested_endpoints: str = ""
    status: str = ""
    access: str = ""
    exception: Exception | None = None
    remark: str = ""
    device: str = ""


class Device(ABC):
    """abstract base class on which all device implementations are based."""

    @abstractmethod
    async def get_sensors(self) -> Sensors:
        """Returns a list of all supported sensors"""

    @abstractmethod
    async def new_session(self) -> bool:
        """Starts a new session"""

    @abstractmethod
    async def device_info(self) -> dict:
        """Return a Dict with basic device information"""

    @abstractmethod
    async def read(self, sensors: Sensors) -> bool:
        """Updates all sensors"""

    @abstractmethod
    async def close_session(self) -> None:
        """Closes the session"""

    @abstractmethod
    async def detect(self, ip: str) -> List[DiscoveryInformation]:
        """ Try to detect SMA devices """

    @abstractmethod
    async def get_debug(self) -> Dict[str, Any]:
        """Return a dict with all debug information."""

    def set_options(self, options: Dict[str, Any]) -> None:
        """Set options"""
        pass

    def set_parameter(self, sensor: Sensor | str, value: int) -> None:
        """Set Parameters."""
        pass
