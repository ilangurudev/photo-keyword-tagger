# Photo Keyword Tagger

A Python package for managing Lightroom catalogues by adding keywords to collections of photos.

## Overview

Photo Keyword Tagger simplifies the process of organizing and tagging large collections of photos in Adobe Lightroom. Whether you're a professional photographer, photo enthusiast, or digital asset manager, this tool helps you efficiently manage and categorize your photo library.

## Features

🚧 **Currently in early development**

Planned features:
- Batch keyword application to photo collections
- Lightroom catalogue integration
- Smart keyword suggestions
- Flexible keyword management system
- Command-line interface
- Python API for custom workflows

## Installation

### From Source (Development)

```bash
# Clone the repository
git clone https://github.com/yourusername/photo-keyword-tagger.git
cd photo-keyword-tagger

# Install with uv
uv pip install -e .
```

### From PyPI (Coming Soon)

```bash
pip install photo-keyword-tagger
```

## Quick Start

```python
from photo_keyword_tagger import hello

# Basic example (demonstration only)
print(hello())
```

## Development

### Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Project Structure

```
photo-keyword-tagger/
├── src/
│   └── photo_keyword_tagger/
│       ├── __init__.py
│       └── hello_world.py
├── tests/
│   ├── __init__.py
│   └── test_hello_world.py
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

- [ ] Core Lightroom catalogue reading functionality
- [ ] Keyword management system
- [ ] Batch processing engine
- [ ] CLI interface
- [ ] Documentation
- [ ] PyPI release

## Support

For issues, questions, or contributions, please open an issue on GitHub.

