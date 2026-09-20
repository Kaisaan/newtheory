"""Dialogue, messages, portraits, and text boxes."""

from dataclasses import dataclass, field

from ..model import Block
from ..text import Text
from .base import Operation, RawOperation


@dataclass(kw_only=True)
class TextOperation(Operation):
    text: Text = field(default_factory=Text)

    def __post_init__(self):
        self.text = Text(self.text)


@dataclass(kw_only=True)
class ActorTextOperation(Operation):
    actor_id: int = 0
    text: Text = field(default_factory=Text)

    def __post_init__(self):
        self.text = Text(self.text)


@dataclass(kw_only=True)
class ChoiceMessage(ActorTextOperation):
    body: Block = field(default_factory=Block)


@dataclass(kw_only=True)
class ActorDialogue(Operation):
    actor_id: int = 0
    character_name: Text = field(default_factory=Text)
    text: Text = field(default_factory=Text)
    portrait_id: int = 0

    def __post_init__(self):
        self.character_name = Text(self.character_name)
        self.text = Text(self.text)


class Message(TextOperation):
    pass


class CloseMessage(Operation):
    pass


class ActorMessage(ActorTextOperation):
    pass


class PortraitCmdA(RawOperation):
    pass


class PortraitCmdB(RawOperation):
    pass


class PortraitWait(RawOperation):
    pass


class TextboxCmd(RawOperation):
    pass


class TextboxClear(Operation):
    pass


class ShowActorPortrait(RawOperation):
    pass


class TextboxSet(RawOperation):
    pass


class TextboxSetTimed(RawOperation):
    pass


class TextboxDefaultTimed(Operation):
    pass


class ResetSelectionList(Operation):
    pass


class AddSelectionEntry(RawOperation):
    pass


class SelectionMenu(Operation):
    pass


class CenterMessage(TextOperation):
    pass


class TextboxSetFromDefault(RawOperation):
    pass


class TextboxParam(RawOperation):
    pass


class PortraitActorCmd(RawOperation):
    pass


class MessageAuto(TextOperation):
    pass


class HidePortrait(Operation):
    pass


class CenterMessageAuto(TextOperation):
    pass
