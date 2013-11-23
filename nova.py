#!/usr/bin/env python
# coding: utf-8

import libtcodpy as libtcod
import math
from random import randrange, choice

thrust_exhaust_index = 10
thrust_exhaust_colormap = libtcod.color_gen_map(
    [ libtcod.Color( 0,0,0 ), libtcod.Color(255, 144, 0),  libtcod.Color(255, 222, 0) ],
    [ 0,                      thrust_exhaust_index/2,      thrust_exhaust_index] )
thrust_exhaust_character_map = [176, 176, 176, 177, 177, 178, 178, 219, 219, 219]

laser_index = 20
laser_colormap = libtcod.color_gen_map(
    [ libtcod.Color(0, 144, 255),  libtcod.Color(0, 222, 255) ],
    [ 0,                           laser_index] )
laser_character_map = [4 for i in range(0, laser_index+1)]

class Particle:
    def __init__(self, x, y, particle_type, index, colormap, charactermap, velocity=0.0, angle=0.0,
            velocity_component_x=0.0, velocity_component_y=0.0):
        self.x = x
        self.y = y
        self.velocity = velocity
        self.angle = angle
        self.particle_type = particle_type
        self.index = index
        self.colormap = colormap
        self.charactermap = charactermap
        self.valid = True
        self.velocity_component_x = velocity_component_x
        self.velocity_component_y = velocity_component_y

    def update_position(self):
        if self.velocity > 0.0:
            self.x += math.cos(self.angle) * self.velocity
            self.y += math.sin(self.angle) * self.velocity

        self.x += self.velocity_component_x
        self.y += self.velocity_component_y

class Starfield:
    def __init__(self):
        self.parallax_speeds = [0.3, 0.6, 1.0]
        # self.star_characters = [7, ord('*'), 15]
        self.star_characters = [ord('.'), 7]
        self.stars = [
            [float(randrange(0, SCREEN_WIDTH)), float(randrange(0, SCREEN_HEIGHT)),
                choice(self.parallax_speeds), choice(self.star_characters)]
                    for i in range(0, MAX_STARS) ]
        self.particles = []

    def __getitem__(self, index):
        return self.stars[index]

    def add_particle(self, particle):
        self.particles.append( particle )

    def scroll(self, heading=0.0, velocity=0.0):
        deltax = math.cos(heading) * velocity * -1
        deltay = math.sin(heading) * velocity * -1

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

    def update_particle_positions(self):
        for p in self.particles:
            p.update_position()

    def scroll_particles(self, heading=0.0, velocity=0.0):
        deltax = math.cos(heading) * velocity * -1
        deltay = math.sin(heading) * velocity * -1
        # remove particles which have faded
        self.particles = [p for p in self.particles if p.valid]
        for particle in self.particles:
            if particle.valid:
                particle.x += deltax * 1.0
                particle.y += deltay * 1.0
                particle.index -= 1
                if particle.index < 0:
                    particle.valid = False

class Ship:
    def __init__(self):
        self.x = (SCREEN_WIDTH / 2) - 4
        self.y = (SCREEN_HEIGHT / 2) - 4

        self.deltav = 0.15
        self.turn_rate = math.radians(5.0)
        self.twopi = 2 * math.pi
        self.max_heading = self.twopi - self.turn_rate

        self.velocity_angle = 0.0
        self.velocity_angle_opposite = 180.0
        self.heading = 0.0
        self.velocity = 0.0
        self.velocity_component_x = 0.0
        self.velocity_component_y = 0.0

        self.ship = [libtcod.image_load('images/ship_{0}.png'.format(str(angle).zfill(3))) for angle in range(0, 360, 10)]

        self.throttle_open = False
        self.turning_left  = False
        self.turning_right = False
        self.reversing     = False
        self.laser_firing  = False

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

        x_component = math.cos(self.heading)
        y_component = math.sin(self.heading)
        deltavx = x_component * self.deltav
        deltavy = y_component * self.deltav

        newx = velocity_vectorx + deltavx
        newy = velocity_vectory + deltavy
        self.velocity_component_x = newx
        self.velocity_component_y = newy

        # print(repr((newy,newx)))

        self.velocity = math.sqrt(newx**2 + newy**2)
        try:
            self.velocity_angle = math.atan(newy / newx)
        except:
            self.velocity_angle = 0.0

        if newx > 0.0 and newy < 0.0:
            self.velocity_angle += self.twopi
        elif newx < 0.0:
            self.velocity_angle += math.pi

        if self.velocity_angle > math.pi:
            self.velocity_angle_opposite = self.velocity_angle - math.pi
        else:
            self.velocity_angle_opposite = self.velocity_angle + math.pi

        if self.velocity < 0.15:
            self.velocity = 0.0
        elif self.velocity > 5.0:
            self.velocity = 5.0

        starfield.add_particle(
            Particle( self.x+3+x_component*-3, self.y+4+y_component*-3,
                "thrust_exhaust",
                thrust_exhaust_index,
                thrust_exhaust_colormap,
                thrust_exhaust_character_map,
                1.0,
                self.heading - math.pi if self.heading > math.pi else self.heading + math.pi,
                newx, newy)
        )

    def reverse_direction(self):
        if self.velocity > 0.0:
            if not (self.velocity_angle_opposite - self.turn_rate*0.9) < self.heading < (self.velocity_angle_opposite + self.turn_rate*0.9):
                if self.heading > self.velocity_angle_opposite or self.heading < self.velocity_angle:
                    self.turn_right()
                else:
                    self.turn_left()

    def draw(self):
        sprite_index = int(round(math.degrees(self.heading), -1)/10)
        if sprite_index > 35 or sprite_index < 0:
            sprite_index = 0

        ship = self.ship[sprite_index]
        libtcod.image_set_key_color(ship, libtcod.blue)
        # libtcod.image_blit(ship, con, self.x+4, self.y+4, libtcod.BKGND_SET, 1.0, 1.0, 0)
        libtcod.image_blit_rect(ship, con, self.x-4, self.y-4, -1, -1, libtcod.BKGND_SET)

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
    def fire_laser(self):
        x_component = math.cos(self.heading)
        y_component = math.sin(self.heading)
        starfield.add_particle(
            Particle(
                # self.x,
                self.x+3+x_component*6,
                self.y+4+y_component*6,
                # self.y-y_component*10,
                "laser",
                laser_index,
                laser_colormap,
                laser_character_map,
                3.0,
                self.heading,
                self.velocity_component_x,
                self.velocity_component_y
            )
        )

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
                buffer.set_fore(x+1, mirror_y_coordinate(y),   color[0], color[1], color[2], character)
                buffer.set_fore(x-1, mirror_y_coordinate(y),   color[0], color[1], color[2], character)
                buffer.set_fore(x,   mirror_y_coordinate(y+1), color[0], color[1], color[2], character)
                buffer.set_fore(x,   mirror_y_coordinate(y-1), color[0], color[1], color[2], character)
            else:
                buffer.set_fore(x,   mirror_y_coordinate(y),   color[0], color[1], color[2], character)

    for object in objects:
        object.draw()

    buffer.blit(con)
    player_ship.draw()
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

    # libtcod.console_blit(ship_console, 0, 0, 0, 0, 0, player_ship.x, player_ship.y, 0.9, 0.9)

    libtcod.console_print_ex(panel_console, 0, 0, libtcod.BKGND_NONE, libtcod.LEFT,
            "Ship [Heading: {0}]  [Velocity: {1}] [VelocityAngle: {2}]  Particles: {3}".format(
            round(math.degrees(player_ship.heading),2),
            round(player_ship.velocity,2),
            round(math.degrees(player_ship.velocity_angle),2),
            len(starfield.particles)
        ).ljust(SCREEN_WIDTH)
    )

    # panel_buffer.blit( panel_console )
    libtcod.console_blit(panel_console, 0, 0, HUD_WIDTH, HUD_HEIGHT, 0, 0, 0)

    buffer.clear()
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
    else:
        for i in range(2):
            starfield.add_particle(
                Particle(
                    randrange(0, SCREEN_WIDTH), randrange(0, SCREEN_HEIGHT),
                    "thrust_exhaust",
                    thrust_exhaust_index,
                    thrust_exhaust_colormap,
                    thrust_exhaust_character_map,
                )
            )

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

HUD_HEIGHT = 1
HUD_WIDTH = SCREEN_WIDTH
LIMIT_FPS = 30
MAX_STARS = 80

# hm = libtcod.heightmap_new(10,10)
# libtcod.heightmap_mid_point_displacement(hm, 0, 5.0)
# for x in range(0, 10):
#     print(repr([libtcod.heightmap_get_value(hm, x, y) for y in range(0, 10)]))

# libtcod.console_set_custom_font('fonts/8x8.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=48)
# libtcod.console_set_custom_font('fonts/12x12.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=48)
# libtcod.console_set_custom_font('fonts/terminal8x8_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=16)
# libtcod.console_set_custom_font('fonts/terminal8x8_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=16)
libtcod.console_set_custom_font('fonts/terminal12x12_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=16)


libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)
libtcod.sys_set_fps(LIMIT_FPS)

panel_console = libtcod.console_new(HUD_WIDTH, HUD_HEIGHT)
panel_buffer  = libtcod.ConsoleBuffer(HUD_WIDTH, HUD_HEIGHT)
libtcod.console_set_default_foreground(panel_console, libtcod.white)

buffer = libtcod.ConsoleBuffer(SCREEN_WIDTH, SCREEN_HEIGHT)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

ship_console = libtcod.console_new(8, 8)
# libtcod.console_set_key_color(ship_console, libtcod.blue)

mouse = libtcod.Mouse()
key = libtcod.Key()

libtcod.console_set_keyboard_repeat(1, 10)


starfield = Starfield()
player_ship = Ship()

objects = []

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

