import pygame as pg
pg.init()

from workbench import Workbench
from constants import *

sc = pg.display.set_mode(flags=pg.FULLSCREEN, vsync=False)
pg.display.set_caption("PyBlocks")
# sc = pg.display.set_mode((1600, 900))
WIDTH, HEIGHT = sc.get_size()

clock = pg.Clock()
dt = clock.tick() / 1000

FONT = pg.Font("assets/arial.ttf")

workbench = Workbench((int(WIDTH * 0.75), HEIGHT), [])
CONSOLE_START = int(WIDTH * 0.75)

pg.key.set_repeat(500, 50)
pg.time.set_timer(pg.USEREVENT, 100 // 6)

console_x = 0
y = 0
char_size = MONO.render("I", True, (0, 0, 0)).get_size()
MAX_LINES = HEIGHT // char_size[1]

while True:
    #try:
        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                exit()
            if ev.type == pg.MOUSEWHEEL:
                if pg.mouse.get_pos()[0] < CONSOLE_START:
                    workbench.event(ev)
                else:
                    if pg.key.get_pressed()[pg.K_LSHIFT] or pg.key.get_pressed()[pg.K_RSHIFT]:
                        console_x -= char_size[0] * ev.y
                        console_x = max(console_x, 0)
                    else:
                        y -= ev.y
                    y = max(y, 0)
            else:
                had_exec = workbench.executor
                workbench.event(ev)
                if had_exec is None and workbench.executor is not None:
                    y = 0
                    console_x = 0

        sc.fill((0, 0, 0))
        workbench.update(dt)

        # print(len(workbench.environment.output), y, y+MAX_LINES)
        sc.blit(MONO.render("\n".join(workbench.environment.output[y:y + MAX_LINES]), True, (255, 255, 255)), (CONSOLE_START + 10 - console_x, 10))
        sc.blit(workbench.draw(), (0, 0))

        pg.display.flip()
        dt = clock.tick() / 1000

    #except Exception as e:
    #    print(e)