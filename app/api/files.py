from pathlib import Path
from uuid import UUID, uuid4

from fastapi import (
    APIRouter,
    Depends,
    File as FastAPIFile,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_database
from app.core.config import settings
from app.schemas.common import ErrorResponse
from app.schemas.file import FileResponse
from app.services.file_query_service import FileQueryService
from app.services.file_service import FileService
from app.utils.file_utils import validate_extension


router = APIRouter(
    prefix="/files",
    tags=["Files"],
)

@router.post(
    "/",
    response_model=FileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and process a geospatial file",
    description=(
        "Upload a KML file or a ZIP archive "
        "containing a Shapefile."
    ),
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorResponse,
            "description": "The file type is not supported.",
        },
        status.HTTP_413_CONTENT_TOO_LARGE: {
            "model": ErrorResponse,
            "description": "The uploaded file is too large.",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorResponse,
            "description": "The file could not be processed.",
        },
    },
)
async def upload_file(
    file: UploadFile = FastAPIFile(
        ...,
        description=(
            "KML file or ZIP archive containing "
            "a Shapefile."
        ),
    ),
    db: Session = Depends(get_database),
):
    filename = file.filename
    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required.",
        )

    extension = validate_extension(filename)

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    stored_filename = str(uuid4())
    destination = upload_dir / f"{stored_filename}{extension}"

    file_size = 0
    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024

    try:
        with destination.open("wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                file_size += len(chunk)

                if file_size > max_size:
                    raise HTTPException(
                        status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                        detail=(
                            "File exceeds the maximum "
                            "size of "
                            f"{settings.MAX_FILE_SIZE_MB} MB."
                        ),
                    )

                buffer.write(chunk)

        service = FileService(db)

        record = service.process_file(
            source_path=destination,
            filename=filename,
            file_size=file_size,
        )

        return record

    finally:
        destination.unlink(
            missing_ok=True
        )

@router.get(
    "/{file_id}/",
    response_model=FileResponse,
    summary="Get uploaded file information",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "File not found.",
        },
    },
)
def get_file(
    file_id: UUID,
    db: Session = Depends(get_database),
):
    service = FileQueryService(db)
    return service.get_file(file_id)