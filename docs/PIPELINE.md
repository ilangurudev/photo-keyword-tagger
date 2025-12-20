# Pipeline Module

The pipeline module provides a complete, automated workflow for processing directories of JPEG images and adding AI-generated keywords to their corresponding RAW files.

## Overview

The `process_directory()` function orchestrates the entire keyword tagging workflow:

1. **Find JPEG files**: Scans the specified directory for JPEG images
2. **Locate RAW files**: Finds the corresponding RAW files in the search path
3. **Verify XMP sidecars**: Ensures all RAW files have XMP sidecar files
4. **Generate keywords**: Uses AI to analyze each JPEG and generate keywords based on your taxonomy
5. **Write keywords**: Adds the generated keywords to the RAW files' XMP sidecars

## Usage

### Basic Example

```python
from photo_keyword_tagger import process_directory

results = process_directory(
    jpeg_dir="/path/to/exported/jpegs",
    raw_search_path="/Volumes/T7/Pictures",
    taxonomy_path="/path/to/taxonomy.txt",
)

# Display results
for raw_file, keywords in results.items():
    print(f"{raw_file.name}: {', '.join(keywords)}")
```

### With Custom Options

```python
from photo_keyword_tagger import process_directory

results = process_directory(
    jpeg_dir="/path/to/exported/jpegs",
    raw_search_path="/Volumes/T7/Pictures",
    taxonomy_path="/path/to/taxonomy.txt",
    api_key="your-gemini-api-key",  # Or use GEMINI_API_KEY env var
    model="gemini-flash-lite-latest",  # Customize AI model
    thinking_budget=8132,  # Adjust AI thinking budget
    exiftool_path="/custom/path/to/exiftool",  # Custom exiftool location
    extensions=[".arw", ".ARW", ".nef", ".NEF"],  # Custom RAW extensions
)
```

## Function Reference

### `process_directory()`

Process a directory of JPEG files and add keywords to their corresponding RAW files.

**Parameters:**

- `jpeg_dir` (str | Path): Directory containing JPEG files to process
- `raw_search_path` (str | Path): Base directory to search for corresponding RAW files
- `taxonomy_path` (str | Path): Path to the Lightroom keyword taxonomy txt file
- `api_key` (str | None, optional): Gemini API key (defaults to `GEMINI_API_KEY` environment variable)
- `model` (str, optional): Gemini model to use for keyword generation (default: "gemini-flash-lite-latest")
- `thinking_budget` (int, optional): Thinking budget for the model (default: 8132)
- `exiftool_path` (str, optional): Path to exiftool binary (default: "exiftool")
- `extensions` (list[str] | None, optional): List of raw file extensions to search for (default: [".arw", ".dng", ".ARW", ".DNG"])

**Returns:**

- `dict[Path, list[str]]`: Dictionary mapping RAW file paths to their generated keywords

**Raises:**

- `FileNotFoundError`: If jpeg_dir, raw_search_path, or taxonomy_path doesn't exist
- `PipelineError`: If no JPEG files found or RAW files missing
- `XMPSidecarError`: If any RAW file is missing its XMP sidecar
- `ValueError`: If API key is not provided

## Progress Tracking

The pipeline uses `tqdm` to show progress bars for:

- Finding RAW files for each JPEG
- Generating keywords for each image

This provides real-time feedback during long-running operations.

## Error Handling

The pipeline is designed to fail fast and provide clear error messages:

1. **Missing directories/files**: Validates all paths before processing
2. **Missing RAW files**: Lists all JPEGs that don't have corresponding RAW files
3. **Missing XMP sidecars**: Lists all RAW files without XMP sidecars and stops before any modifications
4. **API errors**: Propagates Gemini API errors with clear messages

## Workflow Details

### Step 1: Find JPEG Files

The pipeline searches for files with extensions: `.jpg`, `.JPG`, `.jpeg`, `.JPEG`

### Step 2: Locate RAW Files

For each JPEG, the pipeline:
- Extracts the filename stem (e.g., "DSC00089" from "DSC00089.jpg")
- Recursively searches the RAW search path for files with matching stems
- Supports multiple RAW formats: ARW, DNG, NEF, CR2, etc.

### Step 3: Verify XMP Sidecars

The pipeline ensures all RAW files have corresponding XMP sidecar files. If any are missing, it aborts the entire operation before generating any keywords. This prevents partial processing.

### Step 4: Generate Keywords

For each JPEG:
- Sends the image and taxonomy to the Gemini AI model
- The AI analyzes the image content (subjects, locations, actions, colors, mood, etc.)
- Returns relevant keywords from your taxonomy
- Progress is shown via tqdm progress bar

### Step 5: Write Keywords

After all keywords are generated:
- Uses `batch_add_keywords()` to write all keywords to XMP files
- Keywords are appended to existing keywords (not replaced)
- Uses exiftool to ensure proper XMP format

## Example Output

```
Scanning for JPEG files in /path/to/jpegs...
Found 3 JPEG files

Finding RAW files in /Volumes/T7/Pictures...
Locating RAW files: 100%|████████████████████| 3/3 [00:02<00:00,  1.23it/s]
Found all 3 RAW files

Verifying XMP sidecars...
Verified 3 XMP sidecars

Generating keywords using AI...
Generating keywords: 100%|████████████████████| 3/3 [00:15<00:00,  5.12s/it]
Generated keywords for 3 files

Writing keywords to XMP sidecars...
Successfully wrote keywords to all files

================================================================================
PROCESSING COMPLETE
================================================================================

Processed 3 files:

DSC00089.ARW:
  Keywords: landscape, mountain, sunset, nature, outdoor

DSC00090.ARW:
  Keywords: portrait, indoor, natural-light, bokeh

DSC00091.ARW:
  Keywords: wildlife, bird, in-flight, action
```

## See Also

- [File Finder](RAW_FILE_FINDER.md) - RAW file discovery
- [XMP Tagging](XMP_TAGGING.md) - XMP sidecar management
- [Keyword Generator](../src/photo_keyword_tagger/keyword_generator.py) - AI keyword generation
