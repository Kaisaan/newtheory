"""Read and write the nscript DSL."""

from dataclasses import fields

from .errors import NscriptParseError, ValidationError
from .model import Block, Script
from .operations.base import Operation
from .operations.flow import ConditionalBlock
from .operations.text import ChoiceMessage
from .registry import BY_NAME, get_spec
from .syntax import (
    format_label,
    format_value,
    parse_instruction,
    parse_label,
    parse_value,
)

_STRUCTURAL_FIELDS = {"labels", "predicate", "body"}


class Reader:
    def __init__(self, text: str):
        self.lines = [
            (number, line.removesuffix("\r"))
            for number, line in enumerate(text.split("\n"), 1)
            if line.strip()
        ]
        self.index = 0

    def error(self, message: str) -> NscriptParseError:
        if self.index < len(self.lines):
            number, line = self.lines[self.index]
            return NscriptParseError(f"nscript line {number}: {message}; got {line!r}")
        return NscriptParseError(f"End of nscript: {message}")

    def peek(self) -> str | None:
        return self.lines[self.index][1] if self.index < len(self.lines) else None

    def read_labels(self) -> list[int]:
        """
        Read labels until the first non-label line
        """
        labels = []
        while (line := self.peek()) is not None:
            token = line.strip()
            if not token.startswith("LABEL_") or not token.endswith(":"):
                break
            try:
                labels.append(parse_label(token[:-1]))
            except ValueError as exc:
                raise self.error(str(exc)) from exc
            self.index += 1
        return labels

    def expect(self, marker: str):
        line = self.peek()
        if line is None or line.strip() != marker:
            raise self.error(f"Expected {marker}")
        self.index += 1

    def read_operation(self, labels: list[int]) -> Operation:
        line = self.peek()
        if line is None or line.strip() in ("StartBlock:", "EndBlock:"):
            raise self.error("Expected an operation")
        try:
            name, values = parse_instruction(line)
            spec = BY_NAME.get(name)
            if spec is None:
                raise ValueError(f"Unknown operation: {name}")
            allowed = {
                field.name
                for field in fields(spec.operation_type)
                if field.name not in _STRUCTURAL_FIELDS
            }
            unknown = values.keys() - allowed
            if unknown:
                raise ValueError(
                    f"Unknown fields for {name}: {', '.join(sorted(unknown))}"
                )
            kwargs = {key: parse_value(key, value) for key, value in values.items()}
            if spec.operation_type is ConditionalBlock:
                operation = None
            else:
                operation = spec.operation_type(labels=labels, **kwargs)
                get_spec(operation)
        except (TypeError, ValueError) as exc:
            raise self.error(str(exc)) from exc
        self.index += 1
        if spec.operation_type is ConditionalBlock:
            predicate = self.read_operation(self.read_labels())
            self.expect("StartBlock:")
            return ConditionalBlock(
                labels=labels, predicate=predicate, body=self.read_block(nested=True)
            )
        if isinstance(operation, ChoiceMessage):
            self.expect("StartBlock:")
            operation.body = self.read_block(nested=True)
        return operation

    def read_block(self, *, nested: bool = False) -> Block:
        block = Block()
        while True:
            labels = self.read_labels()
            line = self.peek()
            if line is None:
                if nested:
                    raise self.error("Expected EndBlock:")
                block.end_labels = labels
                return block
            if line.strip() == "EndBlock:":
                if not nested:
                    raise self.error("Unmatched EndBlock:")
                self.index += 1
                block.end_labels = labels
                return block
            block.operations.append(self.read_operation(labels))


def loads(text: str) -> Script:
    return Script(Reader(text).read_block())


class Writer:
    def __init__(self):
        self.lines: list[str] = []

    def write_labels(self, labels: list[int], indent: int):
        for label in labels:
            self.lines.append(" " * indent + format_label(label) + ":")

    def write_operation(self, operation: Operation, indent: int):
        spec = get_spec(operation)
        self.write_labels(operation.labels, indent)
        terms = [spec.name]
        for field in fields(operation):
            if field.name not in _STRUCTURAL_FIELDS:
                value = format_value(field.name, getattr(operation, field.name))
                terms.append(f"{field.name}:{value}")
        self.lines.append(" " * indent + "\t".join(terms))
        if isinstance(operation, ConditionalBlock):
            self.write_operation(operation.predicate, indent + 2)
        if isinstance(operation, (ConditionalBlock, ChoiceMessage)):
            self.lines.append(" " * indent + "StartBlock:")
            self.write_block(operation.body, indent + 2)
            self.lines.append(" " * indent + "EndBlock:")

    def write_block(self, block: Block, indent: int = 0):
        for operation in block.operations:
            self.write_operation(operation, indent)
        self.write_labels(block.end_labels, indent)


def dumps(script: Script) -> str:
    writer = Writer()
    try:
        writer.write_block(script.body)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"Cannot format nscript: {exc}") from exc
    return "\n".join(writer.lines) + ("\n" if writer.lines else "")
