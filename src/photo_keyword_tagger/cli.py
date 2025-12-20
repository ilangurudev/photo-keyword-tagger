"""Command-line interface for photo keyword tagger."""

import sys
from pathlib import Path

import click

from .pipeline import PipelineError, process_directory


@click.command()
@click.argument(
    "jpeg_dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
)
@click.argument(
    "raw_search_path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
)
@click.argument(
    "taxonomy_path",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
)
@click.option(
    "--api-key",
    type=str,
    envvar="GEMINI_API_KEY",
    help="Gemini API key (can also use GEMINI_API_KEY environment variable)",
)
@click.option(
    "--model",
    type=str,
    default="gemini-flash-lite-latest",
    show_default=True,
    help="Gemini model to use for keyword generation",
)
@click.option(
    "--thinking-budget",
    type=int,
    default=2000,
    show_default=True,
    help="Thinking budget for the model",
)
@click.option(
    "--exiftool-path",
    type=str,
    default="exiftool",
    show_default=True,
    help="Path to exiftool binary",
)
@click.option(
    "--extensions",
    type=str,
    multiple=True,
    help="RAW file extensions to search for (e.g., --extensions .arw --extensions .dng)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
def main(
    jpeg_dir: Path,
    raw_search_path: Path,
    taxonomy_path: Path,
    api_key: str | None,
    model: str,
    thinking_budget: int,
    exiftool_path: str,
    extensions: tuple[str, ...],
    verbose: bool,
):
    """
    Process JPEG files and add AI-generated keywords to their corresponding RAW files.

    \b
    JPEG_DIR: Directory containing JPEG files to process
    RAW_SEARCH_PATH: Base directory to search for corresponding RAW files
    TAXONOMY_PATH: Path to the Lightroom keyword taxonomy txt file

    \b
    Example:
        photo-keyword-tagger /path/to/exports /Volumes/T7/Pictures /path/to/taxonomy.txt
    """
    try:
        # Convert extensions tuple to list if provided
        extensions_list = list(extensions) if extensions else None

        # Validate API key
        if not api_key:
            click.echo(
                "Error: API key not provided. Set GEMINI_API_KEY environment variable "
                "or use --api-key option.",
                err=True,
            )
            sys.exit(1)

        if verbose:
            click.echo("Starting photo keyword tagger pipeline...")
            click.echo(f"JPEG directory: {jpeg_dir}")
            click.echo(f"RAW search path: {raw_search_path}")
            click.echo(f"Taxonomy file: {taxonomy_path}")
            click.echo(f"Model: {model}")
            if extensions_list:
                click.echo(f"Extensions: {', '.join(extensions_list)}")

        # Run the pipeline
        results = process_directory(
            jpeg_dir=jpeg_dir,
            raw_search_path=raw_search_path,
            taxonomy_path=taxonomy_path,
            api_key=api_key,
            model=model,
            thinking_budget=thinking_budget,
            exiftool_path=exiftool_path,
            extensions=extensions_list,
        )

        # Success message
        click.echo(
            click.style(f"\n✓ Successfully processed {len(results)} files!", fg="green", bold=True)
        )

        if verbose:
            click.echo("\nProcessed files:")
            for raw_file, keywords in results.items():
                click.echo(f"  {raw_file.name}: {len(keywords)} keywords")

    except PipelineError as e:
        click.echo(f"Pipeline error: {e}", err=True)
        sys.exit(1)
    except FileNotFoundError as e:
        click.echo(f"File not found: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
