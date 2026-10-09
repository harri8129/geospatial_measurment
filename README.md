# Geospatial File Measurement API

A FastAPI service that accepts KML files and ZIP archives containing a
Shapefile, extracts their features, calculates supported measurements in a
projected coordinate reference system (CRS), and stores file and feature data
in PostgreSQL.

## Features

- Upload `.kml` files and `.zip` Shapefile archives.
- Validate file extensions, upload size, and Shapefile archive structure.
- Extract feature geometry, attributes, and source CRS with GeoPandas/pyogrio.
- Calculate polygon area and line length after projecting geometries.
- Store file metadata, geometry, properties, CRS, and measurement results.
- Retrieve file information and stored measurements over a REST API.

## Technology

- Python 3.12+
- FastAPI and Pydantic
- PostgreSQL and SQLAlchemy
- Alembic
- GeoPandas, pyogrio, Shapely, and PyProj
- Docker Compose (for local PostgreSQL)

## Setup

### Prerequisites

- Python 3.12 or newer.
- Docker Engine with the Docker Compose plugin, or a PostgreSQL server.
- GDAL support for KML in the installed GeoPandas/pyogrio environment.

### Install dependencies

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

On Windows PowerShell, activate the environment with:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Configure PostgreSQL

Start the included PostgreSQL service:

```bash
docker compose up -d postgres
docker compose ps
```

Copy the example environment file, then edit `.env` in the repository root:

```bash
cp .env.example .env
```

Set a local password in `POSTGRES_PASSWORD` and use the same password in
`DATABASE_URL`. Keep `.env` private; it is git-ignored. Use URL-encoded
passwords if they contain characters that have special meaning in a URL.
For a deployed environment, use secret management rather than `.env` files.

Apply the database migrations:

```bash
alembic upgrade head
```

### Run the API

```bash
uvicorn app.main:app --reload
```

The API listens at `http://127.0.0.1:8000`. Interactive OpenAPI docs are at
[`/docs`](http://127.0.0.1:8000/docs); the OpenAPI document is at
[`/openapi.json`](http://127.0.0.1:8000/openapi.json).

### Run tests

```bash
pytest -v
```

The API tests use a fake database session for repeatable endpoint tests. They
do not replace a live PostgreSQL integration test.

## API

All routes are prefixed with `/api`. File uploads use multipart form data with
a required field named `file`.

### Health

#### `GET /api/health`

No input required.

```bash
curl -i http://127.0.0.1:8000/api/health
```

Expected response (`200 OK`):

```json
{"status": "healthy"}
```

#### `GET /api/health/database`

No input required. Executes a database connectivity check.

```bash
curl -i http://127.0.0.1:8000/api/health/database
```

Expected response when PostgreSQL is reachable (`200 OK`):

```json
{"status": "healthy", "database": "connected"}
```

If the database is unavailable, the endpoint returns `503 Service
Unavailable`:

```json
{"detail": "Database is unavailable."}
```

### Upload a file

#### `POST /api/files/`

Accepted extensions: `.kml` and `.zip`. A ZIP must contain exactly one
Shapefile with `.shp`, `.shx`, and `.dbf` components. The default maximum
upload size is 50 MB.

Example KML upload:

```bash
curl -i -X POST \
  http://127.0.0.1:8000/api/files/ \
  -F "file=@data/test.kml"
```

Example successful response (`201 Created`):

```json
{
  "id": "0e8d0000-0000-4000-8000-000000000000",
  "filename": "test.kml",
  "file_type": ".kml",
  "file_size": 4821,
  "feature_count": 3,
  "crs": "EPSG:4326",
  "status": "COMPLETED",
  "error_message": null,
  "created_at": "2026-10-09T10:00:00Z",
  "updated_at": "2026-10-09T10:00:00Z"
}
```

The ID, byte size, and timestamps above are examples; use the values returned
by your request. The repository's local `data/test.kml` is git-ignored. Use
your own KML file or create a local fixture before running the example.

Common errors:

- `400 Bad Request`: unsupported extension or missing filename.
- `413 Content Too Large`: upload exceeds `MAX_FILE_SIZE_MB`.
- `422 Unprocessable Content`: malformed KML/ZIP or invalid Shapefile archive.

Example unsupported extension:

```bash
printf 'hello\n' > /tmp/test.txt
curl -i -X POST \
  http://127.0.0.1:8000/api/files/ \
  -F "file=@/tmp/test.txt"
```

Expected response (`400 Bad Request`):

```json
{
  "detail": "Unsupported file type '.txt'. Allowed types: .kml, .zip"
}
```

Example malformed ZIP:

```bash
printf 'not a zip\n' > /tmp/bad.zip
curl -i -X POST \
  http://127.0.0.1:8000/api/files/ \
  -F "file=@/tmp/bad.zip"
```

Expected response (`422 Unprocessable Content`):

```json
{"detail": "Uploaded ZIP file is invalid."}
```

### Retrieve file information

#### `GET /api/files/{file_id}/`

Replace `{file_id}` with the UUID returned by the upload endpoint.

```bash
curl -i \
  http://127.0.0.1:8000/api/files/0e8d0000-0000-4000-8000-000000000000/
```

Expected response (`200 OK`): the same file metadata fields as the upload
response. An unknown but valid UUID returns `404 Not Found`; a malformed UUID
returns `422 Unprocessable Content`.

### Retrieve measurements

#### `GET /api/files/{file_id}/measurements/`

```bash
curl -i \
  http://127.0.0.1:8000/api/files/0e8d0000-0000-4000-8000-000000000000/measurements/
```

Expected response (`200 OK`):

```json
{
  "file_id": "0e8d0000-0000-4000-8000-000000000000",
  "feature_count": 2,
  "measurements": [
    {
      "feature_id": "7b8e6a8f-3a40-4784-bbe2-83bc1b4b32bd",
      "feature_index": 0,
      "geometry_type": "Point",
      "measurement_type": null,
      "value": null,
      "unit": null,
      "source_crs": "EPSG:4326",
      "measurement_crs": "EPSG:32643",
      "message": "No measurement required for point geometry.",
      "properties": {"name": "Sample point"}
    },
    {
      "feature_id": "49c73fe9-a735-4a44-a944-3f149400c956",
      "feature_index": 1,
      "geometry_type": "Polygon",
      "measurement_type": "area",
      "value": "12345.678901",
      "unit": "m²",
      "source_crs": "EPSG:4326",
      "measurement_crs": "EPSG:32643",
      "message": null,
      "properties": {"name": "Sample polygon"}
    }
  ]
}
```

The example values are illustrative. Polygon and MultiPolygon features return
area; LineString and MultiLineString features return length. Point and
MultiPoint features have no measurement. Measurements are stored during
upload and this endpoint retrieves the stored values. A file that has not
completed processing returns `409 Conflict`; an unknown file ID returns
`404 Not Found`.

When a source CRS is missing, the calculator intentionally does not measure
the geometry: calculating area or length in unknown coordinate units would be
unsafe. Supply correct CRS metadata in the input data and upload it again to
get measurements. The API currently returns `null` measurement fields for
that case.

## Architecture

### Application structure

- `app/api/`: HTTP routers, request handling, and shared API dependencies.
- `app/core/`: configuration, SQLAlchemy database setup, and application
  exceptions.
- `app/geo/`: geospatial parser interfaces, normalized feature data, CRS
  selection, and measurement calculation.
- `app/models/`: SQLAlchemy models for uploaded files and their features.
- `app/schemas/`: Pydantic response schemas.
- `app/services/`: file persistence, lookup, and measurement-query logic.
- `app/utils/`: file extension validation and Shapefile ZIP validation.
- `alembic/`: database schema migrations.
- `tests/`: extension validation and HTTP API tests.

### File-processing flow

1. `POST /api/files/` validates the filename extension and streams the upload
   to a temporary file, enforcing the configured size limit.
2. For ZIP uploads, the archive utility checks its contents and extracts the
   single Shapefile. KML files go directly to their parser.
3. The parser reads features with GeoPandas and pyogrio, preserving each
   feature's geometry, properties, and detected source CRS.
4. The file service calculates measurements per feature, then stores file
   metadata and feature records in PostgreSQL.
5. The request returns the created file metadata. The staged upload is
   removed; extracted Shapefile contents currently remain under
   `data/extracted/`.

### Measurement and CRS flow

Measurements are calculated during upload, not when the measurements endpoint
is requested. For each geometry:

1. If the geometry is empty or its source CRS is missing, no measurement is
   produced.
2. If the source CRS is projected, it is reused.
3. If the source CRS is geographic (for example, EPSG:4326), the CRS service
   estimates a suitable UTM CRS for the geometry.
4. GeoPandas transforms the geometry into that projected CRS.
5. Shapely calculates polygon area or line length on projected coordinates.
6. The measurement value, unit, source CRS, and measurement CRS are stored
   alongside the feature.

This avoids treating latitude/longitude degrees as metres. The estimate is
designed for local/UTM-scale data; larger or unusual datasets may require
choosing a domain-appropriate projected CRS.

## Design decisions

- **Separate file parsing from measurement:** format-specific parsers extract
  feature data; CRS and measurement logic are separate, so parsing does not
  own measurement rules.
- **Use GeoPandas/pyogrio and Shapely:** these provide the file drivers,
  geometry normalization, coordinate transformation, and geometry operations
  needed by the current formats. Driver availability depends on the GDAL
  installation bundled with the environment.
- **Measure only in projected coordinates:** area and length in geographic
  degrees are not reported as physical measurements. Missing CRS is treated
  as an inability to measure rather than silently guessing.
- **Persist measurements at upload time:** retrieval is a database read and
  does not re-run geospatial calculations. If measurement rules change,
  existing records need to be reprocessed.
- **Store feature geometry and properties as PostgreSQL JSONB:** this keeps
  the original normalized feature data available without introducing a
  PostGIS dependency in this implementation. A PostGIS geometry column would
  be a better fit for spatial indexing and spatial queries at larger scale.
- **Use synchronous processing for this version:** it keeps the initial
  workflow straightforward and makes the upload response include the result.
  A background job queue would be more appropriate for large or slow uploads.
- **Limit supported uploads to KML and Shapefile ZIP:** supporting more
  formats requires additional validation, security checks, and driver tests.

## Learning and future scope

This project provided hands-on experience with FastAPI request/response
design, database migrations, geospatial parsing, feature/property
normalization, CRS selection, projected measurements, ZIP validation, and
HTTP-level testing.

Possible next steps:

- Add a dedicated test database and live PostgreSQL integration tests.
- Fix and validate missing or ambiguous source CRS before measurement, and
  persist per-feature measurement status/messages for accurate API reporting.
- Add robust archive safeguards (for example, compression-ratio and extracted
  size limits) and clean up extracted data according to a retention policy.
- Move large-file processing to background jobs and expose processing status.
- Adopt PostGIS for spatial data types, spatial indexes, and spatial queries.
- Add pagination for measurement results, authentication, structured logging,
  and deployment configuration.
- Add caching only after measuring read load and defining invalidation rules.

## Public repository

This project is hosted at
[github.com/harri8129/geospatial_measurment](https://github.com/harri8129/geospatial_measurment).
