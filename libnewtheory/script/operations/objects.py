"""Field object lifecycle and action operations."""

from .base import Operation, RawOperation


class SpawnActorObject(RawOperation):
    pass


class StartObjectAction(RawOperation):
    pass


class StopObjectAction(RawOperation):
    pass


class WaitObjectAction(RawOperation):
    pass


class SpawnActorObjectAlt(RawOperation):
    pass


class SpawnEffect(RawOperation):
    pass


class SpawnObjectAtXYZ(RawOperation):
    pass


class ObjectCmd(RawOperation):
    pass


class StartObjectActionAlt(RawOperation):
    pass


class StopObjectActionAlt(RawOperation):
    pass


class WaitObjectActionAlt(RawOperation):
    pass


class SpawnFieldObject(RawOperation):
    pass
