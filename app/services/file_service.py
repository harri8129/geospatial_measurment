from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import (
    FileProcessingError,
    GeospatialFileError,
)
from app.geo.parser_factory import get_parser
from app.models import File, FileStatus, Feature
from app.utils.archive import extract_shapefile_archive
from app.utils.file_utils import validate_extension
from app.geo.measurement_calculator import MeasurementCalculator
from shapely.geometry import shape

class FileService:
    def __init__(self, db: Session):
        self.db = db

    def process_file(
        self,
        source_path: Path,
        filename: str,
        file_size: int,
    ) -> File:

        extension = validate_extension(filename)

        file_record = File(
            filename=filename,
            file_type=extension,
            file_size=file_size,
            status=FileStatus.PROCESSING,
        )

        self.db.add(file_record)
        self.db.flush()

        try:
            processing_path = source_path

            if extension == ".zip":
                extraction_dir = (
                    Path(settings.EXTRACTED_DIR)
                    / str(file_record.id)
                )

                processing_path = extract_shapefile_archive(
                    source_path,
                    extraction_dir,
                )

            parser = get_parser(extension)

            crs, normalized_features = parser.parse(
                processing_path
            )

            file_record.crs = crs
            file_record.feature_count = len(
                normalized_features
            )

            calculator = MeasurementCalculator()

            for normalized in normalized_features:

                geometry = shape(
                    normalized.geometry
                )

                measurement = calculator.calculate(
                    geometry=geometry,
                    source_crs=normalized.crs,
                )

                feature = Feature(
                    file_id=file_record.id,
                    feature_index=normalized.index,
                    geometry_type=normalized.geometry_type,
                    geometry=normalized.geometry,
                    crs=normalized.crs,
                    properties=normalized.properties,
                    measurement_type=measurement.measurement_type,
                    measurement_value=measurement.value,
                    measurement_unit=measurement.unit,
                    measurement_crs=measurement.measurement_crs,
                )

                self.db.add(feature)

            file_record.status = FileStatus.COMPLETED

            self.db.commit()
            self.db.refresh(file_record)

            return file_record

        except GeospatialFileError as exc:
            self._save_failed_record(
                file_record.id,
                filename,
                extension,
                file_size,
                str(exc),
            )
            raise

        except Exception as exc:
            self._save_failed_record(
                file_record.id,
                filename,
                extension,
                file_size,
                str(exc),
            )
            raise FileProcessingError(
                f"Failed to process file: {exc}"
            ) from exc

    def _save_failed_record(
        self,
        file_id: UUID,
        filename: str,
        extension: str,
        file_size: int,
        error_message: str,
    ) -> None:
        self.db.rollback()

        failed_record = File(
            id=file_id,
            filename=filename,
            file_type=extension,
            file_size=file_size,
            status=FileStatus.FAILED,
            error_message=error_message,
        )

        self.db.add(failed_record)
        self.db.commit()
        self.db.refresh(failed_record)