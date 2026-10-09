from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import FileNotFoundError
from app.models import Feature, File, FileStatus


class MeasurementService:

    def __init__(self, db: Session):
        self.db = db

    def get_file_measurements(
        self,
        file_id: UUID,
    ) -> tuple[File, list[Feature]]:

        file_statement = (
            select(File)
            .where(File.id == file_id)
        )
        file_record = self.db.scalar(file_statement)

        if file_record is None:
            raise FileNotFoundError(
                f"File '{file_id}' was not found."
            )

        if file_record.status != FileStatus.COMPLETED:
            raise ValueError(
                "Measurements are not available "
                "for a file that has not completed "
                "processing."
            )

        statement = (
            select(Feature)
            .where(Feature.file_id == file_id)
            .order_by(Feature.feature_index)
        )

        features = list(
            self.db.scalars(statement)
        )

        return file_record, features