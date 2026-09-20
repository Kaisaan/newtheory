# /// script
# requires-python = ">=3.10"
# ///
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from libnewtheory.script import binary, nscript


def decompile_script(input_path: Path, output_path: Path) -> None:
    """Convert one script binary to UTF-8 nscript text."""
    source = nscript.dumps(binary.loads(input_path.read_bytes()))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(source, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert a script .bin file to nscript text.",
    )
    parser.add_argument("input", type=Path, help="Path to the source script .bin file")
    parser.add_argument(
        "output",
        type=Path,
        nargs="?",
        help="Output path (default: input path with a .nscript suffix)",
    )
    args = parser.parse_args()
    output_path = args.output if args.output is not None else args.input.with_suffix(".nscript")

    try:
        decompile_script(args.input, output_path)
    except OSError as exc:
        parser.exit(1, f"{parser.prog}: file error: {exc}\n")
    except ValueError as exc:
        parser.exit(1, f"{parser.prog}: decompile error: {exc}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
