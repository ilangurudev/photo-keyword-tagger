"""Example of using the complete pipeline to process a directory of JPEGs."""

from photo_keyword_tagger import process_directory

# Example configuration
JPEG_DIR = "/path/to/exported/jpegs"
RAW_SEARCH_PATH = "/Volumes/T7/Pictures"
TAXONOMY_PATH = "/path/to/taxonomy.txt"

# Optional: Set API key explicitly (or use GEMINI_API_KEY environment variable)
# API_KEY = "your-api-key-here"

if __name__ == "__main__":
    try:
        # Process the directory
        results = process_directory(
            jpeg_dir=JPEG_DIR,
            raw_search_path=RAW_SEARCH_PATH,
            taxonomy_path=TAXONOMY_PATH,
            # api_key=API_KEY,  # Optional: if not using environment variable
            # model="gemini-flash-lite-latest",  # Optional: customize model
            # thinking_budget=8132,  # Optional: customize thinking budget
        )

        # Display results
        print("\n" + "=" * 80)
        print("PROCESSING COMPLETE")
        print("=" * 80)
        print(f"\nProcessed {len(results)} files:")

        for raw_file, keywords in results.items():
            print(f"\n{raw_file.name}:")
            print(f"  Keywords: {', '.join(keywords)}")

    except Exception as e:
        print(f"\nError: {e}")
        exit(1)
