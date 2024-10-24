from enum import Enum, auto
from typing import Any, Generator

__all__ = [
    "BlockType", "CompT", "DataType",
    "Environment",
    "Component", "Label",
    "Block", "BlockDef", "Stack"
]

class BlockType(Enum):
    HAT = auto()
    CAP = auto()
    STATEMENT = auto()
    REPORTER = auto()

    def __repr__(self):
        return self.name

class CompT(Enum):
    LABEL = auto()
    TEXT_INPUT = auto()
    NUMBER_INPUT = auto()
    BOOLEAN_INPUT = auto()
    VARIABLE_INPUT = auto()
    BLOCK_INPUT = auto()
    STATEMENT_INPUT = auto()
    INPUT = auto()

    def __repr__(self):
        return self.name

class DataType(Enum):
    TEXT = auto()
    NUMBER = auto()
    BOOLEAN = auto()
    ANY = auto()
    NIL = auto()

    def __repr__(self):
        return self.name

class Component:
    def __init__(self, type: CompT, default: object = None, text: str = None):
        self.type = type
        self.default = self.get_default()
        if default is not None:
            self.default = default
        self.text = text

    def get_default(self):
        match self.type:
            case CompT.BOOLEAN_INPUT:
                return False
            case CompT.STATEMENT_INPUT:
                return Stack([])
            case _:
                return ""

    def fit(self, data_type: DataType) -> bool:
        if data_type == DataType.ANY:
            if self.type not in (CompT.STATEMENT_INPUT, CompT.BLOCK_INPUT, CompT.VARIABLE_INPUT):
                return True
            return False

        match self.type:
            case CompT.NUMBER_INPUT:
                return data_type == DataType.NUMBER
            case CompT.TEXT_INPUT:
                return data_type == DataType.TEXT
            case CompT.BOOLEAN_INPUT:
                return data_type == DataType.BOOLEAN
            case CompT.INPUT:
                return True
            case _:
                return False

    def __repr__(self):
        return f"C({self.type!r}, {self.text!r})"

    def serialize(self) -> dict:
        return {
            "type": self.type.name,
            "text": self.text
        }

    @classmethod
    def deserialize(cls, json: dict):
        return cls(CompT(json["type"]), json["text"])

def Label(text: str) -> Component:
    return Component(CompT.LABEL, text=text)

class Environment:
    def __init__(self):
        self.globals = {}
        self.sleep_timer = 0
        self.output = []
        self.input_line = None
        self.stdin = ""

    def __getitem__(self, item):
        return self.globals[item]

    def __setitem__(self, key, value):
        self.globals[key] = value

class BlockDef:
    """
    Definition of a block.
    Not actually a block, but is the blueprint for one.
    """
    def __init__(self, id: str, block_type: BlockType, components: list[Component], color: tuple[int, int, int] | int = None, output_type: DataType = DataType.NIL):
        self.id = id
        self.block_type = block_type
        self.components = components
        self.non_label_components = list(filter(lambda c: c.type != CompT.LABEL, self.components))
        self.color = color
        self.execute = lambda v, e, b: None
        self.output_type = output_type

    def input_id(self, id: int) -> Component:
        return self.non_label_components[id]

    def count_inputs(self) -> int:
        return len(self.non_label_components)

    def on_trigger(self):
        """
        Example::

            @block.on_trigger()
            def method(params, environment):
                pass

        """
        def wrapper(func):
            def inner(params: list, environment: Environment, block: Block):
                return func(params, environment, block)

            self.execute = func
            return inner

        return wrapper

    def __repr__(self):
        display = []

        for component in self.components:
            match component.type:
                case CompT.LABEL:
                    display.append(component.text)
                case CompT.TEXT_INPUT:
                    display.append("[]")
                case CompT.NUMBER_INPUT:
                    display.append("()")
                case CompT.BOOLEAN_INPUT:
                    display.append("<>")
                case CompT.VARIABLE_INPUT:
                    display.append("[ v]")
                case CompT.STATEMENT_INPUT:
                    display.append("[>  >]")
                case _:
                    display.append("{}")

        display = " ".join(display)
        if self.block_type in (BlockType.STATEMENT, BlockType.CAP, BlockType.HAT):
            return display
        else:
            if self.output_type == bool:
                return "<" + display + ">"
            else:
                return "(" + display + ")"

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "blockType": self.block_type.name,
            "components": [comp.serialize() for comp in self.components],
            "outputType": self.output_type.name
        }

    @classmethod
    def deserialize(cls, json: dict):
        return cls(json["id"], BlockType(json["blockType"]), [Component.deserialize(comp) for comp in json["components"]], DataType(json["outputType"]))

class Block:
    """
    This is actually the block
    """
    def __init__(self, definition: BlockDef, values: list):
        self.definition = definition
        self.values = values
        self.rect: tuple[int | float, int | float, int | float, int | float] = 0, 0, 0, 0 # set at render time
        self.values_rect: list[tuple[int | float, int | float, int | float, int | float]] = [] # set at render time

    def copy(self) -> 'Block':
        copied_values = []
        for val in self.values:
            if isinstance(val, (Block, Stack)):
                val = val.copy()
            copied_values.append(val)

        return Block(self.definition, copied_values)

    def __eq__(self, other: 'Block') -> bool:
        if other is None: return False
        return self.definition == other.definition and self.values == other.values

    def __hash__(self):
        return hash(hash(self.definition) + hash(tuple(self.values)) + hash(self.rect) + hash(tuple(self.values_rect)))

    def execute(self, environment: Environment) -> Generator | None:
        # print(self)
        parsed = []
        for i, value in enumerate(self.values):
            if isinstance(value, Block):
                while isinstance(value, Block):
                    value = next(value.execute(environment))
            elif value is None:
                value = self.definition.input_id(i).default

            if self.definition.input_id(i).type == CompT.NUMBER_INPUT:
                value = float(value)
            elif self.definition.input_id(i).type == CompT.TEXT_INPUT:
                value = str(value)

            parsed.append(value)

        return self.definition.execute(parsed, environment, self)

    def get_value(self, index: int, environment: Environment) -> object:
        value = self.values[index]
        if value is None:
            return self.definition.input_id(index).default
        if isinstance(value, Block):
            while isinstance(value, Block):
                value = next(value.execute(environment))
        return value

    def __repr__(self):
        return f"Block(\"{self.definition.id}\", {self.values!r}, rect={self.rect!r})"

    def serialize(self) -> dict:
        return {
            "definition": self.definition.id,
            "values": [value.serialize() if isinstance(value, (Block, Stack)) else value for value in self.values]
        }

    @classmethod
    def deserialize(cls, block_definitions: list[BlockDef], json: dict):
        try:
            return Block(list(filter(lambda d: d.id == json["definition"], block_definitions))[0], [(Block.deserialize(block_definitions, value) if "definition" in value else Stack.deserialize(block_definitions, value)) if isinstance(value, dict) else value for value in json["values"]])
        except IndexError:
            return Block(BlockDef("deprecated", BlockType.STATEMENT, [Label("deprecated code")], (255, 0, 0)), [])

class Stack:
    def __init__(self, blocks: list[Block], position: tuple[int, int] = None):
        self.blocks = blocks
        self.position = tuple(position) if position is not None else None

    def copy(self) -> 'Stack':
        stack = Stack(self.blocks.copy(), self.position)
        return stack

    def __repr__(self):
        return f"Stack({self.blocks!r}, {self.position!r})"

    def __hash__(self):
        return hash(hash(tuple(self.blocks)) + hash(self.position))

    def execute(self, environment: Environment):
        for block in self.blocks:
            yield from block.execute(environment)

    def serialize(self) -> dict:
        return {
            "blocks": [block.serialize() for block in self.blocks],
            "pos": self.position
        }

    @classmethod
    def deserialize(cls, block_definitions: list[BlockDef], json: dict):
        stack = Stack([Block.deserialize(block_definitions, block) for block in json["blocks"]], json["pos"])
        return stack

