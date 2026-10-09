from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FileResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    filename: str
    file_type: str
    file_size: int = Field(
        description="Uploaded file size in bytes.",
    )
    feature_count: int
    crs: str | None
    status: str
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    @field_validator("status", mode="before")
    @classmethod
    def serialize_status(cls, value: object) -> str:
        if isinstance(value, Enum):
            return value.name
        return str(value).upper()


class FileSummaryResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    filename: str
    feature_count: int
    crs: str | None
    status: str

    @field_validator("status", mode="before")
    @classmethod
    def serialize_status(cls, value: object) -> str:
        if isinstance(value, Enum):
            return value.name
        return str(value).upper()