#!/usr/bin/env python
# coding: utf-8

import libtcodpy as libtcod
import math

from particle import Particle
from ship import Ship
from starfield import Starfield
from sector import Sector
from planet import Planet
import collections

class Game:
    def __init__(self, screen_width=120, screen_height=70):
        self.screen_width = screen_width
        self.screen_height = screen_height

        libtcod.console_init_root(self.screen_width, self.screen_height, 'Nova', False)

        self.buffer = libtcod.ConsoleBuffer(self.screen_width, self.screen_height)
        self.console = libtcod.console_new(self.screen_width, self.screen_height)

        self.mouse = libtcod.Mouse()
        self.key = libtcod.Key()

        self.sector = Sector(self.screen_width, self.screen_height, self.buffer)
        self.starfield = Starfield(self.sector, max_stars=50)
        self.player_ship = Ship(self.sector)

        self.set_minimap(20)

        self.targeting_height = 14
        self.targeting_width = 26
        self.targeting_console = libtcod.console_new(self.targeting_width, self.targeting_height)
        libtcod.console_set_default_foreground(self.targeting_console, libtcod.white)
        libtcod.console_set_default_background(self.targeting_console, self.sector.background)

        self.message_height = 4
        self.message_width = self.screen_width
        self.messages = collections.deque([])
        self.message_console = libtcod.console_new(self.message_width, self.message_height)
        libtcod.console_set_default_foreground(self.message_console, libtcod.white)
        libtcod.console_set_default_background(self.message_console, self.sector.background)

        self.landing_screen_width = self.screen_width / 2 - 2
        self.landing_screen_height = self.screen_height - 4
        self.landing_console = libtcod.console_new(self.landing_screen_width, self.landing_screen_height)
        libtcod.console_set_default_foreground(self.landing_console, libtcod.white)
        libtcod.console_set_default_background(self.landing_console, self.sector.background)

    def set_minimap(self, size):
        self.minimap_width  = size+3
        self.minimap_height = size+3
        self.minimap_buffer  = libtcod.ConsoleBuffer(self.minimap_width, self.minimap_height)
        self.minimap_console = libtcod.console_new(self.minimap_width, self.minimap_height)
        libtcod.console_set_default_foreground(self.minimap_console, libtcod.white)
        libtcod.console_set_default_background(self.minimap_console, self.sector.background)


    def render_all(self):
        if self.player_ship.velocity > 0.0:
            self.starfield.scroll( self.player_ship.velocity_angle, self.player_ship.velocity )

        self.sector.update_particle_positions()
        self.sector.scroll_particles( self.player_ship.velocity_angle, self.player_ship.velocity )

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

        if self.sector.selected_planet is not None:
            # Target window
            libtcod.console_print_frame(self.targeting_console, 0, 0, self.targeting_width, self.targeting_height, clear=True, flag=libtcod.BKGND_SET, fmt=0)

            self.sector.update_selected_planet_distance(self.player_ship)
            libtcod.console_print_ex(self.targeting_console, 1, 1, libtcod.BKGND_SET, libtcod.LEFT,
                "Distance: {0}".format( round(self.sector.selected_planet_distance()) ).ljust(self.targeting_width-2))

            libtcod.console_print_ex(self.targeting_console, 1, 2, libtcod.BKGND_SET, libtcod.LEFT,
                    ( " Ship Heading: {0}\n"
                      "     Velocity: {1}\n"
                      "VelocityAngle: {2}\n"
                      "    Particles: {3}\n"
                    ).format(
                        round(math.degrees(self.player_ship.heading),2),
                        round(self.player_ship.velocity,2),
                        round(math.degrees(self.player_ship.velocity_angle),2),
                        len(self.sector.particles),
                ).ljust(self.targeting_width-2)
            )
            libtcod.console_blit(self.targeting_console, 0, 0, self.targeting_width, self.targeting_height, 0, 0, 0, 1.0, 0.25)

        # Bottom Messages
        if len(self.messages) > 0:
            libtcod.console_print_ex(self.message_console, 0, 0, libtcod.BKGND_SET, libtcod.LEFT,
                    "\n".join([message.ljust(self.message_width) for message in self.messages]) )
            libtcod.console_blit(self.message_console, 0, 0, self.message_width, self.message_height, 0, 0, self.screen_height-self.message_height, 1.0, 0.25)

        # Minimap
        self.sector.draw_minimap(self.minimap_buffer, self.minimap_width, self.minimap_height, self.player_ship)
        self.minimap_buffer.blit(self.minimap_console)
        libtcod.console_print_frame(self.minimap_console, 0, 0, self.minimap_width, self.minimap_height, clear=False, flag=libtcod.BKGND_SET, fmt=0)
        libtcod.console_print_ex(self.minimap_console, 1, self.minimap_height-1, libtcod.BKGND_SET, libtcod.LEFT,
            ("[ {0} {1} ]").format(
                int(self.player_ship.sector_position_x),
                int(self.player_ship.sector_position_y),
            ).center(self.minimap_width-2, chr(196))
        )
        libtcod.console_blit(self.minimap_console, 0, 0, self.minimap_width, self.minimap_height, 0, self.screen_width-self.minimap_width, 0, 1.0, 0.25)

        # for i in range(2):
        #     self.sector.add_particle(
        #         Particle(
        #             randrange(0, self.screen_width), randrange(0, self.screen_height),
        #             "thrust_exhaust",
        #             thrust_exhaust_index,
        #             thrust_exhaust_colormap,
        #             thrust_exhaust_character_map,
        #         )
        #     )

        libtcod.console_flush()
        self.buffer.clear(self.sector.background[0], self.sector.background[1], self.sector.background[2])

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

        if self.key.pressed and self.key.vk == libtcod.KEY_ENTER and self.key.lalt:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
        elif self.key.pressed and self.key.vk == libtcod.KEY_ESCAPE:
            return 1  #exit game
        elif self.key.pressed:
            key_character = chr(self.key.c)
            if key_character == 'l':
                landed, message, planet_index = self.sector.land_at_closest_planet(self.player_ship)
                if message:
                    self.add_message(message)
                if landed:
                    self.landed_loop(planet_index)

            elif key_character == 'm':
                if self.minimap_width == 63:
                    self.set_minimap(20)
                elif self.minimap_width == 23:
                    self.set_minimap(40)
                else:
                    self.set_minimap(60)

            elif key_character == 'p':
                self.sector.cycle_planet_target(self.player_ship)

    def add_message(self, message):
        if len(self.messages) == self.message_height:
            self.messages.popleft()
        self.messages.append(message)

    def landed_loop(self, planet_index):
        done = False
        planet = self.sector.planets[planet_index]
        while not done:
            libtcod.sys_check_for_event(libtcod.KEY_PRESSED|libtcod.KEY_RELEASED|libtcod.EVENT_MOUSE, self.key, self.mouse)

            for star in self.starfield:
                color = 255
                if star[2] > 0.9:
                    color = 255
                elif 0.5 < star[2] < 0.7:
                    color = 170
                elif 0.2 < star[2] < 0.4:
                    color = 85
                self.buffer.set_fore(int(round(star[0])), self.sector.mirror_y_coordinate(int(round(star[1]))), color, color, color, star[3])
            planet.render_detail()
            self.buffer.blit(self.console)

            libtcod.console_blit(self.console, 0, 0, self.screen_width, self.screen_height, 0, 0, 0)

            libtcod.console_print_frame(self.landing_console, 0, 0, self.landing_screen_width, self.landing_screen_height, clear=True, flag=libtcod.BKGND_SET, fmt=0)
            title = "[ Landed at Planet ... ]"
            libtcod.console_print_ex(self.landing_console,
                    (self.landing_screen_width/2) - (len(title)/2),
                    0, libtcod.BKGND_SET, libtcod.LEFT, title)
            libtcod.console_print_ex(self.landing_console,
                    2, 2, libtcod.BKGND_SET, libtcod.LEFT,
                    "Class: {0}".format(planet.planet_class))
            libtcod.console_blit(self.landing_console, 0, 0, self.landing_screen_width, self.landing_screen_height, 0, self.screen_width/2, 2, 1.0, 0.25)

            libtcod.console_flush()
            self.buffer.clear(self.sector.background[0], self.sector.background[1], self.sector.background[2])

            player_action = self.handle_keys()
            if player_action == 1:
                self.add_message("Taking off from Planet X")
                done = True

    def main_loop(self):
        while not libtcod.console_is_window_closed():
            libtcod.sys_check_for_event(libtcod.KEY_PRESSED|libtcod.KEY_RELEASED|libtcod.EVENT_MOUSE, self.key, self.mouse)

            self.render_all()

            player_action = self.handle_keys()
            if player_action == 1:
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

# libtcod setup

libtcod.sys_set_fps(30)
libtcod.sys_set_renderer(libtcod.RENDERER_GLSL)
# libtcod.sys_set_renderer(libtcod.RENDERER_OPENGL)
# libtcod.sys_set_renderer(libtcod.RENDERER_SDL)
libtcod.console_set_keyboard_repeat(1, 10)
# libtcod.console_set_custom_font('fonts/8x8.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=48)
# libtcod.console_set_custom_font('fonts/12x12.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=48)
# libtcod.console_set_custom_font('fonts/terminal8x8_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=16)
libtcod.console_set_custom_font('fonts/terminal12x12_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=16)
# libtcod.console_set_custom_font('fonts/terminal16x16_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=16)

# game = Game(90, 53)
game = Game()
# game = Game(180, 120)
game.main_loop()

