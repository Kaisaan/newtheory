"""Export script text for translation and apply a CSV to the clean source script."""

import csv
from collections.abc import Iterator
from copy import deepcopy
from io import StringIO
from os import PathLike
from pathlib import Path

from .model import Block, Script
from .operations.base import Operation
from .operations.flow import ConditionalBlock
from .operations.text import (
    ActorDialogue,
    ActorTextOperation,
    ChoiceMessage,
    TextOperation,
)
from .syntax import parse_text
from .text import Text, fix_ascii


_COLUMNS = ("ID", "Speaker", "JP Text", "EN Text", "Comments", "Text Type")
_TEXT_OPERATIONS = (TextOperation, ActorTextOperation, ActorDialogue)


def walk_operation(operation: Operation, path: str) -> Iterator[tuple[str, Operation]]:
    if isinstance(operation, _TEXT_OPERATIONS):
        yield path, operation
    if isinstance(operation, ConditionalBlock):
        yield from walk_operation(operation.predicate, f"{path}.predicate")
    if isinstance(operation, (ConditionalBlock, ChoiceMessage)):
        yield from walk_block(operation.body, path)


def walk_block(block: Block, path: str = "") -> Iterator[tuple[str, Operation]]:
    for index, operation in enumerate(block.operations):
        operation_path = f"{path}.{index}" if path else str(index)
        yield from walk_operation(operation, operation_path)


def script_id_from_path(filename: str | PathLike[str]) -> str:
    """Use the source directory relative to decompiled/, or its absolute path."""
    path = Path(filename).resolve()
    for root in path.parents:
        if root.name == "decompiled":
            return path.parent.relative_to(root).as_posix()
    return path.parent.as_posix()


def text_id(script_id: str, path: str, operation: Operation) -> str:
    return f"{script_id}||{path}||{type(operation).__name__}"


def format_text(value: Text) -> str:
    # Use real line breaks in spreadsheet cells, retaining nscript escapes for
    # literal backslashes and '<' so inline controls can still round-trip.
    return "".join(
        part.replace("\\", "\\\\").replace("<", "\\<")
        if isinstance(part, str)
        else f"<{part.kind} {part.value}>"
        for part in value.parts
    )


def dump_csv(script: Script, script_id: str) -> str:
    """Return CSV text with one row per text-carrying opcode, including nested ones.

    IDs combine the source script ID, zero-based operation path, and opcode name.
    Numeric path steps implicitly enter bodies; predicates use an explicit step.
    Scripts can share a CSV; each source's structure must remain unchanged.
    Speaker names are context; translations go in the initially empty EN Text.
    Return an empty string if the script contains no text-carrying opcodes.
    """
    operations = list(walk_block(script.body))
    if not operations:
        return ""
    output = StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(_COLUMNS)
    for path, operation in operations:
        speaker = (
            format_text(operation.character_name)
            if isinstance(operation, ActorDialogue)
            else ""
        )
        writer.writerow(
            [
                text_id(script_id, path, operation),
                speaker,
                format_text(operation.text),
                "",
                "",
                type(operation).__name__,
            ]
        )
    return output.getvalue()


def patch_from_csv(
    script: Script, filename: str | PathLike[str], script_id: str
) -> Script:
    """Return a copy with nonempty EN Text cells applied after fix_ascii.

    Missing rows and empty translations keep their original Japanese text.
    Translation cells accept nscript controls and escapes as well as actual
    line breaks. Rows may be reordered; ID alone selects the target operation.
    Rows belonging to other script IDs are ignored, allowing a combined CSV.
    """
    patched = deepcopy(script)
    targets = {
        text_id(script_id, path, operation): operation
        for path, operation in walk_block(patched.body)
    }
    with open(filename, encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, strict=True)
        try:
            if not {"ID", "EN Text"}.issubset(reader.fieldnames or ()):
                raise ValueError("CSV must contain ID and EN Text columns")
            seen = set()
            for row in reader:
                row_id, translation = row["ID"], row["EN Text"]
                if row_id is None or translation is None or None in row:
                    raise ValueError(f"CSV line {reader.line_num}: malformed row")
                if row_id.partition("||")[0] != script_id:
                    continue
                if row_id not in targets:
                    raise ValueError(
                        f"CSV line {reader.line_num}: unknown ID {row_id!r}"
                    )
                if row_id in seen:
                    raise ValueError(
                        f"CSV line {reader.line_num}: duplicate ID {row_id!r}"
                    )
                seen.add(row_id)
                if translation:
                    try:
                        targets[row_id].text = parse_text(fix_ascii(translation))
                    except ValueError as exc:
                        raise ValueError(
                            f"CSV line {reader.line_num}, ID {row_id!r}: {exc}"
                        ) from exc
        except csv.Error as exc:
            raise ValueError(f"CSV line {reader.line_num}: {exc}") from exc
    return patched
