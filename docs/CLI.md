# Command-Line Interface Guide

The `photo-keyword-tagger` CLI provides a convenient way to process photos directly from the command line without writing any Python code.

## Installation

After installing the package, the CLI becomes available as a command:

```bash
# Install the package
uv sync  # or pip install -e .

# The photo-keyword-tagger command is now available
photo-keyword-tagger --help
```

## Basic Usage

The CLI requires three positional arguments:

1. **JPEG_DIR**: Directory containing JPEG files to process
2. **RAW_SEARCH_PATH**: Base directory to search for corresponding RAW files
3. **TAXONOMY_PATH**: Path to your Lightroom keyword taxonomy file

```bash
# Set your API key
export GEMINI_API_KEY="your-api-key-here"

# Run the CLI
photo-keyword-tagger \
    /path/to/exported/jpegs \
    /Volumes/T7/Pictures \
    /path/to/lightroom_taxonomy.txt
```

## Options

### API Key

```bash
# Use environment variable (recommended)
export GEMINI_API_KEY="your-api-key-here"
photo-keyword-tagger /jpegs /raw /taxonomy.txt

# Or pass directly (not recommended for security)
photo-keyword-tagger --api-key "your-api-key" /jpegs /raw /taxonomy.txt
```

### Model Selection

Choose which Gemini model to use:

```bash
photo-keyword-tagger \
    --model gemini-2.0-flash-exp \
    /path/to/jpegs /path/to/raw /path/to/taxonomy.txt
```

Available models:
- `gemini-flash-lite-latest` (default) - Fast and efficient
- `gemini-2.0-flash-exp` - Latest experimental features
- `gemini-1.5-pro` - More thorough analysis

### Thinking Budget

Control how much "thinking" the AI model does (affects quality and speed):

```bash
photo-keyword-tagger \
    --thinking-budget 16000 \
    /path/to/jpegs /path/to/raw /path/to/taxonomy.txt
```

- Lower values (e.g., 4000): Faster, less thorough
- Default: 8132
- Higher values (e.g., 16000): Slower, more thorough

### RAW File Extensions

Specify which RAW file formats to search for:

```bash
photo-keyword-tagger \
    --extensions .arw --extensions .dng --extensions .cr2 \
    /path/to/jpegs /path/to/raw /path/to/taxonomy.txt
```

Default extensions: `.arw`, `.dng`, `.ARW`, `.DNG`

### ExifTool Path

If exiftool is not in your PATH, specify its location:

```bash
photo-keyword-tagger \
    --exiftool-path /usr/local/bin/exiftool \
    /path/to/jpegs /path/to/raw /path/to/taxonomy.txt
```

### Verbose Output

Enable detailed progress information:

```bash
photo-keyword-tagger -v \
    /path/to/jpegs /path/to/raw /path/to/taxonomy.txt
```

This shows:
- Configuration details
- File-by-file processing information
- Keyword counts for each file

## Examples

### Simple Processing

Process photos with default settings:

```bash
export GEMINI_API_KEY="your-key"
photo-keyword-tagger \
    ~/Desktop/exported-jpegs \
    /Volumes/Photos/Lightroom \
    ~/Documents/lr-taxonomy.txt
```

### Custom Configuration

Use specific model and extensions:

```bash
photo-keyword-tagger \
    --model gemini-2.0-flash-exp \
    --thinking-budget 12000 \
    --extensions .arw --extensions .ARW \
    --verbose \
    ~/Desktop/exported-jpegs \
    /Volumes/Photos/Lightroom \
    ~/Documents/lr-taxonomy.txt
```

### Multiple Projects

Process different photo collections:

```bash
# Travel photos
photo-keyword-tagger \
    ~/exports/travel \
    /Volumes/Photos/2024/Travel \
    ~/Documents/lr-taxonomy.txt

# Portrait sessions
photo-keyword-tagger \
    ~/exports/portraits \
    /Volumes/Photos/2024/Portraits \
    ~/Documents/lr-taxonomy.txt
```

## Running as a Module

You can also run the CLI as a Python module:

```bash
python -m photo_keyword_tagger \
    /path/to/jpegs \
    /path/to/raw \
    /path/to/taxonomy.txt
```

This is useful when:
- The console script isn't available
- You're using a virtual environment
- You need to test development changes

## Error Handling

The CLI provides clear error messages for common issues:

### Missing API Key
```
Error: API key not provided. Set GEMINI_API_KEY environment variable or use --api-key option.
```

### Missing JPEG Files
```
Pipeline error: No JPEG files found in /path/to/directory
```

### Missing RAW Files
```
Pipeline error: Failed to find RAW files for 3 JPEG(s):
  - DSC00089.jpg
  - DSC00090.jpg
  - DSC00091.jpg
```

### Missing XMP Sidecars
```
XMP sidecar error: Missing XMP sidecars for 2 file(s):
  - /Volumes/Photos/DSC00089.ARW
  - /Volumes/Photos/DSC00090.ARW
```

## Exit Codes

- `0`: Success
- `1`: Error (pipeline error, file not found, etc.)

## Tips

1. **Test with a small directory first**: Process a few photos to verify everything works before running on large collections

2. **Use verbose mode for debugging**: The `-v` flag helps identify issues

3. **Check XMP sidecars exist**: Before running, ensure you've created XMP sidecars in Lightroom (`Metadata > Save Metadata to File`)

4. **Monitor API usage**: The CLI makes one API call per JPEG file

5. **Consider batch sizes**: For very large collections, process in smaller batches to track progress

## Integration with Shell Scripts

You can integrate the CLI into shell scripts:

```bash
#!/bin/bash

# Process multiple directories
for dir in ~/exports/*/; do
    echo "Processing $dir..."
    photo-keyword-tagger \
        "$dir" \
        /Volumes/Photos \
        ~/taxonomy.txt
done

echo "All directories processed!"
```

## See Also

- [Pipeline Guide](PIPELINE.md) - Understanding the processing pipeline
- [XMP Tagging Guide](XMP_TAGGING.md) - Details on XMP sidecar handling
- [Main README](../README.md) - Full documentation
