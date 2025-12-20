# Architecture Documentation

## System Overview

Photo Keyword Tagger is a modular Python package that automates the process of adding AI-generated keywords to RAW photo files in Lightroom Classic workflows. The system operates on exported JPEG files, uses AI to generate relevant keywords, and writes them to RAW files via XMP sidecar files.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                           │
│  ┌──────────────────────────┐  ┌──────────────────────────────┐ │
│  │   CLI (cli.py)           │  │   Python API (__init__.py)   │ │
│  │   - Command-line tool    │  │   - Direct function calls    │ │
│  │   - Argument parsing     │  │   - Library interface        │ │
│  └──────────────────────────┘  └──────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Orchestration Layer                           │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                   Pipeline (pipeline.py)                     ││
│  │   - Complete automated workflow                              ││
│  │   - Coordinates all modules                                  ││
│  │   - Progress tracking and error handling                     ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌───────────────────┐ ┌───────────────┐ ┌──────────────────┐
│   File Finder     │ │   Keyword     │ │   XMP Tagger     │
│(file_finder.py)   │ │  Generator    │ │ (xmp_tagger.py)  │
│                   │ │(keyword_      │ │                  │
│- Locate RAW files │ │ generator.py) │ │- XMP operations  │
│- Directory search │ │               │ │- exiftool mgmt   │
│- Batch finding    │ │- AI analysis  │ │- Batch writing   │
└───────────────────┘ │- Gemini API   │ └──────────────────┘
                      │- Taxonomy     │
                      │  integration  │
                      └───────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  External Deps  │
                    │                 │
                    │ - Google Gemini │
                    │ - exiftool      │
                    └─────────────────┘
```

## Component Details

### 1. CLI Module (`cli.py`)

**Purpose**: Provides command-line interface for quick photo processing.

**Key Functions**:
- `main()`: Entry point for CLI, handles argument parsing and error reporting

**Features**:
- Click-based argument parsing
- Environment variable support for API keys
- Verbose and quiet modes
- Custom model and extension support

**Error Handling**:
- Validates all paths before processing
- Clear error messages for common issues
- Proper exit codes (0 for success, 1 for failure)

**See**: [CLI.md](CLI.md) for detailed CLI documentation

---

### 2. Pipeline Module (`pipeline.py`)

**Purpose**: Orchestrates the complete automated workflow.

**Key Functions**:
- `process_directory()`: Main pipeline function that coordinates all steps

**Workflow Steps**:
1. **JPEG Discovery**: Scans directory for JPEG files (`.jpg`, `.JPG`, `.jpeg`, `.JPEG`)
2. **RAW Mapping**: Uses `file_finder` to locate corresponding RAW files
3. **XMP Validation**: Ensures all RAW files have XMP sidecars (fail-fast)
4. **Keyword Generation**: Calls `keyword_generator` for each JPEG
5. **Batch Writing**: Uses `xmp_tagger` to write all keywords

**Design Principles**:
- **Fail-fast**: Validates everything before making changes
- **Atomic operations**: All-or-nothing approach for batch processing
- **Progress tracking**: Real-time feedback via tqdm
- **Comprehensive logging**: Status messages at each step

**Error Handling**:
- `PipelineError`: Custom exception for pipeline-specific failures
- Propagates errors from child modules with context
- Lists all problematic files before aborting

**See**: [PIPELINE.md](PIPELINE.md) for detailed pipeline documentation

---

### 3. File Finder Module (`file_finder.py`)

**Purpose**: Locates source RAW files from exported JPEG filenames.

**Key Functions**:
- `find_raw_file()`: Find single RAW file by JPEG stem
- `find_raw_files()`: Batch finding for multiple JPEGs

**How It Works**:
1. Extract filename stem from JPEG (e.g., "DSC00089" from "DSC00089.jpg")
2. Recursively search base path using glob patterns
3. Support multiple RAW formats via configurable extensions
4. Return first match (or all matches for duplicate detection)

**Search Strategy**:
- Uses `Path.glob()` with recursive patterns (`**/*.ext`)
- Case-insensitive by checking both uppercase and lowercase extensions
- Returns `None` if not found (no exceptions for missing files)

**Performance Considerations**:
- Recursive search can be slow on large directories
- Consider narrowing base_path to specific subdirectories
- Uses first-match optimization (stops after first find)

**Supported Formats**:
- Default: `.arw`, `.dng`, `.ARW`, `.DNG`
- Extensible via `extensions` parameter
- Supports any RAW format (CR2, NEF, RAF, etc.)

**See**: [RAW_FILE_FINDER.md](RAW_FILE_FINDER.md) for detailed file finder documentation

---

### 4. Keyword Generator Module (`keyword_generator.py`)

**Purpose**: Uses Google Gemini AI to generate relevant keywords from images.

**Key Functions**:
- `generate_keywords()`: Analyzes image and returns keywords based on taxonomy

**How It Works**:
1. **Image Encoding**: Reads and base64-encodes image
2. **MIME Type Detection**: Determines image format from extension
3. **Taxonomy Loading**: Reads Lightroom keyword taxonomy file
4. **Prompt Construction**: Creates structured prompt with taxonomy and instructions
5. **AI Analysis**: Sends to Gemini via streaming API
6. **Response Parsing**: Extracts keywords from JSON response

**AI Configuration**:
- **Model**: Configurable (default: `gemini-flash-lite-latest`)
- **Thinking Budget**: Controls AI reasoning depth (default: 8132)
- **Response Format**: JSON-only mode for reliable parsing
- **Streaming**: Uses `generate_content_stream()` for better responsiveness

**Prompt Engineering**:
- Instructs AI to select ONLY keywords from provided taxonomy
- Emphasizes direct relevance and specificity
- Limits keywords per category and total count
- Requests exact spelling/casing from taxonomy

**Error Handling**:
- Validates image and taxonomy file existence
- Requires API key (env var or parameter)
- Handles JSON parsing failures with clear messages
- Propagates Gemini API errors

**Dependencies**:
- `google-genai`: Official Google AI Python SDK
- Base64 encoding for image data
- JSON parsing for response

**See**: Source code docstrings in `keyword_generator.py`

---

### 5. XMP Tagger Module (`xmp_tagger.py`)

**Purpose**: Manages XMP sidecar files and writes keywords using exiftool.

**Key Functions**:
- `get_xmp_path()`: Calculate expected XMP path from RAW file
- `check_xmp_exists()`: Verify XMP sidecar exists
- `ensure_xmp_sidecars()`: Batch validation (fail-fast)
- `add_keywords_to_xmp()`: Write keywords to XMP file
- `add_keywords_to_raw()`: Convenience wrapper for RAW files
- `batch_add_keywords()`: Process multiple files atomically

**XMP Sidecar Structure**:
- XMP files are XML-based metadata sidecars
- Named identically to RAW file with `.xmp` extension
- Example: `DSC00089.ARW` → `DSC00089.xmp`
- Must be created in Lightroom before tagging

**exiftool Integration**:
```bash
exiftool -overwrite_original \
  -XMP-dc:Subject+=keyword1 \
  -XMP-dc:Subject+=keyword2 \
  -XMP-dc:Subject+=keyword3 \
  file.xmp
```

**Command Flags**:
- `-overwrite_original`: No backup files (keeps directory clean)
- `-XMP-dc:Subject+=`: Appends keywords (doesn't replace)
- Multiple arguments: One per keyword for reliability

**Safety Features**:
1. **Pre-validation**: Checks all XMP files exist before writing
2. **Atomic batching**: All-or-nothing for batch operations
3. **Keyword appending**: Never replaces existing keywords
4. **Error propagation**: Subprocess errors are caught and raised

**Error Handling**:
- `XMPSidecarError`: Custom exception for missing XMP files
- Lists all problematic files in error message
- Validates file existence before operations
- Captures and reports exiftool errors

**See**: [XMP_TAGGING.md](XMP_TAGGING.md) for detailed XMP documentation

---

## Data Flow

### Complete End-to-End Flow

```
1. User Input
   ├─ JPEG directory path
   ├─ RAW search base path
   ├─ Taxonomy file path
   └─ Configuration (API key, model, etc.)
          │
          ▼
2. Pipeline Initialization
   ├─ Validate all paths exist
   ├─ Scan for JPEG files
   └─ Verify taxonomy file
          │
          ▼
3. File Discovery Phase
   ├─ For each JPEG:
   │   ├─ Extract filename stem
   │   ├─ Search for RAW file
   │   └─ Map JPEG → RAW
   │
   └─ Abort if any RAW not found
          │
          ▼
4. XMP Validation Phase
   ├─ For each RAW file:
   │   ├─ Calculate XMP path
   │   └─ Check existence
   │
   └─ Abort if any XMP missing
          │
          ▼
5. Keyword Generation Phase
   ├─ For each JPEG:
   │   ├─ Encode image to base64
   │   ├─ Load taxonomy
   │   ├─ Send to Gemini API
   │   ├─ Parse JSON response
   │   └─ Store keywords
   │
   └─ Build RAW → keywords mapping
          │
          ▼
6. Keyword Writing Phase
   ├─ For each RAW file:
   │   ├─ Get XMP sidecar path
   │   ├─ Build exiftool command
   │   └─ Execute subprocess
   │
   └─ Verify all writes succeeded
          │
          ▼
7. Result Reporting
   ├─ Return RAW → keywords dict
   ├─ Print summary statistics
   └─ Exit with appropriate code
```

### Data Structures

**JPEG to RAW Mapping**:
```python
{
    Path("/exports/DSC00089.jpg"): Path("/photos/2024/DSC00089.ARW"),
    Path("/exports/DSC00090.jpg"): Path("/photos/2024/DSC00090.ARW"),
}
```

**RAW to Keywords Mapping**:
```python
{
    Path("/photos/2024/DSC00089.ARW"): ["landscape", "mountain", "sunset"],
    Path("/photos/2024/DSC00090.ARW"): ["portrait", "indoor", "natural-light"],
}
```

**Gemini Response Format**:
```json
{
    "keywords": ["landscape", "mountain", "sunset", "nature", "outdoor"]
}
```

---

## Error Handling Strategy

### Error Hierarchy

```
Exception
├─ FileNotFoundError (built-in)
│  └─ Used for missing files/directories
│
├─ ValueError (built-in)
│  └─ Used for invalid parameters (e.g., missing API key)
│
├─ subprocess.CalledProcessError (built-in)
│  └─ Used for exiftool failures
│
├─ PipelineError (custom)
│  ├─ No JPEG files found
│  ├─ Missing RAW files
│  └─ General pipeline failures
│
└─ XMPSidecarError (custom)
   └─ Missing XMP sidecars
```

### Error Handling Principles

1. **Fail Fast**: Validate all inputs before making changes
2. **Informative Messages**: List all problematic items
3. **No Partial Updates**: Atomic operations for batch processing
4. **Proper Cleanup**: No temporary files or partial state
5. **Exit Codes**: Proper return codes for shell integration

### Example Error Messages

**Missing RAW Files**:
```
PipelineError: Failed to find RAW files for 2 JPEG(s):
  - DSC00089.jpg
  - DSC00090.jpg
```

**Missing XMP Sidecars**:
```
XMPSidecarError: Missing XMP sidecar files for the following RAW files:
  - /photos/DSC00089.ARW
    Expected: /photos/DSC00089.xmp
  - /photos/DSC00090.ARW
    Expected: /photos/DSC00090.xmp
```

---

## Dependencies

### Python Dependencies

**Core Dependencies**:
- `google-genai>=0.4.0`: Google Gemini AI API client
- `tqdm>=4.66.0`: Progress bars for long operations
- `click>=8.1.0`: CLI argument parsing and formatting

**Standard Library**:
- `pathlib`: Modern path handling
- `subprocess`: exiftool command execution
- `json`: Response parsing
- `base64`: Image encoding
- `os`: Environment variable access

**See**: `pyproject.toml` for complete dependency list

### External Tools

**exiftool**:
- **Purpose**: XMP metadata manipulation
- **Installation**: Via package managers (brew, apt, etc.)
- **Version**: Any recent version (tested with 12.x)
- **Alternative**: None - exiftool is required

**Google Gemini API**:
- **Purpose**: AI-powered keyword generation
- **API Key**: Required (from Google AI Studio)
- **Models**: Supports multiple Gemini models
- **Quota**: Subject to Google's API limits

---

## Testing Strategy

### Test Structure

```
tests/
├── __init__.py
├── test_file_finder.py      # RAW file discovery tests
├── test_keyword_generator.py # AI keyword generation tests
├── test_xmp_tagger.py        # XMP operations tests
└── test_pipeline.py          # End-to-end pipeline tests
```

### Test Coverage

- **Unit Tests**: Each module tested independently
- **Integration Tests**: Pipeline tests with mocked components
- **Mock Strategy**: Mock external dependencies (Gemini API, exiftool)
- **Fixtures**: Temporary directories and files for file operations

### Running Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=photo_keyword_tagger

# Specific module
uv run pytest tests/test_pipeline.py -v

# Single test
uv run pytest tests/test_pipeline.py::test_process_directory_success -v
```

**See**: Individual test files for detailed test documentation

---

## Configuration

### Environment Variables

- `GEMINI_API_KEY`: Gemini API key (required)

### Command-Line Options

See [CLI.md](CLI.md) for complete CLI option documentation.

### Python API Configuration

All functions accept configuration via parameters:

```python
# Full configuration example
results = process_directory(
    jpeg_dir="/path/to/jpegs",
    raw_search_path="/Volumes/Photos",
    taxonomy_path="/path/to/taxonomy.txt",
    api_key="optional-if-env-set",
    model="gemini-flash-lite-latest",
    thinking_budget=8132,
    exiftool_path="exiftool",
    extensions=[".arw", ".dng", ".ARW", ".DNG"],
)
```

---

## Performance Considerations

### Bottlenecks

1. **Gemini API Calls**: ~2-5 seconds per image
   - Rate limited by Google's API quotas
   - Sequential processing (one at a time)

2. **RAW File Search**: Variable (depends on library size)
   - Recursive filesystem traversal
   - Can be slow on network drives

3. **XMP Writing**: ~100ms per file
   - Subprocess overhead
   - Sequential exiftool calls

### Optimization Strategies

**For Large Batches**:
1. Process in smaller chunks (50-100 files)
2. Use specific RAW search paths (year/month folders)
3. Monitor API quota usage
4. Consider caching RAW file locations

**For Network Drives**:
1. Copy JPEGs to local disk first
2. Search local RAW copies if available
3. Use SSD for better search performance

**Future Enhancements**:
- [ ] Parallel keyword generation (multiple API calls)
- [ ] Cached file index for faster RAW searches
- [ ] Batch exiftool operations (single command for all files)

---

## Extension Points

### Adding New RAW Formats

```python
# In file_finder.py or as parameter
extensions = [".arw", ".dng", ".cr2", ".nef", ".raf"]
find_raw_file(jpeg_stem, base_path, extensions=extensions)
```

### Custom Keyword Processing

```python
# Post-process keywords before writing
raw_to_keywords = process_directory(...)

# Filter or transform keywords
for raw_file, keywords in raw_to_keywords.items():
    # Add custom logic here
    filtered_keywords = [k for k in keywords if len(k) > 3]
    raw_to_keywords[raw_file] = filtered_keywords

# Write with custom keywords
batch_add_keywords(raw_to_keywords)
```

### Alternative AI Models

```python
# Use different Gemini model
generate_keywords(
    image_path=jpeg_path,
    taxonomy_path=taxonomy_path,
    model="gemini-2.0-flash-exp",  # or "gemini-1.5-pro"
    thinking_budget=16000,  # Higher for more thorough analysis
)
```

---

## Security Considerations

### API Key Management

- **Never commit API keys** to version control
- Use environment variables (`GEMINI_API_KEY`)
- For production: Use secret management systems
- CLI accepts keys via `--api-key` (use with caution)

### File System Access

- Validates all paths before operations
- No destructive operations on source files
- XMP sidecars modified, never RAW files directly
- Uses `-overwrite_original` to prevent backup clutter

### External Command Execution

- exiftool paths are not sanitized (use trusted paths only)
- Keyword strings are passed as command arguments (no shell expansion)
- Subprocess calls use `check=True` for error detection

---

## Troubleshooting

### Common Issues

**1. "exiftool: command not found"**
- Solution: Install exiftool or provide path via `--exiftool-path`

**2. "Missing XMP sidecar files"**
- Solution: In Lightroom, select photos → `Metadata > Save Metadata to File`

**3. "Failed to find RAW files"**
- Check filename consistency (JPEG and RAW should have same stem)
- Verify RAW search path contains the files
- Try custom extensions if using non-standard RAW formats

**4. Keywords don't appear in Lightroom**
- Solution: `Metadata > Read Metadata from Files` in Lightroom
- Or restart Lightroom to force refresh

**5. Slow performance on network drives**
- Copy files to local disk before processing
- Narrow RAW search path to specific subdirectories

**See**: Individual module documentation for specific troubleshooting

---

## Future Architecture Enhancements

### Planned Features

1. **Lightroom Catalogue Direct Integration**
   - Read from Lightroom SQLite database
   - Write keywords directly to catalogue
   - No need for XMP sidecars

2. **Performance Improvements**
   - Parallel API calls for keyword generation
   - File index caching for faster searches
   - Batch exiftool operations

3. **Additional AI Providers**
   - Support for OpenAI Vision
   - Support for Claude Vision
   - Abstract AI provider interface

4. **Enhanced CLI**
   - Interactive mode for reviewing keywords
   - Dry-run mode (preview without writing)
   - Resume interrupted operations

### Architecture Evolution

The current modular design allows easy extension:
- New modules can be added under `src/photo_keyword_tagger/`
- Existing modules have minimal coupling
- Pipeline can orchestrate new functionality
- Tests ensure backward compatibility

---

## References

### Documentation

- [CLI Guide](CLI.md) - Command-line interface
- [Pipeline Guide](PIPELINE.md) - Automated workflow
- [RAW File Finder](RAW_FILE_FINDER.md) - File discovery
- [XMP Tagging](XMP_TAGGING.md) - Metadata management
- [Implementation Summary](IMPLEMENTATION_SUMMARY.md) - Development history

### External Resources

- [exiftool Documentation](https://exiftool.org/)
- [Google Gemini API](https://ai.google.dev/)
- [XMP Specification](https://www.adobe.com/devnet/xmp.html)
- [Lightroom Metadata](https://helpx.adobe.com/lightroom-classic/help/metadata-basics-actions.html)
