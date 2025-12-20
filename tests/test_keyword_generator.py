"""Tests for keyword_generator module."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from photo_keyword_tagger.keyword_generator import _get_mime_type, generate_keywords


class TestGetMimeType:
    """Tests for _get_mime_type function."""

    def test_jpeg_extensions(self):
        """Test JPEG file extensions."""
        assert _get_mime_type(Path("image.jpg")) == "image/jpeg"
        assert _get_mime_type(Path("image.jpeg")) == "image/jpeg"
        assert _get_mime_type(Path("IMAGE.JPG")) == "image/jpeg"

    def test_png_extension(self):
        """Test PNG file extension."""
        assert _get_mime_type(Path("image.png")) == "image/png"

    def test_other_extensions(self):
        """Test other image extensions."""
        assert _get_mime_type(Path("image.gif")) == "image/gif"
        assert _get_mime_type(Path("image.webp")) == "image/webp"
        assert _get_mime_type(Path("image.bmp")) == "image/bmp"
        assert _get_mime_type(Path("image.tiff")) == "image/tiff"

    def test_unknown_extension(self):
        """Test unknown extension defaults to jpeg."""
        assert _get_mime_type(Path("image.xyz")) == "image/jpeg"


class TestGenerateKeywords:
    """Tests for generate_keywords function."""

    @pytest.fixture
    def mock_image_file(self, tmp_path):
        """Create a mock image file."""
        image_path = tmp_path / "test_image.jpg"
        image_path.write_bytes(b"fake image data")
        return image_path

    @pytest.fixture
    def mock_taxonomy_file(self, tmp_path):
        """Create a mock taxonomy file."""
        taxonomy_path = tmp_path / "taxonomy.txt"
        taxonomy_content = """nature
landscape
mountain
sunset
animal
dog
cat
"""
        taxonomy_path.write_text(taxonomy_content)
        return taxonomy_path

    def test_file_not_found_image(self):
        """Test FileNotFoundError when image doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Image file not found"):
            generate_keywords("nonexistent.jpg", "taxonomy.txt", api_key="fake_key")

    def test_file_not_found_taxonomy(self, mock_image_file):
        """Test FileNotFoundError when taxonomy doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Taxonomy file not found"):
            generate_keywords(mock_image_file, "nonexistent.txt", api_key="fake_key")

    def test_no_api_key(self, mock_image_file, mock_taxonomy_file):
        """Test ValueError when API key is not provided."""
        with (
            patch.dict("os.environ", {}, clear=True),
            pytest.raises(ValueError, match="API key must be provided"),
        ):
            generate_keywords(mock_image_file, mock_taxonomy_file)

    @patch("photo_keyword_tagger.keyword_generator.genai.Client")
    def test_successful_generation(self, mock_client_class, mock_image_file, mock_taxonomy_file):
        """Test successful keyword generation."""
        # Mock the Gemini API response
        mock_chunk = MagicMock()
        mock_chunk.text = json.dumps({"keywords": ["landscape", "mountain", "sunset"]})

        mock_client = MagicMock()
        mock_client.models.generate_content_stream.return_value = [mock_chunk]
        mock_client_class.return_value = mock_client

        # Call the function
        keywords = generate_keywords(
            mock_image_file,
            mock_taxonomy_file,
            api_key="test_api_key",
        )

        # Verify results
        assert keywords == ["landscape", "mountain", "sunset"]
        mock_client_class.assert_called_once_with(api_key="test_api_key")
        mock_client.models.generate_content_stream.assert_called_once()

    @patch("photo_keyword_tagger.keyword_generator.genai.Client")
    def test_api_key_from_environment(self, mock_client_class, mock_image_file, mock_taxonomy_file):
        """Test API key is read from environment variable."""
        mock_chunk = MagicMock()
        mock_chunk.text = json.dumps({"keywords": ["test"]})

        mock_client = MagicMock()
        mock_client.models.generate_content_stream.return_value = [mock_chunk]
        mock_client_class.return_value = mock_client

        with patch.dict("os.environ", {"GEMINI_API_KEY": "env_api_key"}):
            generate_keywords(mock_image_file, mock_taxonomy_file)

        mock_client_class.assert_called_once_with(api_key="env_api_key")

    @patch("photo_keyword_tagger.keyword_generator.genai.Client")
    def test_streaming_response(self, mock_client_class, mock_image_file, mock_taxonomy_file):
        """Test handling of streaming response chunks."""
        # Mock multiple chunks
        mock_chunk1 = MagicMock()
        mock_chunk1.text = '{"keywords": ['
        mock_chunk2 = MagicMock()
        mock_chunk2.text = '"nature", "landscape"'
        mock_chunk3 = MagicMock()
        mock_chunk3.text = "]}"

        mock_client = MagicMock()
        mock_client.models.generate_content_stream.return_value = [
            mock_chunk1,
            mock_chunk2,
            mock_chunk3,
        ]
        mock_client_class.return_value = mock_client

        keywords = generate_keywords(
            mock_image_file,
            mock_taxonomy_file,
            api_key="test_api_key",
        )

        assert keywords == ["nature", "landscape"]

    @patch("photo_keyword_tagger.keyword_generator.genai.Client")
    def test_invalid_json_response(self, mock_client_class, mock_image_file, mock_taxonomy_file):
        """Test error handling for invalid JSON response."""
        mock_chunk = MagicMock()
        mock_chunk.text = "invalid json"

        mock_client = MagicMock()
        mock_client.models.generate_content_stream.return_value = [mock_chunk]
        mock_client_class.return_value = mock_client

        with pytest.raises(ValueError, match="Failed to parse Gemini response"):
            generate_keywords(
                mock_image_file,
                mock_taxonomy_file,
                api_key="test_api_key",
            )

    @patch("photo_keyword_tagger.keyword_generator.genai.Client")
    def test_empty_keywords_list(self, mock_client_class, mock_image_file, mock_taxonomy_file):
        """Test handling of empty keywords list."""
        mock_chunk = MagicMock()
        mock_chunk.text = json.dumps({"keywords": []})

        mock_client = MagicMock()
        mock_client.models.generate_content_stream.return_value = [mock_chunk]
        mock_client_class.return_value = mock_client

        keywords = generate_keywords(
            mock_image_file,
            mock_taxonomy_file,
            api_key="test_api_key",
        )

        assert keywords == []
