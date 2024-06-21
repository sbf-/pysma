"""Helper functions for the pysma library."""

import dataclasses
import json
from typing import Any, Dict
from urllib.parse import urlparse


class BetterJSONEncoder(json.JSONEncoder):
    """JSON Encoder that handles dataclasses and non serialziable objects."""

    def default(self, o: Any) -> Any:
        """Handler for the Encoder."""
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return str(o)


def splitUrl(url: str) -> Dict[str, Any]:
    if "://" not in url:
        url = "fake://" + url
    x = urlparse(url)
    return {
        "schema": x.scheme,
        "host": x.hostname,
        "netloc": x.netloc,
        "port": x.port,
    }


def toJson(obj: Any):
    """Converts a object to a json String.
    Incl. handling of dataclass."""
    return json.dumps(obj, cls=BetterJSONEncoder, indent=4)


def version_int_to_string(version_integer: int) -> str:
    """Convert a version integer to a readable string.

    Args:
        version_integer (int): The version integer, as retrieved from the device.

    Returns:
        str: The version translated to a readable string.
    """
    if not version_integer:
        return ""

    appendixes = ["N", "E", "A", "B", "R", "S"]
    version_bytes = version_integer.to_bytes(4, "big")
    version_appendix = (
        appendixes[version_bytes[3]] if 0 <= version_bytes[3] < len(appendixes) else ""
    )
    return f"{version_bytes[0]:x}.{version_bytes[1]:x}.{version_bytes[2]}.{version_appendix}"


def isInteger(s: str) -> bool:
    """Test if the string is a integer"""
    try:
        int(s)
        return True
    except ValueError:
        return False
