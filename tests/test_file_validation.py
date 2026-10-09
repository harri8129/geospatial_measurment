import pytest

from app.core.exceptions import UnsupportedFileTypeError
from app.utils.file_utils import validate_extension


def test_kml_extension():
    assert validate_extension("survey.kml") == ".kml"


def test_zip_extension():
    assert validate_extension("survey.zip") == ".zip"


def test_invalid_extension():
    with pytest.raises(UnsupportedFileTypeError):
        validate_extension("survey.pdf")
