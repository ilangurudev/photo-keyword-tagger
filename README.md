# Photo Keyword Tagger

A Python package for for helping to add keywords to collections of photos in Lightroom Classic.

## Overview

Photo Keyword Tagger simplifies the process of organizing and tagging large collections of photos in Adobe Lightroom. Whether you're a professional photographer, photo enthusiast, or digital asset manager, this tool helps you efficiently manage and categorize your photo library.

## Features

### ✅ Available Now
- **Complete Automated Pipeline**: Process entire directories of photos with a single function call
- **Command-Line Interface**: Easy-to-use CLI for quick processing from the terminal
- **AI-Powered Keyword Generation**: Use Google Gemini to automatically generate keywords for images based on your Lightroom taxonomy
- **RAW File Finder**: Locate source RAW files (ARW/DNG) from exported JPEG filenames
- **XMP Keyword Tagging**: Add keywords to RAW files via XMP sidecar files using exiftool
- **Batch Processing**: Process multiple files at once with safety checks
- **Progress Tracking**: Real-time progress bars for long-running operations
- **Taxonomy-Based**: Ensures keywords are consistent with your existing Lightroom keyword structure
- **Flexible API**: Easy-to-use Python API with sensible defaults


## Installation

### From Source (Development)

```bash
# Clone the repository
git clone https://github.com/yourusername/photo-keyword-tagger.git
cd photo-keyword-tagger

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e .
```

### From PyPI (Coming Soon)

```bash
pip install photo-keyword-tagger
```

### Dependencies

The package requires:
- Python 3.12+
- `google-genai` for AI-powered keyword generation
- `tqdm` for progress tracking
- `exiftool` for XMP metadata manipulation (external dependency)

## Quick Start

### Prerequisites

1. **Gemini API Key**: Get a Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```

2. **Install exiftool**: Required for XMP metadata manipulation
   ```bash
   # macOS
   brew install exiftool

   # Linux (Ubuntu/Debian)
   sudo apt-get install libimage-exiftool-perl

   # Windows: Download from https://exiftool.org/
   ```

3. **Create XMP Sidecars in Lightroom**: Before adding keywords, you need to create XMP sidecar files
   - In Lightroom, select your photos
   - Choose `Metadata > Save Metadata to File`
   - This creates `.xmp` files alongside your RAW files

   > If there are no xmp fails, this process will fail.

4. Run the tool using the [Basic Usage](#basic-usage) section, either through the CLI or from Python.

5. Once the xmp files are updated:
   - In Lightroom, select your photos
   - Choose `Metadata > Read Metadata from Files`
   - This will update your keywords.

### Basic Usage

#### Command-Line Interface (Quickest)

Export the RAW files to jpegs to a smaller size to keep the AI tagging costs low.

The fastest way to process photos is using the CLI:

```bash
# Set your Gemini API key
export GEMINI_API_KEY="your-api-key-here"

# Process photos
photo-keyword-tagger \
    /path/to/exported/jpegs \
    /Volumes/T7/Pictures \
    /path/to/lightroom_taxonomy.txt

# Or run as a module
python -m photo_keyword_tagger \
    /path/to/exported/jpegs \
    /Volumes/T7/Pictures \
    /path/to/lightroom_taxonomy.txt
```

**CLI Options:**
```bash
# Get help
photo-keyword-tagger --help

# Use a different model
photo-keyword-tagger \
    --model gemini-2.0-flash-exp \
    /path/to/jpegs /path/to/raw /path/to/taxonomy.txt

# Specify custom RAW extensions
photo-keyword-tagger \
    --extensions .arw --extensions .dng \
    /path/to/jpegs /path/to/raw /path/to/taxonomy.txt

# Verbose output
photo-keyword-tagger -v \
    /path/to/jpegs /path/to/raw /path/to/taxonomy.txt
```

#### Python API - Complete Pipeline

The simplest way to process a directory of photos from Python:

```python
from photo_keyword_tagger import process_directory

# Process entire directory automatically
results = process_directory(
    jpeg_dir="/path/to/exported/jpegs",
    raw_search_path="/Volumes/T7/Pictures",
    taxonomy_path="/path/to/lightroom_taxonomy.txt",
)

# Display results
print(f"Processed {len(results)} files:")
for raw_file, keywords in results.items():
    print(f"{raw_file.name}: {', '.join(keywords)}")
```

This single function:
1. Finds all JPEG files in the directory
2. Locates their corresponding RAW files
3. Verifies XMP sidecars exist
4. Generates keywords using AI (with progress bar)
5. Writes keywords to XMP sidecars

See the [Pipeline Documentation](docs/PIPELINE.md) for more details.

#### Individual Components

You can also use individual components for more control:

##### Keyword Generation

```python
from photo_keyword_tagger import generate_keywords

# Generate keywords for an image using your Lightroom taxonomy
keywords = generate_keywords(
    image_path="path/to/your/photo.jpg",
    taxonomy_path="path/to/lightroom_taxonomy.txt"
)

print(f"Generated keywords: {keywords}")
# Output: Generated keywords: ['landscape', 'mountain', 'sunset', 'nature']
```

#### Finding RAW Files

```python
from photo_keyword_tagger import find_raw_file, find_raw_directory
from pathlib import Path

# Find source RAW file from an exported JPEG
jpeg_path = "/path/to/exported/DSC00089.jpg"
base_search_path = "/path/to/photo/library"

# Get the filename stem
jpeg_stem = Path(jpeg_path).stem  # "DSC00089"

# Find the RAW file
raw_file = find_raw_file(jpeg_stem, base_search_path)
print(f"Found RAW file: {raw_file}")
# Output: Found RAW file: /path/to/photo/library/2024/January/DSC00089.ARW

# Or just find the directory
raw_dir = find_raw_directory(jpeg_stem, base_search_path)
print(f"RAW directory: {raw_dir}")
# Output: RAW directory: /path/to/photo/library/2024/January
```

#### Adding Keywords to RAW Files

```python
from photo_keyword_tagger import add_keywords_to_raw
from pathlib import Path

# Add keywords to a RAW file via its XMP sidecar
raw_file = Path("/path/to/photo/DSC00089.ARW")
keywords = ["landscape", "sunset", "nature"]

add_keywords_to_raw(raw_file, keywords)
print(f"Added {len(keywords)} keywords to {raw_file.name}")
```

#### Complete Workflow

```python
from pathlib import Path
from photo_keyword_tagger import (
    find_raw_file,
    generate_keywords,
    add_keywords_to_raw,
)

# 1. Find RAW file from JPEG export
jpeg_path = "/path/to/exported/DSC00089.jpg"
jpeg_stem = Path(jpeg_path).stem
raw_file = find_raw_file(jpeg_stem, "/path/to/photo/library")

# 2. Generate keywords using AI
keywords = generate_keywords(
    image_path=jpeg_path,
    taxonomy_path="taxonomy.txt"
)

# 3. Add keywords to RAW file
add_keywords_to_raw(raw_file, keywords)
print(f"Complete! Added {len(keywords)} keywords.")
```

#### Batch Processing

```python
from photo_keyword_tagger import batch_add_keywords
from pathlib import Path

# Process multiple RAW files at once
raw_files_keywords = {
    Path("/photos/DSC00089.ARW"): ["landscape", "sunset"],
    Path("/photos/DSC00090.ARW"): ["portrait", "indoor"],
    Path("/photos/DSC00091.ARW"): ["macro", "nature"],
}

# This will check all XMP sidecars exist first, then add keywords
batch_add_keywords(raw_files_keywords)
print(f"Added keywords to {len(raw_files_keywords)} files")
```

### Exporting Keyword Taxonomy from Lightroom

1. In Lightroom, go to **Library** > **Keyword List**
2. Right-click on the keyword list and select **Export**
3. Save the file as a `.txt` file
4. Use this file as your `taxonomy_path`

See the [examples/sample_taxonomy.txt](examples/sample_taxonomy.txt) file for an example of the expected format.

## Documentation

- [Pipeline Guide](docs/PIPELINE.md) - **Start here!** Complete automated workflow
- [RAW File Finder Guide](docs/RAW_FILE_FINDER.md) - Detailed guide for finding RAW files
- [XMP Tagging Guide](docs/XMP_TAGGING.md) - Comprehensive guide for adding keywords to RAW files
- [Complete Workflow Example](examples/complete_workflow.py) - End-to-end example combining all features
- [Pipeline Example](examples/pipeline_usage.py) - Example using the automated pipeline

## Development

### Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies (creates venv automatically)
uv sync

# Activate virtual environment (optional, uv commands work without it)
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=photo_keyword_tagger
```

### Project Structure

```
photo-keyword-tagger/
├── src/
│   └── photo_keyword_tagger/
│       ├── __init__.py
│       ├── __main__.py             # Module entry point
│       ├── cli.py                  # Command-line interface
│       ├── pipeline.py             # Complete automated workflow
│       ├── keyword_generator.py   # AI keyword generation
│       ├── file_finder.py          # RAW file location
│       └── xmp_tagger.py           # XMP keyword tagging
├── tests/
│   ├── __init__.py
│   ├── test_pipeline.py
│   ├── test_keyword_generator.py
│   ├── test_file_finder.py
│   └── test_xmp_tagger.py
├── examples/
│   ├── pipeline_usage.py           # Simple pipeline example
│   ├── complete_workflow.py        # End-to-end manual example
│   ├── basic_usage.py
│   ├── find_raw_files.py
│   └── sample_taxonomy.txt
├── docs/
│   ├── PIPELINE.md                 # Pipeline documentation
│   ├── RAW_FILE_FINDER.md
│   └── XMP_TAGGING.md
├── nbs/
│   └── build.ipynb
├── pyproject.toml
├── README.md
└── AGENTS.md
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License (or your preferred license)

## Author

Gurudev Ilangovan

## Roadmap

- [x] AI-powered keyword generation using Gemini
- [x] Taxonomy-based keyword selection
- [x] RAW file finder utilities (ARW/DNG)
- [x] XMP sidecar keyword tagging with exiftool
- [x] Batch processing with safety checks
- [x] Complete automated pipeline with progress tracking
- [x] CLI interface
- [ ] Core Lightroom catalogue reading functionality (SQLite)
- [ ] Direct catalogue integration (write keywords to catalogue)
- [ ] Additional AI models support
- [ ] PyPI release

## Support

For issues, questions, or contributions, please open an issue on GitHub.
