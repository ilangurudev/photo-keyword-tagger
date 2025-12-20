"""Example: Finding RAW files from JPEG exports.

This example demonstrates how to find source RAW files (ARW/DNG) given
exported JPEG filenames and a base search location.
"""

from pathlib import Path

from photo_keyword_tagger import find_raw_file, find_raw_files


def example_1_find_single_raw_file():
    """Example 1: Find a single RAW file from a JPEG path."""
    print("=" * 60)
    print("Example 1: Find a single RAW file")
    print("=" * 60)

    # Path to an exported JPEG
    jpeg_path = "/Volumes/T7/Pictures/Lightroom Saved Photos/test-kw/DSC00089.jpg"

    # Base directory where RAW files are stored
    base_search_path = "/Volumes/T7/Pictures"

    print(f"Looking for RAW file for: {Path(jpeg_path).name}")

    # Find the RAW file
    raw_file = find_raw_file(jpeg_path, base_search_path)

    if raw_file:
        print(f"✓ Found RAW file: {raw_file}")
        print(f"  Directory: {raw_file.parent}")
        print(f"  Size: {raw_file.stat().st_size / (1024*1024):.2f} MB")
    else:
        print("✗ No RAW file found")

    print()


def example_2_batch_processing():
    """Example 2: Process multiple JPEGs in batch."""
    print("=" * 60)
    print("Example 2: Batch processing multiple JPEGs")
    print("=" * 60)

    # List of exported JPEGs from Lightroom
    jpeg_files = [
        "/Volumes/T7/Pictures/Lightroom Saved Photos/DSC00089.jpg",
        "/Volumes/T7/Pictures/Lightroom Saved Photos/DSC00090.jpg",
        "/Volumes/T7/Pictures/Lightroom Saved Photos/IMG_1234.jpg",
        "/Volumes/T7/Pictures/Lightroom Saved Photos/NOTFOUND.jpg",
    ]

    base_search_path = "/Volumes/T7/Pictures"

    print(f"Processing {len(jpeg_files)} JPEG files...")
    print()

    # Find RAW files for all JPEGs
    results = find_raw_files(jpeg_files, base_search_path)

    # Display results
    found = 0
    not_found = 0

    print(f"{'JPEG Filename':<35} {'RAW File':<50}")
    print("-" * 85)

    for jpeg_path, raw_path in results.items():
        jpeg_name = jpeg_path.name if isinstance(jpeg_path, Path) else Path(jpeg_path).name
        if raw_path:
            print(f"{jpeg_name:<35} {raw_path!s:<50}")
            found += 1
        else:
            print(f"{jpeg_name:<35} {'NOT FOUND':<50}")
            not_found += 1

    print()
    print(f"Summary: {found} found, {not_found} not found")
    print()


def example_3_custom_extensions():
    """Example 3: Search for specific RAW file extensions."""
    print("=" * 60)
    print("Example 3: Custom file extensions")
    print("=" * 60)

    jpeg_path = "/Volumes/T7/Pictures/Lightroom Saved Photos/DSC00089.jpg"
    base_search_path = "/Volumes/T7/Pictures"

    # Search only for Sony ARW files
    print("Searching for Sony ARW files only...")
    raw_file = find_raw_file(jpeg_path, base_search_path, extensions=[".ARW", ".arw"])

    if raw_file:
        print(f"✓ Found: {raw_file}")
    else:
        print("✗ No ARW file found")

    print()

    # Search only for DNG files
    print("Searching for DNG files only...")
    raw_file = find_raw_file(jpeg_path, base_search_path, extensions=[".DNG", ".dng"])

    if raw_file:
        print(f"✓ Found: {raw_file}")
    else:
        print("✗ No DNG file found")

    print()


def example_4_with_pathlib():
    """Example 4: Using pathlib Path objects."""
    print("=" * 60)
    print("Example 4: Using pathlib Path objects")
    print("=" * 60)

    # Using Path objects instead of strings
    jpeg_path = Path("/Volumes/T7/Pictures/Lightroom Saved Photos/DSC00089.jpg")
    base_search_path = Path("/Volumes/T7/Pictures")

    print(f"Looking for RAW file for: {jpeg_path.name}")

    raw_file = find_raw_file(jpeg_path, base_search_path)

    if raw_file:
        print(f"✓ Found: {raw_file}")
        print(f"  Extension: {raw_file.suffix}")
        print(f"  Parent directory: {raw_file.parent.name}")
    else:
        print("✗ Not found")

    print()


def main():
    """Run all examples."""
    print("\n")
    print("=" * 60)
    print("RAW File Finder Examples")
    print("=" * 60)
    print("\n")

    # Note: These examples use hypothetical paths
    # Adjust the paths to match your actual photo library structure

    print("NOTE: Update the paths in the examples to match your setup!\n")

    try:
        example_1_find_single_raw_file()
        example_2_batch_processing()
        example_3_custom_extensions()
        example_4_with_pathlib()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("\nPlease update the paths in this example to match your photo library.")


if __name__ == "__main__":
    main()
