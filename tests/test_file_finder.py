"""Tests for file_finder module."""

import tempfile
from pathlib import Path

import pytest

from photo_keyword_tagger.file_finder import find_raw_file, find_raw_files


@pytest.fixture
def temp_photo_structure():
    """Create a temporary directory structure with sample photos."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)

        # Create directory structure
        jan_2024 = base / "2024" / "January"
        feb_2024 = base / "2024" / "February"
        exports = base / "exports"

        jan_2024.mkdir(parents=True)
        feb_2024.mkdir(parents=True)
        exports.mkdir(parents=True)

        # Create sample RAW files
        (jan_2024 / "DSC00089.ARW").touch()
        (jan_2024 / "DSC00090.arw").touch()  # lowercase
        (feb_2024 / "IMG_1234.DNG").touch()

        # Create sample JPEG files
        (exports / "DSC00089.jpg").touch()
        (exports / "DSC00090.jpg").touch()
        (exports / "IMG_1234.jpg").touch()
        (exports / "NOTFOUND.jpg").touch()

        yield base


def test_find_raw_file_found(temp_photo_structure):
    """Test finding a RAW file that exists."""
    jpeg_path = temp_photo_structure / "exports" / "DSC00089.jpg"
    result = find_raw_file(jpeg_path, temp_photo_structure)

    assert result is not None
    assert result.name == "DSC00089.ARW"
    assert result.exists()


def test_find_raw_file_case_insensitive(temp_photo_structure):
    """Test finding RAW files with different case extensions."""
    jpeg_path = temp_photo_structure / "exports" / "DSC00090.jpg"
    result = find_raw_file(jpeg_path, temp_photo_structure)

    assert result is not None
    assert result.name == "DSC00090.arw"
    assert result.exists()


def test_find_raw_file_dng(temp_photo_structure):
    """Test finding DNG files."""
    jpeg_path = temp_photo_structure / "exports" / "IMG_1234.jpg"
    result = find_raw_file(jpeg_path, temp_photo_structure)

    assert result is not None
    assert result.name == "IMG_1234.DNG"
    assert result.exists()


def test_find_raw_file_not_found(temp_photo_structure):
    """Test when RAW file doesn't exist."""
    jpeg_path = temp_photo_structure / "exports" / "NONEXISTENT.jpg"
    result = find_raw_file(jpeg_path, temp_photo_structure)

    assert result is None


def test_find_raw_file_custom_extensions(temp_photo_structure):
    """Test with custom file extensions."""
    jpeg_path = temp_photo_structure / "exports" / "DSC00089.jpg"
    result = find_raw_file(jpeg_path, temp_photo_structure, extensions=[".DNG"])

    assert result is None  # Should not find ARW when only looking for DNG


def test_find_raw_file_string_path(temp_photo_structure):
    """Test that string paths work."""
    jpeg_path = str(temp_photo_structure / "exports" / "DSC00089.jpg")
    result = find_raw_file(jpeg_path, str(temp_photo_structure))

    assert result is not None
    assert result.name == "DSC00089.ARW"


def test_find_raw_files_batch(temp_photo_structure):
    """Test batch finding of RAW files."""
    jpeg_paths = [
        temp_photo_structure / "exports" / "DSC00089.jpg",
        temp_photo_structure / "exports" / "DSC00090.jpg",
        temp_photo_structure / "exports" / "IMG_1234.jpg",
        temp_photo_structure / "exports" / "NOTFOUND.jpg",
    ]

    results = find_raw_files(jpeg_paths, temp_photo_structure)

    assert len(results) == 4

    # Check successful matches
    jpeg1 = temp_photo_structure / "exports" / "DSC00089.jpg"
    assert results[jpeg1] is not None
    assert results[jpeg1].name == "DSC00089.ARW"

    jpeg2 = temp_photo_structure / "exports" / "DSC00090.jpg"
    assert results[jpeg2] is not None
    assert results[jpeg2].name == "DSC00090.arw"

    jpeg3 = temp_photo_structure / "exports" / "IMG_1234.jpg"
    assert results[jpeg3] is not None
    assert results[jpeg3].name == "IMG_1234.DNG"

    # Check not found
    jpeg4 = temp_photo_structure / "exports" / "NOTFOUND.jpg"
    assert results[jpeg4] is None


def test_find_raw_files_empty_list(temp_photo_structure):
    """Test with empty list of JPEGs."""
    results = find_raw_files([], temp_photo_structure)
    assert len(results) == 0


def test_find_raw_files_custom_extensions(temp_photo_structure):
    """Test batch with custom extensions."""
    jpeg_paths = [
        temp_photo_structure / "exports" / "DSC00089.jpg",
        temp_photo_structure / "exports" / "IMG_1234.jpg",
    ]

    # Search only for DNG
    results = find_raw_files(jpeg_paths, temp_photo_structure, extensions=[".DNG"])

    assert len(results) == 2
    assert results[jpeg_paths[0]] is None  # ARW not found
    assert results[jpeg_paths[1]] is not None  # DNG found
    assert results[jpeg_paths[1]].name == "IMG_1234.DNG"


def test_invalid_base_path():
    """Test with non-existent base path."""
    jpeg_path = Path("/some/path/DSC00089.jpg")

    with pytest.raises(FileNotFoundError):
        find_raw_file(jpeg_path, "/this/path/does/not/exist")


def test_find_raw_files_invalid_base_path():
    """Test batch with non-existent base path."""
    jpeg_paths = [Path("/some/path/DSC00089.jpg")]

    with pytest.raises(FileNotFoundError):
        find_raw_files(jpeg_paths, "/this/path/does/not/exist")
