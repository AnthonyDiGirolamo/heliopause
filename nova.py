#!/usr/bin/env python
# coding: latin_1

import libtcodpy as libtcod
import math
from random import randrange, choice

SCREEN_WIDTH = 180
SCREEN_HEIGHT = 106

HUD_WIDTH = SCREEN_WIDTH
HUD_HEIGHT = 1
LIMIT_FPS = 30
MAX_STARS = 250

# hm = libtcod.heightmap_new(10,10)
# libtcod.heightmap_mid_point_displacement(hm, 0, 5.0)
# for x in range(0, 10):
#     print(repr([libtcod.heightmap_get_value(hm, x, y) for y in range(0, 10)]))

libtcod.console_set_custom_font('8x8.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=48)

libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)
libtcod.sys_set_fps(LIMIT_FPS)

panel_console = libtcod.console_new(HUD_WIDTH, HUD_HEIGHT)
panel_buffer  = libtcod.ConsoleBuffer(HUD_WIDTH, HUD_HEIGHT)

buffer = libtcod.ConsoleBuffer(SCREEN_WIDTH, SCREEN_HEIGHT)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

mouse = libtcod.Mouse()
key = libtcod.Key()

class Starfield:
    def __init__(self):
        self.parallax_speeds = [0.3, 0.6, 1.0]
        self.stars = [
            [float(randrange(0, SCREEN_WIDTH)), float(randrange(0, SCREEN_HEIGHT)), choice(self.parallax_speeds)]
                for i in range(0, MAX_STARS) ]

    def __getitem__(self, index):
        return self.stars[index]

    def scroll(self, heading=0.0, velocity=0.0):
        # if heading == 0:
        #     deltax = 1.0
        #     deltay = 0.0
        # elif heading == 90:
        #     deltax = 0.0
        #     deltay = 1.0
        # elif heading == 180:
        #     deltax = -1.0
        #     deltay = 0.0
        # elif heading == 270:
        #     deltax = 0.0
        #     deltay = -1.0

        deltax = math.cos(heading) * velocity
        deltay = math.sin(heading) * velocity

        for star in self.stars:
            star[0] += deltax * star[2]
            star[1] += deltay * star[2]
            if star[0] >= SCREEN_WIDTH-1:
                star[0] = 0
                star[1] = randrange(0, SCREEN_HEIGHT-1)
                star[2] = choice(self.parallax_speeds)
            elif star[0] < 0:
                star[0] = SCREEN_WIDTH-1
                star[1] = randrange(0, SCREEN_HEIGHT-1)
                star[2] = choice(self.parallax_speeds)
            elif star[1] >= SCREEN_HEIGHT-1:
                star[0] = randrange(0, SCREEN_WIDTH-1)
                star[1] = 0
                star[2] = choice(self.parallax_speeds)
            elif star[1] < 0:
                star[0] = randrange(0, SCREEN_WIDTH-1)
                star[1] = SCREEN_HEIGHT-1
                star[2] = choice(self.parallax_speeds)

starfield = Starfield()

class Ship:
    def __init__(self):
        self.x = SCREEN_WIDTH / 2
        self.y = SCREEN_HEIGHT / 2

        self.deltav = 1.0
        self.turn_rate = math.radians(1.0)
        self.twopi = 2 * math.pi

        self.heading = 0.0
        self.velocity = 0.0
        self.ship = [
            # r'  ^   ',
            # r' /#\  ',
            # r' ###  ',
            # r'/#V#\ ',
            # r'\/ \/ ',]
            r'  ª   ',
            r' ûÛú  ',
            r' ÛÛÛ  ',
            r'ûÛVÛú ',
            r'üý üý ',]

    def turn_left(self):
        self.heading += self.turn_rate
        if self.heading > self.twopi:
            self.heading = 0.0

    def turn_right(self):
        self.heading -= self.turn_rate
        if self.heading < 0.0:
            self.heading = self.twopi

    def increase_throttle(self):
        self.velocity += self.deltav

    def decrease_throttle(self):
        self.velocity -= self.deltav
        if self.velocity < 0:
            self.velocity = 0.0

    def draw(self):
        for y, line in enumerate(self.ship):
            for x, char in enumerate(line):
                if char != " ":
                    # if char == "\\":
                    #     code = 252
                    # else:
                    code = ord(char)

                    buffer.set_fore(self.x + x, self.y + y, 255, 255, 255, code)

        # buffer.set_fore(self.x, self.y, 255, 255, 255, ord('@'))


player_ship = Ship()
objects = [player_ship]

def render_all():
    for star in starfield:
        color = 255
        if star[2] > 0.9:
            color = 255
        elif 0.5 < star[2] < 0.7:
            color = 170
        elif 0.2 < star[2] < 0.4:
            color = 85
        buffer.set_fore(int(round(star[0])), int(round(star[1])), color, color, color, 15)

    for object in objects:
        object.draw()

    buffer.blit(con)
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

    libtcod.console_set_default_foreground(panel_console, libtcod.white)
    libtcod.console_print_ex(panel_console, 0, 0, libtcod.BKGND_NONE, libtcod.LEFT,
        "Ship [Heading: {}]  [Velocity: {}]  [Position: {}, {}]".format(
            round(math.degrees(player_ship.heading),2), player_ship.velocity, player_ship.x, player_ship.y) )

    # panel_buffer.blit( panel_console )
    libtcod.console_blit(panel_console, 0, 0, HUD_WIDTH, HUD_HEIGHT, 0, 0, 0)

    buffer.clear()


def handle_keys():
    global key;

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    elif key.vk == libtcod.KEY_ESCAPE:
        return 'exit'  #exit game
    # if game_state == 'playing':
    #     #movement keys
    if key.vk == libtcod.KEY_UP:
        player_ship.increase_throttle()
    elif key.vk == libtcod.KEY_DOWN:
        player_ship.decrease_throttle()
        # starfield.scroll(270)
        # player_ship.y += 1
    elif key.vk == libtcod.KEY_LEFT:
        player_ship.turn_left()
        # starfield.scroll(0)
        # player_ship.x -= 1
    elif key.vk == libtcod.KEY_RIGHT:
        player_ship.turn_right()
        # starfield.scroll(180)
        # player_ship.x += 1
    #     else:
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

while not libtcod.console_is_window_closed():
    libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse)

    if player_ship.velocity > 0.0:
        starfield.scroll( player_ship.heading, player_ship.velocity )

    render_all()
    libtcod.console_flush()

    player_action = handle_keys()
    if player_action == 'exit':
        break

