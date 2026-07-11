import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from libnewtheory.graphics import extract_graphics


# Map of graphics files to extract (name without .TM2 suffix -> source path in DATA)
GRAPHICS_FILES = {
    "E_ICON": "DAT/EFFECT/CMN2D/EMOTION/E_ICON.TM2",
    "OP_7": "DAT/FRAME/MENU/OP07.TM2"
}


def extract_all_graphics():
    """Extract graphics from all .TM2 files."""
    print("\nExtracting graphics from .TM2 files...")

    # Create graphics/orig directory
    graphics_orig = Path("graphics/orig")
    if graphics_orig.exists():
        shutil.rmtree(graphics_orig)
    graphics_orig.mkdir(parents=True, exist_ok=True)

    # Copy .TM2 files to graphics/orig
    for name, source_path in GRAPHICS_FILES.items():
        source = Path(source_path)
        if source.exists():
            dest = graphics_orig / f"{name}.TM2"
            print(f"Copying {source} to {dest}")
            shutil.copy2(source, dest)
        else:
            print(f"Warning: {source} not found, skipping")

    # Extract graphics from each file
    for name in GRAPHICS_FILES.keys():
        tim2_file = graphics_orig / f"{name}.TM2"
        if tim2_file.exists():
            print(f"\nExtracting {name}...")
            extract_graphics(tim2_file)

    print("\nGraphics extraction complete!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_graphic.py <filepath> [frame]")
        sys.exit(1)

    filepath = sys.argv[1]

    extract_graphics(filepath)
