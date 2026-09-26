"""The editable script tree, independent of its serialized formats."""

from dataclasses import dataclass, field

from .operations.base import Operation


@dataclass
class Block:
    operations: list[Operation] = field(default_factory=list)
    end_labels: list[int] = field(default_factory=list)


@dataclass
class Script:
    body: Block = field(default_factory=Block)


@dataclass(frozen=True)
class StageId:
    group: int
    local: int

    def __post_init__(self):
        if any(
            not isinstance(value, int) or not 0 <= value <= 0xFF
            for value in (self.group, self.local)
        ):
            raise ValueError("Stage components must be between 0 and 255")
