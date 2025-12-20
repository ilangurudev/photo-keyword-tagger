"""Utilities for finding source RAW image files."""

from pathlib import Path


def find_raw_file(
    jpeg_path: str | Path,
    base_path: str | Path,
    extensions: list[str] | None = None,
) -> Path | None:
    """
    Find the source RAW file (ARW/DNG) given a JPEG file path.

    Args:
        jpeg_path: Path to the JPEG file (e.g., "/path/to/DSC00089.jpg")
        base_path: Base directory to search for RAW files
        extensions: List of raw file extensions to search for (default: [".arw", ".dng", ".ARW", ".DNG"])

    Returns:
        Path to the RAW file if found, None otherwise

    Example:
        >>> raw_file = find_raw_file("/path/to/exports/DSC00089.jpg", "/Volumes/T7/Pictures")
        >>> print(raw_file)
        /Volumes/T7/Pictures/2024/January/DSC00089.ARW
    """
    if extensions is None:
        extensions = [".arw", ".dng", ".ARW", ".DNG"]

    jpeg_path = Path(jpeg_path)
    base_path = Path(base_path)

    if not base_path.exists():
        raise FileNotFoundError(f"Base path does not exist: {base_path}")

    # Extract stem from JPEG path
    jpeg_stem = jpeg_path.stem

    # Search recursively for files with the given stem and any of the extensions
    for ext in extensions:
        pattern = f"**/{jpeg_stem}{ext}"
        matches = list(base_path.glob(pattern))
        if matches:
            return matches[0]  # Return first match

    return None


def find_raw_files(
    jpeg_paths: list[str | Path],
    base_path: str | Path,
    extensions: list[str] | None = None,
) -> dict[Path, Path | None]:
    """
    Find RAW files for multiple JPEG file paths in batch.

    Args:
        jpeg_paths: List of JPEG file paths
        base_path: Base directory to search for RAW files
        extensions: List of raw file extensions to search for (default: [".arw", ".dng", ".ARW", ".DNG"])

    Returns:
        Dictionary mapping JPEG path to RAW file path (None if not found)

    Example:
        >>> jpeg_files = [
        ...     "/Volumes/T7/Pictures/Lightroom Saved Photos/DSC00089.jpg",
        ...     "/Volumes/T7/Pictures/Lightroom Saved Photos/DSC00090.jpg",
        ... ]
        >>> results = find_raw_files(jpeg_files, "/Volumes/T7/Pictures")
        >>> for jpeg_path, raw_path in results.items():
        ...     if raw_path:
        ...         print(f"{jpeg_path.name} -> {raw_path}")
        ...     else:
        ...         print(f"{jpeg_path.name} -> NOT FOUND")
    """
    results = {}
    for jpeg_path in jpeg_paths:
        jpeg_path = Path(jpeg_path)
        raw_file = find_raw_file(jpeg_path, base_path, extensions)
        results[jpeg_path] = raw_file

    return results
