from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import FileNotFoundError
from app.models import File


class FileQueryService:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def get_file(
        self,
        file_id: UUID,
    ) -> File:

        statement = (
            select(File)
            .where(File.id == file_id)
        )

        file_record = self.db.scalar(statement)

        if file_record is None:
            raise FileNotFoundError(
                f"File '{file_id}' was not found."
            )

        return file_record