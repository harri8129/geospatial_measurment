from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class MeasurementResult:
    measurement_type: Optional[str]
    value: Optional[Decimal]
    unit: Optional[str]
    measurement_crs: Optional[str]
    message: Optional[str] = None