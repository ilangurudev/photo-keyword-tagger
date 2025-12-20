# XMP Sidecar Keyword Tagging

This module provides functionality to add keywords to RAW image files using XMP sidecar files and exiftool.

## Overview

The XMP tagging module allows you to:
- Check if XMP sidecar files exist for RAW files
- Ensure all files in a batch have XMP sidecars before processing
- Add keywords to XMP files using exiftool
- Process multiple files in batch

## Prerequisites

### exiftool Installation

You need to have `exiftool` installed on your system:

**macOS:**
```bash
brew install exiftool
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install libimage-exiftool-perl
```

**Windows:**
Download from [exiftool.org](https://exiftool.org/)

### XMP Sidecar Files

XMP sidecar files are separate `.xmp` files that store metadata for RAW files. They must exist before you can add keywords.

**Creating XMP sidecars in Lightroom:**
1. Select photos in Library module
2. Choose `Metadata > Save Metadata to File`
3. This creates `.xmp` files alongside your RAW files

## Usage

### Check if XMP Sidecar Exists

```python
from pathlib import Path
from photo_keyword_tagger import check_xmp_exists

raw_file = Path("/photos/DSC00089.ARW")

if check_xmp_exists(raw_file):
    print("XMP sidecar exists")
else:
    print("No XMP sidecar found")
```

### Ensure All Files Have XMP Sidecars

Before processing a batch of files, ensure all have XMP sidecars:

```python
from photo_keyword_tagger import ensure_xmp_sidecars, XMPSidecarError

raw_files = [
    Path("/photos/DSC00089.ARW"),
    Path("/photos/DSC00090.ARW"),
]

try:
    ensure_xmp_sidecars(raw_files)
    print("All XMP sidecars exist")
except XMPSidecarError as e:
    print(f"Missing XMP sidecars: {e}")
```

### Add Keywords to a Single RAW File

```python
from pathlib import Path
from photo_keyword_tagger import add_keywords_to_raw

raw_file = Path("/photos/DSC00089.ARW")
keywords = ["landscape", "sunset", "nature"]

# This will add keywords to /photos/DSC00089.xmp
add_keywords_to_raw(raw_file, keywords)
```

### Add Keywords to XMP File Directly

```python
from pathlib import Path
from photo_keyword_tagger import add_keywords_to_xmp

xmp_file = Path("/photos/DSC00089.xmp")
keywords = ["landscape", "sunset", "nature"]

add_keywords_to_xmp(xmp_file, keywords)
```

### Batch Processing

Process multiple RAW files in one operation:

```python
from pathlib import Path
from photo_keyword_tagger import batch_add_keywords

# Dictionary mapping RAW files to their keywords
raw_files_keywords = {
    Path("/photos/DSC00089.ARW"): ["landscape", "sunset"],
    Path("/photos/DSC00090.ARW"): ["portrait", "indoor"],
    Path("/photos/DSC00091.ARW"): ["macro", "nature"],
}

# This will:
# 1. Check all XMP sidecars exist (aborts if any missing)
# 2. Add keywords to all files
batch_add_keywords(raw_files_keywords)
```

### Custom exiftool Path

If exiftool is not in your PATH, specify its location:

```python
from photo_keyword_tagger import add_keywords_to_xmp

add_keywords_to_xmp(
    xmp_file,
    keywords,
    exiftool_path="/usr/local/bin/exiftool"
)
```

## Complete Workflow Example

```python
from pathlib import Path
from photo_keyword_tagger import (
    find_raw_file,
    generate_keywords,
    add_keywords_to_raw,
)

# 1. Find RAW file from JPEG export
jpeg_path = "/exports/DSC00089.jpg"
jpeg_stem = Path(jpeg_path).stem
raw_file = find_raw_file(jpeg_stem, "/photos")

# 2. Generate keywords using Gemini AI
keywords = generate_keywords(
    image_path=jpeg_path,
    taxonomy_path="taxonomy.txt"
)

# 3. Add keywords to RAW file
add_keywords_to_raw(raw_file, keywords)
print(f"Added {len(keywords)} keywords to {raw_file}")
```

## API Reference

### Functions

#### `get_xmp_path(raw_file: Path) -> Path`
Get the expected path for an XMP sidecar file.

#### `check_xmp_exists(raw_file: Path) -> bool`
Check if an XMP sidecar file exists for a RAW file.

#### `ensure_xmp_sidecars(raw_files: list[Path]) -> None`
Ensure all RAW files have XMP sidecars. Raises `XMPSidecarError` if any are missing.

#### `add_keywords_to_xmp(xmp_file: Path, keywords: list[str], exiftool_path: str = "exiftool") -> None`
Add keywords to an XMP file using exiftool.

**Parameters:**
- `xmp_file`: Path to the XMP sidecar file
- `keywords`: List of keywords to add
- `exiftool_path`: Path to exiftool binary (default: "exiftool")

#### `add_keywords_to_raw(raw_file: Path, keywords: list[str], exiftool_path: str = "exiftool") -> None`
Add keywords to a RAW file via its XMP sidecar.

**Parameters:**
- `raw_file`: Path to the RAW image file
- `keywords`: List of keywords to add
- `exiftool_path`: Path to exiftool binary (default: "exiftool")

#### `batch_add_keywords(raw_files_keywords: dict[Path, list[str]], exiftool_path: str = "exiftool") -> None`
Add keywords to multiple RAW files in batch.

**Parameters:**
- `raw_files_keywords`: Dictionary mapping RAW file paths to their keywords
- `exiftool_path`: Path to exiftool binary (default: "exiftool")

### Exceptions

#### `XMPSidecarError`
Raised when XMP sidecar file operations fail, typically when required XMP files are missing.

## exiftool Command Details

The module uses exiftool with the following command structure:

```bash
exiftool -overwrite_original -XMP-dc:Subject+=keyword1 -XMP-dc:Subject+=keyword2 -XMP-dc:Subject+=keyword3 file.xmp
```

**Flags:**
- `-overwrite_original`: Prevents creation of `.xmp_original` backup files
- `-XMP-dc:Subject+=`: Appends to existing keywords (doesn't replace them)
- Each keyword is added as a separate `-XMP-dc:Subject+=` argument for reliability

## Important Notes

### Safety Features

1. **Batch Processing Safety**: The `batch_add_keywords()` function checks that ALL XMP sidecars exist before adding keywords to ANY file. This prevents partial updates if some files are missing XMP sidecars.

2. **Keyword Appending**: Keywords are appended to existing keywords, not replaced. This prevents accidental loss of existing metadata.

3. **No Backup Files**: The `-overwrite_original` flag prevents creation of `.xmp_original` backup files, keeping your directory clean.

### Best Practices

1. **Always create XMP sidecars in Lightroom first** using `Metadata > Save Metadata to File`

2. **Check for XMP sidecars** before batch operations using `ensure_xmp_sidecars()`

3. **Use batch processing** for multiple files to ensure atomic operations

4. **Verify keywords** in Lightroom after adding them (keywords should appear in the Keyword List panel)

### Troubleshooting

**"Missing XMP sidecar files" error:**
- Ensure XMP files exist for all RAW files
- In Lightroom: Select photos → `Metadata > Save Metadata to File`

**"exiftool: command not found" error:**
- Install exiftool (see Prerequisites section)
- Or provide full path using `exiftool_path` parameter

**Keywords don't appear in Lightroom:**
- In Lightroom: Select photos → `Metadata > Read Metadata from File`
- Or restart Lightroom to force metadata refresh

## Examples

See the complete workflow examples in:
- `examples/complete_workflow.py` - Full end-to-end workflow
- `examples/find_raw_files.py` - Finding RAW files from JPEGs

## Testing

Run the XMP tagging tests:

```bash
uv run pytest tests/test_xmp_tagger.py -v
```

All 21 tests should pass.
