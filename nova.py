#!/usr/bin/env python
# coding: utf-8

import libtcodpy as libtcod
import math
from random import randrange, choice

from particle import Particle
from ship import Ship
from starfield import Starfield

# sector_background = libtcod.Color(32,32,64)
sector_background = libtcod.Color(0,0,0)

thrust_exhaust_index = 10
thrust_exhaust_colormap = libtcod.color_gen_map(
    [ sector_background, libtcod.Color(255, 144, 0),  libtcod.Color(255, 222, 0) ],
    [ 0,                      thrust_exhaust_index/2,      thrust_exhaust_index] )
thrust_exhaust_character_map = [176, 176, 176, 177, 177, 178, 178, 219, 219, 219]

laser_index = 20
laser_colormap = libtcod.color_gen_map(
    [ libtcod.Color(0, 144, 255),  libtcod.Color(0, 222, 255) ],
    [ 0,                           laser_index] )
laser_character_map = [4 for i in range(0, laser_index+1)]

class Planet:
    def __init__(self):
        self.sector_position_x = -10
        self.sector_position_y = 10
        self.width = 20
        self.height = 20

    def draw(self):
        # +-----+
        # |  +--+---------+
        # |  |  |         |
        # +--+--+         |
        #    |       +----+--+
        #    +-------|----+  |
        #            +-------+

        visible_space_left   = player_ship.sector_position_x - SCREEN_WIDTH/2
        visible_space_top    = player_ship.sector_position_y + SCREEN_HEIGHT/2
        visible_space_right  = visible_space_left + SCREEN_WIDTH
        visible_space_bottom = visible_space_top - SCREEN_HEIGHT
        feature_left         = self.sector_position_x
        feature_top          = self.sector_position_y
        feature_right        = self.sector_position_x + self.width
        feature_bottom       = self.sector_position_y + self.height

        # !(r2.left > r1.right || r2.right < r1.left || r2.top > r1.bottom || r2.bottom < r1.top);
        startingx = int(self.sector_position_x - visible_space_left)
        startingy = int(self.sector_position_y - visible_space_bottom)
        endingx = startingx + self.width
        endingy = startingy - self.height
        # print(repr((startingx, startingy)), repr((endingx, endingy)))

        startingx = int(max([0, startingx]))
        startingy = int(min([SCREEN_HEIGHT-1,  startingy]))
        endingx = int(min([SCREEN_WIDTH, endingx]))
        endingy = int(max([-1, endingy]))
        # print(repr((startingx, startingy)), repr((endingx, endingy)))

        for x in range(startingx, endingx):
            for y in range(startingy, endingy, -1):
                buffer.set_fore( x, mirror_y_coordinate(y), 128, 255, 128, ord('@') )

def mirror_y_coordinate(y):
    return (SCREEN_HEIGHT - 1 - y)

def render_all():
    # for x in range(0, SCREEN_HEIGHT):
    #     # for y in range(0, SCREEN_HEIGHT):
    #     buffer.set_fore(x, mirror_y_coordinate(x), 255, 255, 255, ord('$'))

    for star in starfield:
        color = 255
        if star[2] > 0.9:
            color = 255
        elif 0.5 < star[2] < 0.7:
            color = 170
        elif 0.2 < star[2] < 0.4:
            color = 85
        buffer.set_fore(int(round(star[0])), mirror_y_coordinate(int(round(star[1]))), color, color, color, star[3])

    for o in objects:
        o.draw()

    for p in starfield.particles:
        if p.valid:
            color = p.colormap[p.index]
            character = p.charactermap[p.index]
            x = int(round(p.x))
            y = int(round(p.y))
            if x < 2 or x > SCREEN_WIDTH-2 or y < 2 or y > SCREEN_HEIGHT-3:
                p.valid = False
                continue

            if p.particle_type == "thrust_exhaust":
                buffer.set_fore(x,   mirror_y_coordinate(y),   color[0], color[1], color[2], character)
                buffer.set_fore(x,   mirror_y_coordinate(y-1), color[0], color[1], color[2], character)
                buffer.set_fore(x+1, mirror_y_coordinate(y),   color[0], color[1], color[2], character)
                buffer.set_fore(x+1, mirror_y_coordinate(y-1), color[0], color[1], color[2], character)
            else:
                buffer.set_fore(x,   mirror_y_coordinate(y),   color[0], color[1], color[2], character)

    player_ship.draw()
    buffer.blit(con)
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

    # libtcod.console_blit(ship_console, 0, 0, 0, 0, 0, player_ship.x, player_ship.y, 0.9, 0.9)

    libtcod.console_print_frame(panel_console, 0, 0, HUD_WIDTH, HUD_HEIGHT, clear=True, flag=libtcod.BKGND_SET, fmt=0)
    libtcod.console_print_ex(panel_console, 1, 1, libtcod.BKGND_SET, libtcod.LEFT,
            ( " Ship Heading: {0}\n"
              "     Velocity: {1}\n"
              "VelocityAngle: {2}\n"
              "    Particles: {3}\n"
              "Sector Position:\n"
              " {4}, {5}\n"
              "Top Left:\n"
              " {6}, {7}\n"
              "Bottom Right:\n"
              " {8}, {9}\n"
            ).format(
                round(math.degrees(player_ship.heading),2),
                round(player_ship.velocity,2),
                round(math.degrees(player_ship.velocity_angle),2),
                len(starfield.particles),
                round(player_ship.sector_position_x),
                round(player_ship.sector_position_y),
                round(player_ship.sector_position_x - SCREEN_WIDTH/2),
                round(player_ship.sector_position_y + SCREEN_HEIGHT/2),
                round(player_ship.sector_position_x - SCREEN_WIDTH/2 + SCREEN_WIDTH),
                round(player_ship.sector_position_y + SCREEN_HEIGHT/2 - SCREEN_HEIGHT),
        ).ljust(HUD_WIDTH)
    )

    # panel_buffer.blit( panel_console )
    libtcod.console_blit(panel_console, 0, 0, HUD_WIDTH, HUD_HEIGHT, 0, 0, 0, 0.75, 0.75)

    buffer.clear(sector_background[0],sector_background[1],sector_background[2])

    # libtcod.console_set_default_background(ship_console, libtcod.black)
    # libtcod.console_clear(ship_console)


def handle_keys():
    global key;

    if key.vk == libtcod.KEY_UP:
        player_ship.throttle_open = key.pressed
    if key.vk == libtcod.KEY_DOWN:
        player_ship.reversing = key.pressed
    if key.vk == libtcod.KEY_LEFT:
        player_ship.turning_left = key.pressed
    if key.vk == libtcod.KEY_RIGHT:
        player_ship.turning_right = key.pressed

    if key.vk == libtcod.KEY_SPACE:
        player_ship.laser_firing = key.pressed

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    elif key.vk == libtcod.KEY_ESCAPE:
        return 'exit'  #exit game
    # else:
    #     for i in range(2):
    #         starfield.add_particle(
    #             Particle(
    #                 randrange(0, SCREEN_WIDTH), randrange(0, SCREEN_HEIGHT),
    #                 "thrust_exhaust",
    #                 thrust_exhaust_index,
    #                 thrust_exhaust_colormap,
    #                 thrust_exhaust_character_map,
    #             )
    #         )

    #         #test for other keys
    #         key_char = chr(key.c)
    #         if key_char == 'g':
    #             #pick up an item
    #             for object in objects:  #look for an item in the player's tile
    #                 if object.x == player.x and object.y == player.y and object.item:
    #                     object.item.pick_up()
    #                     break
    #         if key_char == 'i':
    #             #show the inventory; if an item is selected, use it
    #             chosen_item = inventory_menu('Press the key next to an item to use it, or any other to cancel.\n')
    #             if chosen_item is not None:
    #                 chosen_item.use()
    #         if key_char == 'd':
    #             #show the inventory; if an item is selected, drop it
    #             chosen_item = inventory_menu('Press the key next to an item to drop it, or any other to cancel.\n')
    #             if chosen_item is not None:
    #                 chosen_item.drop()
    #         return 'didnt-take-turn'

SCREEN_WIDTH = 120
SCREEN_HEIGHT = 70
# SCREEN_WIDTH = 180
# SCREEN_HEIGHT = 106

HUD_HEIGHT = 14
HUD_WIDTH = 26
LIMIT_FPS = 30
MAX_STARS = 50

# hm = libtcod.heightmap_new(10,10)
# libtcod.heightmap_mid_point_displacement(hm, 0, 5.0)
# for x in range(0, 10):
#     print(repr([libtcod.heightmap_get_value(hm, x, y) for y in range(0, 10)]))

# libtcod.console_set_custom_font('fonts/8x8.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=48)
# libtcod.console_set_custom_font('fonts/12x12.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=48)
# libtcod.console_set_custom_font('fonts/terminal8x8_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=16)
# libtcod.console_set_custom_font('fonts/terminal8x8_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=16)
libtcod.console_set_custom_font('fonts/terminal12x12_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=16)
libtcod.console_set_keyboard_repeat(1, 10)

libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)
libtcod.sys_set_fps(LIMIT_FPS)


# buffer = ConsoleBuffer(width, height, back_r=0, back_g=0, back_b=0, fore_r=0, fore_g=0, fore_b=0, char=' ')
panel_buffer  = libtcod.ConsoleBuffer(HUD_WIDTH, HUD_HEIGHT, sector_background[0], sector_background[1], sector_background[2])

panel_console = libtcod.console_new(HUD_WIDTH, HUD_HEIGHT)

libtcod.console_set_default_foreground(panel_console, libtcod.white)
libtcod.console_set_default_background(panel_console, libtcod.black)

buffer = libtcod.ConsoleBuffer(SCREEN_WIDTH, SCREEN_HEIGHT)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
libtcod.console_set_default_background(panel_console, sector_background)

# ship_console = libtcod.console_new(8, 8)
# libtcod.console_set_key_color(ship_console, libtcod.blue)

mouse = libtcod.Mouse()
key = libtcod.Key()


starfield = Starfield(SCREEN_WIDTH, SCREEN_HEIGHT, MAX_STARS)
player_ship = Ship(SCREEN_WIDTH, SCREEN_HEIGHT, buffer, con, starfield)

objects = [ Planet() ]

while not libtcod.console_is_window_closed():
    libtcod.sys_check_for_event(libtcod.KEY_PRESSED|libtcod.KEY_RELEASED|libtcod.EVENT_MOUSE,key,mouse)

    if player_ship.velocity > 0.0:
        starfield.scroll( player_ship.velocity_angle, player_ship.velocity )
    starfield.update_particle_positions()
    starfield.scroll_particles( player_ship.velocity_angle, player_ship.velocity )

    render_all()
    libtcod.console_flush()

    player_action = handle_keys()
    if player_action == 'exit':
        break

    if player_ship.throttle_open:
        player_ship.apply_thrust()

    if player_ship.laser_firing:
        player_ship.fire_laser()

    if player_ship.reversing:
        player_ship.reverse_direction()
    elif player_ship.turning_left:
        player_ship.turn_left()
    elif player_ship.turning_right:
        player_ship.turn_right()

