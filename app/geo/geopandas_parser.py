from app.core import database
from datetime import datetime,date
import math
from anyio import to_interpreter
from app.core.database import engine
from pathlib import Path
from typing import Any
import numpy as np

import geopandas as gpd
from shapely.geometry import mapping

from app.geo.models import NormalizedFeature
from app.geo.parser import GeoFileParser


class GeoPandasParser(GeoFileParser):

    def parse(
        self,
        file_path: Path,
    ) -> tuple[str | None, list[NormalizedFeature]]:

        gdf = gpd.read_file(
            file_path,
            engine="pyogrio",
        )

        crs = self._get_crs(gdf)

        features: list[NormalizedFeature] = []

        for index, row in gdf.iterrows():
            geometry = row.geometry

            if geometry is None or geometry.is_empty:
                geometry_data: dict[str, Any] = {
                    "type": "GeometryCollection",
                    "geometries": [],
                }

                geometry_type = "GeometryCollection"
            else:
                geometry_data = mapping(geometry)
                geometry_type = geometry.geom_type

            properties = {}

            for column in gdf.columns:
                if column == gdf.geometry.name:
                    continue

                value = row[column]

                if value is not None:
                    properties[column] = self._serialize_value(value)

            features.append(
                NormalizedFeature(
                    index=int(index),
                    geometry_type=geometry_type,
                    geometry=geometry_data,
                    crs=crs,
                    properties=properties,
                )
            )

        return crs, features

    @staticmethod
    def _get_crs(
        gdf: gpd.GeoDataFrame,
    ) -> str | None:

        if gdf.crs is None:
            return None

        try:
            return gdf.crs.to_string()
        except Exception:
            return str(gdf.crs)

    @staticmethod
    def _serialize_value(value: Any) -> Any:
        """Convert geospatial attribute values to valid JSON values."""

        # Convert NumPy scalar types to native Python types.
        if isinstance(value, np.generic):
            value = value.item()

        # JSON does not support NaN or infinite numbers.
        if isinstance(value, float):
            if not math.isfinite(value):
                return None
            return value

        # Convert date/time values to JSON-compatible strings.
        if isinstance(value, (datetime, date)):
            return value.isoformat()

        # Handle NumPy arrays if a driver returns them as attributes.
        if isinstance(value, np.ndarray):
            return [
                GeoPandasParser._serialize_value(item)
                for item in value.tolist()
            ]

        # Recursively sanitize nested dictionaries.
        if isinstance(value, dict):
            return {
                str(key): GeoPandasParser._serialize_value(item)
                for key, item in value.items()
            }

        # Recursively sanitize lists and tuples.
        if isinstance(value, (list, tuple)):
            return [
                GeoPandasParser._serialize_value(item)
                for item in value
            ]

        # Keep ordinary JSON-compatible values unchanged.
        if value is None or isinstance(
            value, (str, int, bool)
        ):
            return value

        # Fallback for driver-specific attribute types.
        return str(value)