"""Errors reported by script codecs."""


class ScriptError(ValueError):
    pass


class BinaryParseError(ScriptError):
    pass


class NscriptParseError(ScriptError):
    pass


class ValidationError(ScriptError):
    pass
