#!/usr/bin/env python
# coding: utf-8

import libtcodpy as libtcod
import math
import collections
import textwrap
from random import randrange, random, shuffle
import pprint
pp = pprint.PrettyPrinter(indent=4, width=200).pprint

from particle import Particle
from ship import Ship
from starfield import Starfield
from nebula import Nebula
from sector import Sector
from planet import Planet

class Game:
    def __init__(self, screen_width=120, screen_height=70):
        self.screen_width = screen_width
        self.screen_height = screen_height

        libtcod.console_init_root(self.screen_width, self.screen_height, 'Heliopause', False)

        self.buffer = libtcod.ConsoleBuffer(self.screen_width, self.screen_height)
        self.console = libtcod.console_new(self.screen_width, self.screen_height)

        self.set_minimap(20)

        self.targeting_width = 20
        self.targeting_height = 26
        self.targeting_buffer  = libtcod.ConsoleBuffer(self.targeting_width, self.targeting_height)
        self.targeting_console = libtcod.console_new(self.targeting_width, self.targeting_height)
        libtcod.console_set_default_foreground(self.targeting_console, libtcod.white)
        libtcod.console_set_default_background(self.targeting_console, libtcod.black)

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

        self.planet_names = []
        with open("planet_names", "r") as planet_names_file:
            self.planet_names = planet_names_file.readlines()
        shuffle(self.planet_names)
        self.planet_name_index = -1

        self.loading_message("Scanning Planets")
        self.sector = Sector(self.screen_width, self.screen_height, self.buffer)
        self.add_planets()

        self.loading_message("Reading Background Radiation", clear=False)
        self.starfield = Starfield(self.sector, max_stars=50)
        self.nebula = Nebula(self.sector)
        self.player_ship = Ship(self.sector)

    def next_name(self):
        self.planet_name_index += 1
        if self.planet_name_index > len(self.planet_names):
            self.planet_name_index = 0
        return self.planet_names[self.planet_name_index].strip()

    def set_minimap(self, size):
        self.minimap_width  = size+3
        self.minimap_height = size+3
        self.minimap_buffer  = libtcod.ConsoleBuffer(self.minimap_width, self.minimap_height)
        self.minimap_console = libtcod.console_new(self.minimap_width, self.minimap_height)
        libtcod.console_set_default_foreground(self.minimap_console, libtcod.white)
        libtcod.console_set_default_background(self.minimap_console, libtcod.black)

    def loading_message(self, message, clear=True):
        if clear:
            libtcod.console_clear(self.console)
        libtcod.console_set_fade(255,libtcod.black)
        center_height = self.screen_height/2
        third_width = self.screen_width/2
        libtcod.console_print_ex(self.console, 0, center_height, libtcod.BKGND_SET, libtcod.LEFT, message.center(self.screen_width))
        libtcod.console_print_frame(self.console, int(third_width*0.5), center_height-2, third_width, 5, clear=False, flag=libtcod.BKGND_SET, fmt=0)
        libtcod.console_blit(self.console, 0, 0, self.screen_width, self.screen_height, 0, 0, 0)
        libtcod.console_flush()

    def print_planet_loading_icon(self, icon, color, offset=0, count=0):
        center_height = self.screen_height/2
        center_width = self.screen_width/2
        # quarter_width = self.screen_width/4
        # libtcod.console_set_color_control(libtcod.COLCTRL_1, color, libtcod.black)
        # libtcod.console_print(self.console, quarter_width*2+2, center_height+4, ("%c"+chr(icon)+"%c")%(libtcod.COLCTRL_1,libtcod.COLCTRL_STOP))
        libtcod.console_put_char_ex(self.console, center_width-((count+2)/2)+offset, center_height+4, icon, color, libtcod.black)
        libtcod.console_blit(self.console, 0, 0, self.screen_width, self.screen_height, 0, 0, 0)
        libtcod.console_flush()

    def add_planets(self):
        total_planets = 10
        icon, color, planet_count = self.sector.add_planet(planet_class='star',      position_x=0, position_y=0,       diameter=50, name=self.next_name())
        self.print_planet_loading_icon(icon, color, planet_count, total_planets)
        icon, color, planet_count = self.sector.add_planet(planet_class='terran',    position_x=randrange(-1000,1001), position_y=randrange(-1000,1001), diameter=randrange(12, self.screen_height), seed=randrange(1,100000), name=self.next_name())
        self.print_planet_loading_icon(icon, color, planet_count, total_planets)
        icon, color, planet_count = self.sector.add_planet(planet_class='ocean',     position_x=randrange(-1000,1001), position_y=randrange(-1000,1001), diameter=randrange(12, self.screen_height), seed=randrange(1,100000), name=self.next_name())
        self.print_planet_loading_icon(icon, color, planet_count, total_planets)
        icon, color, planet_count = self.sector.add_planet(planet_class='jungle',    position_x=randrange(-1000,1001), position_y=randrange(-1000,1001), diameter=randrange(12, self.screen_height), seed=randrange(1,100000), name=self.next_name())
        self.print_planet_loading_icon(icon, color, planet_count, total_planets)
        icon, color, planet_count = self.sector.add_planet(planet_class='lava',      position_x=randrange(-1000,1001), position_y=randrange(-1000,1001), diameter=randrange(12, self.screen_height), seed=randrange(1,100000), name=self.next_name())
        self.print_planet_loading_icon(icon, color, planet_count, total_planets)
        icon, color, planet_count = self.sector.add_planet(planet_class='tundra',    position_x=randrange(-1000,1001), position_y=randrange(-1000,1001), diameter=randrange(12, self.screen_height), seed=randrange(1,100000), name=self.next_name())
        self.print_planet_loading_icon(icon, color, planet_count, total_planets)
        icon, color, planet_count = self.sector.add_planet(planet_class='arid',      position_x=randrange(-1000,1001), position_y=randrange(-1000,1001), diameter=randrange(12, self.screen_height), seed=randrange(1,100000), name=self.next_name())
        self.print_planet_loading_icon(icon, color, planet_count, total_planets)
        icon, color, planet_count = self.sector.add_planet(planet_class='desert',    position_x=randrange(-1000,1001), position_y=randrange(-1000,1001), diameter=randrange(12, self.screen_height), seed=randrange(1,100000), name=self.next_name())
        self.print_planet_loading_icon(icon, color, planet_count, total_planets)
        icon, color, planet_count = self.sector.add_planet(planet_class='artic',     position_x=randrange(-1000,1001), position_y=randrange(-1000,1001), diameter=randrange(12, self.screen_height), seed=randrange(1,100000), name=self.next_name())
        self.print_planet_loading_icon(icon, color, planet_count, total_planets)
        icon, color, planet_count = self.sector.add_planet(planet_class='barren',    position_x=randrange(-1000,1001), position_y=randrange(-1000,1001), diameter=randrange(12, self.screen_height), seed=randrange(1,100000), name=self.next_name())
        self.print_planet_loading_icon(icon, color, planet_count, total_planets)
        icon, color, planet_count = self.sector.add_planet(planet_class='gas giant', position_x=randrange(-1000,1001), position_y=randrange(-1000,1001), diameter=randrange(12, self.screen_height), seed=randrange(1,100000), name=self.next_name())
        self.print_planet_loading_icon(icon, color, planet_count, total_planets)

    def new_sector(self):
        index, distance = self.sector.closest_planet(self.player_ship)
        # if self.sector.distance_from_center(self.player_ship) > 500:
        if distance > 500:
            fade_speed = 10
            # Fade out
            for fade in range(255,0,-1*fade_speed):
                libtcod.console_set_fade(fade,libtcod.black)
                libtcod.console_flush()

            self.loading_message("Scanning Planets")
            self.sector.clear_selected_planet()
            self.sector = Sector(self.screen_width, self.screen_height, self.buffer)
            self.add_planets()

            self.player_ship.sector = self.sector
            self.player_ship.about_face()

            self.loading_message("Reading Background Radiation")
            self.starfield = Starfield(self.sector, max_stars=50)
            self.nebula = Nebula(self.sector, r_factor=random(), g_factor=random(), b_factor=random(), seed=randrange(1,100000))
            self.add_message("nebula colors: r:{0} g:{1} b:{2}".format(
                round(self.nebula.r_factor,2),
                round(self.nebula.g_factor,2),
                round(self.nebula.b_factor,2)))

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

            # libtcod.console_print_ex(self.targeting_console, 1, 17, libtcod.BKGND_SET, libtcod.LEFT,
            #         ( "  Heading: {0}\n"
            #           " Velocity: {1}\n"
            #           " VelAngle: {2}\n"
            #           "Particles: {3}\n"
            #         ).format(
            #             round(math.degrees(self.player_ship.heading),2),
            #             round(self.player_ship.velocity,2),
            #             round(math.degrees(self.player_ship.velocity_angle),2),
            #             len(self.sector.particles),
            #     ).ljust(self.targeting_width-2)
            # )
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

            elif key_character == 'r':
                self.new_sector()

            elif key_character == 'S':
                libtcod.sys_save_screenshot()
                self.add_message("Saved screenshot")

    def add_message(self, message):
        if len(self.messages) == self.message_height:
            self.messages.popleft()
        self.messages.append(message)

    def landed_loop(self, planet_index):
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
# libtcod.console_set_custom_font('fonts/10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=48)
# libtcod.console_set_custom_font('fonts/12x12.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=48)

# libtcod.console_set_custom_font('fonts/terminal8x8_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=16)
# libtcod.console_set_custom_font('fonts/terminal12x12_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=16)
# libtcod.console_set_custom_font('fonts/terminal16x16_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=16)

# libtcod.console_set_custom_font('fonts/8x8_limited.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=16)
# libtcod.console_set_custom_font('fonts/10x10_limited.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=16)
libtcod.console_set_custom_font('fonts/12x12_limited.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=16)

game = Game(90, 56)
# game = Game()
# game = Game(180, 120)
game.main_loop()
