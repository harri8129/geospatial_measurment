import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.file import File



class Feature(Base):
    __tablename__ = "features"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    feature_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    geometry_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    geometry: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    crs: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    properties: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )

    measurement_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    measurement_value: Mapped[Decimal | None] = mapped_column(
        Numeric(20, 6),
        nullable=True,
    )

    measurement_unit: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    measurement_crs: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    file: Mapped["File"] = relationship(
        "File",
        back_populates="features",
    )