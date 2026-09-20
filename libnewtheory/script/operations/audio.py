"""Music, sound, and audio-channel operations."""

from .base import Operation, RawOperation


class AudioCmdAWait(RawOperation):
    pass


class AudioCmdBWait(RawOperation):
    pass


class AudioCmdC(RawOperation):
    pass


class AudioStop(Operation):
    pass


class Audio1CmdAWait(RawOperation):
    pass


class Audio1CmdBWait(RawOperation):
    pass


class PlayEffect(RawOperation):
    pass


class AudioParamPair(RawOperation):
    pass
