import pygame as pg
from math import sqrt

__all__ = ["DEFAULT_PADDING", "DEFAULT_BLOCK_SIZE", "DEFAULT_CONNECTION_SIZE", "LINE_WIDTH", "FONT", "BIG_FONT", "SMALL_FONT", "MONO", "number", "distance_squared", "distance"]

DEFAULT_BLOCK_SIZE = 30
DEFAULT_PADDING = 8
DEFAULT_CONNECTION_SIZE = 16
LINE_WIDTH = 3
FONT = pg.Font("assets/arial.ttf", 17)
MONO = pg.Font("assets/mono.ttf", 17)
BIG_FONT = pg.Font("assets/arial.ttf", int(FONT.get_point_size() * 2))
SMALL_FONT = pg.Font("assets/arial.ttf", int(FONT.get_point_size() * 0.75))

type number = int | float

def distance_squared(a: tuple[number, number], b: tuple[number, number]) -> float:
    x , y = b[0] - a[0], b[1] - a[1]
    return x * x + y * y

def distance(a: tuple[number, number], b: tuple[number, number]) -> float:
    return sqrt(distance_squared(a, b))
