import pygame as pg
from enum import Enum
from typing import Callable
from constants import *

class Button(Enum):
    YES = "YES"
    OK = "OKAY"
    CONFIRM = "CONFIRM"
    NO = "NO"
    CANCEL = "CANCEL"

class Modal:
    def __init__(self, size: tuple[int, int], window_size: tuple[int, int], title: str, message: str, buttons: list[Button], callback: Callable[['Modal', Button], None]):
        self.title = title
        self.message = message
        self.buttons = buttons
        self.buttons.reverse()
        self.callback = callback

        self.size = size
        self.window_size = window_size

        self.dark_bg = pg.Surface(window_size, pg.SRCALPHA)
        self.dark_bg.fill((0, 0, 0, 200))

        self.modal_box = pg.Surface(size, pg.SRCALPHA)
        pg.draw.rect(self.modal_box, (255, 255, 255), ((0, 0), size), border_radius=10)

        self.title_render = BIG_FONT.render(title, True, (0, 0, 0))
        pg.draw.rect(self.modal_box, (200, 200, 255), (0, 0, size[0], 40 + self.title_render.get_height()), border_top_left_radius=10, border_top_right_radius=10)
        self.modal_box.blit(self.title_render, (20, 20))
        self.modal_box.blit(FONT.render(message, True, (0, 0, 0)), (20, 60 + self.title_render.get_height()))

        self.buttons_rect: list[tuple[number, number, number, number]] = []
        x = size[0] - 20
        for button in buttons:
            button_image = FONT.render(button.value, True, (0, 0, 0))
            surface = pg.Surface((button_image.get_width() + 40, button_image.get_height() + 40), pg.SRCALPHA)
            pg.draw.rect(surface, (200, 200, 255), ((0, 0), surface.get_size()), border_radius=5)
            pg.draw.rect(surface, (0, 0, 0), ((0, 0), surface.get_size()), LINE_WIDTH, border_radius=5)
            surface.blit(button_image, (20, 20))
            top_left = (x - surface.get_width(), size[1] - 20 - surface.get_height())
            self.buttons_rect.append((top_left[0] + (self.window_size[0] - self.size[0]) / 2, top_left[1] + (self.window_size[1] - self.size[1]) / 2, surface.get_width(), surface.get_height()))
            self.modal_box.blit(surface, top_left)
            x -= surface.get_width() + 20

        pg.draw.rect(self.modal_box, (155, 155, 155), ((0, 0), size), LINE_WIDTH, 10)

    def update(self, dt: float):
        pass

    def draw(self, sc: pg.Surface):
        sc.blit(self.dark_bg, (0, 0))
        sc.blit(self.modal_box, ((self.window_size[0] - self.size[0]) / 2, (self.window_size[1] - self.size[1]) / 2))

    def event(self, ev: pg.Event):
        if ev.type == pg.MOUSEBUTTONUP:
            for i, rect in enumerate(self.buttons_rect):
                if pg.Rect(rect).collidepoint(pg.mouse.get_pos()):
                    self.callback(self, self.buttons[i])
                    return

class Prompt(Modal):
    def __init__(self, size: tuple[int, int], window_size: tuple[int, int], title: str, message: str, buttons: list[Button], callback: Callable[['Prompt', Button], None]):
        super().__init__(size, window_size, title, message, buttons, callback)

        self.prompt_rect = (20, 100 + self.title_render.get_height(), size[0] - 40, 40)
        pg.draw.rect(self.modal_box, (222, 222, 255), self.prompt_rect, border_radius=5)
        pg.draw.rect(self.modal_box, (0, 0, 0), self.prompt_rect, LINE_WIDTH, border_radius=5)

        self.value = ""

    def event(self, ev: pg.Event):
        super().event(ev)
        if ev.type == pg.KEYDOWN:
            if ev.key == pg.K_BACKSPACE:
                self.value = self.value[:-1]
            elif ev.key == pg.K_RETURN:
                self.callback(self, Button.CONFIRM)
            else:
                self.value += ev.unicode

    def draw(self, sc: pg.Surface):
        super().draw(sc)
        sc.blit(FONT.render(self.value, True, (0, 0, 0)), ((self.window_size[0] - self.size[0]) / 2 + 25, (self.window_size[1] - self.size[1]) / 2 + self.prompt_rect[1] + 5))

