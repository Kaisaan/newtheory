# /// script
# requires-python = ">=3.10"
# ///
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from libnewtheory.script import csv, nscript


def to_csv(input_path: Path, output_path: Path) -> None:
    """Export one UTF-8 nscript file's text, skipping scripts without text rows."""
    script = nscript.loads(input_path.read_text(encoding="utf-8"))
    data = csv.dump_csv(script, csv.script_id_from_path(input_path))
    if not data:
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as output:
        output.write(data)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export an nscript file's text to a translation CSV.",
    )
    parser.add_argument("input", type=Path, help="Path to the source .nscript file")
    parser.add_argument(
        "output",
        type=Path,
        nargs="?",
        help="Output path (default: input path with a .csv suffix)",
    )
    args = parser.parse_args()
    output_path = (
        args.output if args.output is not None else args.input.with_suffix(".csv")
    )

    try:
        to_csv(args.input, output_path)
    except OSError as exc:
        parser.exit(1, f"{parser.prog}: file error: {exc}\n")
    except ValueError as exc:
        parser.exit(1, f"{parser.prog}: CSV export error: {exc}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
