from pathlib import Path

from app.core.config import settings
from app.core.exceptions import UnsupportedFileTypeError

def validate_extension(
    filename: str,
) -> str:

    extension = Path(filename).suffix.lower()

    if extension not in settings.ALLOWED_FILE_EXTENSIONS:
        raise UnsupportedFileTypeError(
            f"Unsupported file type '{extension}'. "
            "Allowed types: "
            f"{', '.join(settings.ALLOWED_FILE_EXTENSIONS)}"
        )

    return extension