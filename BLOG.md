---
title: "I Built a Photo Keywording Tool in a Weekend"
description: "Using AI to build a real tool with tests, linting, and all the things that used to feel like overhead."
pubDate: 2024-12-20
tags: ["ai", "python", "photography", "llm", "software-development"]
---

# I Built a Photo Keywording Tool in a Weekend

I have around 15,000 photos in my Lightroom catalog. Most of them have zero keywords. Searching for "that sunset shot from last year" means scrolling through months of thumbnails hoping my brain recognizes it before my eyes give out.

So I built a tool that uses AI to automatically keyword my photos based on my existing Lightroom taxonomy.

It took a weekend. And it has tests. And pre-commit hooks. And a CLI. The kind of stuff that used to feel like overkill for a personal project.

## The Real Story Here

This isn't really a post about photo management. It's about how much easier it's become to build things.

A year ago, I would have looked at this problem and thought:
- "I'd need to figure out how to read XMP metadata"
- "I'd have to learn some image analysis library"
- "Writing tests would double the time"
- "Setting up linting and pre-commit feels like overkill for a personal project"

And I probably would have given up before starting.

Now? I built the whole thing by having a conversation with an AI and being very opinionated about how I wanted each piece to work.

## The Opinionated Workflow

Here's what I've learned about building with AI: don't try to offload the whole thing. Break it down. Be specific. Direct the AI piece by piece.

My workflow looked like this:

**Step 1:** "Build me a keyword generator using Gemini Flash. It takes an image file and a taxonomy file, and returns keywords from that taxonomy."

**Step 2:** "Now build a file finder that takes a JPEG filename and finds the corresponding RAW file (ARW or DNG) somewhere in a search directory."

**Step 3:** "Now build an XMP tagger that appends keywords to the existing keywords in an XMP sidecar file using exiftool."

**Step 4:** "Now wire these together into a pipeline that processes an entire directory."

**Step 5:** "Add a CLI."

Each step was a focused conversation. Each step produced working, tested code. By the end, I had a complete tool—not because I asked for "a photo keywording tool," but because I guided the construction of each brick in the wall.

## The Three-Step Core

The actual workflow is pretty simple:

### 1. Find the XMP File

When you export JPEGs from Lightroom for review, you lose the connection to the original RAW file. My tool finds it:

```python
def find_raw_file(jpeg_path, base_path, extensions=None):
    """Find the source RAW file given a JPEG filename."""
    jpeg_stem = Path(jpeg_path).stem  # "DSC00089"
    for ext in extensions or [".arw", ".dng", ".ARW", ".DNG"]:
        matches = list(base_path.glob(f"**/{jpeg_stem}{ext}"))
        if matches:
            return matches[0]
    return None
```

This recursively searches your photo library to find `DSC00089.ARW` when you give it `DSC00089.jpg`. Simple, but exactly what I needed.

### 2. Generate Keywords with AI

I feed Gemini the image along with my actual Lightroom taxonomy:

```python
prompt = """I have a keyword taxonomy from my Lightroom catalog.
Analyze this image and return applicable keywords.

Keyword Taxonomy:
{taxonomy_content}

Instructions:
1. Analyze the image content—subjects, locations, mood, composition
2. Select ONLY keywords from the provided taxonomy
3. Keep to 5-6 most important keywords, max 10
4. Return as JSON: {"keywords": ["landscape", "sunset", ...]}
"""
```

The key insight: I'm not asking the AI to invent keywords. I'm asking it to **select from my existing taxonomy.** This keeps everything consistent with how I already organize my library.

### 3. Write to XMP

The final step appends keywords to the XMP sidecar using exiftool:

```python
def add_keywords_to_xmp(xmp_file, keywords, exiftool_path="exiftool"):
    cmd = [exiftool_path, "-overwrite_original"]
    for keyword in keywords:
        cmd.append(f"-XMP-dc:Subject+={keyword}")
    cmd.append(str(xmp_file))
    subprocess.run(cmd, capture_output=True, text=True, check=True)
```

The `+=` syntax appends to existing keywords rather than replacing them. So any manual keywords you've already added stay intact.

## The Part That Would Have Stopped Me Before

Here's my `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: detect-private-key

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.4
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
```

Every commit runs linting, formatting, and the full test suite. If tests fail, the commit fails.

A year ago, setting this up would have felt like overkill for a weekend project. Now? I asked the AI to set it up and it was done in minutes. The "professional" touches that used to add days of friction now add minutes.

These touches matter more than you'd think. When the AI introduces a regression (and it does), the tests catch it. When I come back to this code in six months, the consistent formatting means I can actually read it.

## Tests That Actually Test Things

The test suite mocks external dependencies (no real Gemini API calls, no real exiftool) and tests the logic:

```python
@patch("photo_keyword_tagger.pipeline.generate_keywords")
@patch("photo_keyword_tagger.pipeline.batch_add_keywords")
def test_process_directory_success(mock_batch_add, mock_generate, ...):
    """Test that process_directory successfully processes files."""
    # Create temp JPEG and taxonomy files
    # Mock the RAW file finder and XMP checker
    # Mock keyword generation to return ["keyword1", "keyword2"]

    results = process_directory(
        jpeg_dir=jpeg_dir,
        raw_search_path=raw_dir,
        taxonomy_path=taxonomy_file,
        api_key="fake-api-key",
    )

    assert len(results) == 1
    assert results[mock_raw_file] == ["keyword1", "keyword2"]
```

These tests aren't just for show. They saved me multiple times when changes to one module broke assumptions in another.

## How I Actually Use It

```bash
# Export a folder of JPEGs from Lightroom (small size, just for AI analysis)
# Then run:

export GEMINI_API_KEY="your-key-here"

photo-keyword-tagger \
    /path/to/exported/jpegs \
    /Volumes/T7/Pictures \
    /path/to/my-taxonomy.txt
```

It finds the RAW files, checks they have XMP sidecars, generates keywords, and writes them. Then I go back to Lightroom, select the photos, and hit "Read Metadata from Files."

That's it. Now I can actually search my library.

## The Honest Part

A few observations from doing this:

**You still need to know what you're building.** I knew I needed to find files, call an API, and write XMP metadata. The AI helped me execute each step faster, but I still designed the architecture.

**Step-by-step beats "build me an app."** When I tried to describe the whole tool at once, the results were messy. When I broke it into focused pieces, each piece was clean.

**Tests are your safety net.** The AI makes mistakes. It will change something that breaks something else. Tests catch this. Without them, you're debugging mystery regressions.

**The "professional touches" are worth it.** Pre-commit hooks, linting, type hints—these used to feel like enterprise overhead. Now they're table stakes because they cost almost nothing to set up.

## What This Means

For complex systems, you still need real engineering. But for tools like this—personal utilities that solve specific problems—the friction is a lot lower than it used to be.

I spent years not building things because the setup cost felt too high. Now I can build things in weekends that would have taken weeks, and they end up better because I can afford to include the "optional" quality stuff that I would have skipped before.

If you've been sitting on an idea because "it would take too long" or "it's not worth the setup"—maybe give it a shot. Break it into pieces. Direct the AI step by step. Add the tests and the linting because they're basically free now.

---

*The code is at [github.com/ilangurudev/photo-keyword-tagger](https://github.com/ilangurudev/photo-keyword-tagger). It's a real tool I actually use, not a demo.*
