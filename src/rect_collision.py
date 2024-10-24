import pygame as pg

class RectCollision[T]:
    def __init__(self, surf: pg.Surface, obj: T, rect: tuple[float, float, float, float], orig_surf: pg.Surface | None = None):
        self.orig_surf = orig_surf
        self.surf = surf
        self.obj = obj
        self.rect = pg.Rect(rect)

    def __repr__(self) -> str:
        return f"RectCollision(..., {self.obj!r}, {self.rect!r})"
