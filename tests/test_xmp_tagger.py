"""Tests for XMP sidecar management and keyword tagging."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from photo_keyword_tagger.xmp_tagger import (
    XMPSidecarError,
    add_keywords_to_raw,
    add_keywords_to_xmp,
    batch_add_keywords,
    check_xmp_exists,
    ensure_xmp_sidecars,
    get_xmp_path,
)


def test_get_xmp_path():
    """Test getting XMP sidecar path from RAW file path."""
    raw_file = Path("/photos/2024/DSC00089.ARW")
    xmp_path = get_xmp_path(raw_file)

    assert xmp_path == Path("/photos/2024/DSC00089.xmp")
    assert xmp_path.stem == raw_file.stem
    assert xmp_path.parent == raw_file.parent


def test_get_xmp_path_different_extensions():
    """Test XMP path generation for different RAW extensions."""
    test_cases = [
        (Path("/photos/DSC00089.ARW"), Path("/photos/DSC00089.xmp")),
        (Path("/photos/DSC00089.arw"), Path("/photos/DSC00089.xmp")),
        (Path("/photos/IMG_1234.DNG"), Path("/photos/IMG_1234.xmp")),
        (Path("/photos/IMG_1234.dng"), Path("/photos/IMG_1234.xmp")),
    ]

    for raw_file, expected_xmp in test_cases:
        assert get_xmp_path(raw_file) == expected_xmp


def test_check_xmp_exists_true(tmp_path):
    """Test checking for existing XMP sidecar."""
    # Create a dummy RAW file and XMP sidecar
    raw_file = tmp_path / "DSC00089.ARW"
    xmp_file = tmp_path / "DSC00089.xmp"

    raw_file.touch()
    xmp_file.touch()

    assert check_xmp_exists(raw_file) is True


def test_check_xmp_exists_false(tmp_path):
    """Test checking for non-existent XMP sidecar."""
    raw_file = tmp_path / "DSC00089.ARW"
    raw_file.touch()

    assert check_xmp_exists(raw_file) is False


def test_ensure_xmp_sidecars_all_exist(tmp_path):
    """Test ensuring XMP sidecars when all exist."""
    raw_files = []
    for i in range(3):
        raw_file = tmp_path / f"DSC0008{i}.ARW"
        xmp_file = tmp_path / f"DSC0008{i}.xmp"
        raw_file.touch()
        xmp_file.touch()
        raw_files.append(raw_file)

    # Should return all files in with_xmp list
    with_xmp, without_xmp = ensure_xmp_sidecars(raw_files)
    assert len(with_xmp) == 3
    assert len(without_xmp) == 0
    assert set(with_xmp) == set(raw_files)


def test_ensure_xmp_sidecars_one_missing(tmp_path):
    """Test ensuring XMP sidecars when one is missing."""
    raw_files = []
    for i in range(3):
        raw_file = tmp_path / f"DSC0008{i}.ARW"
        raw_file.touch()
        raw_files.append(raw_file)

        # Only create XMP for first two files
        if i < 2:
            xmp_file = tmp_path / f"DSC0008{i}.xmp"
            xmp_file.touch()

    # Should return separate lists
    with_xmp, without_xmp = ensure_xmp_sidecars(raw_files)
    assert len(with_xmp) == 2
    assert len(without_xmp) == 1
    assert without_xmp[0] == raw_files[2]


def test_ensure_xmp_sidecars_multiple_missing(tmp_path):
    """Test ensuring XMP sidecars when multiple are missing."""
    raw_files = []
    for i in range(3):
        raw_file = tmp_path / f"DSC0008{i}.ARW"
        raw_file.touch()
        raw_files.append(raw_file)

    # Don't create any XMP files
    with_xmp, without_xmp = ensure_xmp_sidecars(raw_files)
    assert len(with_xmp) == 0
    assert len(without_xmp) == 3
    assert set(without_xmp) == set(raw_files)


def test_ensure_xmp_sidecars_empty_list():
    """Test ensuring XMP sidecars with empty list."""
    # Should return two empty lists
    with_xmp, without_xmp = ensure_xmp_sidecars([])
    assert len(with_xmp) == 0
    assert len(without_xmp) == 0


@patch("subprocess.run")
def test_add_keywords_to_xmp_success(mock_run, tmp_path):
    """Test adding keywords to XMP file."""
    xmp_file = tmp_path / "DSC00089.xmp"
    xmp_file.touch()

    # Mock successful exiftool execution
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

    keywords = ["landscape", "sunset", "nature"]
    add_keywords_to_xmp(xmp_file, keywords)

    # Verify exiftool was called with correct arguments
    mock_run.assert_called_once()
    call_args = mock_run.call_args
    cmd = call_args[0][0]

    assert cmd[0] == "exiftool"
    assert "-overwrite_original" in cmd
    # Each keyword should be added as a separate argument
    assert "-XMP-dc:Subject+=landscape" in cmd
    assert "-XMP-dc:Subject+=sunset" in cmd
    assert "-XMP-dc:Subject+=nature" in cmd
    assert str(xmp_file) in cmd

    # Verify check=True was used
    assert call_args[1]["check"] is True


@patch("subprocess.run")
def test_add_keywords_to_xmp_custom_exiftool_path(mock_run, tmp_path):
    """Test adding keywords with custom exiftool path."""
    xmp_file = tmp_path / "DSC00089.xmp"
    xmp_file.touch()

    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

    keywords = ["test"]
    custom_path = "/usr/local/bin/exiftool"
    add_keywords_to_xmp(xmp_file, keywords, exiftool_path=custom_path)

    call_args = mock_run.call_args
    cmd = call_args[0][0]
    assert cmd[0] == custom_path


@patch("subprocess.run")
def test_add_keywords_to_xmp_empty_keywords(mock_run, tmp_path):
    """Test adding empty keyword list (should do nothing)."""
    xmp_file = tmp_path / "DSC00089.xmp"
    xmp_file.touch()

    add_keywords_to_xmp(xmp_file, [])

    # Should not call exiftool
    mock_run.assert_not_called()


def test_add_keywords_to_xmp_missing_file(tmp_path):
    """Test adding keywords to non-existent XMP file."""
    xmp_file = tmp_path / "nonexistent.xmp"
    keywords = ["test"]

    with pytest.raises(FileNotFoundError) as exc_info:
        add_keywords_to_xmp(xmp_file, keywords)

    assert str(xmp_file) in str(exc_info.value)


@patch("subprocess.run")
def test_add_keywords_to_xmp_exiftool_failure(mock_run, tmp_path):
    """Test handling exiftool execution failure."""
    xmp_file = tmp_path / "DSC00089.xmp"
    xmp_file.touch()

    # Mock exiftool failure
    mock_run.side_effect = subprocess.CalledProcessError(
        returncode=1, cmd=["exiftool"], output="Error", stderr="Exiftool error"
    )

    keywords = ["test"]

    with pytest.raises(subprocess.CalledProcessError):
        add_keywords_to_xmp(xmp_file, keywords)


@patch("subprocess.run")
def test_add_keywords_to_raw_success(mock_run, tmp_path):
    """Test adding keywords to RAW file via XMP sidecar."""
    raw_file = tmp_path / "DSC00089.ARW"
    xmp_file = tmp_path / "DSC00089.xmp"
    raw_file.touch()
    xmp_file.touch()

    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

    keywords = ["landscape", "nature"]
    add_keywords_to_raw(raw_file, keywords)

    # Verify exiftool was called
    mock_run.assert_called_once()
    call_args = mock_run.call_args
    cmd = call_args[0][0]

    # Each keyword should be added as a separate argument
    assert "-XMP-dc:Subject+=landscape" in cmd
    assert "-XMP-dc:Subject+=nature" in cmd
    assert str(xmp_file) in cmd


def test_add_keywords_to_raw_missing_xmp(tmp_path):
    """Test adding keywords to RAW file without XMP sidecar."""
    raw_file = tmp_path / "DSC00089.ARW"
    raw_file.touch()

    keywords = ["test"]

    with pytest.raises(XMPSidecarError) as exc_info:
        add_keywords_to_raw(raw_file, keywords)

    assert "Missing XMP sidecar" in str(exc_info.value)


def test_add_keywords_to_raw_missing_raw_file(tmp_path):
    """Test adding keywords to non-existent RAW file."""
    raw_file = tmp_path / "nonexistent.ARW"
    keywords = ["test"]

    with pytest.raises(FileNotFoundError) as exc_info:
        add_keywords_to_raw(raw_file, keywords)

    assert str(raw_file) in str(exc_info.value)


@patch("subprocess.run")
def test_batch_add_keywords_success(mock_run, tmp_path):
    """Test batch adding keywords to multiple RAW files."""
    # Create test files
    raw_files_keywords = {}
    for i in range(3):
        raw_file = tmp_path / f"DSC0008{i}.ARW"
        xmp_file = tmp_path / f"DSC0008{i}.xmp"
        raw_file.touch()
        xmp_file.touch()
        raw_files_keywords[raw_file] = [f"keyword{i}", "common"]

    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

    batch_add_keywords(raw_files_keywords)

    # Should call exiftool 3 times (once per file)
    assert mock_run.call_count == 3


@patch("subprocess.run")
def test_batch_add_keywords_one_missing_xmp(mock_run, tmp_path):
    """Test batch operation skips files with missing XMP."""
    # Create files with one missing XMP
    raw_files_keywords = {}
    for i in range(3):
        raw_file = tmp_path / f"DSC0008{i}.ARW"
        raw_file.touch()
        raw_files_keywords[raw_file] = [f"keyword{i}"]

        # Only create XMP for first two files
        if i < 2:
            xmp_file = tmp_path / f"DSC0008{i}.xmp"
            xmp_file.touch()

    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

    # Should process only files with XMP
    batch_add_keywords(raw_files_keywords)

    # Should call exiftool only for the 2 files with XMP
    assert mock_run.call_count == 2


@patch("subprocess.run")
def test_batch_add_keywords_empty_keywords(mock_run, tmp_path):
    """Test batch operation skips files with empty keyword lists."""
    raw_files_keywords = {}
    for i in range(3):
        raw_file = tmp_path / f"DSC0008{i}.ARW"
        xmp_file = tmp_path / f"DSC0008{i}.xmp"
        raw_file.touch()
        xmp_file.touch()

        # Only first file has keywords
        if i == 0:
            raw_files_keywords[raw_file] = ["keyword"]
        else:
            raw_files_keywords[raw_file] = []

    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

    batch_add_keywords(raw_files_keywords)

    # Should only call exiftool once (for the file with keywords)
    assert mock_run.call_count == 1


@patch("subprocess.run")
def test_batch_add_keywords_empty_dict(mock_run):
    """Test batch operation with empty dictionary."""
    batch_add_keywords({})

    # Should not call exiftool
    mock_run.assert_not_called()


def test_batch_add_keywords_missing_raw_file(tmp_path):
    """Test batch operation with non-existent RAW file."""
    raw_file = tmp_path / "nonexistent.ARW"
    raw_files_keywords = {raw_file: ["keyword"]}

    with pytest.raises(FileNotFoundError):
        batch_add_keywords(raw_files_keywords)
