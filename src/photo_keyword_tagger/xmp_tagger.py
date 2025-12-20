"""XMP sidecar management and keyword tagging using exiftool."""

import subprocess
from pathlib import Path


class XMPSidecarError(Exception):
    """Raised when XMP sidecar file operations fail."""

    pass


def get_xmp_path(raw_file: Path) -> Path:
    """
    Get the expected path for an XMP sidecar file.

    Args:
        raw_file: Path to the RAW image file

    Returns:
        Path to the corresponding XMP sidecar file

    Example:
        >>> raw_file = Path("/photos/DSC00089.ARW")
        >>> xmp_path = get_xmp_path(raw_file)
        >>> print(xmp_path)
        /photos/DSC00089.xmp
    """
    return raw_file.parent / f"{raw_file.stem}.xmp"


def check_xmp_exists(raw_file: Path) -> bool:
    """
    Check if an XMP sidecar file exists for a RAW file.

    Args:
        raw_file: Path to the RAW image file

    Returns:
        True if XMP sidecar exists, False otherwise

    Example:
        >>> raw_file = Path("/photos/DSC00089.ARW")
        >>> if check_xmp_exists(raw_file):
        ...     print("XMP sidecar found")
    """
    xmp_path = get_xmp_path(raw_file)
    return xmp_path.exists()


def ensure_xmp_sidecars(raw_files: list[Path]) -> tuple[list[Path], list[Path]]:
    """
    Check which RAW files have corresponding XMP sidecar files.

    This function checks that every RAW file in the list has a separate
    XMP sidecar file and separates them into two lists.

    Args:
        raw_files: List of RAW file paths to check

    Returns:
        Tuple of (files_with_xmp, files_without_xmp)

    Example:
        >>> raw_files = [
        ...     Path("/photos/DSC00089.ARW"),
        ...     Path("/photos/DSC00090.ARW"),
        ... ]
        >>> with_xmp, without_xmp = ensure_xmp_sidecars(raw_files)
    """
    files_with_xmp = []
    files_without_xmp = []

    for raw_file in raw_files:
        if check_xmp_exists(raw_file):
            files_with_xmp.append(raw_file)
        else:
            files_without_xmp.append(raw_file)

    return files_with_xmp, files_without_xmp


def add_keywords_to_xmp(
    xmp_file: Path,
    keywords: list[str],
    exiftool_path: str = "exiftool",
) -> None:
    """
    Add keywords to an XMP sidecar file using exiftool.

    This function appends keywords to the existing keywords in the XMP file
    using exiftool's -XMP-dc:Subject+= syntax. The -overwrite_original flag
    is used to prevent creation of backup files.

    Args:
        xmp_file: Path to the XMP sidecar file
        keywords: List of keywords to add
        exiftool_path: Path to exiftool binary (default: "exiftool")

    Raises:
        FileNotFoundError: If XMP file doesn't exist
        subprocess.CalledProcessError: If exiftool command fails

    Example:
        >>> xmp_file = Path("/photos/DSC00089.xmp")
        >>> keywords = ["landscape", "sunset", "nature"]
        >>> add_keywords_to_xmp(xmp_file, keywords)
    """
    if not xmp_file.exists():
        raise FileNotFoundError(f"XMP file not found: {xmp_file}")

    if not keywords:
        return  # Nothing to do

    # Build exiftool command
    # -overwrite_original prevents creation of .xmp_original backup files
    # Add each keyword separately using multiple -XMP-dc:Subject+= arguments
    cmd = [
        exiftool_path,
        "-overwrite_original",
    ]

    # Add each keyword as a separate argument
    for keyword in keywords:
        cmd.append(f"-XMP-dc:Subject+={keyword}")

    # Add the file path at the end
    cmd.append(str(xmp_file))

    # Execute exiftool
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
    )

    # Check if exiftool reported success
    if result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode,
            cmd,
            result.stdout,
            result.stderr,
        )


def add_keywords_to_raw(
    raw_file: Path,
    keywords: list[str],
    exiftool_path: str = "exiftool",
) -> None:
    """
    Add keywords to a RAW file via its XMP sidecar.

    This is a convenience function that finds the XMP sidecar for a RAW file
    and adds keywords to it.

    Args:
        raw_file: Path to the RAW image file
        keywords: List of keywords to add
        exiftool_path: Path to exiftool binary (default: "exiftool")

    Raises:
        FileNotFoundError: If RAW or XMP file doesn't exist
        XMPSidecarError: If XMP sidecar doesn't exist
        subprocess.CalledProcessError: If exiftool command fails

    Example:
        >>> raw_file = Path("/photos/DSC00089.ARW")
        >>> keywords = ["landscape", "sunset", "nature"]
        >>> add_keywords_to_raw(raw_file, keywords)
    """
    if not raw_file.exists():
        raise FileNotFoundError(f"RAW file not found: {raw_file}")

    # Check if XMP sidecar exists
    _files_with_xmp, files_without_xmp = ensure_xmp_sidecars([raw_file])
    if files_without_xmp:
        raise XMPSidecarError(
            f"Missing XMP sidecar file for {raw_file}\n" f"Expected: {get_xmp_path(raw_file)}"
        )

    # Get XMP path and add keywords
    xmp_file = get_xmp_path(raw_file)
    add_keywords_to_xmp(xmp_file, keywords, exiftool_path)


def batch_add_keywords(
    raw_files_keywords: dict[Path, list[str]],
    exiftool_path: str = "exiftool",
) -> None:
    """
    Add keywords to multiple RAW files in batch.

    This function only processes files that have XMP sidecars. Files without
    XMP sidecars are skipped silently (the caller should warn about them).

    Args:
        raw_files_keywords: Dictionary mapping RAW file paths to their keywords
        exiftool_path: Path to exiftool binary (default: "exiftool")

    Raises:
        FileNotFoundError: If any RAW file doesn't exist
        subprocess.CalledProcessError: If exiftool command fails

    Example:
        >>> files_kw = {
        ...     Path("/photos/DSC00089.ARW"): ["landscape", "sunset"],
        ...     Path("/photos/DSC00090.ARW"): ["portrait", "indoor"],
        ... }
        >>> batch_add_keywords(files_kw)
    """
    raw_files = list(raw_files_keywords.keys())

    # Check all files exist
    for raw_file in raw_files:
        if not raw_file.exists():
            raise FileNotFoundError(f"RAW file not found: {raw_file}")

    # Check which files have XMP sidecars
    files_with_xmp, _ = ensure_xmp_sidecars(raw_files)

    # Only add keywords to files that have XMP sidecars
    for raw_file, keywords in raw_files_keywords.items():
        if raw_file in files_with_xmp and keywords:
            xmp_file = get_xmp_path(raw_file)
            add_keywords_to_xmp(xmp_file, keywords, exiftool_path)
