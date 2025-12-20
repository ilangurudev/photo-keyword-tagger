"""Keyword generation using Google Gemini AI."""

import base64
import json
import os
from pathlib import Path

from google import genai
from google.genai import types


def generate_keywords(
    image_path: str | Path,
    taxonomy_path: str | Path,
    api_key: str | None = None,
    model: str = "gemini-flash-lite-latest",
    thinking_budget: int = 8132,
) -> list[str]:
    """
    Generate keywords for an image based on a Lightroom keyword taxonomy.

    Args:
        image_path: Path to the image file
        taxonomy_path: Path to the Lightroom keyword taxonomy txt file
        api_key: Gemini API key (defaults to GEMINI_API_KEY environment variable)
        model: Gemini model to use
        thinking_budget: Thinking budget for the model

    Returns:
        List of keywords extracted from the image

    Raises:
        FileNotFoundError: If image or taxonomy file doesn't exist
        ValueError: If API key is not provided
    """
    # Convert paths to Path objects
    image_path = Path(image_path)
    taxonomy_path = Path(taxonomy_path)

    # Validate files exist
    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")
    if not taxonomy_path.exists():
        raise FileNotFoundError(f"Taxonomy file not found: {taxonomy_path}")

    # Get API key
    if api_key is None:
        api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("API key must be provided or set in GEMINI_API_KEY environment variable")

    # Read and encode image
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    # Determine image MIME type
    mime_type = _get_mime_type(image_path)

    # Read taxonomy
    with open(taxonomy_path) as f:
        taxonomy_content = f.read()

    # Create the prompt
    prompt = f"""I have a keyword taxonomy that I use in my lightroom catalog. I will share an image and you must return the applicable "leaf" keywords.

Keyword Taxonomy:
{taxonomy_content}

Instructions:
1. Carefully analyze the image content, including subjects, locations, actions, colors, mood, composition, and any other relevant details
2. Select ONLY keywords from the provided taxonomy that accurately describe the image
3. Choose keywords that are specific and DIRECTLY relevant - don't include generic keywords unless they truly apply.
   For instance, all pictures might have a light source but unless a picture's main subject is that, it doesn't apply
4. In each category, choose atmost two keywords. Keep the total number of keywords to around 5-6 most important keywords and a maximum of 10.
5. Return your response as a JSON object with a single key "keywords" containing an array of keyword strings
6. Use the spellings and casing as it is from the taxonomy.

Example response format:
{{"keywords": ["landscape", "mountain", "sunset", "nature", "outdoor"]}}

Start by describing what the photo is about in a few sentences in your thoughts. For instance, "This is a street photography shot of a person walking on a street. It seems to be composed with the rule of thirds but this is not prominent enough. The colors are very pastel."
Then select the most important keywords from the taxonomy in your response. For instance, "street photography", "dreamy", "walking".

Now analyze the image and provide the keywords. """

    # Create Gemini client
    client = genai.Client(api_key=api_key)

    # Prepare content with image
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_bytes(
                    data=base64.b64decode(image_data),
                    mime_type=mime_type,
                ),
                types.Part.from_text(text=prompt),
            ],
        ),
    ]

    # Configure generation
    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_budget=thinking_budget,
        ),
        response_mime_type="application/json",
    )

    # Generate keywords
    response_text = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if chunk.text:
            response_text += chunk.text

    # Parse JSON response
    try:
        result = json.loads(response_text)
        keywords = result.get("keywords", [])
        return keywords
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse Gemini response as JSON: {response_text}") from e


def _get_mime_type(image_path: Path) -> str:
    """
    Determine MIME type from file extension.

    Args:
        image_path: Path to the image file

    Returns:
        MIME type string
    """
    extension = image_path.suffix.lower()
    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".bmp": "image/bmp",
        ".tiff": "image/tiff",
        ".tif": "image/tiff",
    }
    return mime_types.get(extension, "image/jpeg")
