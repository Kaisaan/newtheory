# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-api-python-client",
#     "google-auth",
#     "pillow",
#     "ReverseBox"
# ]
# ///
import argparse
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from libnewtheory.archive import pack
from scripts.tasks.compile import compile_script
from scripts.tasks.export_all_csv import csv_basename
from scripts.tasks.from_csv import from_csv


PATCHED_ISO = "english.iso"


def generate_translated_xml(in_xml: str, out_xml: str):
    """
    Rewrite every source="extracted/..." in the ISO project XML to point
    at translated/... so mkps2iso pulls the patched copies.
    """
    tree = ET.parse(in_xml)
    for elem in tree.iter():
        src = elem.get("source")
        if src and src.startswith("extracted"):
            elem.set("source", "translated" + src[len("extracted") :])
    tree.write(out_xml, encoding="utf-8", xml_declaration=True)


def gen_mappings(decompiled_root: Path, csv_root: Path) -> (dict, dict):
    if not decompiled_root.is_dir() or not csv_root.is_dir():
        raise FileNotFoundError(
            "Expected decompiled/ and csvs/en/; extract the ISO and prepare the CSVs first"
        )

    sources = sorted(decompiled_root.rglob("*.nscript"))
    if not sources:
        raise ValueError(f"No scripts found in {decompiled_root}")
    # CITY_CASNAN_00AREA -> decompiled/CITY/CASNAN/00_AREA/SCRIPT.nscript
    source_by_name = {csv_basename(path, decompiled_root): path for path in sources}
    if len(source_by_name) != len(sources):
        raise ValueError("Multiple scripts have the same CSV basename")

    # CITY_CASNAN_00AREA -> csvs/jp/CITY_CASNAN_00AREA.csv
    csv_by_name = {}
    for path in sorted(csv_root.rglob("*.csv")):
        if path.stem in csv_by_name:
            raise ValueError(f"Multiple translation CSVs named {path.name}")
        if path.stem not in source_by_name:
            raise ValueError(f"No script matches translation CSV {path}")
        csv_by_name[path.stem] = path
    if not csv_by_name:
        raise ValueError(f"No translation CSVs found in {csv_root}")

    return csv_by_name


def main():
    from scripts.tasks.update_graphics import insert_all_graphics

    csv_by_name = gen_mappings(Path("decompiled"), Path("csvs/en"))
    nscript_files = sorted(Path("decompiled").rglob("*.nscript"))
    print("Applying CSV translations...")
    for nscript_file in nscript_files:
        relative_path = nscript_file.relative_to(Path("decompiled"))
        output_path = (Path("DAT/STAGE") / relative_path).with_suffix(".BIN")
        csv_path = csv_by_name.get(csv_basename(nscript_file, Path("decompiled")))
        if csv_path is not None:
            from_csv(nscript_file, csv_path, nscript_file)
        print(f"  Patched {nscript_file}")

    print("Compiling nscripts...")
    for nscript_file in nscript_files:
        compile_script(nscript_file, output_path)
        print(f"  {nscript_file} -> {output_path}")
    print("Done!")

    print("Updating graphics...")
    insert_all_graphics()
    print("Done!")

    print("Repacking DAT.PAK and DAT.PKI...")
    pack()
    print("Done!")

    print("Applying SLPM patches with armips...")
    # subprocess.run(["armips", "asm/patch.asm"], check=True)
    print("Done!")

    print("Generating translated.xml...")
    generate_translated_xml("newtheory.xml", "translated.xml")
    print("Done!")

    print("Rebuilding ISO...")
    subprocess.run(
        [
            "mkps2iso",
            "-y",
            "-o",
            PATCHED_ISO,
            "translated.xml",
        ],
        check=True,
    )
    print(f"Patched ISO saved to {PATCHED_ISO}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Patch ISO with translations")
    parser.add_argument(
        "--sheets",
        action="store_true",
        help="Legacy flag; the build currently uses local csvs/en/ files only.",
    )
    args = parser.parse_args()
    if args.sheets:
        print(
            "Note: --sheets does not fetch Google Sheets; using csvs/en/.",
            file=sys.stderr,
        )
    main()
