from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.models import FileStatus
from app.services.file_service import FileService


class FakeSession:
    def __init__(self):
        self.file_record = None
        self.features = []

    def add(self, record):
        if getattr(record, "id", None) is None:
            record.id = uuid4()

    def flush(self):
        pass

    def commit(self):
        pass

    def rollback(self):
        pass

    def refresh(self, record):
        pass

    def scalar(self, statement):
        return self.file_record

    def scalars(self, statement):
        return iter(self.features)

    def execute(self, statement):
        return None


@pytest.fixture
def client():
    db = FakeSession()

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client, db
    app.dependency_overrides.clear()


def _file_record(**overrides):
    values = {
        "id": uuid4(),
        "filename": "test.kml",
        "file_type": ".kml",
        "file_size": 1234,
        "feature_count": 3,
        "crs": "EPSG:4326",
        "status": FileStatus.COMPLETED,
        "error_message": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_health(client):
    test_client, _ = client

    response = test_client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_database_health(client):
    test_client, _ = client

    response = test_client.get("/api/health/database")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "database": "connected",
    }


def test_upload_kml_response(client, monkeypatch):
    test_client, _ = client
    expected_file = _file_record()

    def process_file(self, source_path, filename, file_size):
        return expected_file

    monkeypatch.setattr(FileService, "process_file", process_file)

    response = test_client.post(
        "/api/files/",
        files={
            "file": (
                "test.kml",
                b"<kml/>",
                "application/vnd.google-earth.kml+xml",
            )
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "COMPLETED"
    assert response.json()["feature_count"] == 3


def test_invalid_extension_returns_expected_error(client):
    test_client, _ = client

    response = test_client.post(
        "/api/files/",
        files={"file": ("test.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": (
            "Unsupported file type '.txt'. "
            "Allowed types: .kml, .zip"
        )
    }


def test_invalid_zip_returns_validation_error(
    client,
    monkeypatch,
    tmp_path,
):
    test_client, _ = client
    monkeypatch.setattr(
        "app.api.files.settings.UPLOAD_DIR",
        str(tmp_path / "uploads"),
    )
    monkeypatch.setattr(
        "app.core.config.settings.EXTRACTED_DIR",
        str(tmp_path / "extracted"),
    )

    response = test_client.post(
        "/api/files/",
        files={"file": ("bad.zip", b"not a zip", "application/zip")},
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Uploaded ZIP file is invalid."
    }


def test_file_not_found_returns_404(client):
    test_client, _ = client

    response = test_client.get(
        f"/api/files/{uuid4()}/"
    )

    assert response.status_code == 404
    assert "was not found" in response.json()["detail"]


def test_invalid_file_id_returns_422(client):
    test_client, _ = client

    response = test_client.get("/api/files/not-a-uuid/")

    assert response.status_code == 422


def test_measurements_response_envelope(client):
    test_client, db = client
    file_record = _file_record()
    feature_id = uuid4()
    db.file_record = file_record
    db.features = [
        SimpleNamespace(
            id=feature_id,
            feature_index=0,
            geometry_type="LineString",
            measurement_type="length",
            measurement_value=Decimal("123.456"),
            measurement_unit="m",
            crs="EPSG:4326",
            measurement_crs="EPSG:32643",
            properties={"name": "Route"},
        )
    ]

    response = test_client.get(
        f"/api/files/{file_record.id}/measurements/"
    )

    assert response.status_code == 200
    assert response.json() == {
        "file_id": str(file_record.id),
        "feature_count": 1,
        "measurements": [
            {
                "feature_id": str(feature_id),
                "feature_index": 0,
                "geometry_type": "LineString",
                "measurement_type": "length",
                "value": "123.456",
                "unit": "m",
                "source_crs": "EPSG:4326",
                "measurement_crs": "EPSG:32643",
                "message": None,
                "properties": {"name": "Route"},
            }
        ],
    }


def test_measurements_unavailable_until_processing_completes(client):
    test_client, db = client
    db.file_record = _file_record(
        status=FileStatus.PROCESSING
    )

    response = test_client.get(
        f"/api/files/{db.file_record.id}/measurements/"
    )

    assert response.status_code == 409


def test_openapi_includes_measurements_endpoint(client):
    test_client, _ = client

    response = test_client.get("/openapi.json")

    assert response.status_code == 200
    assert "/api/files/{file_id}/measurements/" in response.json()["paths"]
