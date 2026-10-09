from pathlib import Path

from app.core.exceptions import UnsupportedFileTypeError
from app.geo.kml_parser import KMLParser
from app.geo.parser import GeoFileParser
from app.geo.shapefile_parser import ShapefileParser


def get_parser(
    file_type: str,
) -> GeoFileParser:

    if file_type == ".kml":
        return KMLParser()

    if file_type == ".zip":
        return ShapefileParser()

    raise UnsupportedFileTypeError(
        f"Unsupported file type: {file_type}"
    )