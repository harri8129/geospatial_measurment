from pathlib import Path
from zipfile import BadZipFile, ZipFile

from app.core.exceptions import InvalidShapefileArchiveError


REQUIRED_SHAPEFILE_FILES = {
    ".shp",
    ".shx",
    ".dbf",
}


def extract_shapefile_archive(
    zip_path: Path,
    extraction_dir: Path,
) -> Path:

    extraction_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        with ZipFile(zip_path, "r") as archive:

            members = archive.namelist()

            file_names = {
                Path(member).name.lower()
                for member in members
                if not member.endswith("/")
            }

            extensions = {
                Path(name).suffix.lower()
                for name in file_names
            }

            missing = REQUIRED_SHAPEFILE_FILES - extensions

            if missing:
                raise InvalidShapefileArchiveError(
                    "ZIP archive does not contain a complete "
                    f"Shapefile. Missing: {sorted(missing)}"
                )

            _validate_archive_paths(members)

            archive.extractall(extraction_dir)

    except BadZipFile as exc:
        raise InvalidShapefileArchiveError(
            "Uploaded ZIP file is invalid."
        ) from exc

    shapefiles = list(
        extraction_dir.rglob("*.shp")
    )

    if not shapefiles:
        raise InvalidShapefileArchiveError(
            "No .shp file found in ZIP archive."
        )

    if len(shapefiles) > 1:
        raise InvalidShapefileArchiveError(
            "ZIP archive contains multiple Shapefiles. "
            "Please upload an archive containing exactly one Shapefile."
        )

    return shapefiles[0]


def _validate_archive_paths(
    members: list[str],
) -> None:

    for member in members:
        member_path = Path(member)

        if member_path.is_absolute():
            raise InvalidShapefileArchiveError(
                "ZIP archive contains an absolute path."
            )

        if ".." in member_path.parts:
            raise InvalidShapefileArchiveError(
                "ZIP archive contains an unsafe path."
            )