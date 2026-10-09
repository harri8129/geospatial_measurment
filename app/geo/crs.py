from __future__ import annotations
from os import stat

from typing import Optional

import geopandas as gpd
from pyproj import CRS
from shapely.geometry.base import BaseGeometry

class CRSService :
    """
    Handle CRS detection and selection of an appropriate
    projected CRS for measurment calculations.
    """

    @staticmethod
    def normalize_crs(crs: Optional[str]) -> Optional[CRS]:
        """
        Convert a CRS string into  pyproj CRS object
        """

        if not crs :
            return None

        return CRS.from_user_input(crs)

    @staticmethod
    def is_geographic(crs: CRS) -> bool:
        """
        Return True is the crs uses geographic coordinates ,
        such as latitude / longitude
        """

        return crs.is_geographic

    @staticmethod
    def is_projected(
        crs: CRS,
    ) -> bool:
        """
        Return True if the CRS is already projected.
        """

        return crs.is_projected

    @staticmethod
    def get_projected_crs(geometry : BaseGeometry,source_crs:CRS) -> CRS:
        """
        Select an appropriate projected CRS for measurements.

        If the source CRS is already projected, it is reused.

        If the source CRS is geographic, GeoPandas is used to
        estimate an appropriate UTM CRS based on the geometry.
        """

        if source_crs.is_projected:
            return source_crs

        if not source_crs.is_geographic:
            raise ValueError(
                f"Unsupported CRS type: {source_crs}"
            )

        if geometry is None or geometry.is_empty:
            raise ValueError(
                "Cannot determine projected CRS for empty geometry."
            )

        geometry_gdf = gpd.GeoDataFrame(
            geometry=[geometry],
            crs=source_crs,
        )

        projected_crs = geometry_gdf.estimate_utm_crs()

        if projected_crs is None:
            raise ValueError(
                "Could not determine a suitable projected CRS."
            )

        return projected_crs