"""Script control flow, flags, and events."""

from dataclasses import dataclass, field

from ..model import Block, StageId
from .base import Operation, RawOperation


@dataclass(kw_only=True)
class SpawnEventOperation(Operation):
    stage: StageId
    x: int = 0
    y: int = 0
    z: int = 0
    resume: int = 0


@dataclass(kw_only=True)
class SetContextAndJump(Operation):
    target: int
    x: int = 0
    y: int = 0
    z: int = 0


@dataclass(kw_only=True)
class ConditionalBlock(Operation):
    predicate: Operation
    body: Block = field(default_factory=Block)


@dataclass(kw_only=True)
class Jump(Operation):
    target: int


class WaitFrames(RawOperation):
    pass


class SpawnInlineEvent(SpawnEventOperation):
    pass


class SetScriptFlag(RawOperation):
    pass


class ClearScriptFlag(RawOperation):
    pass


class TestScriptFlag(RawOperation):
    pass


class EndScript(Operation):
    pass


class RandomModTest(RawOperation):
    pass


class LocalEventCmd(RawOperation):
    pass


class SetStageFlag1(Operation):
    pass


class ClearStageFlag1(Operation):
    pass


class SetStageFlag0(Operation):
    pass


class ClearStageFlag0(Operation):
    pass


class EventCmdA(RawOperation):
    pass


class EventCmdB(RawOperation):
    pass


class SpawnInlineEventBlocking(SpawnEventOperation):
    pass


class TestScriptFlagRange(RawOperation):
    pass


class ClearScriptFlagRange(RawOperation):
    pass


class SetScriptFlagRange(RawOperation):
    pass


class LookupValue(RawOperation):
    pass


class ClearGlobalFlag2(Operation):
    pass


class SetGlobalFlag2(Operation):
    pass


class ClearGlobalFlag1(Operation):
    pass


class SetGlobalFlag1(Operation):
    pass
