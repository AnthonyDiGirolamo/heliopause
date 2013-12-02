#!/usr/bin/env python
# coding: utf-8

import libtcodpy as libtcod
import math
import time
from random import randrange, choice

import pprint
pp = pprint.PrettyPrinter(indent=4).pprint

SCREEN_WIDTH = 8
SCREEN_HEIGHT = 8

LIMIT_FPS = 30

libtcod.console_set_custom_font('fonts/terminal12x12_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=16)

libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)
libtcod.sys_set_fps(LIMIT_FPS)

# sector_background = libtcod.Color(32,32,64)
sector_background = libtcod.Color(0,0,0)

con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
libtcod.console_set_default_background(con, sector_background)

frames = []

color_masks = [[0, 0, 255], [68,68,196], [66,66,193]]

for angle in range(0, 360, 10):
    ship = libtcod.image_load('images/ship_{0}.png'.format(str(angle).zfill(3)))

    # libtcod.image_blit(ship, con, 8, 8, libtcod.BKGND_SET, 1.0, 1.0, 0)
    libtcod.image_blit_2x(ship, con, 0, 0)
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

    frame = []
    for y in range(0, SCREEN_HEIGHT):
        row = []
        for x in range(0, SCREEN_WIDTH):
            b = libtcod.console_get_char_background(con,x,y)
            f = libtcod.console_get_char_foreground(con,x,y)
            c = libtcod.console_get_char(con,x,y)
            if c == 32:
                f = b
                c = 219
            if [b[0], b[1], b[2]] in color_masks or [f[0], f[1], f[2]] in color_masks:
                row.append( None )
            elif [b[0], b[1], b[2]] == [0,0,0] and [f[0], f[1], f[2]] == [0,0,0]:
                row.append( None )
            else:
                row.append( [b, f, c] )
        frame.append(row)
    # pp(frame)
    frames.append(frame)

    libtcod.console_flush()

    # time.sleep(0.1)

print(repr(frames))
