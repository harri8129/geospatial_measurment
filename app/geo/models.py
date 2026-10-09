from dataclasses import dataclass
from typing import Any


@dataclass
class NormalizedFeature:
    index: int
    geometry_type: str
    geometry: dict[str, Any]
    crs: str | None
    properties: dict[str, Any]