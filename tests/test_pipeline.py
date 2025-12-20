"""Tests for the pipeline module."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from photo_keyword_tagger.pipeline import PipelineError, process_directory


def test_process_directory_validates_jpeg_dir():
    """Test that process_directory validates the JPEG directory exists."""
    with pytest.raises(FileNotFoundError, match="JPEG directory not found"):
        process_directory(
            jpeg_dir="/nonexistent/path",
            raw_search_path="/some/path",
            taxonomy_path="/some/taxonomy.txt",
        )


def test_process_directory_validates_raw_search_path():
    """Test that process_directory validates the RAW search path exists."""
    with (
        tempfile.TemporaryDirectory() as tmpdir,
        pytest.raises(FileNotFoundError, match="RAW search path not found"),
    ):
        process_directory(
            jpeg_dir=tmpdir,
            raw_search_path="/nonexistent/path",
            taxonomy_path="/some/taxonomy.txt",
        )


def test_process_directory_validates_taxonomy_path():
    """Test that process_directory validates the taxonomy file exists."""
    with (
        tempfile.TemporaryDirectory() as tmpdir1,
        tempfile.TemporaryDirectory() as tmpdir2,
        pytest.raises(FileNotFoundError, match="Taxonomy file not found"),
    ):
        process_directory(
            jpeg_dir=tmpdir1,
            raw_search_path=tmpdir2,
            taxonomy_path="/nonexistent/taxonomy.txt",
        )


def test_process_directory_raises_on_no_jpegs():
    """Test that process_directory raises an error when no JPEG files are found."""
    with tempfile.TemporaryDirectory() as jpeg_dir, tempfile.TemporaryDirectory() as raw_dir:
        # Create a taxonomy file
        taxonomy_file = Path(jpeg_dir) / "taxonomy.txt"
        taxonomy_file.write_text("Category1\n  keyword1\n  keyword2\n")

        with pytest.raises(PipelineError, match="No JPEG files found"):
            process_directory(
                jpeg_dir=jpeg_dir,
                raw_search_path=raw_dir,
                taxonomy_path=taxonomy_file,
            )


def test_process_directory_raises_when_no_raw_files_found():
    """Test that process_directory raises an error when NO RAW files are found at all."""
    with tempfile.TemporaryDirectory() as jpeg_dir, tempfile.TemporaryDirectory() as raw_dir:
        # Create a JPEG file
        jpeg_file = Path(jpeg_dir) / "test.jpg"
        jpeg_file.write_bytes(b"fake jpeg data")

        # Create a taxonomy file
        taxonomy_file = Path(jpeg_dir) / "taxonomy.txt"
        taxonomy_file.write_text("Category1\n  keyword1\n  keyword2\n")

        with pytest.raises(PipelineError, match="No RAW files found for any JPEG files"):
            process_directory(
                jpeg_dir=jpeg_dir,
                raw_search_path=raw_dir,
                taxonomy_path=taxonomy_file,
            )


@patch("photo_keyword_tagger.pipeline.find_raw_file")
@patch("photo_keyword_tagger.pipeline.ensure_xmp_sidecars")
def test_process_directory_raises_when_no_xmp_files(mock_ensure_xmp, mock_find_raw_file):
    """Test that process_directory raises an error when no files have XMP sidecars."""
    with tempfile.TemporaryDirectory() as jpeg_dir, tempfile.TemporaryDirectory() as raw_dir:
        # Create a JPEG file
        jpeg_file = Path(jpeg_dir) / "test.jpg"
        jpeg_file.write_bytes(b"fake jpeg data")

        # Create a taxonomy file
        taxonomy_file = Path(jpeg_dir) / "taxonomy.txt"
        taxonomy_file.write_text("Category1\n  keyword1\n  keyword2\n")

        # Mock find_raw_file to return a fake RAW file path
        mock_raw_file = Path(raw_dir) / "test.ARW"
        mock_find_raw_file.return_value = mock_raw_file

        # Mock ensure_xmp_sidecars to return no files with XMP
        mock_ensure_xmp.return_value = ([], [mock_raw_file])

        with pytest.raises(PipelineError, match="No files with XMP sidecars found"):
            process_directory(
                jpeg_dir=jpeg_dir,
                raw_search_path=raw_dir,
                taxonomy_path=taxonomy_file,
            )


@patch("photo_keyword_tagger.pipeline.find_raw_file")
@patch("photo_keyword_tagger.pipeline.ensure_xmp_sidecars")
@patch("photo_keyword_tagger.pipeline.generate_keywords")
@patch("photo_keyword_tagger.pipeline.batch_add_keywords")
def test_process_directory_success(
    mock_batch_add, mock_generate, mock_ensure_xmp, mock_find_raw_file
):
    """Test that process_directory successfully processes files."""
    with tempfile.TemporaryDirectory() as jpeg_dir, tempfile.TemporaryDirectory() as raw_dir:
        # Create a JPEG file
        jpeg_file = Path(jpeg_dir) / "test.jpg"
        jpeg_file.write_bytes(b"fake jpeg data")

        # Create a taxonomy file
        taxonomy_file = Path(jpeg_dir) / "taxonomy.txt"
        taxonomy_file.write_text("Category1\n  keyword1\n  keyword2\n")

        # Mock find_raw_file to return a fake RAW file path
        mock_raw_file = Path(raw_dir) / "test.ARW"
        mock_find_raw_file.return_value = mock_raw_file

        # Mock ensure_xmp_sidecars to return the file with XMP
        mock_ensure_xmp.return_value = ([mock_raw_file], [])

        # Mock generate_keywords to return fake keywords
        mock_generate.return_value = ["keyword1", "keyword2"]

        # Mock batch_add_keywords to pass
        mock_batch_add.return_value = None

        # Process directory
        results = process_directory(
            jpeg_dir=jpeg_dir,
            raw_search_path=raw_dir,
            taxonomy_path=taxonomy_file,
            api_key="fake-api-key",
        )

        # Verify results
        assert len(results) == 1
        assert mock_raw_file in results
        assert results[mock_raw_file] == ["keyword1", "keyword2"]

        # Verify mocks were called correctly
        mock_find_raw_file.assert_called_once()
        mock_ensure_xmp.assert_called_once()
        mock_generate.assert_called_once()
        mock_batch_add.assert_called_once()


@patch("photo_keyword_tagger.pipeline.find_raw_file")
@patch("photo_keyword_tagger.pipeline.ensure_xmp_sidecars")
@patch("photo_keyword_tagger.pipeline.generate_keywords")
@patch("photo_keyword_tagger.pipeline.batch_add_keywords")
def test_process_directory_skips_files_without_raw(
    mock_batch_add, mock_generate, mock_ensure_xmp, mock_find_raw_file
):
    """Test that process_directory skips files when RAW files are not found."""
    with tempfile.TemporaryDirectory() as jpeg_dir, tempfile.TemporaryDirectory() as raw_dir:
        # Create two JPEG files
        jpeg_file1 = Path(jpeg_dir) / "test1.jpg"
        jpeg_file1.write_bytes(b"fake jpeg data 1")
        jpeg_file2 = Path(jpeg_dir) / "test2.jpg"
        jpeg_file2.write_bytes(b"fake jpeg data 2")

        # Create a taxonomy file
        taxonomy_file = Path(jpeg_dir) / "taxonomy.txt"
        taxonomy_file.write_text("Category1\n  keyword1\n  keyword2\n")

        # Mock find_raw_file: only first file has RAW, second returns None
        mock_raw_file1 = Path(raw_dir) / "test1.ARW"
        mock_find_raw_file.side_effect = [mock_raw_file1, None]

        # Mock ensure_xmp_sidecars: the file that has RAW also has XMP
        mock_ensure_xmp.return_value = ([mock_raw_file1], [])

        # Mock generate_keywords to return fake keywords
        mock_generate.return_value = ["keyword1", "keyword2"]

        # Mock batch_add_keywords to pass
        mock_batch_add.return_value = None

        # Process directory - should succeed and skip the file without RAW
        results = process_directory(
            jpeg_dir=jpeg_dir,
            raw_search_path=raw_dir,
            taxonomy_path=taxonomy_file,
            api_key="fake-api-key",
        )

        # Verify results - only file with RAW should be processed
        assert len(results) == 1
        assert mock_raw_file1 in results
        assert results[mock_raw_file1] == ["keyword1", "keyword2"]

        # Verify generate_keywords was only called once (for file with RAW)
        assert mock_generate.call_count == 1


@patch("photo_keyword_tagger.pipeline.find_raw_file")
@patch("photo_keyword_tagger.pipeline.ensure_xmp_sidecars")
@patch("photo_keyword_tagger.pipeline.generate_keywords")
@patch("photo_keyword_tagger.pipeline.batch_add_keywords")
def test_process_directory_skips_files_without_xmp(
    mock_batch_add, mock_generate, mock_ensure_xmp, mock_find_raw_file
):
    """Test that process_directory skips files without XMP sidecars."""
    with tempfile.TemporaryDirectory() as jpeg_dir, tempfile.TemporaryDirectory() as raw_dir:
        # Create two JPEG files
        jpeg_file1 = Path(jpeg_dir) / "test1.jpg"
        jpeg_file1.write_bytes(b"fake jpeg data 1")
        jpeg_file2 = Path(jpeg_dir) / "test2.jpg"
        jpeg_file2.write_bytes(b"fake jpeg data 2")

        # Create a taxonomy file
        taxonomy_file = Path(jpeg_dir) / "taxonomy.txt"
        taxonomy_file.write_text("Category1\n  keyword1\n  keyword2\n")

        # Mock find_raw_file to return different RAW files
        mock_raw_file1 = Path(raw_dir) / "test1.ARW"
        mock_raw_file2 = Path(raw_dir) / "test2.ARW"
        mock_find_raw_file.side_effect = [mock_raw_file1, mock_raw_file2]

        # Mock ensure_xmp_sidecars: only first file has XMP
        mock_ensure_xmp.return_value = ([mock_raw_file1], [mock_raw_file2])

        # Mock generate_keywords to return fake keywords
        mock_generate.return_value = ["keyword1", "keyword2"]

        # Mock batch_add_keywords to pass
        mock_batch_add.return_value = None

        # Process directory
        results = process_directory(
            jpeg_dir=jpeg_dir,
            raw_search_path=raw_dir,
            taxonomy_path=taxonomy_file,
            api_key="fake-api-key",
        )

        # Verify results - only file with XMP should be processed
        assert len(results) == 1
        assert mock_raw_file1 in results
        assert mock_raw_file2 not in results
        assert results[mock_raw_file1] == ["keyword1", "keyword2"]

        # Verify generate_keywords was only called once (for file with XMP)
        assert mock_generate.call_count == 1
