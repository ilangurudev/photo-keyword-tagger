"""Quick test to demonstrate the exiftool command format fix."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from photo_keyword_tagger.xmp_tagger import add_keywords_to_xmp


# Create a temporary test
def test_command_format():
    """Show the actual command that gets executed."""

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        # Simulate adding multiple keywords
        xmp_file = Path("/tmp/test.xmp")
        xmp_file.touch()

        keywords = ["landscape", "sunset", "nature"]
        add_keywords_to_xmp(xmp_file, keywords)

        # Get the actual command that was executed
        call_args = mock_run.call_args
        cmd = call_args[0][0]

        print("\n" + "=" * 60)
        print("EXIFTOOL COMMAND FORMAT")
        print("=" * 60)
        print("\nCommand as list:")
        for i, arg in enumerate(cmd):
            print(f"  [{i}] {arg}")

        print("\nCommand as string:")
        print(f"  {' '.join(cmd)}")

        print("\n" + "=" * 60)
        print("EXPLANATION")
        print("=" * 60)
        print("\n❌ OLD (incorrect) approach:")
        print('   exiftool -overwrite_original -XMP-dc:Subject+="landscape,sunset,nature" file.xmp')
        print("   This treats the entire string as ONE keyword\n")

        print("✅ NEW (correct) approach:")
        print("   exiftool -overwrite_original \\")
        print("     -XMP-dc:Subject+=landscape \\")
        print("     -XMP-dc:Subject+=sunset \\")
        print("     -XMP-dc:Subject+=nature \\")
        print("     file.xmp")
        print("   Each keyword gets its own -XMP-dc:Subject+= argument\n")

        print("=" * 60)

        # Cleanup
        xmp_file.unlink()


if __name__ == "__main__":
    test_command_format()
