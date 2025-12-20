# RAW File Finder Documentation

## Overview

The RAW File Finder module helps you locate source RAW image files (ARW, DNG) given exported JPEG filenames. This is particularly useful when you've exported JPEGs from Lightroom and need to find the corresponding original RAW files in your photo library.

## Use Cases

1. **Post-Export Workflow**: After exporting JPEGs from Lightroom, quickly find the source RAW files for further processing
2. **Backup Verification**: Check if RAW files exist in your archive for exported photos
3. **Batch Organization**: Process multiple exported photos and locate their source files
4. **Duplicate Detection**: Find all copies of a RAW file across different backup locations

## Functions

### `find_raw_file(jpeg_stem, base_path, extensions=None)`

Finds the first matching RAW file.

**Parameters:**
- `jpeg_stem` (str): Filename without extension (e.g., "DSC00089")
- `base_path` (str | Path): Root directory to search
- `extensions` (list[str], optional): File extensions to search (default: [".arw", ".dng", ".ARW", ".DNG"])

**Returns:**
- `Path | None`: Path to the RAW file, or None if not found

**Example:**
```python
from photo_keyword_tagger import find_raw_file

raw_file = find_raw_file("DSC00089", "/Volumes/T7/Pictures")
if raw_file:
    print(f"Found: {raw_file}")
```

### `find_raw_directory(jpeg_stem, base_path, extensions=None)`

Finds the directory containing the RAW file.

**Parameters:**
- Same as `find_raw_file`

**Returns:**
- `Path | None`: Path to the directory, or None if not found

**Example:**
```python
from photo_keyword_tagger import find_raw_directory

raw_dir = find_raw_directory("DSC00089", "/Volumes/T7/Pictures")
if raw_dir:
    print(f"Directory: {raw_dir}")
```

### `find_all_raw_files(jpeg_stem, base_path, extensions=None)`

Finds all matching RAW files (useful for finding duplicates/backups).

**Parameters:**
- Same as `find_raw_file`

**Returns:**
- `list[Path]`: List of all matching RAW files (empty if none found)

**Example:**
```python
from photo_keyword_tagger import find_all_raw_files

all_files = find_all_raw_files("DSC00089", "/Volumes/T7/Pictures")
print(f"Found {len(all_files)} copies:")
for f in all_files:
    print(f"  - {f}")
```

### `batch_find_raw_directories(jpeg_paths, base_path, extensions=None)`

Process multiple JPEGs at once.

**Parameters:**
- `jpeg_paths` (list[str | Path]): List of JPEG file paths
- `base_path` (str | Path): Root directory to search
- `extensions` (list[str], optional): File extensions to search

**Returns:**
- `dict[str, Path | None]`: Dictionary mapping JPEG filename to RAW directory

**Example:**
```python
from photo_keyword_tagger import batch_find_raw_directories

jpeg_files = [
    "/path/to/exports/DSC00089.jpg",
    "/path/to/exports/DSC00090.jpg",
]

results = batch_find_raw_directories(jpeg_files, "/Volumes/T7/Pictures")

for jpeg_name, raw_dir in results.items():
    print(f"{jpeg_name} -> {raw_dir}")
```

## Supported File Formats

By default, the finder searches for:
- ARW files (Sony RAW format): `.arw`, `.ARW`
- DNG files (Adobe Digital Negative): `.dng`, `.DNG`

You can customize this by passing a custom `extensions` list:

```python
# Search only for Sony ARW files
find_raw_file("DSC00089", base_path, extensions=[".ARW", ".arw"])

# Search only for DNG files
find_raw_file("IMG_1234", base_path, extensions=[".DNG", ".dng"])

# Add support for other RAW formats
find_raw_file("IMG_1234", base_path, extensions=[".CR2", ".cr2", ".NEF", ".nef"])
```

## Performance Considerations

- The finder uses recursive glob patterns to search directories
- Search time depends on the size of your photo library
- For large libraries (>100k files), consider:
  - Narrowing down the `base_path` to specific years/months
  - Using the batch functions to process multiple files at once
  - Caching results if searching for the same files repeatedly

## Error Handling

The functions handle common errors gracefully:

```python
from photo_keyword_tagger import find_raw_file

try:
    raw_file = find_raw_file("DSC00089", "/nonexistent/path")
except FileNotFoundError as e:
    print(f"Error: {e}")
    # Output: Error: Base path does not exist: /nonexistent/path

# If file not found, returns None (no exception)
raw_file = find_raw_file("NOTFOUND", "/valid/path")
print(raw_file)  # Output: None
```

## Integration with Lightroom Workflow

### Typical Workflow

1. **Export JPEGs from Lightroom**
   - Export selected photos to a directory
   - Use consistent naming (Lightroom maintains original filenames)

2. **Generate Keywords**
   ```python
   from photo_keyword_tagger import generate_keywords

   keywords = generate_keywords(
       image_path="/path/to/export/DSC00089.jpg",
       taxonomy_path="/path/to/taxonomy.txt"
   )
   ```

3. **Find Source RAW Files**
   ```python
   from pathlib import Path
   from photo_keyword_tagger import find_raw_file

   jpeg_path = Path("/path/to/export/DSC00089.jpg")
   raw_file = find_raw_file(jpeg_path.stem, "/path/to/library")
   ```

4. **Apply Keywords**
   - Use the keywords with the RAW file location
   - Future feature: Direct Lightroom catalogue integration

## Examples

See the following files for complete examples:
- `examples/find_raw_files.py` - Comprehensive examples
- `nbs/build.ipynb` - Interactive notebook examples

## Testing

The module includes comprehensive tests:

```bash
# Run all tests
uv run pytest tests/test_file_finder.py -v

# Run specific test
uv run pytest tests/test_file_finder.py::test_find_raw_file_found -v
```

## Future Enhancements

Potential improvements:
- [ ] Performance optimization with parallel searching
- [ ] Fuzzy matching for similar filenames
- [ ] Support for video files (MOV, MP4 originals)
- [ ] Integration with XMP sidecar files
- [ ] Database caching for large libraries
