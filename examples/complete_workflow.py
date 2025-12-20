"""Complete workflow example: From JPEG to RAW file with keywords.

This example demonstrates the complete workflow:
1. Find RAW files from exported JPEGs
2. Generate keywords using Gemini AI
3. Add keywords to RAW files via XMP sidecars
"""

import os
from pathlib import Path

from photo_keyword_tagger import (
    XMPSidecarError,
    add_keywords_to_raw,
    batch_add_keywords,
    find_raw_file,
    generate_keywords,
)


def example_single_file_workflow():
    """Example: Complete workflow for a single image."""
    print("=" * 60)
    print("Example: Single File Workflow")
    print("=" * 60)

    # Step 1: Configure paths
    jpeg_path = "/Volumes/T7/Pictures/Lightroom Saved Photos/test-kw/DSC00089.jpg"
    base_search_path = "/Volumes/T7/Pictures"
    taxonomy_path = "examples/sample_taxonomy.txt"

    print(f"JPEG: {jpeg_path}")
    print()

    # Step 2: Find the RAW file
    print("Step 1: Finding RAW file...")
    jpeg_stem = Path(jpeg_path).stem
    raw_file = find_raw_file(jpeg_stem, base_search_path)

    if not raw_file:
        print(f"✗ RAW file not found for {jpeg_stem}")
        return

    print(f"✓ Found RAW file: {raw_file}")
    print()

    # Step 3: Generate keywords using Gemini
    print("Step 2: Generating keywords with Gemini AI...")
    try:
        keywords = generate_keywords(
            image_path=jpeg_path,
            taxonomy_path=taxonomy_path,
            # API key will be read from GEMINI_API_KEY env var
        )
        print(f"✓ Generated {len(keywords)} keywords:")
        for kw in keywords:
            print(f"  - {kw}")
        print()
    except Exception as e:
        print(f"✗ Failed to generate keywords: {e}")
        return

    # Step 4: Add keywords to RAW file
    print("Step 3: Adding keywords to RAW file...")
    try:
        add_keywords_to_raw(raw_file, keywords)
        print(f"✓ Successfully added keywords to {raw_file.name}")
        print(f"  Keywords written to: {raw_file.parent / f'{raw_file.stem}.xmp'}")
    except XMPSidecarError as e:
        print(f"✗ XMP sidecar error: {e}")
        print("\nTip: Make sure the XMP sidecar file exists for the RAW file.")
        print("You can create it in Lightroom by selecting the photo and")
        print("choosing Metadata > Save Metadata to File")
    except Exception as e:
        print(f"✗ Failed to add keywords: {e}")

    print()


def example_batch_workflow():
    """Example: Batch process multiple images."""
    print("=" * 60)
    print("Example: Batch Workflow")
    print("=" * 60)

    # Step 1: Configure paths
    jpeg_files = [
        "/Volumes/T7/Pictures/Lightroom Saved Photos/DSC00089.jpg",
        "/Volumes/T7/Pictures/Lightroom Saved Photos/DSC00090.jpg",
        "/Volumes/T7/Pictures/Lightroom Saved Photos/IMG_1234.jpg",
    ]
    base_search_path = "/Volumes/T7/Pictures"
    taxonomy_path = "examples/sample_taxonomy.txt"

    print(f"Processing {len(jpeg_files)} JPEG files...")
    print()

    # Step 2: Find all RAW files
    print("Step 1: Finding RAW files...")
    raw_files = []
    for jpeg_path in jpeg_files:
        jpeg_stem = Path(jpeg_path).stem
        raw_file = find_raw_file(jpeg_stem, base_search_path)
        if raw_file:
            print(f"✓ {jpeg_stem} -> {raw_file}")
            raw_files.append((jpeg_path, raw_file))
        else:
            print(f"✗ {jpeg_stem} -> NOT FOUND")
    print()

    if not raw_files:
        print("No RAW files found. Exiting.")
        return

    # Step 3: Generate keywords for each image
    print("Step 2: Generating keywords...")
    raw_files_keywords = {}

    for jpeg_path, raw_file in raw_files:
        print(f"Processing {Path(jpeg_path).name}...")
        try:
            keywords = generate_keywords(
                image_path=jpeg_path,
                taxonomy_path=taxonomy_path,
            )
            raw_files_keywords[raw_file] = keywords
            print(f"  ✓ Generated {len(keywords)} keywords")
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            # Skip this file
            continue
    print()

    if not raw_files_keywords:
        print("No keywords generated. Exiting.")
        return

    # Step 4: Add keywords to all RAW files in batch
    print("Step 3: Adding keywords to RAW files...")
    try:
        batch_add_keywords(raw_files_keywords)
        print(f"✓ Successfully added keywords to {len(raw_files_keywords)} files:")
        for raw_file, keywords in raw_files_keywords.items():
            print(f"  - {raw_file.name}: {len(keywords)} keywords")
    except XMPSidecarError as e:
        print("✗ Batch operation aborted due to missing XMP sidecars:")
        print(f"  {e}")
        print("\nTip: Make sure ALL RAW files have XMP sidecars before running batch operations.")
    except Exception as e:
        print(f"✗ Failed to add keywords: {e}")

    print()


def example_check_xmp_sidecars():
    """Example: Check which RAW files have XMP sidecars."""
    print("=" * 60)
    print("Example: Check XMP Sidecars")
    print("=" * 60)

    from photo_keyword_tagger import check_xmp_exists

    jpeg_files = [
        "/Volumes/T7/Pictures/Lightroom Saved Photos/DSC00089.jpg",
        "/Volumes/T7/Pictures/Lightroom Saved Photos/DSC00090.jpg",
        "/Volumes/T7/Pictures/Lightroom Saved Photos/IMG_1234.jpg",
    ]
    base_search_path = "/Volumes/T7/Pictures"

    print("Checking XMP sidecar status...")
    print()

    for jpeg_path in jpeg_files:
        jpeg_stem = Path(jpeg_path).stem
        raw_file = find_raw_file(jpeg_stem, base_search_path)

        if not raw_file:
            print(f"✗ {jpeg_stem}: RAW file not found")
            continue

        has_xmp = check_xmp_exists(raw_file)
        status = "✓ HAS XMP" if has_xmp else "✗ NO XMP"
        print(f"{status} {jpeg_stem} ({raw_file})")

    print()
    print("Tip: To create XMP sidecars in Lightroom:")
    print("  1. Select photos in Library")
    print("  2. Choose Metadata > Save Metadata to File")
    print("  3. This creates .xmp files alongside your RAW files")
    print()


def main():
    """Run examples based on configuration."""
    print("\n")
    print("=" * 60)
    print("Photo Keyword Tagger - Complete Workflow Examples")
    print("=" * 60)
    print("\n")

    # Check for API key
    if not os.environ.get("GEMINI_API_KEY"):
        print("⚠ WARNING: GEMINI_API_KEY environment variable not set")
        print("Some examples will fail without an API key.\n")

    print("NOTE: Update the paths in the examples to match your setup!\n")

    # Uncomment the example you want to run:

    # Check XMP sidecar status first
    # example_check_xmp_sidecars()

    # Single file workflow
    # example_single_file_workflow()

    # Batch workflow
    # example_batch_workflow()

    print("\nTip: Uncomment one of the example functions in main() to run it.")


if __name__ == "__main__":
    main()
