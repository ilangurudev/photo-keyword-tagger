"""Photo Keyword Tagger - Automated keyword generation for Lightroom catalogues."""

from photo_keyword_tagger.file_finder import find_raw_file, find_raw_files
from photo_keyword_tagger.keyword_generator import generate_keywords
from photo_keyword_tagger.pipeline import PipelineError, process_directory
from photo_keyword_tagger.xmp_tagger import (
    XMPSidecarError,
    add_keywords_to_raw,
    add_keywords_to_xmp,
    batch_add_keywords,
    check_xmp_exists,
    ensure_xmp_sidecars,
    get_xmp_path,
)

__all__ = [
    "PipelineError",
    "XMPSidecarError",
    "add_keywords_to_raw",
    "add_keywords_to_xmp",
    "batch_add_keywords",
    "check_xmp_exists",
    "ensure_xmp_sidecars",
    "find_raw_file",
    "find_raw_files",
    "generate_keywords",
    "get_xmp_path",
    "process_directory",
]


def hello() -> str:
    return "Hello from photo-keyword-tagger!"
