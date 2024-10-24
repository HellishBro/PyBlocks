import math
import random

from blockly import *

class Category:
    def __init__(self, name: str, description: str, color: tuple[int, int, int], blocks: list[BlockDef]):
        self.name = name
        self.description = description
        self.color = color
        self.blocks = blocks
        for block in self.blocks:
            if not block.color:
                block.color = self.color

class BlockCategories:
    CONTROL = Category("Control", "Controls how the program runs.", (255, 229, 158), [
        BlockDef("start", BlockType.HAT, [Label("when the program starts")]),
        BlockDef("sleep", BlockType.STATEMENT, [Label("wait for"), Component(CompT.NUMBER_INPUT, 1), Label("seconds")]),
        BlockDef("repeat", BlockType.STATEMENT, [Label("repeat"), Component(CompT.NUMBER_INPUT, 10), Label("times"), Component(CompT.STATEMENT_INPUT)]),
        BlockDef("for", BlockType.STATEMENT, [Label("for each"), Component(CompT.VARIABLE_INPUT), Label("in"), Component(CompT.VARIABLE_INPUT), Component(CompT.STATEMENT_INPUT)]),
        BlockDef("while", BlockType.STATEMENT, [Label("repeat while"), Component(CompT.BOOLEAN_INPUT, True), Label("is true"), Component(CompT.STATEMENT_INPUT)]),
        BlockDef("if", BlockType.STATEMENT, [Label("if"), Component(CompT.BOOLEAN_INPUT), Label("then"), Component(CompT.STATEMENT_INPUT)]),
        BlockDef("if-else", BlockType.STATEMENT, [Label("if"), Component(CompT.BOOLEAN_INPUT), Label("then"), Component(CompT.STATEMENT_INPUT), Label("else"), Component(CompT.STATEMENT_INPUT)]),
        BlockDef("try", BlockType.STATEMENT, [Label("try to do"), Component(CompT.STATEMENT_INPUT), Label("except on error"), Component(CompT.STATEMENT_INPUT)]),
        BlockDef("break", BlockType.CAP, [Label("stop the current loop")]),
        BlockDef("continue", BlockType.CAP, [Label("skip to next iteration")]),
        BlockDef("quit", BlockType.CAP, [Label("quit the program")])
    ])
    INPUT = Category("Input", "Gathers input from the user.", (158, 168, 255), [
        BlockDef("input", BlockType.REPORTER, [Label("ask"), Component(CompT.TEXT_INPUT, "What's your name? ")], output_type=DataType.TEXT),
        BlockDef("read-file", BlockType.REPORTER, [Label("read from file"), Component(CompT.TEXT_INPUT, "input.txt")], output_type=DataType.TEXT)
    ])
    OUTPUT = Category("Output", "How the program outputs information.", (255, 158, 182), [
        BlockDef("print", BlockType.STATEMENT, [Label("say"), Component(CompT.TEXT_INPUT, "Hello world!")]),
        BlockDef("write-file", BlockType.STATEMENT, [Label("write to file"), Component(CompT.TEXT_INPUT, "output.txt"), Label("contents"), Component(CompT.TEXT_INPUT, "Hello world!")])
    ])
    NUMBER = Category("Number", "Manipulates numbers and does calculations.", (164, 255, 158), [
        BlockDef("+", BlockType.REPORTER, [Component(CompT.NUMBER_INPUT), Label("+"), Component(CompT.NUMBER_INPUT)], output_type=DataType.NUMBER),
        BlockDef("-", BlockType.REPORTER, [Component(CompT.NUMBER_INPUT), Label("-"), Component(CompT.NUMBER_INPUT)], output_type=DataType.NUMBER),
        BlockDef("*", BlockType.REPORTER, [Component(CompT.NUMBER_INPUT), Label("×"), Component(CompT.NUMBER_INPUT)], output_type=DataType.NUMBER),
        BlockDef("/", BlockType.REPORTER, [Component(CompT.NUMBER_INPUT), Label("÷"), Component(CompT.NUMBER_INPUT)], output_type=DataType.NUMBER),
        BlockDef("^", BlockType.REPORTER, [Component(CompT.NUMBER_INPUT), Label("^"), Component(CompT.NUMBER_INPUT)], output_type=DataType.NUMBER),
        BlockDef("%", BlockType.REPORTER, [Component(CompT.NUMBER_INPUT), Label("mod"), Component(CompT.NUMBER_INPUT)], output_type=DataType.NUMBER),
        BlockDef("rand", BlockType.REPORTER, [Label("random number between"), Component(CompT.NUMBER_INPUT, 1), Label("and"), Component(CompT.NUMBER_INPUT, 10)], output_type=DataType.NUMBER),
        BlockDef("parse-number", BlockType.REPORTER, [Label("parse"), Component(CompT.TEXT_INPUT, "-17.25"), Label("as a number")], output_type=DataType.NUMBER),
        BlockDef("convert-base", BlockType.REPORTER, [Label("convert"), Component(CompT.TEXT_INPUT, "2A"), Label("from base"), Component(CompT.NUMBER_INPUT, 16)], output_type=DataType.NUMBER),
        BlockDef("round", BlockType.REPORTER, [Label("round"), Component(CompT.NUMBER_INPUT)], output_type=DataType.NUMBER),
        BlockDef("floor", BlockType.REPORTER, [Label("round down"), Component(CompT.NUMBER_INPUT)], output_type=DataType.NUMBER),
        BlockDef("ceil", BlockType.REPORTER, [Label("round up"), Component(CompT.NUMBER_INPUT)], output_type=DataType.NUMBER),
        BlockDef("pos", BlockType.REPORTER, [Label("positive of"), Component(CompT.NUMBER_INPUT)], output_type=DataType.NUMBER),
        BlockDef("neg", BlockType.REPORTER, [Label("negative of"), Component(CompT.NUMBER_INPUT)], output_type=DataType.NUMBER),
        BlockDef("root", BlockType.REPORTER, [Component(CompT.NUMBER_INPUT, 2), Label("th root of"), Component(CompT.NUMBER_INPUT)], output_type=DataType.NUMBER),
        BlockDef("log", BlockType.REPORTER, [Label("log base"), Component(CompT.NUMBER_INPUT, 10), Label("of"), Component(CompT.NUMBER_INPUT)], output_type=DataType.NUMBER),
    ])
    COMPARISON = Category("Compare", "Compare and contrasts different values.", (158, 245, 255), [
        BlockDef("=", BlockType.REPORTER, [Component(CompT.INPUT), Label("="), Component(CompT.INPUT, 50)], output_type=DataType.BOOLEAN),
        BlockDef("!=", BlockType.REPORTER, [Component(CompT.INPUT), Label("≠"), Component(CompT.INPUT, 50)], output_type=DataType.BOOLEAN),
        BlockDef(">", BlockType.REPORTER, [Component(CompT.NUMBER_INPUT), Label(">"), Component(CompT.NUMBER_INPUT, 50)], output_type=DataType.BOOLEAN),
        BlockDef(">=", BlockType.REPORTER, [Component(CompT.NUMBER_INPUT), Label("≥"), Component(CompT.NUMBER_INPUT, 50)], output_type=DataType.BOOLEAN),
        BlockDef("<", BlockType.REPORTER, [Component(CompT.NUMBER_INPUT), Label("<"), Component(CompT.NUMBER_INPUT, 50)], output_type=DataType.BOOLEAN),
        BlockDef("<=", BlockType.REPORTER, [Component(CompT.NUMBER_INPUT), Label("≤"), Component(CompT.NUMBER_INPUT, 50)], output_type=DataType.BOOLEAN),
    ])
    BOOLEAN = Category("Boolean", "Manipulates booleans for decision making.", (158, 255, 207), [
        BlockDef("bool", BlockType.REPORTER, [Component(CompT.BOOLEAN_INPUT)], output_type=DataType.BOOLEAN),
        BlockDef("not", BlockType.REPORTER, [Label("not"), Component(CompT.BOOLEAN_INPUT)], output_type=DataType.BOOLEAN),
        BlockDef("and", BlockType.REPORTER, [Component(CompT.BOOLEAN_INPUT), Label("and"), Component(CompT.BOOLEAN_INPUT)], output_type=DataType.BOOLEAN),
        BlockDef("or", BlockType.REPORTER, [Component(CompT.BOOLEAN_INPUT), Label("or"), Component(CompT.BOOLEAN_INPUT)], output_type=DataType.BOOLEAN),
        BlockDef("xor", BlockType.REPORTER, [Component(CompT.BOOLEAN_INPUT), Label("xor"), Component(CompT.BOOLEAN_INPUT)], output_type=DataType.BOOLEAN),
        BlockDef("convert-bool", BlockType.REPORTER, [Label("truthiness of"), Component(CompT.INPUT)], output_type=DataType.BOOLEAN)
    ])
    TEXT = Category("Text", "Manipulates different sorts of text.", (255, 158, 232), [
        BlockDef("join", BlockType.REPORTER, [Label("join"), Component(CompT.TEXT_INPUT, "Hello "), Label("with"), Component(CompT.TEXT_INPUT, "world!")], output_type=DataType.TEXT),
        BlockDef("parse-text", BlockType.REPORTER, [Label("turn"), Component(CompT.INPUT, 21), Label("into text")], output_type=DataType.TEXT),
        BlockDef("char-at", BlockType.REPORTER, [Label("character"), Component(CompT.NUMBER_INPUT, 1), Label("of"), Component(CompT.TEXT_INPUT, "Hello world!")], output_type=DataType.TEXT),
        BlockDef("str-len", BlockType.REPORTER, [Label("length of"), Component(CompT.TEXT_INPUT, "Hello world!")], output_type=DataType.NUMBER),
        BlockDef("str-in", BlockType.REPORTER, [Component(CompT.TEXT_INPUT, "Hello world!"), Label("contains"), Component(CompT.TEXT_INPUT, "world")], output_type=DataType.BOOLEAN),
        BlockDef("startswith", BlockType.REPORTER, [Component(CompT.TEXT_INPUT, "Hello world!"), Label("starts with"), Component(CompT.TEXT_INPUT, "H")], output_type=DataType.BOOLEAN),
        BlockDef("endswith", BlockType.REPORTER, [Component(CompT.TEXT_INPUT, "Hello world!"), Label("ends with"), Component(CompT.TEXT_INPUT, "!")], output_type=DataType.BOOLEAN),
        BlockDef("str-remove", BlockType.REPORTER, [Label("remove all"), Component(CompT.TEXT_INPUT, "o"), Label("from"), Component(CompT.TEXT_INPUT, "Hello world!")], output_type=DataType.TEXT),
        BlockDef("str-replace", BlockType.REPORTER, [Label("replace all"), Component(CompT.TEXT_INPUT, "o"), Label("with"), Component(CompT.TEXT_INPUT, "a"), Label("of"), Component(CompT.TEXT_INPUT, "Hello world!")], output_type=DataType.TEXT),
    ])
    VARIABLE = Category("Variable", "Stores and change variables.", (255, 198, 158), [
        BlockDef("get-var", BlockType.REPORTER, [Label("get"), Component(CompT.VARIABLE_INPUT)], output_type=DataType.ANY),
        BlockDef("set", BlockType.STATEMENT, [Label("set variable"), Component(CompT.VARIABLE_INPUT), Label("to"), Component(CompT.INPUT)]),
        BlockDef("increment", BlockType.STATEMENT, [Label("increment"), Component(CompT.VARIABLE_INPUT), Label("by"), Component(CompT.NUMBER_INPUT, 1)]),
        BlockDef("decrement", BlockType.STATEMENT, [Label("decrement"), Component(CompT.VARIABLE_INPUT), Label("by"), Component(CompT.NUMBER_INPUT, 1)])
    ])
    # PROCEDURE = Category("Procedure", "Create and use your own custom blocks", (202, 158, 255), [
    #     BlockDef("return", BlockType.CAP, [Label("return"), Component(CompT.INPUT)])
    # ])

def str2(obj: object) -> str:
    if isinstance(obj, (int, float)):
        return f"{obj:g}"
    elif is_number(obj):
        return f"{float(obj):g}"
    else:
        return str(obj)

def is_number(thing) -> bool:
    if isinstance(thing, (int, float)):
        return True
    try:
        float(thing)
        return True
    except ValueError:
        return False

# CONTROL
for ___ in range(1):
    class LoopBreak(Exception): pass
    class LoopContinue(Exception): pass

    @BlockCategories.CONTROL.blocks[0].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield

    @BlockCategories.CONTROL.blocks[1].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        environment.sleep_timer = params[0]
        while environment.sleep_timer > 0:
            environment.sleep_timer -= 1 / 60
            yield

    @BlockCategories.CONTROL.blocks[2].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        for __ in range(int(params[0])):
            try:
                yield from params[1].execute(environment)
            except LoopBreak:
                break
            except LoopContinue:
                continue

    @BlockCategories.CONTROL.blocks[3].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        for value in environment[params[1]]:
            environment[params[0]] = value
            try:
                yield from params[2].execute(environment)
            except LoopBreak:
                break
            except LoopContinue:
                continue

    @BlockCategories.CONTROL.blocks[4].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        #print(block.get_value(0, environment))
        while block.get_value(0, environment):
            #print("iter")
            try:
                yield from params[1].execute(environment)
            except LoopBreak:
                break
            except LoopContinue:
                continue

    @BlockCategories.CONTROL.blocks[5].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        if params[0]:
            yield from params[1].execute(environment)

    @BlockCategories.CONTROL.blocks[6].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        if params[0]:
            yield from params[1].execute(environment)
        else:
            yield from params[2].execute(environment)

    @BlockCategories.CONTROL.blocks[7].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        try:
            yield from params[0].execute(environment)
        except RuntimeError:
            raise # quit
        except Exception:
            yield from params[1].execute(environment)

    @BlockCategories.CONTROL.blocks[8].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        raise LoopBreak()

    @BlockCategories.CONTROL.blocks[9].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        raise LoopContinue()

    @BlockCategories.CONTROL.blocks[10].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        raise RuntimeError()

# INPUT
for ___ in range(1):
    @BlockCategories.INPUT.blocks[0].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        environment.input_line = str2(params[0])
        return environment.stdin # TODO: fix this

    @BlockCategories.INPUT.blocks[1].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        with open(params[0]) as file:
            data = file.read()
        yield data

# OUTPUT
for ___ in range(1):
    @BlockCategories.OUTPUT.blocks[0].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        environment.output.append(str2(params[0]))
        yield

    @BlockCategories.OUTPUT.blocks[1].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        with open(params[0], "w") as f:
            f.write(str2(params[1]))
        yield

# NUMBER
for ___ in range(1):
    @BlockCategories.NUMBER.blocks[0].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield params[0] + params[1]

    @BlockCategories.NUMBER.blocks[1].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield params[0] - params[1]


    @BlockCategories.NUMBER.blocks[2].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield params[0] * params[1]


    @BlockCategories.NUMBER.blocks[3].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield params[0] / params[1]


    @BlockCategories.NUMBER.blocks[4].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield params[0] ** params[1]


    @BlockCategories.NUMBER.blocks[5].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield params[0] % params[1]


    @BlockCategories.NUMBER.blocks[6].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield random.randint(int(params[0]), int(params[1]))


    @BlockCategories.NUMBER.blocks[7].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield float(params[0])


    @BlockCategories.NUMBER.blocks[8].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield int(params[0], params[1])


    @BlockCategories.NUMBER.blocks[9].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield round(params[0])


    @BlockCategories.NUMBER.blocks[10].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield math.floor(params[0])


    @BlockCategories.NUMBER.blocks[11].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield math.ceil(params[0])


    @BlockCategories.NUMBER.blocks[12].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield abs(params[0])


    @BlockCategories.NUMBER.blocks[13].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield - params[0]


    @BlockCategories.NUMBER.blocks[14].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield params[1] ** (1 / params[0])


    @BlockCategories.NUMBER.blocks[15].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield math.log(params[1], params[0])

# COMPARISON
for ___ in range(1):
    @BlockCategories.COMPARISON.blocks[0].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        if is_number(params[0]) and is_number(params[1]):
            yield float(params[0]) == float(params[1])
        yield str2(params[0]) == str2(params[1])


    @BlockCategories.COMPARISON.blocks[1].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        if is_number(params[0]) and is_number(params[1]):
            yield float(params[0]) != float(params[1])
        yield str2(params[0]) != str2(params[1])


    @BlockCategories.COMPARISON.blocks[2].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield params[0] > params[1]


    @BlockCategories.COMPARISON.blocks[3].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield params[0] >= params[1]


    @BlockCategories.COMPARISON.blocks[4].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield params[0] < params[1]


    @BlockCategories.COMPARISON.blocks[5].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield params[0] <= params[1]

# BOOLEAN
for ___ in range(1):
    @BlockCategories.BOOLEAN.blocks[0].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield bool(params[0])

    @BlockCategories.BOOLEAN.blocks[1].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield not params[1]


    @BlockCategories.BOOLEAN.blocks[2].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield params[0] and params[1]


    @BlockCategories.BOOLEAN.blocks[3].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield params[0] or params[1]


    @BlockCategories.BOOLEAN.blocks[4].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield bool(bool(params[0]) ^ bool(params[1]))


    @BlockCategories.BOOLEAN.blocks[5].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield bool(params[0])

# TEXT
for ___ in range(1):
    @BlockCategories.TEXT.blocks[0].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield str2(params[0]) + str2(params[1])


    @BlockCategories.TEXT.blocks[1].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield str2(params[0])


    @BlockCategories.TEXT.blocks[2].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield params[1][int(params[0] - 1)]


    @BlockCategories.TEXT.blocks[3].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield len(params[0])


    @BlockCategories.TEXT.blocks[4].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield params[1] in params[0]


    @BlockCategories.TEXT.blocks[5].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield params[0].startswith(params[1])


    @BlockCategories.TEXT.blocks[6].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield params[0].endswith(params[1])


    @BlockCategories.TEXT.blocks[7].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield params[1].replace(params[0], "")


    @BlockCategories.TEXT.blocks[6].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield params[2].replace(params[0], params[1])

# VARIABLE
for ___ in range(1):
    @BlockCategories.VARIABLE.blocks[0].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        yield environment[params[0]]

    @BlockCategories.VARIABLE.blocks[1].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        environment[params[0]] = params[1]
        yield

    @BlockCategories.VARIABLE.blocks[2].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        try:
            environment[params[0]] = float(environment[params[0]])
        except ValueError:
            pass

        environment[params[0]] += params[1]
        yield


    @BlockCategories.VARIABLE.blocks[3].on_trigger()
    def _(params: list, environment: Environment, block: Block):
        try:
            environment[params[0]] = float(environment[params[0]])
        except ValueError:
            pass

        environment[params[0]] -= params[1]
        yield

ALL_CATEGORIES = [
    BlockCategories.CONTROL,
    BlockCategories.INPUT,
    BlockCategories.OUTPUT,
    BlockCategories.NUMBER,
    BlockCategories.COMPARISON,
    BlockCategories.BOOLEAN,
    BlockCategories.TEXT,
    BlockCategories.VARIABLE,
    # BlockCategories.PROCEDURE
]

def get_all_blocks():
    all_blocks = []
    for category in ALL_CATEGORIES:
        all_blocks.extend(category.blocks)
    return all_blocks

ELLIPSIS = BlockDef("ellipsis", BlockType.STATEMENT, [Label("...")], (160, 160, 160))
