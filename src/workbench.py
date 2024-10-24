from typing import Callable, Generator
import pygame as pg

from blockly import *
from blockly_render import render_stack, render_block, outline
from constants import *
import pytweening as tween

from modal import Modal, Button, Prompt
from tweenable import Tweenable
from blocks import ALL_CATEGORIES, get_all_blocks
from rect_collision import RectCollision
from enum import Enum, auto

import json
import gzip

SNAP_DISTANCE = 25

class ConnectionType(Enum):
    BEFORE = auto()
    AFTER = auto()
    VALUE = auto()

class ConnectionCandidate:
    def __init__(self, stack: Stack, stack_index: int, block_index: int, block: Block | None, connection_type: ConnectionType, value_index: int = -1):
        self.stack = stack
        self.stack_index = stack_index
        self.block_index = block_index
        self.block = block
        self.conn_type = connection_type
        self.value_index = value_index
        self.outline_rect = pg.Rect((0, 0, 0, 0))

class ContextMenuOption:
    DELETE = "delete"
    DUPLICATE = "duplicate"
    CREATE_VARIABLE = "create variable..."
    RENAME_VARIABLE = "rename variable..."
    DELETE_VARIABLE = "delete variable..."
    VARIABLE = "variable..."
    EMPTY = ""

    def __init__(self, type: str, display_text: str = None):
        self.type = type
        self.display_text = display_text

    def value(self) -> str:
        return self.display_text if self.display_text else self.type

class Workbench:
    def __init__(self, size: tuple[int, int], stacks: list[Stack]):
        self.stacks = stacks
        self.stacks_render: list[RectCollision[Stack]] = []
        self.cursor: Stack | None = None
        self.cursor_render: pg.Surface | None = None
        self.cursor_offset: tuple[int, int] = (0, 0)

        self.cam_x, self.cam_y = Tweenable(tween.easeOutSine, 0, 0.5), Tweenable(tween.easeOutSine, 0, 0.5)
        self.zoom = Tweenable(tween.easeInOutSine, 1, 0.5)
        self.width, self.height = size

        self.palette_mask = pg.Surface((self.width * 0.2, self.height), pg.SRCALPHA)
        self.palette_mask.fill((255, 255, 255, 100))
        self.current_category = 0
        self.category_scroll = Tweenable(tween.easeOutSine, 0, 0.5)
        self.category_render_height = 0
        self.category_blocks: list[RectCollision[Block]] = []

        self.category_surf = pg.Surface((self.width * 0.05, self.height), pg.SRCALPHA)
        self.category_surf.fill((255, 255, 255, 200))

        for index, category in enumerate(ALL_CATEGORIES):
            center = self.width * 0.025, self.width * 0.06 * (index + 0.5)
            pg.draw.circle(self.category_surf, category.color, center, self.width * 0.015)
            pg.draw.circle(self.category_surf, outline(category.color), center, self.width * 0.015, LINE_WIDTH)
            name = SMALL_FONT.render(category.name, True, (0, 0, 0))
            self.category_surf.blit(name, (center[0] - name.get_width() / 2, center[1] + self.width * 0.025 - name.get_height() / 2))

        self.update_palette_draw()

        self.surf = pg.Surface(size, pg.SRCALPHA)

        self.panning = False
        self.held_keys = pg.key.get_pressed()
        self.connection_candidate: ConnectionCandidate | None = None

        self.editing = False
        self.edit_block_index: tuple[Block, int] | None = None

        self.context_menu: tuple[Stack | Block, Block, int, int] | None = None
        self.context_menu_click_var_select: bool = False
        self.context_menu_attach_reporter = False
        self.context_menu_options: list[ContextMenuOption] = []
        self.context_menu_render: list[RectCollision[ContextMenuOption]] = []
        self.selected_context_menu_item = 0
        self.context_menu_rect: pg.Rect = pg.Rect()

        self.excuse_next_mouse_up = False
        self.excuse_next_mouse_down = False

        self.current_modal: Modal | None = None

        self.globals: set[str] = set()
        self.environment = Environment()
        self.executor: Generator | None = None

        self.bottom_text = FONT.render("Save (CTRL-S), Open (CTRL-O), Reset Zoom (CTRL-0), Run (CTRL-ENTER)", True, (255, 255, 255))

    def get_variables(self, stack: Stack) -> set[str]:
        return self.globals

    def set_context_menu(self, stack: Stack | Block, block: Block, stack_index: int = -1, block_index: int = -1, is_value: bool = False, clicked_variable_select: bool = False):
        self.context_menu = stack, block, stack_index, block_index
        self.context_menu_attach_reporter = is_value
        self.context_menu_options = [ContextMenuOption(ContextMenuOption.DELETE), ContextMenuOption(ContextMenuOption.DUPLICATE)]
        self.context_menu_click_var_select = clicked_variable_select
        if clicked_variable_select:
            self.context_menu_options = [ContextMenuOption(ContextMenuOption.CREATE_VARIABLE), ContextMenuOption(ContextMenuOption.RENAME_VARIABLE), ContextMenuOption(ContextMenuOption.DELETE_VARIABLE), ContextMenuOption(ContextMenuOption.EMPTY)]
            for variable in self.get_variables(stack):
                self.context_menu_options.append(ContextMenuOption(ContextMenuOption.VARIABLE, variable))

        surfaces = []
        max_width = 0
        for option in self.context_menu_options:
            surf = FONT.render(option.value(), True, (0, 0, 0))
            surfaces.append((surf, option))
            max_width = max(max_width, surf.get_width())

        y = 0
        self.context_menu_render.clear()
        for surface in surfaces:
            self.context_menu_render.append(RectCollision(surface[0], surface[1], (pg.mouse.get_pos()[0], y + pg.mouse.get_pos()[1], max_width, surface[0].get_height())))
            y += surface[0].get_height()

        self.context_menu_rect = pg.Rect(pg.mouse.get_pos(), (max_width, y))

    def update_palette_draw(self):
        self.palette_mask.fill((255, 255, 255, 100))
        self.category_blocks = []

        category = ALL_CATEGORIES[self.current_category]
        description = SMALL_FONT.render(category.description, True, category.color)
        self.palette_mask.blit(description, ((self.width * 0.2 - description.get_width()) / 2, 10))

        y = 50 - self.category_scroll.get_value()
        for block_def in category.blocks:
            block = Block(block_def, [None] * block_def.count_inputs())
            rendered = pg.transform.smoothscale_by(render_block(block), 0.75)
            self.palette_mask.blit(rendered, (10, y))
            if block_def.id == "start" and len(list(filter(lambda s: s.blocks[0].definition.id == "start", self.stacks))) != 0:
                pass
            else:
                self.category_blocks.append(RectCollision(rendered, block, (10 + self.width * 0.05, y, rendered.get_width(), rendered.get_height())))
            self.category_render_height = y
            y += rendered.get_height() + 25

    def get_editable_value(self, block: Block, stack_index: int, cursor: tuple[number, number], plus_x: int, plus_y: int) -> tuple[Block, int, int] | None:
        """
        Returns the block and index of the value to edit, and the index of the stack
        """
        index = 0
        for comp_i, rect in enumerate(block.values_rect):
            index = comp_i
            if pg.Rect(rect).collidepoint(cursor[0] - plus_x, cursor[1] - plus_y):
                if isinstance(block.values[comp_i], Block):
                    return self.get_editable_value(block.values[comp_i], stack_index, cursor, plus_x + rect[0], plus_y + rect[1] - DEFAULT_PADDING / 2)
                return block, index, stack_index

    def get_value(self, block: Block, cursor: tuple[number, number], plus_x: int, plus_y: int) -> list[int]:
        """
        Returns list of indexes
        """
        indexes = []
        for comp_i, rect in enumerate(block.values_rect):
            if pg.Rect(rect).collidepoint(cursor[0] - plus_x, cursor[1] - plus_y):
                if isinstance(block.values[comp_i], Block):
                    indexes.append(comp_i)
                    indexes.extend(self.get_value(block.values[comp_i], cursor, plus_x + rect[0], plus_y + rect[1] - DEFAULT_PADDING / 2))
                    return indexes
                else:
                    return indexes
        return indexes

    def find_reporter_input(self, stack: Stack, stack_index: int, block: Block, cursor_rect: pg.Rect, plus_x: int, plus_y: int):
        for comp_i, rect in enumerate(block.values_rect):
            a_rect = pg.Rect(rect)
            a_rect.x += plus_x
            a_rect.y += plus_y
            if cursor_rect.colliderect(a_rect):
                if isinstance(block.values[comp_i], Block):
                    self.find_reporter_input(stack, stack_index, block.values[comp_i], cursor_rect, plus_x + rect[0], plus_y + rect[1] - DEFAULT_PADDING / 2)
                    return
                elif block.definition.input_id(comp_i).fit(self.cursor.blocks[0].definition.output_type):
                    self.connection_candidate = ConnectionCandidate(stack, stack_index, 0, block, ConnectionType.VALUE, comp_i)
                    self.connection_candidate.outline_rect = a_rect
                    return
                elif isinstance(block.values[comp_i], Stack):
                    self.check_connection(block.values[comp_i], stack_index)

    def check_connection(self, stack: Stack, stack_index: int):
        if len(stack.blocks) == 0:
            world_cursor = self.view_to_world(self.get_cursor())
            cursor_connect = world_cursor[0] + DEFAULT_CONNECTION_SIZE, world_cursor[1]
            stack_connect = stack.position[0] + DEFAULT_CONNECTION_SIZE, stack.position[1]

            if distance_squared(cursor_connect, stack_connect) <= 25 * 25:
                if self.cursor.blocks[0].definition.block_type in (BlockType.STATEMENT, BlockType.CAP):
                    self.connection_candidate = ConnectionCandidate(stack, stack_index, -1, None, ConnectionType.AFTER)
                    self.connection_candidate.outline_rect = pg.Rect(stack.position, (self.cursor.blocks[0].rect[2], 0))

            return

        for bi, block in enumerate(stack.blocks):
            if self.cursor.blocks[0].definition.block_type == BlockType.REPORTER:
                cursor_rect = pg.Rect(self.view_to_world(self.get_cursor()), self.cursor_render.get_size())
                plus_x = stack.position[0]
                plus_y = stack.position[1] + block.rect[1]
                if stack.blocks[0].definition.block_type == BlockType.REPORTER:
                    plus_y -= DEFAULT_PADDING / 2
                self.find_reporter_input(stack, stack_index, block, cursor_rect, plus_x, plus_y)
                continue

            world_cursor = self.view_to_world(self.get_cursor())
            cursor_connect = world_cursor[0] + DEFAULT_CONNECTION_SIZE, world_cursor[1]
            stack_connect = stack.position[0] + DEFAULT_CONNECTION_SIZE, stack.position[1] + block.rect[1] + block.rect[3]

            if distance_squared(cursor_connect, stack_connect) <= 25 * 25:
                if self.cursor.blocks[0].definition.block_type in (BlockType.CAP, BlockType.STATEMENT) and stack.blocks[bi].definition.block_type not in (BlockType.CAP, BlockType.REPORTER):
                    if self.cursor.blocks[-1].definition.block_type == BlockType.CAP and bi != len(stack.blocks) - 1: break
                    self.connection_candidate = ConnectionCandidate(stack, stack_index, bi, block, ConnectionType.AFTER)
                    self.connection_candidate.outline_rect = pg.Rect((stack.position[0], stack.position[1] + block.rect[1] + block.rect[3] - DEFAULT_PADDING / 2), (self.cursor.blocks[0].rect[2], 0))
                    return

            cursor_connect = world_cursor[0] + DEFAULT_CONNECTION_SIZE, world_cursor[1] + self.cursor_render.get_height()
            stack_connect = stack.position[0] + DEFAULT_CONNECTION_SIZE, stack.position[1] + block.rect[1]
            if distance_squared(cursor_connect, stack_connect) <= 25 * 25:
                if (
                    self.cursor.blocks[0].definition.block_type in (BlockType.HAT, BlockType.STATEMENT)
                and stack.blocks[0].definition.block_type not in (BlockType.HAT, BlockType.REPORTER)
                and self.cursor.blocks[-1].definition.block_type not in (BlockType.CAP, BlockType.REPORTER)
                ):
                    if not (self.cursor.blocks[0].definition.block_type == BlockType.HAT and bi != 0):
                        self.connection_candidate = ConnectionCandidate(stack, stack_index, bi, block, ConnectionType.BEFORE)
                        self.connection_candidate.outline_rect = pg.Rect((stack.position[0], stack.position[1] + block.rect[1] - DEFAULT_PADDING / 2), (self.cursor.blocks[0].rect[2], 0))
                        return

            for comp_i, component in enumerate(block.definition.non_label_components):
                if component.type == CompT.STATEMENT_INPUT:
                    rect = block.values_rect[comp_i]
                    if not isinstance(block.values[comp_i], Stack):
                        block.values[comp_i] = Stack([])
                    block.values[comp_i].position = (stack.position[0] + rect[0] + DEFAULT_PADDING * 2, stack.position[1] + rect[1] + block.rect[1])
                    self.check_connection(block.values[comp_i], stack_index)

    def update(self, dt: float):
        self.held_keys = pg.key.get_pressed()

        if self.current_modal is not None:
            self.current_modal.update(dt)
            return

        self.cam_x.next(dt)
        self.cam_y.next(dt)
        self.zoom.next(dt)
        self.category_scroll.next(dt)

        if not self.category_scroll.ended():
            self.update_palette_draw()

        if not self.zoom.ended():
            for i in range(len(self.stacks)):
                self.start_render_stack(i, False)

        if self.cursor:
            self.cursor_render = render_stack(self.cursor)

        self.connection_candidate = None
        for i, stack in enumerate(self.stacks):
            if self.cursor:
                self.check_connection(stack, i)

        if self.context_menu:
            self.selected_context_menu_item = -1
            for i, coll in enumerate(self.context_menu_render):
                if coll.rect.collidepoint(*pg.mouse.get_pos()):
                    self.selected_context_menu_item = i
                    break

    @staticmethod
    def get_block_index(stack: Stack, click_pos: tuple[number, number]) -> int:
        for i, block in enumerate(stack.blocks):
            before_rect = pg.Rect(block.rect)
            rect = pg.Rect(block.rect)
            rect.x += stack.position[0]
            rect.y += stack.position[1]
            if rect.collidepoint(click_pos[0], click_pos[1]):
                return i

    def mouse_in_workspace(self) -> bool:
        return pg.mouse.get_pos()[0] > self.width * 0.25

    def right_click_stack(self, stack: RectCollision[Stack], stack_index: int):
        if stack.rect.collidepoint(*pg.mouse.get_pos()):
            m_pos = self.view_to_world(pg.mouse.get_pos())
            start_block_index = self.get_block_index(stack.obj, m_pos)
            if start_block_index is None:
                return

            block_pos = stack.obj.blocks[start_block_index].rect
            plus_x = stack.obj.position[0]
            plus_y = stack.obj.position[1] + block_pos[1]
            edit_value = self.get_editable_value(stack.obj.blocks[start_block_index], stack_index, m_pos, plus_x, plus_y)
            if edit_value is None:
                clicked_value = self.get_value(stack.obj.blocks[start_block_index], m_pos, plus_x, plus_y)
                pos = pg.mouse.get_pos()
                if not clicked_value:
                    self.set_context_menu(stack.obj, stack.obj.blocks[start_block_index], stack_index, start_block_index)

                else:
                    prev_index = clicked_value[0]
                    prev_block = stack.obj.blocks[start_block_index]
                    chosen_block: Block = prev_block.values[prev_index]
                    for index in clicked_value[1:]:
                        prev_block = chosen_block
                        prev_index = index
                        chosen_block = chosen_block.values[index]
                    self.set_context_menu(stack.obj, prev_block, stack_index, prev_index, True)

                return True

            else:
                input_type = edit_value[0].definition.input_id(edit_value[1]).type
                if input_type == CompT.STATEMENT_INPUT:
                    self.right_click_stack(self.render_stack(edit_value[0].values[edit_value[1]])[0], stack_index)
                return True

    def click_stack(self, stack: RectCollision[Stack], stack_index: int, stack_remove: Callable[[], None]) -> bool | None:
        if stack.rect.collidepoint(*pg.mouse.get_pos()):
            m_pos = self.view_to_world(pg.mouse.get_pos())
            start_block_index = self.get_block_index(stack.obj, m_pos)
            if start_block_index is None:
                return

            block_pos = stack.obj.blocks[start_block_index].rect
            plus_x = stack.obj.position[0]
            plus_y = stack.obj.position[1] + block_pos[1]
            edit_value = self.get_editable_value(stack.obj.blocks[start_block_index], stack_index, m_pos, plus_x, plus_y)
            if edit_value is None:
                clicked_value = self.get_value(stack.obj.blocks[start_block_index], m_pos, plus_x, plus_y)
                pos = pg.mouse.get_pos()
                if not clicked_value:
                    if start_block_index == 0:
                        self.cursor = stack.obj.copy()
                        origin = stack.rect.topleft
                        stack_remove()
                    else:
                        first_block = stack.obj.blocks[start_block_index].rect
                        first_block = first_block[0] + stack.rect.x, first_block[1] + stack.rect.y
                        self.cursor = Stack(stack.obj.blocks[start_block_index:])
                        stack.obj.blocks = stack.obj.blocks[:start_block_index]
                        origin = first_block

                else:  # TODO: fix this
                    prev_index = clicked_value[0]
                    prev_block = stack.obj.blocks[start_block_index]
                    chosen_block: Block = prev_block.values[prev_index]
                    x, y = stack.rect.x + prev_block.rect[0], stack.rect.y + prev_block.rect[1]
                    for index in clicked_value[1:]:
                        x += chosen_block.values_rect[index][0]
                        y += chosen_block.values_rect[index][1] - DEFAULT_PADDING / 2
                        prev_block = chosen_block
                        prev_index = index
                        chosen_block = chosen_block.values[index]

                    x += prev_block.values_rect[prev_index][0]
                    y += prev_block.values_rect[prev_index][1]
                    self.cursor = Stack([chosen_block.copy()])
                    origin = x, y
                    prev_block.values[prev_index] = None

                self.start_render_stack(stack_index)
                self.cursor_offset = (pos[0] - origin[0]) / self.zoom.get_value(), (pos[1] - origin[1]) / self.zoom.get_value()
                return True

            else:
                input_type = edit_value[0].definition.input_id(edit_value[1]).type
                if input_type == CompT.BOOLEAN_INPUT:
                    value = not edit_value[0].values[edit_value[1]]
                    edit_value[0].values[edit_value[1]] = value
                elif input_type == CompT.STATEMENT_INPUT:
                    self.click_stack(self.render_stack(edit_value[0].values[edit_value[1]])[0], stack_index, lambda: self.delete_sub_stack(edit_value))
                elif input_type == CompT.VARIABLE_INPUT:
                    self.set_context_menu(stack.obj, stack.obj.blocks[start_block_index], stack_index, edit_value, clicked_variable_select=True)
                else:
                    self.editing = True
                    self.edit_block_index = edit_value
                self.start_render_stack(stack_index)
                return True

    def start_render_stack(self, stack_index: int, complete_render: bool = True):
        if stack_index > len(self.stacks) - 1:
            return
        for i in range(len(self.stacks)):
            self.stacks_render[i] = self.render_stack(self.stacks[i], i, complete_render)[0]

    @staticmethod
    def delete_sub_stack(edit_value: tuple[Block, int, int]):
        edit_value[0].values[edit_value[1]] = None

    def remove_stack(self, stack_index: int):
        self.stacks.pop(stack_index)
        self.stacks_render.pop(stack_index)
        self.start_render_stack(-1)

    def do_context_action(self):
        action = self.context_menu_options[self.selected_context_menu_item].type
        stack_action = self.context_menu[3] == 0 and self.stacks[self.context_menu[2]] == self.context_menu[0] and not self.context_menu_attach_reporter
        if action == ContextMenuOption.DELETE:
            if stack_action:
                self.remove_stack(self.stacks.index(self.context_menu[0]))
            elif self.context_menu_attach_reporter:
                self.context_menu[1].values[self.context_menu[3]] = None
                self.start_render_stack(self.context_menu[2])
            else:
                self.context_menu[0].blocks.pop(self.context_menu[3])
                self.start_render_stack(self.context_menu[2])

        elif action == ContextMenuOption.DUPLICATE:
            if stack_action:
                self.cursor = self.context_menu[0].copy()
                origin = self.context_menu[0].position
            elif self.context_menu_attach_reporter:
                self.cursor = Stack([self.context_menu[1].values[self.context_menu[3]].copy()])
                origin = self.view_to_world(pg.mouse.get_pos()) # i give up
            else:
                self.cursor = Stack([self.context_menu[1].copy()])
                origin = self.context_menu[1].rect
                origin = (origin[0] + self.context_menu[0].position[0], origin[1] + self.context_menu[0].position[1])

            origin = self.world_to_view(origin)
            self.excuse_next_mouse_up = True
            self.excuse_next_mouse_down = True
            self.cursor_offset = (self.context_menu_rect.x - origin[0]) / self.zoom.get_value(), (self.context_menu_rect.y - origin[1]) / self.zoom.get_value()

        elif action == ContextMenuOption.VARIABLE:
            var_name = self.context_menu_options[self.selected_context_menu_item].value()
            edit_value = self.context_menu[3]
            edit_value[0].values[edit_value[1]] = var_name
            self.start_render_stack(self.context_menu[2])

        elif action == ContextMenuOption.CREATE_VARIABLE:
            this_context = self.context_menu
            self.current_modal = Prompt((self.width // 2, self.height // 2), (self.width, self.height), "Create Global Variable", "This variable will be accessible to all blocks. Enter variable name:", [Button.CANCEL, Button.CONFIRM], lambda m, b: self.create_global_variable(m, b, this_context))

        elif action == ContextMenuOption.RENAME_VARIABLE:
            prev_name = self.context_menu[3][0].values[self.context_menu[3][1]]
            this_context = self.context_menu
            self.current_modal = Prompt((self.width // 2, self.height // 2), (self.width, self.height), "Rename Variable", "Enter new variable name:", [Button.CANCEL, Button.CONFIRM], lambda m, b: self.rename_variable(m, b, prev_name, this_context))

        elif action == ContextMenuOption.DELETE_VARIABLE:
            prev_name = self.context_menu[3][0].values[self.context_menu[3][1]]
            this_context = self.context_menu
            self.current_modal = Modal((self.width // 2, self.height // 2), (self.width, self.height), "Delete Variable", "Are you sure you want to delete this variable?", [Button.NO, Button.YES], lambda m, b: self.rename_variable(m, b, prev_name, this_context, True))

    def create_global_variable(self, modal: Prompt, button: Button, context_menu: tuple):
        self.current_modal = None
        edit_value = context_menu[3]
        if button == Button.CONFIRM:
            var_name = modal.value
            if not var_name in self.globals:
                edit_value[0].values[edit_value[1]] = var_name
                self.start_render_stack(context_menu[2])
                self.globals.add(var_name)

    def create_local_variable(self, modal: Prompt, button: Button, context_menu: tuple):
        self.current_modal = None
        edit_value = context_menu[3]
        if button == Button.CONFIRM:
            var_name = modal.value
            if not var_name in context_menu[0].variables:
                edit_value[0].values[edit_value[1]] = var_name
                self.start_render_stack(context_menu[2])
                context_menu[0].variables.add(var_name)

    def rename_variable(self, modal: Modal | Prompt, button: Button, prev_name: str, context: tuple, delete: bool = False):
        self.current_modal = None
        if button == Button.YES:
            self.globals.remove(prev_name)

            if not delete:
                self.globals.add(modal.value)
                new_name = modal.value
            else:
                new_name = None

            for i, stack in enumerate(self.stacks):
                for block in stack.blocks:
                    self.rename_variable_in_block(block, prev_name, new_name)
                self.start_render_stack(i)

    def rename_variable_in_block(self, block: Block, prev_name: str, new_name: str):
        for i, value in enumerate(block.values):
            if block.definition.input_id(i).type == CompT.VARIABLE_INPUT:
                if value == prev_name:
                    block.values[i] = new_name
            elif isinstance(value, Stack):
                for block in value.blocks:
                    self.rename_variable_in_block(block, prev_name, new_name)
            elif isinstance(value, Block):
                self.rename_variable_in_block(value, prev_name, new_name)

    def event(self, ev: pg.Event):
        if self.current_modal is not None:
            self.current_modal.event(ev)
            return

        if ev.type == pg.USEREVENT:
            if self.executor:
                self.execute_step()
        elif ev.type == pg.MOUSEBUTTONDOWN:
            if self.excuse_next_mouse_down:
                self.excuse_next_mouse_down = False
                return

            if self.context_menu and self.selected_context_menu_item != -1:
                self.do_context_action()
                self.context_menu = None
                self.editing = False
                return

            self.editing = False
            self.context_menu = None
            if self.mouse_in_workspace():
                if ev.button == 2:
                    self.panning = True
                elif ev.button == 1:
                    for i, stack in enumerate(reversed(self.stacks_render)):
                        actual_i = len(self.stacks_render) - 1 - i
                        do_break = self.click_stack(stack, actual_i, lambda: self.remove_stack(actual_i))
                        if do_break: break
                    else:
                        self.start_render_stack(-1)

                elif ev.button == 3:
                    for i, stack in enumerate(reversed(self.stacks_render)):
                        actual_i = len(self.stacks_render) - 1 - i
                        do_break = self.right_click_stack(stack, actual_i)
                        if do_break: break
                    else:
                        self.start_render_stack(-1)

            else:
                if ev.button == 1:
                    if pg.mouse.get_pos()[0] < self.width * 0.05:
                        for index in range(len(ALL_CATEGORIES)):
                            center_y = self.width * 0.06 * (index + 0.5)
                            lower_bound = center_y - self.width * 0.015
                            upper_bound = center_y + self.width * 0.015
                            if lower_bound <= pg.mouse.get_pos()[1] <= upper_bound:
                                self.current_category = index
                                self.category_scroll.reset_to(0)
                                self.update_palette_draw()
                                return

                    elif pg.mouse.get_pos()[0] < self.width * 0.25:
                        for bl in self.category_blocks:
                            if bl.rect.collidepoint(*pg.mouse.get_pos()):
                                self.cursor = Stack([bl.obj.copy()])
                                pos = pg.mouse.get_pos()
                                origin = bl.rect.topleft
                                self.cursor_offset = pos[0] - origin[0], pos[1] - origin[1]
                                break

        elif ev.type == pg.MOUSEBUTTONUP:
            self.update_palette_draw()
            if self.excuse_next_mouse_up:
                self.excuse_next_mouse_up = False
                return

            if ev.button == 2:
                self.panning = False
            if self.cursor is not None and ev.button == 1:
                if pg.mouse.get_pos()[0] > self.width * 0.25:
                    if self.connection_candidate:
                        if self.connection_candidate.conn_type == ConnectionType.AFTER:
                            if self.connection_candidate.block_index == -1:
                                self.connection_candidate.stack.blocks.extend(self.cursor.blocks.copy())
                            else:
                                self.connection_candidate.stack.blocks[self.connection_candidate.block_index + 1:self.connection_candidate.block_index + 1] = self.cursor.blocks.copy()
                        elif self.connection_candidate.conn_type == ConnectionType.BEFORE:
                            self.connection_candidate.stack.blocks[self.connection_candidate.block_index:self.connection_candidate.block_index] = self.cursor.blocks.copy()
                            pos = self.connection_candidate.stack.position
                            if self.connection_candidate.stack in self.stacks:
                                self.connection_candidate.stack.position = (pos[0], pos[1] - self.cursor_render.get_height() + DEFAULT_PADDING)
                        elif self.connection_candidate.conn_type == ConnectionType.VALUE:
                            self.connection_candidate.block.values[self.connection_candidate.value_index] = self.cursor.blocks[0].copy()

                        self.start_render_stack(self.connection_candidate.stack_index)

                    else:
                        self.cursor.position = self.view_to_world(self.get_cursor())
                        self.stacks.append(self.cursor)
                        self.stacks_render.append(None)
                        self.start_render_stack(-1)

                self.cursor = None

        elif ev.type == pg.MOUSEMOTION and self.panning:
            self.cam_x.reset_to(self.cam_x.get_value() - ev.rel[0] / self.zoom.get_value())
            self.cam_y.reset_to(self.cam_y.get_value() - ev.rel[1] / self.zoom.get_value())

        elif ev.type == pg.MOUSEWHEEL:
            if not self.panning:
                if self.held_keys[pg.K_LCTRL] or self.held_keys[pg.K_RCTRL]:
                    self.zoom.new_target(self.zoom.next_val + ev.y * 0.2)
                    self.zoom.next_val = min(max(self.zoom.next_val, 0.2), 2)
                else:
                    if self.mouse_in_workspace():
                        if self.held_keys[pg.K_LSHIFT] or self.held_keys[pg.K_RSHIFT]:
                            self.cam_x.new_target(self.cam_x.get_value() - ev.y * 100 / self.zoom.get_value())
                        else:
                            self.cam_y.new_target(self.cam_y.get_value() - ev.y * 100 / self.zoom.get_value())
                    else:
                        self.category_scroll.new_target(self.category_scroll.get_value() - ev.y * 200)
                        self.category_scroll.next_val = min(max(self.category_scroll.next_val, 0), self.category_render_height - 50)

        elif ev.type == pg.KEYDOWN:
            if self.editing:
                val = self.edit_block_index[0].values[self.edit_block_index[1]]
                comp_type = self.edit_block_index[0].definition.input_id(self.edit_block_index[1]).type

                if val is None:
                    val = str(self.edit_block_index[0].definition.input_id(self.edit_block_index[1]).default)

                if ev.key == pg.K_BACKSPACE:
                    val = str(val)[:-1]
                else:
                    if comp_type == CompT.TEXT_INPUT or comp_type == CompT.INPUT:
                        val += ev.unicode
                    elif comp_type == CompT.NUMBER_INPUT:
                        if ev.unicode in "-.0123456789,":
                            val = str(val) + ev.unicode

                self.edit_block_index[0].values[self.edit_block_index[1]] = val
                self.start_render_stack(self.edit_block_index[2])
            else:
                ctrl = self.held_keys[pg.K_RCTRL] or self.held_keys[pg.K_LCTRL]
                if ctrl:
                    if ev.key == pg.K_s:
                        self.current_modal = Prompt((self.width // 2, self.height // 2), (self.width, self.height), "Save project", "Please enter the file to save to:", [Button.CANCEL, Button.CONFIRM], self.save)
                    elif ev.key == pg.K_o:
                        self.current_modal = Prompt((self.width // 2, self.height // 2), (self.width, self.height), "Open project", "This will erase everything! Please enter the file to open from:", [Button.CANCEL, Button.CONFIRM], self.open)
                    elif ev.key == pg.K_0:
                        self.zoom.new_target(1)
                    elif ev.key == pg.K_RETURN:
                        if self.executor:
                            self.executor = None
                            self.environment.output.extend(["", "Program stopped."])
                        elif len(list(filter(lambda s: s.blocks[0].definition.id == "start", self.stacks))) != 0:
                            self.environment = Environment()
                            executing_stack: Stack = next(filter(lambda s: s.blocks[0].definition.id == "start", self.stacks))
                            self.executor = executing_stack.execute(self.environment)

    def execute_step(self):
        try:
            next(self.executor)
        except StopIteration:
            self.environment.output.extend(["", "Program finished."])
            self.executor = None
        except RuntimeError:
            self.environment.output.extend(["", "Program finished."])
            self.executor = None
        except Exception as e:
            self.environment.output.extend(["", "Program encountered an error.", str(e)])
            self.executor = None

    def save(self, modal: Prompt, button: Button):
        self.current_modal = None
        if button == Button.CONFIRM:
            path = modal.value
            sjson = {"stacks": [stack.serialize() for stack in self.stacks], "globals": tuple(self.globals)}
            json_data = json.dumps(sjson)
            write = gzip.compress(json_data.encode())
            try:
                with open(path, "wb+") as file:
                    file.write(write)
                self.current_modal = Modal((self.width // 2, self.height // 2), (self.width, self.height), "Saved!", f"The project is saved to\n{path}", [Button.OK], self.close_modal)
            except Exception:
                self.current_modal = Modal((self.width // 2, self.height // 2), (self.width, self.height), "An Error Occurred!", "Please make sure the path exists and it's typed correctly!", [Button.OK], self.close_modal)

    def open(self, modal: Prompt, button: Button):
        self.current_modal = None
        if button == Button.CONFIRM:
            path = modal.value
            try:
                with open(path, "rb+") as file:
                    data = json.loads(gzip.decompress(file.read()).decode())
                    self.stacks = []
                    self.stacks_render = []

                    for i, stack in enumerate(data["stacks"]):
                        self.stacks.append(Stack.deserialize(get_all_blocks(), stack))
                        self.stacks_render.append(None)
                        self.start_render_stack(i)

                    self.globals = set(data["globals"])

            except Exception:
                self.current_modal = Modal((self.width // 3, self.height // 2), (self.width, self.height), "An Error Occurred!", "Please make sure the path exists and it's typed correctly!", [Button.OK], self.close_modal)

    def close_modal(self, modal: Modal, button: Button):
        self.current_modal = None

    def world_to_view(self, coord: tuple[number, number]) -> tuple[float, float]:
        return (coord[0] - self.cam_x.get_value()) * self.zoom.get_value() + self.width / 2, (coord[1] - self.cam_y.get_value()) * self.zoom.get_value() + self.height / 2

    def view_to_world(self, coord: tuple[number, number]) -> tuple[float, float]:
        return (coord[0] - self.width / 2) / self.zoom.get_value() + self.cam_x.get_value(), (coord[1] - self.height / 2) / self.zoom.get_value() + self.cam_y.get_value()

    def render_stack(self, stack: Stack, stack_index: int = 0, complete_render: bool = True) -> tuple[RectCollision[Stack], pg.Surface]:
        if complete_render:
            prerender = render_stack(stack)
        else:
            prerender = self.stacks_render[stack_index].orig_surf

        surf = pg.transform.scale_by(prerender, self.zoom.get_value())
        x, y = self.world_to_view(stack.position)
        return RectCollision(surf, stack, (x, y, surf.get_width(), surf.get_height()), prerender), prerender

    def get_cursor(self) -> tuple[float, float]:
        """
        :return: Top left of the cursor block in view position
        """
        return pg.mouse.get_pos()[0] - self.cursor_offset[0] * self.zoom.get_value(), pg.mouse.get_pos()[1] - self.cursor_offset[1] * self.zoom.get_value()

    def draw(self) -> pg.Surface:
        self.surf.fill((60, 60, 60))

        for i, stack in enumerate(self.stacks_render):
            self.surf.blit(stack.surf, self.world_to_view(stack.obj.position))

        self.surf.blit(self.palette_mask, (self.width * 0.05, 0))
        self.surf.blit(self.category_surf, (0, 0))

        if self.connection_candidate:
            rect = self.connection_candidate.outline_rect
            x, y = rect.x, rect.y
            w, h = rect.w, rect.h
            color = outline(self.cursor.blocks[0].definition.color)
            if h == 0:
                vx, vy = self.world_to_view((x, y))
                pg.draw.line(self.surf, color, (vx, vy), (vx + w * self.zoom.get_value(), vy), DEFAULT_PADDING)
            else:
                pg.draw.rect(self.surf, color, (self.world_to_view((x, y)), (w * self.zoom.get_value(), h * self.zoom.get_value())), LINE_WIDTH)

        if self.cursor:
            self.surf.blit(pg.transform.scale_by(self.cursor_render, self.zoom.get_value()), self.get_cursor())

        if self.context_menu:
            rect = self.context_menu_rect.copy()
            rect.x -= DEFAULT_PADDING
            rect.y -= DEFAULT_PADDING
            rect.h += DEFAULT_PADDING * 2
            rect.w += DEFAULT_PADDING * 4
            pg.draw.rect(self.surf, (255, 255, 255), rect)
            pg.draw.rect(self.surf, (0, 0, 0), rect, LINE_WIDTH)
            for i, coll in enumerate(self.context_menu_render):
                coll_rect = coll.rect.copy()
                if i == self.selected_context_menu_item:
                    coll_rect.x += DEFAULT_PADDING * 2
                self.surf.blit(coll.surf, coll_rect.topleft)

        if self.current_modal is not None:
            self.current_modal.draw(self.surf)

        self.surf.blit(self.bottom_text, (self.width * 0.25 + 10, self.height - self.bottom_text.get_height() - 10))

        return self.surf
