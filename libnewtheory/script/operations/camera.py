"""Camera position, mode, and overlay operations."""

from .base import Operation, RawOperation


class CameraMoveXYZ(RawOperation):
    pass


class CameraMoveActor(RawOperation):
    pass


class CameraCmdA(RawOperation):
    pass


class CameraCmdB(RawOperation):
    pass


class CameraMoveScaled(RawOperation):
    pass


class CameraCmdC(RawOperation):
    pass


class CameraCmdD(RawOperation):
    pass


class CameraMode(RawOperation):
    pass


class CameraOverlayOn(Operation):
    pass


class CameraOverlayOff(Operation):
    pass


class CameraReset(Operation):
    pass


class CameraCmdE(RawOperation):
    pass
