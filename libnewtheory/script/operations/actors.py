"""Actor, player, and party operations."""

from .base import Operation, RawOperation


class MovePlayerToXYZ(RawOperation):
    pass


class MovePlayerToActor(RawOperation):
    pass


class SetActorXYZ(RawOperation):
    pass


class ActorWalkToXYZ(RawOperation):
    pass


class SetActorAnim(RawOperation):
    pass


class SetActorFacingPreset(RawOperation):
    pass


class FaceActorToActor(RawOperation):
    pass


class ActorCmdA(RawOperation):
    pass


class ActorEffect(RawOperation):
    pass


class ToggleControlMode(RawOperation):
    pass


class ActorCmdB(RawOperation):
    pass


class ActorCmdC(RawOperation):
    pass


class ActorEffectStop(RawOperation):
    pass


class ActorCmdD(RawOperation):
    pass


class ActorCmdE(RawOperation):
    pass


class SetPlayerXYZ(RawOperation):
    pass


class CurrentActorReset(Operation):
    pass


class CurrentActorParam(RawOperation):
    pass


class ActorCmdGlobal(Operation):
    pass


class ActorEffectByMode(RawOperation):
    pass


class ActorFlagClear200000(RawOperation):
    pass


class ActorFlagSet200000(RawOperation):
    pass


class PartyCountTest(RawOperation):
    pass


class ActorCmdF(RawOperation):
    pass


class ActorRepeatCmd(RawOperation):
    pass


class ActorRepeatXYZCmd(RawOperation):
    pass


class SetPlayerParam(RawOperation):
    pass
