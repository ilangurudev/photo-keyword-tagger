# AGENTS.md

## Project Overview

Photo Keyword Tagger is a Python package that automates adding AI-generated keywords to RAW photo files in Lightroom Classic. It processes exported JPEGs, uses Google Gemini AI to generate keywords based on your Lightroom taxonomy, and writes them to RAW files via XMP sidecar files.

**Status**: Production-ready with CLI and Python API interfaces.

## Quick Reference

### Core Capabilities
- **Complete Pipeline**: Single-function processing of entire JPEG directories
- **AI Keyword Generation**: Google Gemini-powered analysis using your taxonomy
- **RAW File Discovery**: Locate source RAW files from exported JPEG filenames
- **XMP Tagging**: Write keywords to RAW files via exiftool
- **CLI Tool**: `photo-keyword-tagger` command for quick processing

### Package Structure
```
src/photo_keyword_tagger/
├── __init__.py           # Public API exports
├── __main__.py           # Module entry point (python -m)
├── cli.py                # Command-line interface
├── pipeline.py           # Complete automated workflow
├── keyword_generator.py  # AI keyword generation (Gemini)
├── file_finder.py        # RAW file location/search
└── xmp_tagger.py         # XMP sidecar management (exiftool)
```

### Key Modules

**Pipeline** (`pipeline.py`): Orchestrates complete workflow
- `process_directory()`: Main entry point - processes entire directories

**File Finder** (`file_finder.py`): Locates RAW files
- `find_raw_file()`: Find single RAW from JPEG stem
- `find_raw_files()`: Batch finding for multiple files

**Keyword Generator** (`keyword_generator.py`): AI-powered analysis
- `generate_keywords()`: Analyze image and return taxonomy-based keywords

**XMP Tagger** (`xmp_tagger.py`): Metadata management
- `batch_add_keywords()`: Write keywords to multiple files atomically
- `ensure_xmp_sidecars()`: Validate XMP files exist before processing

## Development Guidelines

### Architecture Principles
- **Modular Design**: Each component has single responsibility
- **Fail-Fast**: Validate all inputs before making changes
- **Atomic Operations**: All-or-nothing for batch processing
- **Progress Tracking**: Real-time feedback for long operations
- **Type Safety**: Type hints required for all public APIs

### Build System
- **Package Manager**: UV (fast, reliable dependency management)
- **Python Version**: 3.12+
- **Layout**: Modern `src/` layout structure
- **Testing**: pytest with >80% coverage target

### Dependencies
- `google-genai`: Gemini AI API client
- `tqdm`: Progress bars
- `click`: CLI framework
- `exiftool`: External tool for XMP manipulation (must be installed separately)

### Workflow
1. **Development**: `uv sync` to install/update dependencies
2. **Testing**: `uv run pytest` before committing
3. **Linting**: Follow PEP 8, use type hints
4. **Documentation**: Update docstrings and relevant docs

### Code Standards
- Use `pathlib.Path` for all file operations
- Return types should be explicit (not implicit None)
- Document all public functions with docstrings (Google style)
- Handle errors with appropriate exceptions (PipelineError, XMPSidecarError)
- Use descriptive variable names (no abbreviations)

## Testing Strategy

### Test Structure
```
tests/
├── test_pipeline.py           # End-to-end workflow tests
├── test_keyword_generator.py  # AI generation tests (mocked)
├── test_file_finder.py        # File discovery tests
└── test_xmp_tagger.py         # XMP operations tests
```

### Test Principles
- **Unit Tests**: Test each module independently
- **Integration Tests**: Pipeline tests with mocked external deps
- **Mock External APIs**: Never call real Gemini API in tests
- **Mock Subprocesses**: Mock exiftool calls for consistency
- **Use Fixtures**: Temporary directories for file operations

### Running Tests
```bash
uv run pytest                    # All tests
uv run pytest --cov              # With coverage
uv run pytest path/to/test.py -v  # Specific tests
```

## AI Agent Instructions

When working on this project:

1. **Maintain Structure**: Keep `src/` layout, add modules under `src/photo_keyword_tagger/`
2. **Update Tests**: Add/update tests for any code changes
3. **Documentation**: Update relevant files in `docs/` for significant changes
4. **Type Hints**: Always use type hints for function signatures
5. **Error Handling**: Use appropriate custom exceptions (PipelineError, XMPSidecarError)
6. **Progress Feedback**: Use tqdm for operations >1 second
7. **Validation**: Validate inputs early, fail fast with clear messages

## Detailed Documentation

For in-depth information, see:

- **[README.md](../README.md)**: User-facing guide with installation and usage
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)**: Complete system architecture and design
- **[PIPELINE.md](docs/PIPELINE.md)**: Automated workflow details
- **[CLI.md](docs/CLI.md)**: Command-line interface guide
- **[XMP_TAGGING.md](docs/XMP_TAGGING.md)**: XMP sidecar management
- **[RAW_FILE_FINDER.md](docs/RAW_FILE_FINDER.md)**: File discovery details
- **[IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md)**: Development history

## Common Tasks

### Adding a New Feature
1. Create module in `src/photo_keyword_tagger/`
2. Add tests in `tests/test_<module>.py`
3. Export public API in `__init__.py`
4. Document in appropriate `docs/*.md` file
5. Update README.md if user-facing

### Modifying Existing Module
1. Update code with type hints
2. Update/add tests to maintain coverage
3. Run `uv run pytest` to verify
4. Update module docstrings
5. Update relevant docs if behavior changes

### Adding External Dependencies
1. Add to `pyproject.toml` under `dependencies`
2. Run `uv sync` to update lock file
3. Document in ARCHITECTURE.md if significant
4. Ensure tests mock external calls
