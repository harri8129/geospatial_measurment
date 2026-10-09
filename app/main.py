from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import (
    FileNotFoundError,
    FileProcessingError,
    GeospatialFileError,
    InvalidGeospatialFileError,
    InvalidShapefileArchiveError,
    UnsupportedFileTypeError,
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Backend service for processing geospatial "
        "files and calculating measurements."
    ),
)


@app.exception_handler(UnsupportedFileTypeError)
async def unsupported_file_handler(
    _request: Request,
    exc: UnsupportedFileTypeError,
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


@app.exception_handler(InvalidShapefileArchiveError)
async def invalid_archive_handler(
    _request: Request,
    exc: InvalidShapefileArchiveError,
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)},
    )


@app.exception_handler(InvalidGeospatialFileError)
async def invalid_geospatial_file_handler(
    _request: Request,
    exc: InvalidGeospatialFileError,
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)},
    )


@app.exception_handler(FileNotFoundError)
async def file_not_found_handler(
    _request: Request,
    exc: FileNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )


@app.exception_handler(FileProcessingError)
async def file_processing_handler(
    _request: Request,
    exc: FileProcessingError,
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)},
    )


@app.exception_handler(GeospatialFileError)
async def geospatial_error_handler(
    _request: Request,
    exc: GeospatialFileError,
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)},
    )


app.include_router(
    api_router,
    prefix=settings.API_PREFIX,
)
