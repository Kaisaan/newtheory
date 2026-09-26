"""Field, scene, battle, inventory, and general UI operations."""

from .base import Operation, RawOperation


class FieldBounds(RawOperation):
    pass


class ShowUI(Operation):
    pass


class SetFieldState(RawOperation):
    pass


class SystemCmd(RawOperation):
    pass


class GiveItem(RawOperation):
    """Set ownership to 1 for the little-endian u16 item ID in arg."""


class HasItem(RawOperation):
    """Read item ownership into the conditional result; arg is a little-endian u16 ID."""


class ScreenEffectStart(RawOperation):
    pass


class ScreenEffectStop(Operation):
    pass


class FieldCmd(Operation):
    pass


class PlayerSceneTransition(Operation):
    pass


class PlayerSceneReset(Operation):
    pass


class BattleCmdA(RawOperation):
    pass


class BattleCmdB(RawOperation):
    pass


class BattleCmdPair(RawOperation):
    pass


class UIModeA(Operation):
    pass


class CheckInventory(RawOperation):
    pass


class CheckEquippedItem(RawOperation):
    pass


class EnableEncounters(Operation):
    pass


class DisableEncounters(Operation):
    pass


class RemoveItem(RawOperation):
    """Clear ownership and a matching equipment slot; arg is a little-endian u16 ID."""


class EquipItem(RawOperation):
    """Equip an owned item by category; arg is a little-endian u16 item ID."""


class SceneCmd(Operation):
    pass


class SetMode1(Operation):
    pass


class SetMode0(Operation):
    pass


class ScheduleShopCallbacks(Operation):
    pass


class StopScene(Operation):
    pass


class WaitResource(RawOperation):
    pass


class UIModeB(Operation):
    pass
