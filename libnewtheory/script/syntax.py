"""Field and text syntax used by the nscript codec."""

import re

from .model import StageId
from .text import Text, TextControl

_LABEL = re.compile(r"LABEL_(-?[0-9a-fA-F]+)")
_TEXT_FIELDS = {"text", "character_name"}
_LABEL_FIELDS = {"target", "resume"}
_ESCAPES = {"n": "\n", "r": "\r", "t": "\t", "\\": "\\", "<": "<"}


def format_label(label: int) -> str:
    if not isinstance(label, int) or not -(1 << 31) <= label < (1 << 31) or label == -1:
        raise ValueError(f"Invalid label ID: {label!r}")
    return f"LABEL_{label:06x}"


def parse_label(value: str) -> int:
    match = _LABEL.fullmatch(value)
    if match is None:
        raise ValueError(f"Invalid label reference: {value!r}")
    label = int(match[1], 16)
    format_label(label)
    return label


def parse_text(value: str) -> Text:
    parts: list[str | TextControl] = []
    literal: list[str] = []
    index = 0
    while index < len(value):
        char = value[index]
        if char == "\\":
            index += 1
            if index == len(value) or value[index] not in _ESCAPES:
                raise ValueError("Invalid text escape")
            literal.append(_ESCAPES[value[index]])
        elif char == "<":
            end = value.find(">", index)
            if end == -1:
                raise ValueError("Unterminated text control")
            terms = value[index + 1 : end].split()
            if len(terms) != 2:
                raise ValueError(f"Invalid text control: {value[index : end + 1]!r}")
            parts.append("".join(literal))
            literal.clear()
            parts.append(TextControl(terms[0], int(terms[1], 0)))
            index = end
        else:
            literal.append(char)
        index += 1
    parts.append("".join(literal))
    return Text(parts)


def format_text(value: Text) -> str:
    parts = []
    for part in Text(value).parts:
        if isinstance(part, TextControl):
            parts.append(f"<{part.kind} {part.value}>")
        else:
            parts.append(
                part.replace("\\", "\\\\")
                .replace("<", "\\<")
                .replace("\n", "\\n")
                .replace("\r", "\\r")
                .replace("\t", "\\t")
            )
    return "".join(parts)


def parse_value(key: str, value: str):
    if key in _TEXT_FIELDS:
        return parse_text(value)
    value = value.strip()
    if key == "arg":
        return bytes.fromhex(value)
    if key in _LABEL_FIELDS:
        return parse_label(value)
    if key == "stage":
        group, local = value.split(".")
        return StageId(int(group, 0), int(local, 0))
    return int(value, 0)


def format_value(key: str, value) -> str:
    if key in _TEXT_FIELDS:
        return format_text(value)
    if key == "arg":
        return value.hex()
    if key in _LABEL_FIELDS:
        return format_label(value)
    if key == "stage":
        return f"{value.group}.{value.local}"
    if not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    return hex(value) if key in ("actor_id", "portrait_id") else str(value)


def parse_instruction(line: str) -> tuple[str, dict[str, str]]:
    name, *terms = line.lstrip().split("\t")
    name = name.strip()
    if not name:
        raise ValueError("Expected an operation name")
    values = {}
    for term in terms:
        key, separator, value = term.partition(":")
        key = key.strip()
        if not separator or not key:
            raise ValueError(f"Invalid instruction field: {term!r}")
        if key in values:
            raise ValueError(f"Duplicate instruction field: {key}")
        values[key] = value
    return name, values
