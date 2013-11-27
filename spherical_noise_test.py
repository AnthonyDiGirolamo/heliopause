#!/usr/bin/env python
# coding: utf-8

import libtcodpy as libtcod
import math
import time

import pprint
pp = pprint.PrettyPrinter(indent=4).pprint

SCREEN_WIDTH = 120
SCREEN_HEIGHT = 70

LIMIT_FPS = 30

libtcod.console_set_custom_font('fonts/terminal12x12_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=16)

libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)
libtcod.sys_set_fps(LIMIT_FPS)

con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
libtcod.console_set_default_background(con, libtcod.Color(0,0,0))

noise_func = 0
noise_dx = 0.0
noise_dy = 0.0
noise_dz = 0.0
noise_octaves = 4.0
noise_zoom = 3.0
noise_hurst = libtcod.NOISE_DEFAULT_HURST
noise_lacunarity = libtcod.NOISE_DEFAULT_LACUNARITY

# noise = libtcod.noise_new(2)
noise = libtcod.noise_new(3)

noise_img=libtcod.image_new(SCREEN_WIDTH, SCREEN_HEIGHT)

noise_dx += 0.01
noise_dy += 0.01
noise_dz += 0.01

pi_times_two = 2 * math.pi
pi_div_two = math.pi / 2.0

theta = 0.0
phi = pi_div_two * -1.0
x = 0
y = 0

while phi <= pi_div_two:
    while theta <= pi_times_two:
        f = [
            noise_zoom * math.cos(phi) * math.cos(theta),
            noise_zoom * math.cos(phi) * math.sin(theta),
            noise_zoom * math.sin(phi),
        ]
        value = 0.0
        value = libtcod.noise_get_fbm(noise, f, noise_octaves, libtcod.NOISE_PERLIN)
        c = int((value + 1.0) / 2.0 * 255)
        if c < 0:
            c = 0
        elif c > 255:
            c = 255
        col = libtcod.Color(c // 2, c // 2, c)
        libtcod.image_put_pixel(noise_img,x,y,col)
        theta += (pi_times_two / SCREEN_WIDTH)
        x += 1
    phi += (math.pi / SCREEN_HEIGHT)
    y += 1
    x = 0
    theta = 0.0

# for y in range(SCREEN_HEIGHT):
#     for x in range(SCREEN_WIDTH):
#         f = [noise_zoom * x / (SCREEN_WIDTH) + noise_dx,
#              noise_zoom * y / (SCREEN_HEIGHT) + noise_dy]
#         pp(f)
#         value = 0.0
#         value = libtcod.noise_get_fbm(noise, f, noise_octaves, libtcod.NOISE_PERLIN)
#         c = int((value + 1.0) / 2.0 * 255)
#         if c < 0:
#             c = 0
#         elif c > 255:
#             c = 255
#         col = libtcod.Color(c // 2, c // 2, c)
#         libtcod.image_put_pixel(noise_img,x,y,col)

libtcod.image_blit_2x(noise_img,con,0,0)
libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
libtcod.console_flush()
time.sleep(5)

