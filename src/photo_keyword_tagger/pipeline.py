"""Pipeline for automated keyword tagging of RAW images."""

from pathlib import Path

from tqdm import tqdm

from .file_finder import find_raw_file
from .keyword_generator import generate_keywords
from .xmp_tagger import batch_add_keywords, ensure_xmp_sidecars


class PipelineError(Exception):
    """Raised when pipeline operations fail."""

    pass


def process_directory(
    jpeg_dir: str | Path,
    raw_search_path: str | Path,
    taxonomy_path: str | Path,
    api_key: str | None = None,
    model: str = "gemini-flash-lite-latest",
    thinking_budget: int = 8132,
    exiftool_path: str = "exiftool",
    extensions: list[str] | None = None,
) -> dict[Path, list[str]]:
    """
    Process a directory of JPEG files and add keywords to their corresponding RAW files.

    This pipeline:
    1. Finds all JPEG files in the specified directory
    2. Locates the corresponding RAW files in the search path
    3. Checks which RAW files have XMP sidecars (warns about missing ones)
    4. Generates keywords for each JPEG with an XMP sidecar using AI
    5. Writes keywords to the RAW files' XMP sidecars

    Files without RAW files or XMP sidecars are skipped with warning messages.

    Args:
        jpeg_dir: Directory containing JPEG files to process
        raw_search_path: Base directory to search for corresponding RAW files
        taxonomy_path: Path to the Lightroom keyword taxonomy txt file
        api_key: Gemini API key (defaults to GEMINI_API_KEY environment variable)
        model: Gemini model to use for keyword generation
        thinking_budget: Thinking budget for the model
        exiftool_path: Path to exiftool binary (default: "exiftool")
        extensions: List of raw file extensions to search for (default: [".arw", ".dng", ".ARW", ".DNG"])

    Returns:
        Dictionary mapping RAW file paths to their generated keywords (only for files with XMP)

    Raises:
        FileNotFoundError: If jpeg_dir, raw_search_path, or taxonomy_path doesn't exist
        PipelineError: If no JPEG files found, no RAW files found, or no files with XMP sidecars
        ValueError: If API key is not provided

    Example:
        >>> results = process_directory(
        ...     jpeg_dir="/path/to/exports",
        ...     raw_search_path="/Volumes/T7/Pictures",
        ...     taxonomy_path="/path/to/taxonomy.txt",
        ... )
        >>> print(f"Processed {len(results)} files")
    """
    # Convert paths to Path objects
    jpeg_dir = Path(jpeg_dir)
    raw_search_path = Path(raw_search_path)
    taxonomy_path = Path(taxonomy_path)

    # Validate directories and files exist
    if not jpeg_dir.exists():
        raise FileNotFoundError(f"JPEG directory not found: {jpeg_dir}")
    if not jpeg_dir.is_dir():
        raise NotADirectoryError(f"JPEG path is not a directory: {jpeg_dir}")
    if not raw_search_path.exists():
        raise FileNotFoundError(f"RAW search path not found: {raw_search_path}")
    if not taxonomy_path.exists():
        raise FileNotFoundError(f"Taxonomy file not found: {taxonomy_path}")

    # Step 1: Find all JPEG files in the directory
    print(f"Scanning for JPEG files in {jpeg_dir}...")
    jpeg_files = list(jpeg_dir.glob("*.jpg")) + list(jpeg_dir.glob("*.JPG"))
    jpeg_files += list(jpeg_dir.glob("*.jpeg")) + list(jpeg_dir.glob("*.JPEG"))

    if not jpeg_files:
        raise PipelineError(f"No JPEG files found in {jpeg_dir}")

    print(f"Found {len(jpeg_files)} JPEG files")

    # Step 2: Find corresponding RAW files
    print(f"\nFinding RAW files in {raw_search_path}...")
    jpeg_to_raw = {}
    missing_raw_files = []

    for jpeg_file in tqdm(jpeg_files, desc="Locating RAW files"):
        raw_file = find_raw_file(jpeg_file, raw_search_path, extensions)
        if raw_file is None:
            missing_raw_files.append(jpeg_file)
        else:
            jpeg_to_raw[jpeg_file] = raw_file

    # Report on RAW file discovery
    if missing_raw_files:
        print(
            f"\n⚠️  Warning: Failed to find RAW files for {len(missing_raw_files)} JPEG(s) (will be skipped):"
        )
        for jpeg_file in missing_raw_files:
            print(f"  - {jpeg_file.name}")

    if not jpeg_to_raw:
        raise PipelineError("No RAW files found for any JPEG files. Cannot proceed.")

    print(f"Found {len(jpeg_to_raw)} RAW file(s)")

    # Step 3: Check which RAW files have XMP sidecars
    print("\nVerifying XMP sidecars...")
    raw_files = list(jpeg_to_raw.values())
    files_with_xmp, files_without_xmp = ensure_xmp_sidecars(raw_files)

    if files_without_xmp:
        print(
            f"\n⚠️  Warning: {len(files_without_xmp)} file(s) missing XMP sidecars (will be skipped):"
        )
        for raw_file in files_without_xmp:
            print(f"  - {raw_file.name}")
            print(f"    Expected: {raw_file.parent}/{raw_file.stem}.xmp")

    if not files_with_xmp:
        raise PipelineError("No files with XMP sidecars found. Cannot proceed.")

    print(f"Verified {len(files_with_xmp)} XMP sidecars")

    # Step 4: Generate keywords only for files with XMP sidecars
    print("\nGenerating keywords using AI...")
    raw_to_keywords = {}

    # Create a mapping of raw files with XMP to their JPEG files
    jpeg_to_raw_with_xmp = {jpeg: raw for jpeg, raw in jpeg_to_raw.items() if raw in files_with_xmp}

    for jpeg_file, raw_file in tqdm(jpeg_to_raw_with_xmp.items(), desc="Generating keywords"):
        keywords = generate_keywords(
            image_path=jpeg_file,
            taxonomy_path=taxonomy_path,
            api_key=api_key,
            model=model,
            thinking_budget=thinking_budget,
        )
        raw_to_keywords[raw_file] = keywords

    print(f"Generated keywords for {len(raw_to_keywords)} files")

    # Step 5: Write keywords to XMP files
    print("\nWriting keywords to XMP sidecars...")
    batch_add_keywords(raw_to_keywords, exiftool_path)
    print("Successfully wrote keywords to all files")

    return raw_to_keywords
