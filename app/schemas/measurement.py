from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class MeasurementResponse(BaseModel):
    feature_id: UUID
    feature_index: int
    geometry_type: str
    measurement_type: str | None
    value: Decimal | None
    unit: str | None
    source_crs: str | None
    measurement_crs: str | None
    message: str | None = None
    properties: dict[str, Any] = Field(
        default_factory=dict,
    )


class MeasurementsResponse(BaseModel):
    file_id: UUID
    feature_count: int
    measurements: list[MeasurementResponse]
