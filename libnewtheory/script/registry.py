"""Operation names, opcode numbers, and fixed payload sizes."""

from dataclasses import dataclass

from .errors import ValidationError
from .operations import actors, audio, camera, flow, objects, text, world
from .operations.base import Operation, RawOperation


@dataclass(frozen=True)
class OperationSpec:
    opcode: int
    operation_type: type[Operation]
    payload_size: int | None = None

    @property
    def name(self) -> str:
        return self.operation_type.__name__


OPERATIONS = (
    OperationSpec(0x05, actors.MovePlayerToXYZ, 14),
    OperationSpec(0x06, actors.MovePlayerToActor, 4),
    OperationSpec(0x0E, actors.SetActorXYZ, 14),
    OperationSpec(0x0F, actors.ActorWalkToXYZ, 14),
    OperationSpec(0x10, actors.SetActorAnim, 4),
    OperationSpec(0x11, actors.SetActorFacingPreset, 4),
    OperationSpec(0x12, actors.FaceActorToActor, 4),
    OperationSpec(0x13, actors.ActorCmdA, 2),
    OperationSpec(0x14, actors.ActorEffect, 4),
    OperationSpec(0x15, actors.ToggleControlMode, 2),
    OperationSpec(0x30, actors.ActorCmdB, 2),
    OperationSpec(0x31, actors.ActorCmdC, 2),
    OperationSpec(0x38, actors.ActorEffectStop, 2),
    OperationSpec(0x39, actors.ActorCmdD, 2),
    OperationSpec(0x3A, actors.ActorCmdE, 2),
    OperationSpec(0x3C, actors.SetPlayerXYZ, 12),
    OperationSpec(0x47, actors.CurrentActorReset, 0),
    OperationSpec(0x48, actors.CurrentActorParam, 4),
    OperationSpec(0x4F, actors.ActorCmdGlobal, 0),
    OperationSpec(0x57, actors.ActorEffectByMode, 6),
    OperationSpec(0x62, actors.ActorFlagClear200000, 2),
    OperationSpec(0x63, actors.ActorFlagSet200000, 2),
    OperationSpec(0x68, actors.PartyCountTest, 2),
    OperationSpec(0x7E, actors.ActorCmdF, 4),
    OperationSpec(0x7F, actors.ActorRepeatCmd, 4),
    OperationSpec(0x80, actors.ActorRepeatXYZCmd, 16),
    OperationSpec(0x86, actors.SetPlayerParam, 2),
    OperationSpec(0x01, audio.AudioCmdAWait, 2),
    OperationSpec(0x02, audio.AudioCmdBWait, 2),
    OperationSpec(0x59, audio.AudioCmdC, 2),
    OperationSpec(0x5A, audio.AudioStop, 0),
    OperationSpec(0x5B, audio.Audio1CmdAWait, 2),
    OperationSpec(0x5C, audio.Audio1CmdBWait, 2),
    OperationSpec(0x69, audio.PlayEffect, 2),
    OperationSpec(0x81, audio.AudioParamPair, 4),
    OperationSpec(0x07, camera.CameraMoveXYZ, 14),
    OperationSpec(0x08, camera.CameraMoveActor, 4),
    OperationSpec(0x09, camera.CameraCmdA, 4),
    OperationSpec(0x0A, camera.CameraCmdB, 4),
    OperationSpec(0x25, camera.CameraMoveScaled, 8),
    OperationSpec(0x26, camera.CameraCmdC, 2),
    OperationSpec(0x3E, camera.CameraCmdD, 4),
    OperationSpec(0x4B, camera.CameraMode, 2),
    OperationSpec(0x51, camera.CameraOverlayOn, 0),
    OperationSpec(0x52, camera.CameraOverlayOff, 0),
    OperationSpec(0x83, camera.CameraReset, 0),
    OperationSpec(0x84, camera.CameraCmdE, 4),
    OperationSpec(0x03, flow.WaitFrames, 2),
    OperationSpec(0x22, flow.SpawnInlineEvent, 16),
    OperationSpec(0x23, flow.SetContextAndJump, 14),
    OperationSpec(0x29, flow.SetScriptFlag, 2),
    OperationSpec(0x2A, flow.ClearScriptFlag, 2),
    OperationSpec(0x2B, flow.TestScriptFlag, 2),
    OperationSpec(0x2C, flow.ConditionalBlock),
    OperationSpec(0x2D, flow.Jump, 2),
    OperationSpec(0x36, flow.EndScript, 0),
    OperationSpec(0x45, flow.RandomModTest, 2),
    OperationSpec(0x58, flow.LocalEventCmd, 2),
    OperationSpec(0x5D, flow.SetStageFlag1, 0),
    OperationSpec(0x5E, flow.ClearStageFlag1, 0),
    OperationSpec(0x5F, flow.SetStageFlag0, 0),
    OperationSpec(0x60, flow.ClearStageFlag0, 0),
    OperationSpec(0x6B, flow.EventCmdA, 2),
    OperationSpec(0x6D, flow.EventCmdB, 2),
    OperationSpec(0x74, flow.SpawnInlineEventBlocking, 16),
    OperationSpec(0x7B, flow.TestScriptFlagRange, 4),
    OperationSpec(0x7C, flow.ClearScriptFlagRange, 4),
    OperationSpec(0x7D, flow.SetScriptFlagRange, 4),
    OperationSpec(0x82, flow.LookupValue, 2),
    OperationSpec(0x87, flow.ClearGlobalFlag2, 0),
    OperationSpec(0x88, flow.SetGlobalFlag2, 0),
    OperationSpec(0x89, flow.ClearGlobalFlag1, 0),
    OperationSpec(0x8A, flow.SetGlobalFlag1, 0),
    OperationSpec(0x35, objects.SpawnActorObject, 6),
    OperationSpec(0x3F, objects.StartObjectAction, 4),
    OperationSpec(0x40, objects.StopObjectAction, 4),
    OperationSpec(0x41, objects.WaitObjectAction, 4),
    OperationSpec(0x42, objects.SpawnActorObjectAlt, 6),
    OperationSpec(0x64, objects.SpawnEffect, 10),
    OperationSpec(0x75, objects.SpawnObjectAtXYZ, 18),
    OperationSpec(0x76, objects.ObjectCmd, 2),
    OperationSpec(0x77, objects.StartObjectActionAlt, 4),
    OperationSpec(0x78, objects.StopObjectActionAlt, 4),
    OperationSpec(0x79, objects.WaitObjectActionAlt, 4),
    OperationSpec(0x7A, objects.SpawnFieldObject, 14),
    OperationSpec(0x04, text.Message),
    OperationSpec(0x0C, text.CloseMessage, 0),
    OperationSpec(0x18, text.ActorMessage),
    OperationSpec(0x19, text.PortraitCmdA, 8),
    OperationSpec(0x1A, text.PortraitCmdB, 4),
    OperationSpec(0x1B, text.PortraitWait, 2),
    OperationSpec(0x1C, text.TextboxCmd, 2),
    OperationSpec(0x1D, text.TextboxClear, 0),
    OperationSpec(0x1E, text.ShowActorPortrait, 4),
    OperationSpec(0x1F, text.TextboxSet, 2),
    OperationSpec(0x20, text.TextboxSetTimed, 2),
    OperationSpec(0x21, text.TextboxDefaultTimed, 0),
    OperationSpec(0x32, text.ResetSelectionList, 0),
    OperationSpec(0x33, text.AddSelectionEntry, 6),
    OperationSpec(0x34, text.SelectionMenu, 0),
    OperationSpec(0x37, text.ChoiceMessage),
    OperationSpec(0x3B, text.CenterMessage),
    OperationSpec(0x43, text.TextboxSetFromDefault, 2),
    OperationSpec(0x44, text.TextboxParam, 2),
    OperationSpec(0x46, text.ActorDialogue),
    OperationSpec(0x61, text.PortraitActorCmd, 8),
    OperationSpec(0x65, text.MessageAuto),
    OperationSpec(0x6C, text.HidePortrait, 0),
    OperationSpec(0x72, text.CenterMessageAuto),
    OperationSpec(0x0B, world.FieldBounds, 2),
    OperationSpec(0x0D, world.ShowUI, 0),
    OperationSpec(0x16, world.SetFieldState, 4),
    OperationSpec(0x24, world.SystemCmd, 6),
    OperationSpec(0x27, world.GiveItem, 2),
    OperationSpec(0x28, world.HasItem, 2),
    OperationSpec(0x2E, world.ScreenEffectStart, 2),
    OperationSpec(0x2F, world.ScreenEffectStop, 0),
    OperationSpec(0x3D, world.FieldCmd, 0),
    OperationSpec(0x49, world.PlayerSceneTransition, 0),
    OperationSpec(0x4A, world.PlayerSceneReset, 0),
    OperationSpec(0x4C, world.BattleCmdA, 2),
    OperationSpec(0x4D, world.BattleCmdB, 2),
    OperationSpec(0x4E, world.BattleCmdPair, 4),
    OperationSpec(0x50, world.UIModeA, 0),
    OperationSpec(0x53, world.CheckInventory, 2),
    OperationSpec(0x54, world.CheckEquippedItem, 4),
    OperationSpec(0x55, world.EnableEncounters, 0),
    OperationSpec(0x56, world.DisableEncounters, 0),
    OperationSpec(0x66, world.RemoveItem, 2),
    OperationSpec(0x67, world.EquipItem, 2),
    OperationSpec(0x6A, world.SceneCmd, 0),
    OperationSpec(0x6E, world.SetMode1, 0),
    OperationSpec(0x6F, world.SetMode0, 0),
    OperationSpec(0x70, world.ScheduleShopCallbacks, 0),
    OperationSpec(0x71, world.StopScene, 0),
    OperationSpec(0x73, world.WaitResource, 2),
    OperationSpec(0x85, world.UIModeB, 0),
)

BY_OPCODE = {spec.opcode: spec for spec in OPERATIONS}
BY_NAME = {spec.name: spec for spec in OPERATIONS}
BY_TYPE = {spec.operation_type: spec for spec in OPERATIONS}

if not len(BY_OPCODE) == len(BY_NAME) == len(BY_TYPE) == len(OPERATIONS):
    raise RuntimeError("Duplicate operation registration")
if set(BY_OPCODE) != set(range(0x01, 0x8B)) - {0x17}:
    raise RuntimeError("Incomplete SCRIPT opcode registry")


def get_spec(operation: Operation) -> OperationSpec:
    try:
        spec = BY_TYPE[type(operation)]
    except KeyError:
        raise ValidationError(
            f"Unregistered operation: {type(operation).__name__}"
        ) from None
    if isinstance(operation, RawOperation):
        if (
            not isinstance(operation.arg, bytes)
            or len(operation.arg) != spec.payload_size
        ):
            raise ValidationError(
                f"{spec.name} requires {spec.payload_size} payload bytes"
            )
    return spec
