from decimal import Decimal, InvalidOperation

import geopandas as gpd
from shapely.geometry.base import BaseGeometry

from app.geo.crs import CRSService
from app.geo.measurement import MeasurementResult


class MeasurementCalculator:
    """
    Calculates measurements for supported geometry types.

    Supported:
        Polygon
        MultiPolygon
        LineString
        MultiLineString

    Point geometries intentionally return no measurement.
    """

    def __init__(
        self,
        crs_service: CRSService | None = None,
    ):
        self.crs_service = (
            crs_service
            or CRSService()
        )

    def calculate(
        self,
        geometry: BaseGeometry,
        source_crs: str | None,
    ) -> MeasurementResult:

        if geometry is None or geometry.is_empty:
            return MeasurementResult(
                measurement_type=None,
                value=None,
                unit=None,
                measurement_crs=None,
                message="Geometry is empty.",
            )

        if source_crs is None:
            return MeasurementResult(
                measurement_type=None,
                value=None,
                unit=None,
                measurement_crs=None,
                message=(
                    "CRS is missing. "
                    "Measurement cannot be calculated safely."
                ),
            )

        source_crs_obj = (
            self.crs_service.normalize_crs(
                source_crs
            )
        )

        projected_crs = (
            self.crs_service.get_projected_crs(
                geometry,
                source_crs_obj,
            )
        )

        projected_geometry = self._project_geometry(
            geometry=geometry,
            source_crs=source_crs_obj,
            projected_crs=projected_crs,
        )

        geometry_type = geometry.geom_type

        if geometry_type in {
            "Polygon",
            "MultiPolygon",
        }:
            return self._calculate_area(
                projected_geometry,
                projected_crs,
            )

        if geometry_type in {
            "LineString",
            "MultiLineString",
        }:
            return self._calculate_length(
                projected_geometry,
                projected_crs,
            )

        if geometry_type in {
            "Point",
            "MultiPoint",
        }:
            return MeasurementResult(
                measurement_type=None,
                value=None,
                unit=None,
                measurement_crs=projected_crs.to_string(),
                message=(
                    "No measurement required "
                    "for point geometry."
                ),
            )

        return MeasurementResult(
            measurement_type=None,
            value=None,
            unit=None,
            measurement_crs=projected_crs.to_string(),
            message=(
                f"Measurement is not supported "
                f"for geometry type '{geometry_type}'."
            ),
        )

    @staticmethod
    def _project_geometry(
        geometry: BaseGeometry,
        source_crs,
        projected_crs,
    ) -> BaseGeometry:

        gdf = gpd.GeoDataFrame(
            geometry=[geometry],
            crs=source_crs,
        )

        projected = gdf.to_crs(
            projected_crs
        )

        return projected.geometry.iloc[0]

    @staticmethod
    def _calculate_area(
        geometry: BaseGeometry,
        projected_crs,
    ) -> MeasurementResult:

        value = geometry.area

        return MeasurementResult(
            measurement_type="area",
            value=MeasurementCalculator._to_decimal(
                value
            ),
            unit="m²",
            measurement_crs=projected_crs.to_string(),
        )

    @staticmethod
    def _calculate_length(
        geometry: BaseGeometry,
        projected_crs,
    ) -> MeasurementResult:

        value = geometry.length

        return MeasurementResult(
            measurement_type="length",
            value=MeasurementCalculator._to_decimal(
                value
            ),
            unit="m",
            measurement_crs=projected_crs.to_string(),
        )

    @staticmethod
    def _to_decimal(
        value: float,
    ) -> Decimal:

        try:
            return Decimal(
                str(round(value, 6))
            )
        except (InvalidOperation, ValueError):
            raise ValueError(
                f"Could not convert measurement "
                f"value '{value}' to Decimal."
            )