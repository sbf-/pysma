from abc import ABC, abstractmethod
from typing import Any, Dict, List
from .sensor import Sensors


class Device(ABC):
    """abstract base class on which all device implementations are based."""

    @abstractmethod
    async def get_sensors(self) -> Sensors:
        """Returns a list of all supported sensors"""
        pass

    @abstractmethod
    async def new_session(self) -> bool:
        """Starts a new session"""
        pass

    @abstractmethod
    async def device_info(self) -> dict:
        """Return a Dict with basic device information"""
        pass

    @abstractmethod
    async def read(self, sensors: Sensors) -> bool:
        """Updates all sensors"""
        pass

    @abstractmethod
    async def close_session(self) -> None:
        """Closes the session"""
        pass

    async def detect(self, ip: str) -> List:
        """Tries an automatic detection of this device and returns the results """
        return [
            {
                "testedEndpoints": "",
                "status": "failed",
                "access": "",
                "device": "",
                "exception": "",
                "remark": "",
            }
        ]

    @abstractmethod
    async def get_debug(self) -> Dict[str, Any]:
        """Return a dict with all debug information."""
        pass
