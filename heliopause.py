#!/usr/bin/env python
# coding: utf-8

import libtcodpy as libtcod
import math
import collections
import textwrap
from random import randrange, random, shuffle
import pprint
pp = pprint.PrettyPrinter(indent=4, width=200).pprint

from particle import Particle, ThrustExhaust
from ship import Ship
from starfield import Starfield
from nebula import Nebula
from sector import Sector
from planet import Planet
from galaxy import Galaxy

class Game:
    def __init__(self, screen_width=120, screen_height=70):
        self.screen_width = screen_width
        self.screen_height = screen_height

        libtcod.console_init_root(self.screen_width, self.screen_height, 'Heliopause', False)

        self.buffer = libtcod.ConsoleBuffer(self.screen_width, self.screen_height)
        self.console = libtcod.console_new(self.screen_width, self.screen_height)

        self.galaxy_map_console = libtcod.console_new(self.screen_width, self.screen_height)

        self.set_minimap(20)

        self.targeting_width = 20
        self.targeting_height = 26
        self.targeting_buffer  = libtcod.ConsoleBuffer(self.targeting_width, self.targeting_height)
        self.targeting_console = libtcod.console_new(self.targeting_width, self.targeting_height)
        libtcod.console_set_default_foreground(self.targeting_console, libtcod.white)
        libtcod.console_set_default_background(self.targeting_console, libtcod.black)

        self.ship_info_width = 20
        self.ship_info_height = 10
        self.ship_info_buffer  = libtcod.ConsoleBuffer(self.ship_info_width, self.ship_info_height)
        self.ship_info_console = libtcod.console_new(self.ship_info_width, self.ship_info_height)
        libtcod.console_set_default_foreground(self.ship_info_console, libtcod.white)
        libtcod.console_set_default_background(self.ship_info_console, libtcod.black)

        self.message_height = 4
        self.message_width = self.screen_width
        self.messages = collections.deque([])
        self.message_console = libtcod.console_new(self.message_width, self.message_height)
        libtcod.console_set_default_foreground(self.message_console, libtcod.white)
        libtcod.console_set_default_background(self.message_console, libtcod.black)

        self.landing_screen_width = self.screen_width / 2 - 2
        self.landing_screen_height = self.screen_height - 4
        self.landing_console = libtcod.console_new(self.landing_screen_width, self.landing_screen_height)
        libtcod.console_set_default_foreground(self.landing_console, libtcod.white)
        libtcod.console_set_default_background(self.landing_console, libtcod.black)

        # Loading Screen
        libtcod.console_set_default_background(self.console, libtcod.black)
        libtcod.console_clear(self.console)

        self.mouse = libtcod.Mouse()
        self.key = libtcod.Key()

        self.galaxy = Galaxy(self.screen_width, self.screen_height)
        self.sector, self.starfield, self.nebula = self.galaxy.sectors[self.galaxy.current_sector].load_sector(self.console, self.buffer)

        starting_planet = self.sector.planets[randrange(1, len(self.sector.planets))]
        self.player_ship = Ship(self.sector, starting_planet.sector_position_x, starting_planet.sector_position_y)
        self.add_message("Taking off from {0}".format(starting_planet.name))
        # self.add_message("Nebula Colors: r:{0} g:{1} b:{2}".format(
        #     round(self.nebula.r_factor,2),
        #     round(self.nebula.g_factor,2),
        #     round(self.nebula.b_factor,2)))


    def set_minimap(self, size):
        self.minimap_width  = size+3
        self.minimap_height = size+3
        self.minimap_buffer  = libtcod.ConsoleBuffer(self.minimap_width, self.minimap_height)
        self.minimap_console = libtcod.console_new(self.minimap_width, self.minimap_height)
        libtcod.console_set_default_foreground(self.minimap_console, libtcod.white)
        libtcod.console_set_default_background(self.minimap_console, libtcod.black)

    def new_sector(self):
        index, distance = self.sector.closest_planet(self.player_ship)
        # if self.sector.distance_from_center(self.player_ship) > 500:
        if distance > 500:
            fade_speed = 10
            # Fade out
            for fade in range(255,0,-1*fade_speed):
                libtcod.console_set_fade(fade,libtcod.black)
                libtcod.console_flush()

            self.sector.clear_selected_planet()

            self.galaxy.current_sector = self.galaxy.sectors[self.galaxy.current_sector].neighbors[self.galaxy.targeted_sector_index]
            self.galaxy.targeted_sector_index = 0
            self.sector, self.starfield, self.nebula = self.galaxy.sectors[self.galaxy.current_sector].load_sector(self.console, self.buffer)

            self.player_ship.sector = self.sector
            self.player_ship.about_face()

            self.clear_messages()
            self.add_message("Arriving in {0}".format(self.galaxy.sectors[self.galaxy.current_sector].name))
            # self.add_message("Nebula Colors: r:{0} g:{1} b:{2}".format(
            #     round(self.nebula.r_factor,2),
            #     round(self.nebula.g_factor,2),
            #     round(self.nebula.b_factor,2)))

            # Fade in
            libtcod.console_set_fade(0,libtcod.black)
            self.render_all()
            for fade in range(0,255,fade_speed):
                libtcod.console_set_fade(fade,libtcod.black)
                libtcod.console_flush()

        else:
            self.add_message("You are not far enough from the nearest planet to jump")

    def render_all(self):
        if self.player_ship.velocity > 0.0:
            self.starfield.scroll( self.player_ship.velocity_angle, self.player_ship.velocity )

        self.starfield.draw()

        self.sector.update_particle_positions()
        self.sector.scroll_particles( self.player_ship.velocity_angle, self.player_ship.velocity )

        self.sector.update_visibility(self.player_ship.sector_position_x, self.player_ship.sector_position_y)

        self.nebula.draw()

        for planet in self.sector.planets:
            planet.draw()

        for asteroid in self.sector.asteroids:
            asteroid.draw()

        for particle in self.sector.particles:
            particle.draw()

        self.player_ship.draw()

        if self.sector.selected_planet is not None:
            self.sector.update_selected_planet_distance(self.player_ship)
            if self.sector.selected_planet_distance() > (self.screen_height/1.5):
                self.player_ship.draw_target_arrow(self.sector.selected_planet_angle)
                # self.sector.draw_target_arrow(self.player_ship)

        self.buffer.blit(self.console)
        libtcod.console_blit(self.console, 0, 0, self.screen_width, self.screen_height, 0, 0, 0)

        if self.sector.selected_planet is not None:
            # Target window
            planet = self.sector.get_selected_planet()
            planet.draw_target_picture(self.targeting_buffer, 4, 2)
            self.targeting_buffer.blit(self.targeting_console)
            libtcod.console_print_frame(self.targeting_console, 0, 0, self.targeting_width, self.targeting_height, clear=False, flag=libtcod.BKGND_SET, fmt=0)

            name = textwrap.wrap(" Name: {0}".format(planet.name), width=self.targeting_width-4)
            libtcod.console_print_ex(self.targeting_console, 1, 16, libtcod.BKGND_SET, libtcod.LEFT,
                "\n  ".join(name)+"\n"
            )
            libtcod.console_print_ex(self.targeting_console, 1, 17+len(name), libtcod.BKGND_SET, libtcod.LEFT,
                (
                  " Class: {0}\n\n"
                  " Distance: {1}\n"
                  " Seed: {2}\n"
                ).format(
                    planet.planet_class.title(),
                    int(self.sector.selected_planet_distance()),
                    planet.seed,
                    # round(math.degrees(self.sector.selected_planet_angle))
                )
            )
            libtcod.console_blit(self.targeting_console, 0, 0, self.targeting_width, self.targeting_height, 0, 0, 0, 1.0, 0.25)

        # Ship Info
        libtcod.console_print_frame(self.ship_info_console, 0, 0, self.ship_info_width, self.ship_info_height, clear=True, flag=libtcod.BKGND_SET, fmt=0)
        libtcod.console_print_ex(self.ship_info_console, 1, 1, libtcod.BKGND_SET, libtcod.LEFT,
                ( "  Heading: {0}\n"
                  " Velocity: {1}\n"
                  " VelAngle: {2}\n"
                  "Particles: {3}\n"
                  "Nebula Position:\n"
                  "l:{4} r:{5}\n"
                  "t:{6} b:{7}\n"
                ).format(
                    round(math.degrees(self.player_ship.heading),2),
                    round(self.player_ship.velocity,2),
                    round(math.degrees(self.player_ship.velocity_angle),2),
                    len(self.sector.particles),
                    self.nebula.left, self.nebula.right, self.nebula.top, self.nebula.bottom
            ).ljust(self.ship_info_width-2)
        )
        libtcod.console_blit(self.ship_info_console, 0, 0, self.ship_info_width, self.ship_info_height, 0, 0, self.screen_height-self.ship_info_height-self.message_height, 1.0, 0.25)

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
            if key_character == 'l' and self.current_screen == 'flight':
                landed, message, planet_index = self.sector.land_at_closest_planet(self.player_ship)
                if message:
                    self.add_message(message)
                if landed:
                    self.landed_loop(planet_index)

            elif key_character == 'g' and self.current_screen == 'flight':
                self.galaxy_map_loop()
            elif key_character == 't' and self.current_screen == 'galaxy':
                self.galaxy.cycle_sector_target()

            elif key_character == 'm':
                if self.minimap_width == self.screen_height:
                    self.set_minimap(20)
                elif self.minimap_width == 23:
                    self.set_minimap(20 + (self.screen_height-20)/2)
                else:
                    self.set_minimap(self.screen_height-3)

            elif key_character == 'p':
                self.sector.cycle_planet_target(self.player_ship)

            elif key_character == 'r':
                self.new_sector()

            elif key_character == 'S':
                libtcod.sys_save_screenshot()
                self.add_message("Saved screenshot")

    def clear_messages(self):
        self.messages.clear()

    def add_message(self, message):
        if len(self.messages) == self.message_height:
            self.messages.popleft()
        self.messages.append(message)

    def galaxy_map_loop(self):
        self.current_screen = 'galaxy'
        done = False
        while not done:
            libtcod.sys_check_for_event(libtcod.KEY_PRESSED|libtcod.KEY_RELEASED|libtcod.EVENT_MOUSE, self.key, self.mouse)

            self.starfield.draw()
            self.nebula.draw()
            self.galaxy.draw(self.buffer)
            self.buffer.blit(self.console)
            libtcod.console_blit(self.console, 0, 0, self.screen_width, self.screen_height, 0, 0, 0)

            libtcod.console_print_frame(self.galaxy_map_console, 0, 0, self.screen_width, self.screen_height,
                    clear=False, flag=libtcod.BKGND_SET, fmt=0)
            title = "[ Galaxy Map - Seed: {0} - Current Sector: {1} - Target Sector: {2} ]".format(
                self.galaxy.seed,
                self.galaxy.sectors[self.galaxy.current_sector].name,
                self.galaxy.sectors[ self.galaxy.sectors[self.galaxy.current_sector].neighbors[self.galaxy.targeted_sector_index] ].name
            )
            libtcod.console_print_ex(self.galaxy_map_console,
                    (self.screen_width/2) - (len(title)/2),
                    0, libtcod.BKGND_SET, libtcod.LEFT, title)
            libtcod.console_blit(self.galaxy_map_console, 0, 0, self.screen_width, self.screen_height, 0, 0, 0, 1.0, 0.25)
            libtcod.console_flush()

            self.buffer.clear(self.sector.background[0], self.sector.background[1], self.sector.background[2])

            player_action = self.handle_keys()
            if player_action == 1:
                done = True

    def landed_loop(self, planet_index):
        self.current_screen = 'landed'
        done = False
        planet = self.sector.planets[planet_index]
        while not done:
            libtcod.sys_check_for_event(libtcod.KEY_PRESSED|libtcod.KEY_RELEASED|libtcod.EVENT_MOUSE, self.key, self.mouse)

            self.starfield.draw()
            self.nebula.draw()

            planet.render_detail()
            self.buffer.blit(self.console)

            libtcod.console_blit(self.console, 0, 0, self.screen_width, self.screen_height, 0, 0, 0)

            libtcod.console_print_frame(self.landing_console, 0, 0, self.landing_screen_width, self.landing_screen_height, clear=True, flag=libtcod.BKGND_SET, fmt=0)
            title = "[ Landed at {0} ]".format(planet.name)
            libtcod.console_print_ex(self.landing_console,
                    (self.landing_screen_width/2) - (len(title)/2),
                    0, libtcod.BKGND_SET, libtcod.LEFT, title)
            libtcod.console_print_ex(self.landing_console,
                    2, 2, libtcod.BKGND_SET, libtcod.LEFT,
                    "Class: {0}".format(planet.planet_class.title()))
            libtcod.console_print_ex(self.landing_console,
                    2, 3, libtcod.BKGND_SET, libtcod.LEFT,
                    "Diameter: {0}".format(planet.width))
            libtcod.console_print_ex(self.landing_console,
                    2, 4, libtcod.BKGND_SET, libtcod.LEFT,
                    "Seed: {0}".format(planet.seed))
            libtcod.console_blit(self.landing_console, 0, 0, self.landing_screen_width, self.landing_screen_height, 0, self.screen_width/2, 2, 1.0, 0.25)

            libtcod.console_flush()
            self.buffer.clear(self.sector.background[0], self.sector.background[1], self.sector.background[2])

            player_action = self.handle_keys()
            if player_action == 1:
                self.add_message("Taking off from {0}".format(planet.name))
                done = True

    def main_loop(self):
        while not libtcod.console_is_window_closed():
            self.current_screen = 'flight'
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
# libtcod.sys_set_renderer(libtcod.RENDERER_GLSL)
# libtcod.sys_set_renderer(libtcod.RENDERER_OPENGL)
# libtcod.sys_set_renderer(libtcod.RENDERER_SDL)
libtcod.console_set_keyboard_repeat(1, 10)

# libtcod.console_set_custom_font('fonts/8x8.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=48)
# libtcod.console_set_custom_font('fonts/10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=48)
# libtcod.console_set_custom_font('fonts/12x12.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=48)

# libtcod.console_set_custom_font('fonts/terminal8x8_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=16)
# libtcod.console_set_custom_font('fonts/terminal12x12_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=16)
# libtcod.console_set_custom_font('fonts/terminal16x16_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=16)

# libtcod.console_set_custom_font('fonts/8x8_limited.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=16)
libtcod.console_set_custom_font('fonts/10x10_limited.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=16)
# libtcod.console_set_custom_font('fonts/12x12_limited.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=16)

# game = Game(85, 48)
# game = Game(128, 72)
game = Game(106, 60)
# game = Game(180, 120)
game.main_loop()
