"""Literal game text and supported inline controls."""

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class TextControl:
    kind: Literal["size", "color", "sleep"]
    value: int

    def __post_init__(self):
        if self.kind not in ("size", "color", "sleep"):
            raise ValueError(f"Unknown text control: {self.kind!r}")
        if not isinstance(self.value, int) or not 0 <= self.value <= 0xFF:
            raise ValueError("Text control value must be between 0 and 255")


@dataclass(frozen=True, init=False)
class Text:
    parts: tuple[str | TextControl, ...]

    def __init__(self, value: "str | Text | Iterable[str | TextControl]" = ""):
        if isinstance(value, Text):
            parts = value.parts
        else:
            parts = (value,) if isinstance(value, str) else value
        normalized: list[str | TextControl] = []
        for part in parts:
            if isinstance(part, str):
                if "\x00" in part:
                    raise ValueError("Text cannot contain NUL characters")
                if not part:
                    continue
                if normalized and isinstance(normalized[-1], str):
                    normalized[-1] += part
                else:
                    normalized.append(part)
            elif isinstance(part, TextControl):
                normalized.append(part)
            else:
                raise TypeError(f"Invalid text part: {part!r}")
        object.__setattr__(self, "parts", tuple(normalized))
