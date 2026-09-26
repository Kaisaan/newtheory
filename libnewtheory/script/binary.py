"""Read and write SCRIPT.BIN with a label table at byte zero."""

from .errors import BinaryParseError, ValidationError
from .model import Block, Script, StageId
from .operations.base import Operation, RawOperation
from .operations.flow import (
    ConditionalBlock,
    Jump,
    SetContextAndJump,
    SpawnEventOperation,
)
from .operations.text import (
    ActorDialogue,
    ActorTextOperation,
    ChoiceMessage,
    TextOperation,
)
from .registry import BY_OPCODE, get_spec
from .text import Text, TextControl

CONTROL_CODES = {"size": 0xFB, "color": 0xFC, "sleep": 0xFD}
CONTROL_NAMES = {code: name for name, code in CONTROL_CODES.items()}


class Reader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
        self.end = len(data)
        self.operations: dict[int, Operation] = {}

    def read(self, size: int) -> bytes:
        if self.pos + size > self.end:
            raise BinaryParseError(
                f"Unexpected end of script or block at {self.pos:#x}; need {size} bytes"
            )
        data = self.data[self.pos : self.pos + size]
        self.pos += size
        return data

    def text(self) -> Text:
        parts: list[str | TextControl] = []
        while True:
            start = self.pos
            raw = bytearray()
            while True:
                try:
                    marker = int.from_bytes(self.read(1), "little")
                except BinaryParseError as exc:
                    raise BinaryParseError(
                        f"Unterminated text at {self.pos:#x}"
                    ) from exc
                if marker in (0, 0xFF):
                    break
                raw.append(marker)
            if raw:
                try:
                    literal = raw.decode("cp932")
                except UnicodeDecodeError as exc:
                    raise BinaryParseError(
                        f"Invalid CP932 text at {start + exc.start:#x}"
                    ) from exc
                if literal.encode("cp932") != raw:
                    raise BinaryParseError(f"Noncanonical CP932 text at {start:#x}")
                parts.append(literal)
            if marker == 0:
                return Text(parts)
            start = self.pos - 1
            code = int.from_bytes(self.read(1), "little")
            if code not in CONTROL_NAMES:
                raise BinaryParseError(f"Unknown text control {code:#x} at {start:#x}")
            parts.append(
                TextControl(CONTROL_NAMES[code], int.from_bytes(self.read(1), "little"))
            )

    def operation(self) -> Operation:
        start = self.pos
        name = "Operation"
        try:
            opcode = int.from_bytes(self.read(2), "little")
            spec = BY_OPCODE.get(opcode)
            if spec is None:
                raise BinaryParseError(f"Unknown SCRIPT opcode {opcode:#04x}")
            cls = spec.operation_type
            name = spec.name
            if issubclass(cls, RawOperation):
                operation = cls(arg=self.read(spec.payload_size))
            elif cls is ConditionalBlock:
                operation = cls(
                    predicate=self.operation(),
                    body=self.block(size=int.from_bytes(self.read(4), "little")),
                )
            elif cls is ChoiceMessage:
                operation = cls(
                    actor_id=int.from_bytes(self.read(2), "little"),
                    text=self.text(),
                    body=self.block(size=int.from_bytes(self.read(4), "little")),
                )
            elif cls is ActorDialogue:
                operation = cls(
                    actor_id=int.from_bytes(self.read(2), "little"),
                    character_name=self.text(),
                    text=self.text(),
                    portrait_id=int.from_bytes(self.read(2), "little"),
                )
            elif issubclass(cls, ActorTextOperation):
                operation = cls(
                    actor_id=int.from_bytes(self.read(2), "little"), text=self.text()
                )
            elif issubclass(cls, TextOperation):
                operation = cls(text=self.text())
            elif issubclass(cls, SpawnEventOperation):
                stage = int.from_bytes(self.read(2), "little")
                operation = cls(
                    stage=StageId(stage >> 8, stage & 0xFF),
                    x=int.from_bytes(self.read(4), "little", signed=True),
                    y=int.from_bytes(self.read(4), "little", signed=True),
                    z=int.from_bytes(self.read(4), "little", signed=True),
                    resume=int.from_bytes(self.read(2), "little"),
                )
            elif cls is SetContextAndJump:
                operation = cls(
                    x=int.from_bytes(self.read(4), "little", signed=True),
                    y=int.from_bytes(self.read(4), "little", signed=True),
                    z=int.from_bytes(self.read(4), "little", signed=True),
                    target=int.from_bytes(self.read(2), "little"),
                )
            elif cls is Jump:
                operation = cls(target=int.from_bytes(self.read(2), "little"))
            elif spec.payload_size == 0:
                operation = cls()
            else:
                raise BinaryParseError(f"No decoder for {name}")
        except ValueError as exc:
            raise BinaryParseError(f"{name} at {start:#x}: {exc}") from exc
        self.operations[start] = operation
        return operation

    def block(self, size: int = -1) -> Block:
        end = self.end if size == -1 else self.pos + size
        block = Block()
        while self.pos < end:
            block.operations.append(self.operation())
        return block


def loads(data: bytes) -> Script:
    reader = Reader(data)
    labels: list[tuple[int, int]] = []
    while True:
        label = int.from_bytes(reader.read(4), "little", signed=True)
        if label == -1:
            break
        offset = int.from_bytes(reader.read(4), "little", signed=True)
        if labels and offset < labels[-1][1]:
            raise BinaryParseError("Label table must be sorted by offset")
        labels.append((label, offset))
    script = Script(reader.block())
    for label, offset in labels:
        if offset == reader.end:
            script.body.end_labels.append(label)
        elif offset in reader.operations:
            reader.operations[offset].labels.append(label)
        else:
            raise BinaryParseError(
                f"Label {label:#x} at {offset:#x} must point to an instruction boundary or EOF"
            )
    return script


class Writer:
    def __init__(self):
        self.code = bytearray()
        self.labels: list[tuple[int, int]] = []
        self.boundaries: set[int] = set()

    def mark_labels(self, labels: list[int]):
        for label in labels:
            if label == -1:
                raise ValidationError(
                    "Label ID -1 is reserved for the table terminator"
                )
            self.labels.append((label, len(self.code)))

    def write_text(self, value: Text):
        for part in Text(value).parts:
            if isinstance(part, TextControl):
                self.code += bytes((0xFF, CONTROL_CODES[part.kind], part.value))
            else:
                try:
                    raw = part.encode("cp932")
                except UnicodeEncodeError as exc:
                    raise ValidationError(
                        f"Text cannot be encoded losslessly: {part!r}"
                    ) from exc
                if b"\xff" in raw or raw.decode("cp932") != part:
                    raise ValidationError(
                        f"Text cannot be encoded losslessly: {part!r}"
                    )
                self.code += raw
        self.code.append(0)

    def write_operation(self, operation: Operation):
        spec = get_spec(operation)
        self.boundaries.add(len(self.code))
        self.mark_labels(operation.labels)
        self.code += spec.opcode.to_bytes(2, "little")
        if isinstance(operation, RawOperation):
            self.code += operation.arg
        elif isinstance(operation, ConditionalBlock):
            self.write_operation(operation.predicate)
            size_pos = len(self.code)
            self.code += bytes(4)
            size = self.write_block(operation.body)
            self.code[size_pos : size_pos + 4] = size.to_bytes(4, "little")
        elif isinstance(operation, ChoiceMessage):
            self.code += operation.actor_id.to_bytes(2, "little")
            self.write_text(operation.text)
            size_pos = len(self.code)
            self.code += bytes(4)
            size = self.write_block(operation.body)
            self.code[size_pos : size_pos + 4] = size.to_bytes(4, "little")
        elif isinstance(operation, ActorDialogue):
            self.code += operation.actor_id.to_bytes(2, "little")
            self.write_text(operation.character_name)
            self.write_text(operation.text)
            self.code += operation.portrait_id.to_bytes(2, "little")
        elif isinstance(operation, ActorTextOperation):
            self.code += operation.actor_id.to_bytes(2, "little")
            self.write_text(operation.text)
        elif isinstance(operation, TextOperation):
            self.write_text(operation.text)
        elif isinstance(operation, SpawnEventOperation):
            stage = (operation.stage.group << 8) | operation.stage.local
            self.code += stage.to_bytes(2, "little")
            self.code += operation.x.to_bytes(4, "little", signed=True)
            self.code += operation.y.to_bytes(4, "little", signed=True)
            self.code += operation.z.to_bytes(4, "little", signed=True)
            self.code += operation.resume.to_bytes(2, "little")
        elif isinstance(operation, SetContextAndJump):
            self.code += operation.x.to_bytes(4, "little", signed=True)
            self.code += operation.y.to_bytes(4, "little", signed=True)
            self.code += operation.z.to_bytes(4, "little", signed=True)
            self.code += operation.target.to_bytes(2, "little")
        elif isinstance(operation, Jump):
            self.code += operation.target.to_bytes(2, "little")
        elif spec.payload_size != 0:
            raise ValidationError(f"No encoder for {spec.name}")

    def write_block(self, block: Block) -> int:
        start = len(self.code)
        for operation in block.operations:
            self.write_operation(operation)
        self.mark_labels(block.end_labels)
        return len(self.code) - start


def dumps(script: Script) -> bytes:
    writer = Writer()
    writer.write_block(script.body)
    writer.boundaries.add(len(writer.code))
    code_start = len(writer.labels) * 8 + 4
    table = bytearray()
    for label, offset in writer.labels:
        if offset not in writer.boundaries:
            raise ValidationError(
                f"Label {label:#x} must point to an instruction boundary or EOF"
            )
        table += label.to_bytes(4, "little", signed=True)
        table += (code_start + offset).to_bytes(4, "little", signed=True)
    return bytes(table + b"\xff\xff\xff\xff" + writer.code)
