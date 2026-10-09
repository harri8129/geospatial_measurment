class GeospatialFileError(Exception):
    """Base exception for geospatial file processing."""


class UnsupportedFileTypeError(GeospatialFileError):
    """Raised when the uploaded file type is unsupported."""


class InvalidGeospatialFileError(GeospatialFileError):
    """Raised when the uploaded file is not a valid geospatial file."""


class InvalidShapefileArchiveError(GeospatialFileError):
    """Raised when a ZIP does not contain a valid Shapefile."""


class FileNotFoundError(GeospatialFileError):
    """Raised when a requested file does not exist."""


class FileProcessingError(GeospatialFileError):
    """Raised when geospatial processing fails."""