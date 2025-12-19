# AGENTS.md

## Project Overview
Photo Keyword Tagger is a Python package designed to help photographers and digital asset managers efficiently manage their Adobe Lightroom catalogues by automatically adding keywords to collections of photos.

## Development Guidelines

### Architecture
- **Package Structure**: Modern Python package using `src` layout
- **Build System**: UV package manager for fast, reliable dependency management
- **Testing**: pytest for unit and integration tests

### Key Components (Planned)
1. **Lightroom Catalogue Interface**: Module to read and write Lightroom catalogue data
2. **Keyword Management**: Core functionality for managing and applying keywords
3. **Batch Processing**: Efficient processing of photo collections
4. **AI/ML Integration** (future): Automatic keyword suggestion based on image content

### Development Workflow
1. Use `uv` for all dependency management
2. Run tests with `pytest` before committing
3. Follow PEP 8 style guidelines
4. Type hints required for all public APIs

### Testing Strategy
- Unit tests for all core functionality
- Integration tests for Lightroom catalogue operations
- Mock external dependencies where appropriate

### Dependencies
- To be determined based on features implemented

## AI Agent Instructions
When working on this project:
1. Maintain the `src` layout structure
2. Add new modules under `src/photo_keyword_tagger/`
3. Keep test coverage high (aim for >80%)
4. Document all public APIs with docstrings
5. Update README.md with new features
6. Use type hints consistently

