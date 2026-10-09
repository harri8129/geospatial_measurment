from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_database
from app.schemas.common import ErrorResponse
from app.schemas.measurement import (
    MeasurementResponse,
    MeasurementsResponse,
)
from app.services.measurement_service import MeasurementService


router = APIRouter(
    prefix="/files",
    tags=["Measurements"],
)


@router.get(
    "/{file_id}/measurements/",
    response_model=MeasurementsResponse,
    summary="Get measurements for a file",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "File not found.",
        },
        status.HTTP_409_CONFLICT: {
            "model": ErrorResponse,
            "description": "File processing is not complete.",
        },
    },
)
def get_measurements(
    file_id: UUID,
    db: Session = Depends(get_database),
):
    service = MeasurementService(db)

    try:
        file_record, features = service.get_file_measurements(
            file_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    measurements = []

    for feature in features:

        message = None

        if feature.measurement_type is None:
            if feature.geometry_type in {
                "Point",
                "MultiPoint",
            }:
                message = (
                    "No measurement required "
                    "for point geometry."
                )
            else:
                message = (
                    "Measurement is not supported "
                    f"for geometry type "
                    f"'{feature.geometry_type}'."
                )

        measurements.append(
            MeasurementResponse(
                feature_id=feature.id,
                feature_index=feature.feature_index,
                geometry_type=feature.geometry_type,
                measurement_type=feature.measurement_type,
                value=feature.measurement_value,
                unit=feature.measurement_unit,
                source_crs=feature.crs,
                measurement_crs=feature.measurement_crs,
                message=message,
                properties=feature.properties,
            )
        )

    return MeasurementsResponse(
        file_id=file_record.id,
        feature_count=len(measurements),
        measurements=measurements,
    )