# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pillow",
#     "ReverseBox",
# ]
# ///
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from libnewtheory.archive import unpack
from scripts.tasks.extract_graphics import extract_all_graphics
from scripts.tasks.decompile import decompile_script


def main():
    if os.path.exists("extracted"):
        shutil.rmtree("extracted")
    print("Extracting ISO...")
    source_iso = Path("newtheory.iso")
    if not source_iso.exists():
        sys.stderr.write(f"Source ISO not found: {source_iso}\n")
        sys.exit(1)
    result = subprocess.run(
        ["dumps2iso", "-o", "extracted", "-x", "newtheory.xml", source_iso],
        capture_output=True,
        text=True,
        shell=False,
    )
    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.returncode != 0:
        sys.stderr.write(f"dumps2iso failed with return code {result.returncode}\n")
        if result.stderr:
            sys.stderr.write(f"stderr:\n{result.stderr}\n")
        sys.exit(result.returncode)

    # Copy extracted to translated
    if os.path.exists("translated"):
        shutil.rmtree("translated")
    shutil.copytree("extracted", "translated")
    print("Done!")

    print("Unpacking DATA.BIN...")
    unpack()
    print("Done!")

    print("Extracting graphics...")
    extract_all_graphics()
    print("Done!")

    print("Decompiling SCRIPT.BIN files into .nscript files...")
    script_root = Path("DAT/STAGE")
    decompiled_root = Path("decompiled")
    if Path("decompiled").exists():
        shutil.rmtree("decompiled")

    for source_path in script_root.rglob("SCRIPT.BIN"):
        relative_path = source_path.relative_to(script_root)
        output_path = (decompiled_root / relative_path).with_suffix(".nscript")
        decompile_script(source_path, output_path)
    print("Done!")


if __name__ == "__main__":
    main()
