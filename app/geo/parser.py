from abc import ABC, abstractmethod
from pathlib import Path

from app.geo.models import NormalizedFeature


class GeoFileParser(ABC):

    @abstractmethod
    def parse(
        self,
        file_path: Path,
    ) -> tuple[str | None, list[NormalizedFeature]]:
        """
        Parse a geospatial file.

        Returns:
            CRS identifier and normalized features.
        """
        raise NotImplementedError