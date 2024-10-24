import pygame as pg
from functools import cache
from blockly import *
from constants import *
from blocks import ELLIPSIS

@cache
def outline(color: tuple[int, int, int]) -> tuple[int, int, int]:
    sub = 100
    return max(color[0] - sub, 0), max(color[1] - sub, 0), max(color[2] - sub, 0)

def top_down_outline(surf: pg.Surface, color: tuple[int, int, int]):
    pg.draw.line(surf, outline(color), (0, 0), (surf.get_width(), 0), LINE_WIDTH)
    pg.draw.line(surf, outline(color), (0, surf.get_height() - 1), (surf.get_width(), surf.get_height() - 1), LINE_WIDTH)

def make_cap(surf: pg.Surface, color: tuple[int, int, int]) -> pg.Surface:
    new_surf = pg.Surface((surf.get_width(), surf.get_height() + DEFAULT_PADDING), pg.SRCALPHA)
    pg.draw.rect(new_surf, color, (0, 0, DEFAULT_CONNECTION_SIZE, DEFAULT_PADDING))
    pg.draw.rect(new_surf, color, (DEFAULT_CONNECTION_SIZE * 2, 0, surf.get_width(), DEFAULT_PADDING))
    new_surf.blit(surf, (0, DEFAULT_PADDING))

    # outlines
    pg.draw.line(new_surf, outline(color), (0, new_surf.get_height() - 1), (new_surf.get_width(), new_surf.get_height() - 1), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (0, 0), (0, new_surf.get_height() - 1), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (new_surf.get_width() - 1, 0), (new_surf.get_width() - 1, new_surf.get_height() - 1), LINE_WIDTH)

    # top
    pg.draw.line(new_surf, outline(color), (0, 0), (DEFAULT_CONNECTION_SIZE, 0), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (DEFAULT_CONNECTION_SIZE, 0), (DEFAULT_CONNECTION_SIZE, DEFAULT_PADDING), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (DEFAULT_CONNECTION_SIZE, DEFAULT_PADDING), (DEFAULT_CONNECTION_SIZE * 2, DEFAULT_PADDING), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (DEFAULT_CONNECTION_SIZE * 2, DEFAULT_PADDING), (DEFAULT_CONNECTION_SIZE * 2, 0), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (DEFAULT_CONNECTION_SIZE * 2, 0), (new_surf.get_width(), 0), LINE_WIDTH)

    return new_surf

def make_hat(surf: pg.Surface, color: tuple[int, int, int]) -> pg.Surface:
    new_surf = pg.Surface((surf.get_width(), surf.get_height() + DEFAULT_PADDING * 5), pg.SRCALPHA)
    height = new_surf.get_height() - 1
    old_height = surf.get_height() + DEFAULT_PADDING * 4
    pg.draw.rect(new_surf, color, (DEFAULT_CONNECTION_SIZE, old_height, DEFAULT_CONNECTION_SIZE, DEFAULT_PADDING))
    pg.draw.rect(new_surf, color, (0, 0, new_surf.get_width(), DEFAULT_PADDING * 4))
    new_surf.blit(surf, (0, DEFAULT_PADDING * 4))

    # outlines
    pg.draw.line(new_surf, outline(color), (0, 0), (new_surf.get_width(), 0), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (0, 0), (0, old_height - 1), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (new_surf.get_width() - 1, 0), (new_surf.get_width() - 1, old_height - 1), LINE_WIDTH)

    # bottom
    pg.draw.line(new_surf, outline(color), (0, old_height), (DEFAULT_CONNECTION_SIZE, old_height), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (DEFAULT_CONNECTION_SIZE, old_height), (DEFAULT_CONNECTION_SIZE, height), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (DEFAULT_CONNECTION_SIZE, height), (DEFAULT_CONNECTION_SIZE * 2, height), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (DEFAULT_CONNECTION_SIZE * 2, height), (DEFAULT_CONNECTION_SIZE * 2, old_height), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (DEFAULT_CONNECTION_SIZE * 2, old_height), (new_surf.get_width(), old_height), LINE_WIDTH)

    return new_surf

def make_stack(surf: pg.Surface, color: tuple[int, int, int]) -> pg.Surface:
    new_surf = pg.Surface((surf.get_width(), surf.get_height() + DEFAULT_PADDING * 2), pg.SRCALPHA)
    height = new_surf.get_height() - 1
    old_height = surf.get_height() + DEFAULT_PADDING
    pg.draw.rect(new_surf, color, (0, 0, DEFAULT_CONNECTION_SIZE, DEFAULT_PADDING))
    pg.draw.rect(new_surf, color, (DEFAULT_CONNECTION_SIZE * 2, 0, surf.get_width(), DEFAULT_PADDING))
    pg.draw.rect(new_surf, color, (DEFAULT_CONNECTION_SIZE, old_height, DEFAULT_CONNECTION_SIZE, DEFAULT_PADDING))
    new_surf.blit(surf, (0, DEFAULT_PADDING))

    # outlines
    pg.draw.line(new_surf, outline(color), (0, 0), (0, old_height - 1), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (new_surf.get_width() - 1, 0), (new_surf.get_width() - 1, old_height - 1), LINE_WIDTH)

    # top
    pg.draw.line(new_surf, outline(color), (0, 0), (DEFAULT_CONNECTION_SIZE, 0), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (DEFAULT_CONNECTION_SIZE, 0), (DEFAULT_CONNECTION_SIZE, DEFAULT_PADDING), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (DEFAULT_CONNECTION_SIZE, DEFAULT_PADDING), (DEFAULT_CONNECTION_SIZE * 2, DEFAULT_PADDING), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (DEFAULT_CONNECTION_SIZE * 2, DEFAULT_PADDING), (DEFAULT_CONNECTION_SIZE * 2, 0), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (DEFAULT_CONNECTION_SIZE * 2, 0), (new_surf.get_width(), 0), LINE_WIDTH)

    # bottom
    pg.draw.line(new_surf, outline(color), (0, old_height), (DEFAULT_CONNECTION_SIZE, old_height), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (DEFAULT_CONNECTION_SIZE, old_height), (DEFAULT_CONNECTION_SIZE, height), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (DEFAULT_CONNECTION_SIZE, height), (DEFAULT_CONNECTION_SIZE * 2, height), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (DEFAULT_CONNECTION_SIZE * 2, height), (DEFAULT_CONNECTION_SIZE * 2, old_height), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (DEFAULT_CONNECTION_SIZE * 2, old_height), (new_surf.get_width(), old_height), LINE_WIDTH)

    return new_surf

def surround_unknown(surf: pg.Surface, color: tuple[int, int, int]) -> pg.Surface:
    pg.draw.rect(surf, (255, 0, 0), (0, 0, surf.get_width(), surf.get_height()), LINE_WIDTH * 2)
    return surf

def surround_bool(surf: pg.Surface, color: tuple[int, int, int]) -> pg.Surface:
    diameter = surf.get_height()
    radius = diameter / 2
    top_down_outline(surf, color)
    new_surf = pg.Surface((surf.get_width() + diameter, diameter), pg.SRCALPHA)
    new_width = new_surf.get_width()

    pg.draw.polygon(new_surf, color, ((radius, 0), (0, radius), (radius, diameter)))
    pg.draw.polygon(new_surf, color, ((new_width - radius, 0), (new_width, radius), (new_width - radius, diameter)))

    # outline
    pg.draw.line(new_surf, outline(color), (radius, 0), (0, radius), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (0, radius + 1), (radius, diameter), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (new_width - radius, 0), (new_width - 1, radius), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (new_width, radius), (new_width - radius, diameter), LINE_WIDTH)

    new_surf.blit(surf, (radius, 0))
    return new_surf

def surround_number(surf: pg.Surface, color: tuple[int, int, int]) -> pg.Surface:
    diameter = surf.get_height()
    radius = diameter / 2
    top_down_outline(surf, color)
    new_surf = pg.Surface((surf.get_width() + diameter, diameter), pg.SRCALPHA)

    pg.draw.circle(new_surf, color, (radius, radius), radius, draw_top_left=True, draw_bottom_left=True)
    pg.draw.circle(new_surf, color, (new_surf.get_width() - radius, radius), radius, draw_top_right=True, draw_bottom_right=True)

    # outlines
    pg.draw.circle(new_surf, outline(color), (radius, radius), radius, LINE_WIDTH, draw_top_left=True, draw_bottom_left=True)
    pg.draw.circle(new_surf, outline(color), (new_surf.get_width() - radius, radius), radius, LINE_WIDTH, draw_top_right=True, draw_bottom_right=True)

    new_surf.blit(surf, (radius, 0))
    return new_surf

def surround_any(surf: pg.Surface, color: tuple[int, int, int]) -> pg.Surface:
    # [| data |]
    new_surf = pg.Surface((surf.get_width() + DEFAULT_PADDING * 4, surf.get_height()), pg.SRCALPHA)
    top_connect_y = (surf.get_height() - DEFAULT_CONNECTION_SIZE) / 2
    bottom_connect_y = new_surf.get_height() - top_connect_y

    pg.draw.rect(new_surf, color, (0, top_connect_y, DEFAULT_PADDING, DEFAULT_CONNECTION_SIZE))
    pg.draw.rect(new_surf, color, (new_surf.get_width() - DEFAULT_PADDING, top_connect_y, DEFAULT_PADDING, DEFAULT_CONNECTION_SIZE))
    pg.draw.rect(new_surf, color, (DEFAULT_PADDING, 0, DEFAULT_PADDING, new_surf.get_height()))
    pg.draw.rect(new_surf, color, (new_surf.get_width() - DEFAULT_PADDING * 2, 0, DEFAULT_PADDING, new_surf.get_height()))

    new_surf.blit(surf, (DEFAULT_PADDING * 2, 0))

    # outlines
    pg.draw.line(new_surf, outline(color), (DEFAULT_PADDING, 0), (new_surf.get_width() - DEFAULT_PADDING, 0), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (DEFAULT_PADDING, new_surf.get_height() - 1), (new_surf.get_width() - DEFAULT_PADDING, new_surf.get_height() - 1), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (0, top_connect_y), (DEFAULT_PADDING, top_connect_y), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (new_surf.get_width() - DEFAULT_PADDING, top_connect_y), (new_surf.get_width(), top_connect_y), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (0, bottom_connect_y), (DEFAULT_PADDING, bottom_connect_y), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (new_surf.get_width() - DEFAULT_PADDING, bottom_connect_y), (new_surf.get_width(), bottom_connect_y), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (DEFAULT_PADDING, 0), (DEFAULT_PADDING, top_connect_y), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (0, top_connect_y), (0, bottom_connect_y), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (DEFAULT_PADDING, bottom_connect_y), (DEFAULT_PADDING, new_surf.get_height()), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (new_surf.get_width() - DEFAULT_PADDING - 1, 0), (new_surf.get_width() - DEFAULT_PADDING - 1, top_connect_y), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (new_surf.get_width() - 1, top_connect_y), (new_surf.get_width() - 1, bottom_connect_y), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (new_surf.get_width() - DEFAULT_PADDING - 1, bottom_connect_y), (new_surf.get_width() - DEFAULT_PADDING - 1, new_surf.get_height()), LINE_WIDTH)

    return new_surf

def surround_text(surf: pg.Surface, color: tuple[int, int, int]) -> pg.Surface:
    ball_radius = surf.get_height() / 4
    width, height = surf.get_size()
    top_down_outline(surf, color)
    new_surf = pg.Surface((surf.get_width() + ball_radius * 2, height), pg.SRCALPHA)

    pg.draw.circle(new_surf, color, (ball_radius, ball_radius), ball_radius, draw_top_left=True)
    pg.draw.circle(new_surf, color, (ball_radius, height - ball_radius), ball_radius, draw_bottom_left=True)
    pg.draw.circle(new_surf, color, (width + ball_radius, ball_radius), ball_radius, draw_top_right=True)
    pg.draw.circle(new_surf, color, (width + ball_radius, height - ball_radius), ball_radius, draw_bottom_right=True)
    pg.draw.rect(new_surf, color, (0, ball_radius, ball_radius, ball_radius * 2 + 1))
    pg.draw.rect(new_surf, color, (width + ball_radius, ball_radius, ball_radius, ball_radius * 2 + 1))

    # outlines
    pg.draw.circle(new_surf, outline(color), (ball_radius, ball_radius), ball_radius, LINE_WIDTH, draw_top_left=True)
    pg.draw.circle(new_surf, outline(color), (ball_radius, height - ball_radius), ball_radius, LINE_WIDTH, draw_bottom_left=True)
    pg.draw.circle(new_surf, outline(color), (width + ball_radius, ball_radius), ball_radius, LINE_WIDTH, draw_top_right=True)
    pg.draw.circle(new_surf, outline(color), (width + ball_radius, height - ball_radius), ball_radius, LINE_WIDTH, draw_bottom_right=True)
    pg.draw.line(new_surf, outline(color), (0, ball_radius), (0, height - ball_radius), LINE_WIDTH)
    pg.draw.line(new_surf, outline(color), (width + ball_radius * 2 - 1, ball_radius), (width + ball_radius * 2 - 1, height - ball_radius), LINE_WIDTH)

    new_surf.blit(surf, (ball_radius, 0))
    return new_surf

def render_bool(value: bool) -> pg.Surface:
    text = FONT.render(str(value).upper(), True, (0, 0, 0))
    surf = pg.Surface((text.get_width(), text.get_height() + DEFAULT_PADDING), pg.SRCALPHA)
    color = (100, 255, 100) if value else (255, 100, 100)
    surf.fill(color)
    surf.blit(text, (0, DEFAULT_PADDING / 2))
    return surround_bool(surf, color)

def render_text(value: str) -> pg.Surface:
    text = FONT.render(str(value), True, (0, 0, 0))
    width = text.get_width()
    width = max(width, DEFAULT_PADDING * 3)
    surf = pg.Surface((width, text.get_height() + DEFAULT_PADDING), pg.SRCALPHA)
    surf.fill((255, 255, 255))
    surf.blit(text, (0, DEFAULT_PADDING / 2))
    return surround_text(surf, (255, 255, 255))

def render_any(value: object) -> pg.Surface:
    text = FONT.render(str(value), True, (0, 0, 0))
    width = text.get_width()
    width = max(width, DEFAULT_PADDING * 3)
    surf = pg.Surface((width, text.get_height() + DEFAULT_PADDING), pg.SRCALPHA)
    surf.fill((255, 255, 255))
    surf.blit(text, (0, DEFAULT_PADDING / 2))
    return surround_any(surf, (255, 255, 255))

def render_number(value: float | int) -> pg.Surface:
    text = FONT.render(str(value), True, (0, 0, 0))
    surf = pg.Surface((text.get_width(), text.get_height() + DEFAULT_PADDING), pg.SRCALPHA)
    surf.fill((255, 255, 255))
    surf.blit(text, (0, DEFAULT_PADDING / 2))
    return surround_number(surf, (255, 255, 255))

def get_top_padding(block_type: BlockType) -> int:
    if block_type in (BlockType.CAP, BlockType.STATEMENT):
        return DEFAULT_PADDING
    elif block_type == BlockType.HAT:
        return DEFAULT_PADDING * 4
    else:
        return DEFAULT_PADDING / 2

def get_left_padding(block: Block, height: int) -> int:
    if block.definition.block_type == BlockType.REPORTER:
        if block.definition.output_type in (DataType.NUMBER, DataType.BOOLEAN):
            return height // 2
        elif block.definition.output_type == DataType.TEXT:
            return height // 4
        elif block.definition.output_type == DataType.ANY:
            return DEFAULT_PADDING * 1.5
    return 0

#@cache
def render_block(block: Block) -> pg.Surface:
    render_queue: list[tuple[list[pg.Surface], tuple[int, int]]] = []
    """
    Dimensions: tuple[int, int]
    ComponentRender: list[pg.Surface]
    Layer: tuple[ComponentRender, Dimensions]
    render_queue: list[Layer]
    """
    index = 0

    is_reporter = block.definition.block_type == BlockType.REPORTER

    current_layer = []
    def push_layer():
        nonlocal current_layer
        if current_layer:
            render_queue.append((current_layer, (sum(comp.get_width() for comp in current_layer) + DEFAULT_PADDING * (len(current_layer) - 1), max(comp.get_height() for comp in current_layer))))
            current_layer = []

    for component in block.definition.components:
        rendered: pg.Surface

        if component.type == CompT.LABEL:
            rendered = FONT.render(component.text, True, (0, 0, 0))

        elif component.type == CompT.STATEMENT_INPUT:
            value = block.values[index]
            if value is None or len(value.blocks) == 0:
                value = Stack([Block(ELLIPSIS, [])])

            push_layer()
            stack_surf = render_stack(value)
            rendered = pg.Surface((stack_surf.get_width() + DEFAULT_PADDING * 2, stack_surf.get_height() + DEFAULT_PADDING))
            rendered.fill(block.definition.color)
            rendered.blit(stack_surf, (DEFAULT_PADDING * 2, 0))
            current_layer.append(rendered)
            push_layer()
            index += 1
            continue

        elif component.type == CompT.VARIABLE_INPUT:
            variable = block.values[index]
            if variable is None:
                variable = "variable..."

            text = FONT.render(variable, True, (0, 0, 0))
            surf = pg.Surface((text.get_width() + DEFAULT_PADDING * 4, text.get_height() + DEFAULT_PADDING), pg.SRCALPHA)
            surf.fill((255, 255, 255))
            surf.blit(text, (0, DEFAULT_PADDING / 2))

            triangle_start = text.get_width() + DEFAULT_PADDING * 2
            center_y = (DEFAULT_PADDING + text.get_height()) / 2
            pg.draw.polygon(surf, outline(block.definition.color), (
                (triangle_start - DEFAULT_PADDING / 2, center_y - DEFAULT_PADDING / 2),
                (triangle_start + DEFAULT_PADDING / 2, center_y - DEFAULT_PADDING / 2),
                (triangle_start, center_y + DEFAULT_PADDING / 2)
            ))

            rendered = surround_text(surf, (255, 255, 255))
            index += 1

        else:
            value = block.values[index]
            if value is None:
                value = component.default

            if isinstance(value, Block):
                rendered = render_block(value)
            elif component.type == CompT.NUMBER_INPUT:
                rendered = render_number(value)
            elif component.type == CompT.INPUT:
                rendered = render_any(value)
            elif component.type == CompT.TEXT_INPUT:
                rendered = render_text(value)
            elif component.type == CompT.BOOLEAN_INPUT:
                rendered = render_bool(value)
            else:
                rendered = pg.Surface((0, 0))

            index += 1

        current_layer.append(rendered)

    push_layer()
    max_length = max(max(layer[1][0] for layer in render_queue), DEFAULT_BLOCK_SIZE)
    max_height = sum(layer[1][1] for layer in render_queue) + DEFAULT_PADDING * len(render_queue)

    if not is_reporter:
        max_length += DEFAULT_PADDING * 4

    surf = pg.Surface((max_length, max_height), pg.SRCALPHA)
    surf.fill(block.definition.color)

    y = DEFAULT_PADDING / 2
    i = 0
    block.values_rect.clear()
    for layer in render_queue:
        width, height = layer[1]
        x = 0 if is_reporter else DEFAULT_PADDING * 2
        for rendered_comp in layer[0]:
            if block.definition.components[i].type != CompT.LABEL:
                block.values_rect.append((x + get_left_padding(block, max_height), y + (height - rendered_comp.get_height()) / 2 + get_top_padding(block.definition.block_type), rendered_comp.get_width(), rendered_comp.get_height()))
            surf.blit(rendered_comp, (x, y + (height - rendered_comp.get_height()) / 2))
            x += rendered_comp.get_width() + DEFAULT_PADDING
            i += 1

        y += height + DEFAULT_PADDING

    if is_reporter:
        match block.definition.output_type:
            case DataType.TEXT:
                surf = surround_text(surf, block.definition.color)
            case DataType.NUMBER:
                surf = surround_number(surf, block.definition.color)
            case DataType.ANY:
                surf = surround_any(surf, block.definition.color)
            case DataType.BOOLEAN:
                surf = surround_bool(surf, block.definition.color)
            case _:
                surf = surround_unknown(surf, block.definition.color)

    elif block.definition.block_type == BlockType.CAP:
        surf = make_cap(surf, block.definition.color)
    elif block.definition.block_type == BlockType.HAT:
        surf = make_hat(surf, block.definition.color)
    elif block.definition.block_type == BlockType.STATEMENT:
        surf = make_stack(surf, block.definition.color)

    block.rect = (0, 0, surf.get_width(), surf.get_height())
    return surf

#@cache
def render_stack(stack: Stack) -> pg.Surface:
    blocks = []
    prev_y = 0
    max_size = 0
    for block in stack.blocks:
        res = render_block(block)
        blocks.append((res, block, prev_y))
        max_size = max(max_size, res.get_width())
        prev_y += res.get_height()
        if block.definition.block_type in (BlockType.STATEMENT, BlockType.HAT):
            prev_y -= DEFAULT_PADDING

    if len(stack.blocks) == 0:
        add = 0
    else:
        add = DEFAULT_PADDING * int(stack.blocks[-1].definition.block_type in (BlockType.HAT, BlockType.STATEMENT))

    surf = pg.Surface((max_size, prev_y + add), pg.SRCALPHA)
    for block in blocks:
        block[1].rect = (0, 0, 0, 0)
        block[1].rect = (0, block[2], block[0].get_width(), block[0].get_height())
        surf.blit(block[0], (0, block[2]))

    return surf
