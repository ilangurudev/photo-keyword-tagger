"""
Basic usage example for photo_keyword_tagger.

Before running this script:
1. Install dependencies: uv sync
2. Set your Gemini API key: export GEMINI_API_KEY="your-api-key"
3. Update the paths below to point to your image and taxonomy file
"""

from pathlib import Path

from photo_keyword_tagger import generate_keywords


def main():
    """Generate keywords for an example image."""
    # Update these paths to point to your actual files
    image_path = Path("path/to/your/image.jpg")
    taxonomy_path = Path("examples/sample_taxonomy.txt")

    # Check if files exist
    if not image_path.exists():
        print(f"Error: Image file not found at {image_path}")
        print("Please update the image_path in this script to point to an actual image.")
        return

    if not taxonomy_path.exists():
        print(f"Error: Taxonomy file not found at {taxonomy_path}")
        print("Please ensure the taxonomy file exists or export one from Lightroom.")
        return

    print(f"Analyzing image: {image_path}")
    print(f"Using taxonomy: {taxonomy_path}")
    print("Generating keywords with Gemini AI...")

    try:
        keywords = generate_keywords(
            image_path=image_path,
            taxonomy_path=taxonomy_path,
        )

        print(f"\n✅ Generated {len(keywords)} keywords:")
        for keyword in keywords:
            print(f"  - {keyword}")

    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure to set your GEMINI_API_KEY environment variable:")
        print('  export GEMINI_API_KEY="your-api-key"')

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
