#!/usr/bin/env python
# coding: utf-8

import random
import time
import math
import pprint
pp = pprint.PrettyPrinter(indent=4, width=200).pprint

import libtcodpy as libtcod
from planet import Planet
from sector import Sector
from nebula import Nebula
from starfield import Starfield

class Galaxy:
    def __init__(self, width, height, seed=52, size=10):
        self.screen_width = width
        self.screen_height = height
        self.seed = seed
        random.seed(seed)

        # Load Random Names
        self.planet_names = []
        with open("planet_names", "r") as planet_names_file:
            self.planet_names = planet_names_file.readlines()
        random.shuffle(self.planet_names)
        self.planet_name_index = -1

        # Build Sectors
        self.sector_count = size
        self.sectors = []
        for i in range(0, self.sector_count):
            self.new_sector()

        self.link_sectors()
        # pp( [sector.neighbors for sector in self.sectors] )

        self.current_sector = 0
        self.targeted_sector_index = 0
        self.selected_blink = 0

    def next_name(self):
        self.planet_name_index += 1
        if self.planet_name_index > len(self.planet_names):
            self.planet_name_index = 0
        return self.planet_names[self.planet_name_index].strip()

    def new_sector(self):
        self.sectors.append( SectorMap( self, random.randrange(0,1000000) ) )

    def cycle_sector_target(self):
        self.targeted_sector_index += 1
        if self.targeted_sector_index >= len(self.sectors[self.current_sector].neighbors):
            self.targeted_sector_index = 0

    def link_sectors(self):
        for index, sector in enumerate(self.sectors):
            if index == self.sector_count-1:
                sector.neighbors.append( 0 )
            else:
                sector.neighbors.append( index+1 )

        # for index, sector in enumerate(self.sectors):
        #     while len(sector.neighbors) == 0:
        #         for i in range(random.randrange(5)):
        #             link = random.randrange(self.sector_count)
        #             if index != link and link not in sector.neighbors and index not in self.sectors[link].neighbors:
        #                 sector.neighbors.append( link )

        pp([sector.neighbors for sector in self.sectors])

    def force_directed(self):
        repulsion_constant = 100
        attraction_constant = 0.05
        spring_length = 4

        displacements = [[0, 0] for sector in self.sectors]

        for index1, sector1 in enumerate(self.sectors):
            for index2, sector2 in enumerate(self.sectors):
                if index1 == index2:
                    continue

                proximity = max( math.sqrt((sector2.galaxy_position_x - sector1.galaxy_position_x)**2 + (sector2.galaxy_position_y - sector1.galaxy_position_y)**2), 1.0)
                repulsion_force = -(repulsion_constant / proximity**2)

                x_displacement = sector2.galaxy_position_x - sector1.galaxy_position_x
                y_displacement = sector2.galaxy_position_y - sector1.galaxy_position_y
                try:
                    angle = math.atan(y_displacement / x_displacement)
                except:
                    angle = 0.0
                if x_displacement > 0.0 and y_displacement < 0.0:
                    angle += math.pi * 2
                elif x_displacement < 0.0:
                    angle += math.pi

                displacements[index1][0] += math.cos(angle) * repulsion_force
                displacements[index1][1] += math.sin(angle) * repulsion_force

        for index1, sector1 in enumerate(self.sectors):
            for neighbor_index in sector1.neighbors:
                sector2 = self.sectors[neighbor_index]

                proximity = max( math.sqrt((sector2.galaxy_position_x - sector1.galaxy_position_x)**2 + (sector2.galaxy_position_y - sector1.galaxy_position_y)**2), 1.0)
                attraction_force = attraction_constant * max(proximity - spring_length, 0)

                x_displacement = sector2.galaxy_position_x - sector1.galaxy_position_x
                y_displacement = sector2.galaxy_position_y - sector1.galaxy_position_y
                try:
                    angle = math.atan(y_displacement / x_displacement)
                except:
                    angle = 0.0
                if x_displacement > 0.0 and y_displacement < 0.0:
                    angle += math.pi * 2
                elif x_displacement < 0.0:
                    angle += math.pi

                displacements[index1][0] += math.cos(angle) * attraction_force
                displacements[index1][1] += math.sin(angle) * attraction_force

        for index, sector in enumerate(self.sectors):
            sector.galaxy_position_x += int(round(displacements[index][0]))
            sector.galaxy_position_y += int(round(displacements[index][1]))

        # Recenter Sector Map
        min_x = min( [sector.galaxy_position_x for sector in self.sectors] )
        min_y = min( [sector.galaxy_position_y for sector in self.sectors] )
        max_x = max( [sector.galaxy_position_x for sector in self.sectors] )
        max_y = max( [sector.galaxy_position_y for sector in self.sectors] )

        width = max_x - min_x
        height = max_y - min_y
        disp_x = ((self.screen_width/2) - (width/2)) - min_x
        disp_y = ((self.screen_height/2) - (height/2)) - min_y

        for index, sector in enumerate(self.sectors):
            sector.galaxy_position_x += disp_x
            sector.galaxy_position_y += disp_y
            if sector.galaxy_position_x < 2:
                sector.galaxy_position_x = 2
            if sector.galaxy_position_y < 2:
                sector.galaxy_position_y = 2
            if sector.galaxy_position_x > self.screen_width - 3:
                sector.galaxy_position_x = self.screen_width - 3
            if sector.galaxy_position_y > self.screen_height - 3:
                sector.galaxy_position_y = self.screen_height - 3

    def draw(self, buffer):
        for index, sector in enumerate(self.sectors):
            # color = [int(sector.nebula_background[0] * 255), int(sector.nebula_background[1] * 255), int(sector.nebula_background[2] * 255)]
            color = libtcod.Color(255, 255, 255)
            buffer.set(sector.galaxy_position_x, sector.galaxy_position_y, 0, 0, 0, color[0], color[1], color[2], ord('*'))

            for neighbor in sector.neighbors:
                if index == self.current_sector and neighbor == sector.neighbors[self.targeted_sector_index]:
                    color = libtcod.Color(64, 200, 64)
                else:
                    color = libtcod.Color(64, 64, 64)

                libtcod.line_init(
                    sector.galaxy_position_x,
                    sector.galaxy_position_y,
                    self.sectors[neighbor].galaxy_position_x,
                    self.sectors[neighbor].galaxy_position_y,
                )
                x,y=libtcod.line_step()
                while x is not None:
                    buffer.set_back(x, y, color[0], color[1], color[2])
                    x,y=libtcod.line_step()

            if self.current_sector is not None and index == self.current_sector:
                t = time.clock()
                if t > self.selected_blink + 0.5:
                    if t > self.selected_blink + 1.0:
                        self.selected_blink = t
                    buffer.set_fore(sector.galaxy_position_x+1, sector.galaxy_position_y, 255, 255, 255, ord('>'))
                    buffer.set_fore(sector.galaxy_position_x-1, sector.galaxy_position_y, 255, 255, 255, ord('<'))

class SectorMap:
    def __init__(self, galaxy, seed):
        self.galaxy = galaxy
        self.screen_width = self.galaxy.screen_width
        self.screen_height = self.galaxy.screen_height

        self.galaxy_position_x = int(random.random() * (self.screen_width/2)) + self.screen_width/4
        self.galaxy_position_y = int(random.random() * (self.screen_height/2)) + self.screen_height/4

        self.seed = seed
        random.seed(seed)

        # self.sector_background = libtcod.Color( random.randrange(0,256), random.randrange(0,256), random.randrange(0,256) )
        self.nebula_background = [ random.random(), random.random(), random.random() ]
        self.nebula_seed       = seed * 3
        self.planet_count      = random.randrange(1, 17)

        self.planets   = []
        self.neighbors = []

        self.new_star()
        for p in range(0, self.planet_count):
            self.new_planet()

        # pp(self)

    def new_star(self):
        self.planets.append( {
            "planet_class" : "star",
            "position_x"   : 0,
            "position_y"   : 0,
            "diameter"     : 50,
            "seed"         : random.randrange(1,1000000),
            "name"         : self.galaxy.next_name(),
        } )

    def new_planet(self):
        self.planets.append( {
            "planet_class" : Planet.classes[ random.randrange(0, len(Planet.classes)) ],
            "position_x"   : random.randrange(-1000,1001),
            "position_y"   : random.randrange(-1000,1001),
            "diameter"     : random.randrange(12, self.galaxy.screen_height),
            "seed"         : random.randrange(1,1000000),
            "name"         : self.galaxy.next_name(),
        } )

    def __repr__(self):
        return repr({ "posx": self.galaxy_position_x, "posy": self.galaxy_position_y, "seed": self.seed, "planet_count": self.planet_count, "nebula_background": self.nebula_background, "planets": self.planets })

    def print_planet_loading_icon(self, console, icon, color, offset=0, count=0):
        center_height = self.screen_height/2
        center_width = self.screen_width/2
        libtcod.console_put_char_ex(console, center_width-((count+2)/2)+offset, center_height+4, icon, color, libtcod.black)
        libtcod.console_blit(console, 0, 0, self.screen_width, self.screen_height, 0, 0, 0)
        libtcod.console_flush()

    def loading_message(self, message, console, clear=True):
        if clear:
            libtcod.console_clear(console)
        libtcod.console_set_fade(255,libtcod.black)
        center_height = self.screen_height/2
        third_width = self.screen_width/2
        libtcod.console_print_ex(console, 0, center_height, libtcod.BKGND_SET, libtcod.LEFT, message.center(self.screen_width))
        libtcod.console_print_frame(console, int(third_width*0.5), center_height-2, third_width, 5, clear=False, flag=libtcod.BKGND_SET, fmt=0)
        libtcod.console_blit(console, 0, 0, self.screen_width, self.screen_height, 0, 0, 0)
        libtcod.console_flush()

    def load_sector(self, console, buffer):
        self.loading_message("Scanning Planets", console)
        sector = Sector(self.screen_width, self.screen_height, buffer)

        for index, planet in enumerate(self.planets):
            # pp(planet)
            icon, color, planet_count = sector.add_planet(
                planet_class=planet['planet_class'],
                position_x=planet['position_x'],
                position_y=planet['position_y'],
                diameter=planet['diameter'],
                seed=planet['seed'],
                name=planet['name'],
            )
            self.print_planet_loading_icon(console, icon, color, offset=index, count=len(self.planets))

        self.loading_message("Reading Background Radiation", console)
        starfield = Starfield(sector, max_stars=50)
        nebula = Nebula(sector, r_factor=self.nebula_background[0], g_factor=self.nebula_background[1], b_factor=self.nebula_background[2], seed=self.nebula_seed)

        return sector, starfield, nebula
