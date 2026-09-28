# /// script
# requires-python = ">=3.10"
# ///
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from libnewtheory.script import csv, nscript


def from_csv(input_path: Path, csv_path: Path, output_path: Path) -> None:
    """Apply a translation CSV to a clean nscript file and write the result."""
    script = nscript.loads(input_path.read_text(encoding="utf-8"))
    source = nscript.dumps(
        csv.patch_from_csv(script, csv_path, csv.script_id_from_path(input_path))
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(source, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Patch a clean nscript file with English text from a CSV.",
    )
    parser.add_argument(
        "input", type=Path, help="Path to the clean source .nscript file"
    )
    parser.add_argument("csv", type=Path, help="Path to the edited translation CSV")
    parser.add_argument("output", type=Path, help="Path to the patched .nscript file")
    args = parser.parse_args()

    try:
        from_csv(args.input, args.csv, args.output)
    except OSError as exc:
        parser.exit(1, f"{parser.prog}: file error: {exc}\n")
    except ValueError as exc:
        parser.exit(1, f"{parser.prog}: CSV patch error: {exc}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
