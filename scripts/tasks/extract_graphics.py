import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from libnewtheory.graphics import extract_graphics


# Map of graphics files to extract (name without .TM2 suffix -> source path in DATA)
GRAPHICS_FILES = {
    "E_ICON": "DAT/EFFECT/CMN2D/EMOTION/E_ICON.TM2",
    "ENDTXT_0": "DAT/EVENTCG/ENDING/STAFFROLL/ENDTXT_0.TM2",
    "ENDTXT_1": "DAT/EVENTCG/ENDING/STAFFROLL/ENDTXT_1.TM2",
    "ENDTXT_2": "DAT/EVENTCG/ENDING/STAFFROLL/ENDTXT_2.TM2",
    "ENDTXT_3": "DAT/EVENTCG/ENDING/STAFFROLL/ENDTXT_3.TM2",
    "ENDTXT_4": "DAT/EVENTCG/ENDING/STAFFROLL/ENDTXT_4.TM2",
    "ENDTXT_5": "DAT/EVENTCG/ENDING/STAFFROLL/ENDTXT_5.TM2",
    "ENDTXT_6": "DAT/EVENTCG/ENDING/STAFFROLL/ENDTXT_6.TM2",
    "ENDTXT_7": "DAT/EVENTCG/ENDING/STAFFROLL/ENDTXT_7.TM2",
    "ENDTXT_8": "DAT/EVENTCG/ENDING/STAFFROLL/ENDTXT_8.TM2",
    "ENDTXT_9": "DAT/EVENTCG/ENDING/STAFFROLL/ENDTXT_9.TM2",
    "OP_7": "DAT/FRAME/MENU/OP07.TM2",
    "ST_A_0": "DAT/FRAME/EVENT/ST_A_0.TM2",
    "ST_A_1": "DAT/FRAME/EVENT/ST_A_1.TM2",
    "ST_B_0": "DAT/FRAME/EVENT/ST_B_0.TM2",
    "ST_B_1": "DAT/FRAME/EVENT/ST_B_1.TM2",
    "ST_C_0": "DAT/FRAME/EVENT/ST_C_0.TM2",
    "ST_C_1": "DAT/FRAME/EVENT/ST_C_1.TM2",
    "ST_D_0": "DAT/FRAME/EVENT/ST_D_0.TM2",
    "ST_D_1": "DAT/FRAME/EVENT/ST_D_1.TM2",
    "ST_SUB": "DAT/FRAME/MENU/ST_SUB.TM2",
    "TL_005": "DAT/FRAME/TITLE/TL_005.TM2",
    "TL_006": "DAT/FRAME/TITLE/TL_006.TM2",
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
