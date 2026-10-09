from pathlib import Path

from app.geo.geopandas_parser import GeoPandasParser
from app.geo.models import NormalizedFeature


class ShapefileParser(GeoPandasParser):

    def parse(
        self,
        file_path: Path,
    ) -> tuple[str | None, list[NormalizedFeature]]:

        return super().parse(file_path)