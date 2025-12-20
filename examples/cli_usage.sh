#!/bin/bash
# Example usage of the photo-keyword-tagger CLI

# Set your Gemini API key (or export in your shell profile)
export GEMINI_API_KEY="your-api-key-here"

# Basic usage: Process JPEG files and tag their corresponding RAW files
photo-keyword-tagger \
    /path/to/exported/jpegs \
    /Volumes/T7/Pictures \
    /path/to/lightroom_taxonomy.txt

# Use a different model
photo-keyword-tagger \
    --model gemini-2.0-flash-exp \
    /path/to/exported/jpegs \
    /Volumes/T7/Pictures \
    /path/to/lightroom_taxonomy.txt

# Specify custom RAW file extensions to search for
photo-keyword-tagger \
    --extensions .arw --extensions .dng --extensions .cr2 \
    /path/to/exported/jpegs \
    /Volumes/T7/Pictures \
    /path/to/lightroom_taxonomy.txt

# Adjust thinking budget for more/less thorough analysis
photo-keyword-tagger \
    --thinking-budget 16000 \
    /path/to/exported/jpegs \
    /Volumes/T7/Pictures \
    /path/to/lightroom_taxonomy.txt

# Use custom exiftool path
photo-keyword-tagger \
    --exiftool-path /usr/local/bin/exiftool \
    /path/to/exported/jpegs \
    /Volumes/T7/Pictures \
    /path/to/lightroom_taxonomy.txt

# Enable verbose output to see detailed progress
photo-keyword-tagger -v \
    /path/to/exported/jpegs \
    /Volumes/T7/Pictures \
    /path/to/lightroom_taxonomy.txt

# Get help
photo-keyword-tagger --help

# Run as a Python module (alternative to console script)
python -m photo_keyword_tagger \
    /path/to/exported/jpegs \
    /Volumes/T7/Pictures \
    /path/to/lightroom_taxonomy.txt
