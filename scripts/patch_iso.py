# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-api-python-client",
#     "google-auth",
#     "pillow",
# ]
# ///
import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
#sys.path.insert(0, str(Path(__file__).resolve().parent))


PATCHED_ISO = "english.iso"




def generate_translated_xml(in_xml: str, out_xml: str):
    """
    Rewrite every source="extracted/..." in the ISO project XML to point
    at translated/... so mkps2iso pulls the patched copies.
    """
    tree = ET.parse(in_xml)
    for elem in tree.iter():
        src = elem.get("source")
        if src and src.startswith("extracted/"):
            elem.set("source", "translated/" + src[len("extracted/"):])
    tree.write(out_xml, encoding="utf-8", xml_declaration=True)


def main():


    print("Repacking DATA.BIN...")

    print("Done!")

    print("Applying SLPM patches with armips...")
    #subprocess.run(["armips", "asm/patch.asm"], check=True)
    print("Done!")

    print("Generating translated.xml...")
    generate_translated_xml("newtheory.xml", "translated.xml")
    print("Done!")

    print("Rebuilding ISO...")
    subprocess.run(
        [
            "mkps2iso.exe",
            "-y",
            "-o",
            PATCHED_ISO,
            "translated.xml",
        ]
    )
    print(f"Patched ISO saved to {PATCHED_ISO}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Patch ISO with translations")
    parser.add_argument(
        "--sheets",
        action="store_true",
        help="Pull latest translations from Google Sheets. If unset, uses local CSV files.",
    )
    args = parser.parse_args()
    main()
