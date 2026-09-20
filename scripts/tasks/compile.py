# /// script
# requires-python = ">=3.10"
# ///
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from libnewtheory.script import binary, nscript


def compile_script(input_path: Path, output_path: Path) -> None:
    """Convert one UTF-8 nscript file to a script binary."""
    data = binary.dumps(nscript.loads(input_path.read_text(encoding="utf-8")))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(data)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert an nscript file to a script .bin file.",
    )
    parser.add_argument("input", type=Path, help="Path to the source .nscript file")
    parser.add_argument(
        "output",
        type=Path,
        nargs="?",
        help="Output path (default: input path with a .bin suffix)",
    )
    args = parser.parse_args()
    output_path = args.output if args.output is not None else args.input.with_suffix(".bin")

    try:
        compile_script(args.input, output_path)
    except OSError as exc:
        parser.exit(1, f"{parser.prog}: file error: {exc}\n")
    except ValueError as exc:
        parser.exit(1, f"{parser.prog}: compile error: {exc}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
