#!/usr/bin/env python
# coding: utf-8

import libtcodpy as libtcod
import math
from random import randrange, choice

from particle import Particle
from ship import Ship
from starfield import Starfield

sector_background = libtcod.Color(0,0,0)

thrust_exhaust_index = 10
thrust_exhaust_colormap = libtcod.color_gen_map(
    [ sector_background, libtcod.Color(255, 144, 0),  libtcod.Color(255, 222, 0) ],
    [ 0,                 thrust_exhaust_index/2,      thrust_exhaust_index] )
thrust_exhaust_character_map = [176, 176, 176, 177, 177, 178, 178, 219, 219, 219]

laser_index = 20
laser_colormap = libtcod.color_gen_map(
    [ libtcod.Color(0, 144, 255),  libtcod.Color(0, 222, 255) ],
    [ 0,                           laser_index] )
laser_character_map = [4 for i in range(0, laser_index+1)]

class Sector:
    def __init__(self, screen_width, screen_height, buffer):
        self.background = libtcod.Color(0,0,0)
        # self.background = libtcod.Color(32,32,64)

        self.buffer = buffer
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.visible_space_left   = 0
        self.visible_space_top    = 0
        self.visible_space_right  = 0
        self.visible_space_bottom = 0

        self.planets = []
        self.add_planet()

        self.particles = []

    def mirror_y_coordinate(self, y):
        return (self.screen_height- 1 - y)

    def add_planet(self):
        self.planets.append(Planet(sector=self))

    def update_visibility(self, player_sector_position_x, player_sector_position_y):
        self.visible_space_left   = player_sector_position_x - self.screen_width/2
        self.visible_space_top    = player_sector_position_y + self.screen_height/2
        self.visible_space_right  = self.visible_space_left + self.screen_width
        self.visible_space_bottom = self.visible_space_top - self.screen_height

    def add_particle(self, particle):
        self.particles.append( particle )

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


class Planet:
    def __init__(self, sector):
        self.sector = sector
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

        feature_left         = self.sector_position_x
        feature_top          = self.sector_position_y
        feature_right        = self.sector_position_x + self.width
        feature_bottom       = self.sector_position_y + self.height

        # !(r2.left > r1.right || r2.right < r1.left || r2.top > r1.bottom || r2.bottom < r1.top);
        startingx = int(self.sector_position_x - self.sector.visible_space_left)
        startingy = int(self.sector_position_y - self.sector.visible_space_bottom)
        endingx = startingx + self.width
        endingy = startingy - self.height
        # print(repr((startingx, startingy)), repr((endingx, endingy)))

        startingx = int(max([0, startingx]))
        startingy = int(min([self.sector.screen_height-1,  startingy]))
        endingx = int(min([self.sector.screen_width, endingx]))
        endingy = int(max([-1, endingy]))
        # print(repr((startingx, startingy)), repr((endingx, endingy)))

        for x in range(startingx, endingx):
            for y in range(startingy, endingy, -1):
                self.sector.buffer.set_fore( x, self.sector.mirror_y_coordinate(y), 128, 255, 128, ord('@') )

class Game:
    def __init__(self, screen_width=120, screen_height=70):
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.hud_height = 14
        self.hud_width = 26

        libtcod.sys_set_fps(30)
        libtcod.console_set_keyboard_repeat(1, 10)
        # libtcod.console_set_custom_font('fonts/8x8.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=48)
        # libtcod.console_set_custom_font('fonts/12x12.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=48)
        libtcod.console_set_custom_font('fonts/terminal8x8_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=16)
        # libtcod.console_set_custom_font('fonts/terminal12x12_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=16)

        libtcod.console_init_root(self.screen_width, self.screen_height, 'Nova', False)

        self.buffer = libtcod.ConsoleBuffer(self.screen_width, self.screen_height)
        # self.buffer = ConsoleBuffer(width, height, back_r=0, back_g=0, back_b=0, fore_r=0, fore_g=0, fore_b=0, char=' ')
        self.console = libtcod.console_new(self.screen_width, self.screen_height)

        self.mouse = libtcod.Mouse()
        self.key = libtcod.Key()

        self.sector = Sector(self.screen_width, self.screen_height, self.buffer)

        self.starfield = Starfield(self.sector, max_stars=50)

        self.player_ship = Ship(self.sector)

        self.panel_console = libtcod.console_new(self.hud_width, self.hud_height)
        libtcod.console_set_default_foreground(self.panel_console, libtcod.white)
        libtcod.console_set_default_background(self.panel_console, self.sector.background)


    def main_loop(self):
        while not libtcod.console_is_window_closed():
            libtcod.sys_check_for_event(libtcod.KEY_PRESSED|libtcod.KEY_RELEASED|libtcod.EVENT_MOUSE, self.key, self.mouse)

            if self.player_ship.velocity > 0.0:
                self.starfield.scroll( self.player_ship.velocity_angle, self.player_ship.velocity )

            self.sector.update_particle_positions()
            self.sector.scroll_particles( self.player_ship.velocity_angle, self.player_ship.velocity )

            self.render_all()
            libtcod.console_flush()

            player_action = self.handle_keys()
            if player_action == 'exit':
                break

            if self.player_ship.throttle_open:
                self.player_ship.apply_thrust()

            if self.player_ship.laser_firing:
                self.player_ship.fire_laser()

            if self.player_ship.reversing:
                self.player_ship.reverse_direction()
            elif self.player_ship.turning_left:
                self.player_ship.turn_left()
            elif self.player_ship.turning_right:
                self.player_ship.turn_right()

    def render_all(self):
        for star in self.starfield:
            color = 255
            if star[2] > 0.9:
                color = 255
            elif 0.5 < star[2] < 0.7:
                color = 170
            elif 0.2 < star[2] < 0.4:
                color = 85
            self.buffer.set_fore(int(round(star[0])), self.sector.mirror_y_coordinate(int(round(star[1]))), color, color, color, star[3])

        self.sector.update_visibility(self.player_ship.sector_position_x, self.player_ship.sector_position_y)

        for planet in self.sector.planets:
            planet.draw()

        for p in self.sector.particles:
            if p.valid:
                color = p.colormap[p.index]
                character = p.charactermap[p.index]
                x = int(round(p.x))
                y = int(round(p.y))
                if x < 2 or x > self.screen_width-2 or y < 2 or y > self.screen_height-3:
                    p.valid = False
                    continue

                if p.particle_type == "thrust_exhaust":
                    self.buffer.set_fore(x,   self.sector.mirror_y_coordinate(y),   color[0], color[1], color[2], character)
                    self.buffer.set_fore(x,   self.sector.mirror_y_coordinate(y-1), color[0], color[1], color[2], character)
                    self.buffer.set_fore(x+1, self.sector.mirror_y_coordinate(y),   color[0], color[1], color[2], character)
                    self.buffer.set_fore(x+1, self.sector.mirror_y_coordinate(y-1), color[0], color[1], color[2], character)
                else:
                    self.buffer.set_fore(x,   self.sector.mirror_y_coordinate(y),   color[0], color[1], color[2], character)

        self.player_ship.draw()
        self.buffer.blit(self.console)

        libtcod.console_blit(self.console, 0, 0, self.screen_width, self.screen_height, 0, 0, 0)

        libtcod.console_print_frame(self.panel_console, 0, 0, self.hud_width, self.hud_height, clear=True, flag=libtcod.BKGND_SET, fmt=0)
        libtcod.console_print_ex(self.panel_console, 1, 1, libtcod.BKGND_SET, libtcod.LEFT,
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
                    round(math.degrees(self.player_ship.heading),2),
                    round(self.player_ship.velocity,2),
                    round(math.degrees(self.player_ship.velocity_angle),2),
                    len(self.sector.particles),
                    round(self.player_ship.sector_position_x),
                    round(self.player_ship.sector_position_y),
                    round(self.player_ship.sector_position_x - self.screen_width/2),
                    round(self.player_ship.sector_position_y + self.screen_height/2),
                    round(self.player_ship.sector_position_x - self.screen_width/2 + self.screen_width),
                    round(self.player_ship.sector_position_y + self.screen_height/2 - self.screen_height),
            ).ljust(self.hud_width)
        )

        libtcod.console_blit(self.panel_console, 0, 0, self.hud_width, self.hud_height, 0, 0, 0, 0.75, 0.75)

        self.buffer.clear(self.sector.background[0],self.sector.background[1],self.sector.background[2])


    def handle_keys(self):
        if self.key.vk == libtcod.KEY_UP:
            self.player_ship.throttle_open = self.key.pressed
        if self.key.vk == libtcod.KEY_DOWN:
            self.player_ship.reversing = self.key.pressed
        if self.key.vk == libtcod.KEY_LEFT:
            self.player_ship.turning_left = self.key.pressed
        if self.key.vk == libtcod.KEY_RIGHT:
            self.player_ship.turning_right = self.key.pressed

        if self.key.vk == libtcod.KEY_SPACE:
            self.player_ship.laser_firing = self.key.pressed

        if self.key.vk == libtcod.KEY_ENTER and self.key.lalt:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
        elif self.key.vk == libtcod.KEY_ESCAPE:
            return 'exit'  #exit game
        # else:
        #     for i in range(2):
        #         self.sector.add_particle(
        #             Particle(
        #                 randrange(0, self.screen_width), randrange(0, self.screen_height),
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

# game = Game(180, 120)
game = Game()
game.main_loop()

