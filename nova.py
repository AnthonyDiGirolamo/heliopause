#!/usr/bin/env python
# coding: latin_1

import libtcodpy as libtcod
import math
from random import randrange, choice

SCREEN_WIDTH = 120
SCREEN_HEIGHT = 70
# SCREEN_WIDTH = 180
# SCREEN_HEIGHT = 106

HUD_HEIGHT = 1
HUD_WIDTH = SCREEN_WIDTH
LIMIT_FPS = 30
MAX_STARS = 150

# hm = libtcod.heightmap_new(10,10)
# libtcod.heightmap_mid_point_displacement(hm, 0, 5.0)
# for x in range(0, 10):
#     print(repr([libtcod.heightmap_get_value(hm, x, y) for y in range(0, 10)]))

# libtcod.console_set_custom_font('8x8.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=48)
# libtcod.console_set_custom_font('data/fonts/terminal8x8_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=16)
# libtcod.console_set_custom_font('data/fonts/terminal8x8_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=16)
libtcod.console_set_custom_font('data/fonts/terminal12x12_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=16)


libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)
libtcod.sys_set_fps(LIMIT_FPS)

panel_console = libtcod.console_new(HUD_WIDTH, HUD_HEIGHT)
panel_buffer  = libtcod.ConsoleBuffer(HUD_WIDTH, HUD_HEIGHT)
libtcod.console_set_default_foreground(panel_console, libtcod.white)

buffer = libtcod.ConsoleBuffer(SCREEN_WIDTH, SCREEN_HEIGHT)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

ship_console = libtcod.console_new(8, 8)
libtcod.console_set_key_color(ship_console, libtcod.blue)

mouse = libtcod.Mouse()
key = libtcod.Key()

class Starfield:
    def __init__(self):
        self.parallax_speeds = [0.3, 0.6, 1.0]
        # self.star_characters = [7, ord('*'), 15]
        self.star_characters = [ord('.'), 7, ord('*')]
        self.stars = [
            [float(randrange(0, SCREEN_WIDTH)), float(randrange(0, SCREEN_HEIGHT)),
                choice(self.parallax_speeds), choice(self.star_characters)]
                    for i in range(0, MAX_STARS) ]

    def __getitem__(self, index):
        return self.stars[index]

    def scroll(self, heading=0.0, velocity=0.0):
        deltax = math.cos(heading) * velocity * -1
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
        self.x = (SCREEN_WIDTH / 2) - 4
        self.y = (SCREEN_HEIGHT / 2) - 4

        self.deltav = 0.25
        self.turn_rate = math.radians(10.0)
        self.twopi = 2 * math.pi
        self.max_heading = self.twopi - self.turn_rate

        self.velocity_angle = 0.0
        self.velocity_angle_opposite = 180.0
        self.heading = 0.0
        self.velocity = 0.0

        self.ship = [libtcod.image_load('ship_{}.png'.format(str(angle).zfill(3))) for angle in range(0, 360, 10)]
        # for ship in self.ship:
        #     libtcod.image_set_key_color(ship, libtcod.black)

            # [
            # [r'    ',
            #  r'####',
            #  r'    ',
            #  r'    ',],
            # [r'    ',
            #  r'  ##',
            #  r'##  ',
            #  r'    ',],
            # [r'   #',
            #  r'  # ',
            #  r' #  ',
            #  r'#   ',],
            # [r'  # ',
            #  r'  # ',
            #  r' #  ',
            #  r' #  ',],
            # [r' #  ',
            #  r' #  ',
            #  r' #  ',
            #  r' #  ',],

            # [
            #     r'####     ',
            #     r' #####   ',
            #     r'  #####  ',
            #     r'  ###### ',
            #     r'  #####  ',
            #     r' #####   ',
            #     r'####     ',
            #     r'         ',],
            # [
            #     r'  #### # ',
            #     r'#########',
            #     r'   ##### ',
            #     r'   ##### ',
            #     r'    #### ',
            #     r'   ###   ',
            #     r'   ###   ',
            #     r'         ',],
            # [
            #     r'      #  ',
            #     r'  # #### ',
            #     r' ####### ',
            #     r'######## ',
            #     r'   ##### ',
            #     r'    ###  ',
            #     r'     #   ',],
            # [
            #     r'    ##   ',
            #     r'   ####  ',
            #     r' ######  ',
            #     r' ######  ',
            #     r'#######  ',
            #     r'##  ###  ',
            #     r'     ##  ',
            #     r'     ##  ',],
            # [
            #     r'   #     ',
            #     r'  ###    ',
            #     r' #####   ',
            #     r' #####   ',
            #     r'#######  ',
            #     r'#######  ',
            #     r'##   ##  ',
            #     r'#     #  ',],

            # r'  ^   ',
            # r' /#\  ',
            # r' ###  ',
            # r'/#V#\ ',
            # r'\/ \/ ',]
            # r'  ª   ',
            # r' ûÛú  ',
            # r' ÛÛÛ  ',
            # r'ûÛVÛú ',
            # r'üý üý ',]
            # ]

    def turn_left(self):
        self.heading += self.turn_rate
        if self.heading > self.max_heading:
            self.heading = 0.0

    def turn_right(self):
        self.heading -= self.turn_rate
        if self.heading < 0.0:
            self.heading = self.max_heading

    def apply_thrust(self):
        velocity_vectorx = math.cos(self.velocity_angle) * self.velocity
        velocity_vectory = math.sin(self.velocity_angle) * self.velocity

        deltavx = math.cos(self.heading) * self.deltav
        deltavy = math.sin(self.heading) * self.deltav

        newx = velocity_vectorx + deltavx
        newy = velocity_vectory + deltavy

        self.velocity = math.sqrt(newx**2 + newy**2)
        self.velocity_angle = math.atan(newy / newx)
        if newx > 0.0 and newy < 0.0:
            self.velocity_angle += self.twopi
        elif newx < 0.0:
            self.velocity_angle += math.pi

        if self.velocity_angle > math.pi:
            self.velocity_angle_opposite = self.velocity_angle - math.pi
        else:
            self.velocity_angle_opposite = self.velocity_angle + math.pi

    def reverse_direction(self):
        if not (self.velocity_angle_opposite - self.turn_rate) < self.heading < (self.velocity_angle_opposite + self.turn_rate):
            self.heading += self.turn_rate

    # def increase_throttle(self):
    #     self.velocity += self.deltav

    # def decrease_throttle(self):
    #     self.velocity -= self.deltav
    #     if self.velocity < 0:
    #         self.velocity = 0.0

    def draw(self):
        # heading = math.degrees(self.heading)
        # if heading >= 348.75 or heading < 11.25:
        #     ship = self.ship[0]
        # elif 11.25 <= heading < 33.75:
        #     ship = self.ship[1]
        # elif 33.75 <= heading < 56.25:
        #     ship = self.ship[2]
        # elif 56.25 <= heading < 78.75:
        #     ship = self.ship[3]
        # elif 78.75 <= heading < 101.25:
        #     ship = self.ship[4]
        # else:
        #     ship = self.ship[0]

        ship = self.ship[int(round(math.degrees(self.heading), -1)/10)]
        libtcod.image_set_key_color(ship, libtcod.blue)
        libtcod.image_blit(ship, con, self.x+4, self.y+4, libtcod.BKGND_SET, 1.0, 1.0, 0)

        # libtcod.image_blit_2x(ship, con, self.x, self.y)
        # libtcod.image_blit_2x(ship, ship_console, 0, 0)

        # for y, line in enumerate(ship):
        #     for x, char in enumerate(line):
        #         if char != " ":
        #             # if char == "\\":
        #             #     code = 252
        #             # else:
        #             code = ord(char)

        #             buffer.set_fore(self.x + x, self.y + y, 255, 255, 255, code)

        # buffer.set_fore(self.x, self.y, 255, 255, 255, ord('@'))


player_ship = Ship()
objects = []

def render_all():
    for star in starfield:
        color = 255
        if star[2] > 0.9:
            color = 255
        elif 0.5 < star[2] < 0.7:
            color = 170
        elif 0.2 < star[2] < 0.4:
            color = 85
        buffer.set_fore(int(round(star[0])), int(round(star[1])), color, color, color, star[3])

    for object in objects:
        object.draw()

    buffer.blit(con)
    player_ship.draw()
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

    # libtcod.console_blit(ship_console, 0, 0, 0, 0, 0, player_ship.x, player_ship.y, 1.0, 1.0)

    libtcod.console_print_ex(panel_console, 0, 0, libtcod.BKGND_NONE, libtcod.LEFT,
        "Ship [Heading: {}]  [Velocity: {}]  [VelocityAngle: {}".format(
            math.degrees(player_ship.heading), player_ship.velocity, math.degrees(player_ship.velocity_angle)) )

    # panel_buffer.blit( panel_console )
    libtcod.console_blit(panel_console, 0, 0, HUD_WIDTH, HUD_HEIGHT, 0, 0, 0)

    buffer.clear()
    # libtcod.console_set_default_background(ship_console, libtcod.black)
    # libtcod.console_clear(ship_console)


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
        player_ship.apply_thrust()
    elif key.vk == libtcod.KEY_DOWN:
        player_ship.reverse_direction()
    elif key.vk == libtcod.KEY_LEFT:
        player_ship.turn_left()
    elif key.vk == libtcod.KEY_RIGHT:
        player_ship.turn_right()
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
        starfield.scroll( player_ship.velocity_angle, player_ship.velocity )

    render_all()
    libtcod.console_flush()

    player_action = handle_keys()
    if player_action == 'exit':
        break

