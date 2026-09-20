"""Shared operation data."""

from dataclasses import dataclass, field


@dataclass(kw_only=True)
class Operation:
    labels: list[int] = field(default_factory=list)


@dataclass
class RawOperation(Operation):
    arg: bytes
