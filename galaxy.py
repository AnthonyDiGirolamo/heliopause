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
from asteroid import Asteroid

class Galaxy:
    def __init__(self, width, height, seed=5234):
        self.screen_width = width
        self.screen_height = height
        self.seed = seed
        random.seed(seed)
        self.rnd = libtcod.random_new_from_seed(self.seed)

        # Load Random Names
        self.planet_names = []
        with open("planet_names", "r") as planet_names_file:
            self.planet_names = planet_names_file.readlines()
        random.shuffle(self.planet_names)
        self.planet_name_index = -1

        # Build Galaxy Map
        self.bsp_depth = 7
        self.bsp = libtcod.bsp_new_with_size(0, 0, self.screen_width, self.screen_height)
        libtcod.bsp_split_recursive(self.bsp, self.rnd, self.bsp_depth, 8, 8, 1.0, 1.0)

        # Count number of sectors
        count = [ 0 ]
        def count_bsp_leaf_nodes(node, userData):
            if node.level == self.bsp_depth:
                count[0] += 1
            return True
        libtcod.bsp_traverse_inverted_level_order(self.bsp, count_bsp_leaf_nodes, userData=None)
        self.sector_count = count[0]
        # self.sector_count = 2**self.bsp_depth # only if we have a fully populated tree (not guaranteed)

        self.sectors = []
        for i in range(0, self.sector_count):
            self.new_sector()

        self.link_sectors()

        self.current_sector = random.randrange(self.sector_count)
        # pp("total sectors: {}  current sector: {}".format(self.sector_count, self.current_sector))
        self.targeted_sector_index = 0
        self.selected_blink = 0

    def next_name(self):
        self.planet_name_index += 1
        if self.planet_name_index > len(self.planet_names):
            self.planet_name_index = 0
        return self.planet_names[self.planet_name_index].strip()

    def new_sector(self):
        self.sectors.append( SectorMap( self, random.randrange(0,1000000), self.next_name() ) )

    def cycle_sector_target(self):
        self.targeted_sector_index += 1
        if self.targeted_sector_index >= len(self.sectors[self.current_sector].neighbors):
            self.targeted_sector_index = 0

    def link_sectors(self):
        self.bsp_nodes = {"index": 0}
        def get_bsp_nodes(node, userData):
            self.bsp_nodes["index"] += 1

            if node.level not in self.bsp_nodes:
                self.bsp_nodes[node.level] = []
            self.bsp_nodes[node.level].append( {"index": self.bsp_nodes["index"]-1, "x": node.x, "y": node.y, "w": node.w, "h": node.h, "node": node } )

            return True

        libtcod.bsp_traverse_inverted_level_order(self.bsp, get_bsp_nodes, userData=None)
        # pp(self.bsp_nodes)

        # Set Sector Galaxy Positions
        for index, sector in enumerate(self.sectors):
            node = self.bsp_nodes[self.bsp_depth][index]
            startx = int(node["x"] + (node["w"]/2.0))
            starty = int(node["y"] + (node["h"]/2.0))
            sector.galaxy_position_x = startx
            sector.galaxy_position_y = starty

        # Link nodes in the bsp tree
        for i in range(self.bsp_depth):
            for index in range(0, self.sector_count, 2**(i+1)):
                # print("current depth: {} starting index: {}".format(i, index))
                node1_index = index
                if i == 0:
                    # we are linking the lowest level nodes
                    node2_index = node1_index + 2**i
                else:
                    # find the two closest nodes in each subtree
                    node2_index = node1_index + 2**i
                    min_distance = self.screen_width
                    min_node1 = None
                    min_node2 = None

                    tree1_start_index = index
                    tree1_stop_index = index + (2**(i+1))/2
                    tree2_start_index = tree1_stop_index
                    tree2_stop_index = tree2_start_index + (2**(i+1))/2
                    # pp([tree1_start_index, tree1_stop_index, tree2_start_index, tree2_stop_index])

                    for n1 in range(tree1_start_index, tree1_stop_index):
                        for n2 in range(tree2_start_index, tree2_stop_index):
                            if n1 != n2 and n1 < self.sector_count and n2 < self.sector_count:
                                # pp((n1, n2))
                                node1 = self.bsp_nodes[self.bsp_depth][n1]
                                node2 = self.bsp_nodes[self.bsp_depth][n2]
                                d = math.sqrt((node2["x"] - node1["x"])**2 + (node2["y"] - node1["y"])**2)
                                if d < min_distance:
                                    min_distance = d
                                    min_node1 = node1["index"]
                                    min_node2 = node2["index"]
                                    # print("new min: {} indexes: {} {}".format(d, min_node1, min_node2))
                                    node1_index = min_node1
                                    node2_index = min_node2

                    # print("done min ---")

                if node2_index < self.sector_count:
                    # print("linked {} -> {}".format(node1_index, node2_index))
                    if node2_index not in self.sectors[node1_index].neighbors:
                        self.sectors[node1_index].neighbors.append( node2_index )

        # Add links in the other direction
        for index, sector in enumerate(self.sectors):
            for neighbor in sector.neighbors:
                if index not in self.sectors[neighbor].neighbors:
                    self.sectors[neighbor].neighbors.append(index)

        self.one_way_links = []
        for index, sector in enumerate(self.sectors):
            for neighbor in sector.neighbors:
                if [index, neighbor] not in self.one_way_links and [neighbor, index] not in self.one_way_links:
                    self.one_way_links.append([index, neighbor])

        # pp([sector.neighbors for sector in self.sectors])
        # pp(self.one_way_links)


    def draw(self, buffer):

        # Draw Connecting Lines
        for index1, index2 in self.one_way_links:
            if index1 == self.current_sector and \
               index2 == self.sectors[self.current_sector].neighbors[self.targeted_sector_index] or \
               index2 == self.current_sector and \
               index1 == self.sectors[self.current_sector].neighbors[self.targeted_sector_index]:
                # if this is a line to the target sector
                color = libtcod.Color(0, 255, 0)
            elif self.sectors[index1].discovered() and self.sectors[index2].discovered():
                # if this is a line between two discovered sectors
                color = libtcod.Color(87, 186, 255)
            else:
                # else standard connecting line
                color = libtcod.Color(150, 150, 150)

            libtcod.line_init(
                self.sectors[index1].galaxy_position_x,
                self.sectors[index1].galaxy_position_y,
                self.sectors[index2].galaxy_position_x,
                self.sectors[index2].galaxy_position_y,
            )
            x,y=libtcod.line_step()
            while x is not None:
                # if self.sectors[index1].discovered() or self.sectors[index2].discovered():
                buffer.set_fore(x, y, color[0], color[1], color[2], 255)
                x,y=libtcod.line_step()

        # Draw Sectors Nodes
        for index, sector in enumerate(self.sectors):
            x, y = sector.galaxy_position_x, sector.galaxy_position_y
            buffer.set_fore(x, y, sector.star_color[0], sector.star_color[1], sector.star_color[2], sector.star_icon)
            for x, y, icon in [(x-1, y-1, ord(' ')), (x, y-1, ord(' ')), (x+1, y-1, ord(' ')),
                               (x-1, y,   ord(' ')),                     (x+1, y,   ord(' ')),
                               (x-1, y+1, ord(' ')), (x, y+1, ord(' ')), (x+1, y+1, ord(' ')) ]:
                buffer.set_fore(x, y, 0, 0, 0, icon )

            if index == self.sectors[self.current_sector].neighbors[self.targeted_sector_index]:
                x, y  = sector.galaxy_position_x, sector.galaxy_position_y
                for x, y, icon in [(x-1, y-1, ord(' ')), (x, y-1, ord('-')), (x+1, y-1, ord(' ')),
                                   (x-1, y,   ord('|')),                     (x+1, y,   ord('|')),
                                   (x-1, y+1, ord(' ')), (x, y+1, ord('-')), (x+1, y+1, ord(' ')) ]:
                    buffer.set_fore(x, y, 255, 128, 128, icon)

            if index == self.current_sector:
                t = time.clock()
                if t > self.selected_blink + 0.5:
                    if t > self.selected_blink + 1.0:
                        self.selected_blink = t
                    x, y  = sector.galaxy_position_x, sector.galaxy_position_y
                    for x, y, icon in [(x-1, y-1, 213), (x, y-1, 205), (x+1, y-1, 184),
                                       (x-1, y,   179),                (x+1, y,   179),
                                       (x-1, y+1, 212), (x, y+1, 205), (x+1, y+1, 190) ]:
                        buffer.set_fore(x, y, 128, 255, 128, icon)

class SectorMap:
    def __init__(self, galaxy, seed, name, posx=None, posy=None):
        self.galaxy = galaxy
        self.screen_width = self.galaxy.screen_width
        self.screen_height = self.galaxy.screen_height

        self.name = name
        self.galaxy_position_x = int(random.random() * (self.screen_width/2)) + self.screen_width/4
        self.galaxy_position_y = int(random.random() * (self.screen_height/2)) + self.screen_height/4

        self.seed = seed
        random.seed(seed)

        # self.sector_background = libtcod.Color( random.randrange(0,256), random.randrange(0,256), random.randrange(0,256) )
        self.nebula_background = [ random.random(), random.random(), random.random() ]
        self.nebula_seed       = seed * 3
        self.planet_count      = random.randrange(1, 17)
        self.asteriod_count    = random.randrange(0, 25)

        self.asteroids = []
        self.planets   = []
        self.neighbors = []

        self.star_icon = ord('?')
        self.star_color = libtcod.Color(255, 255, 255)

        self.new_star()

        for p in range(0, self.planet_count):
            self.new_planet()

        for a in range(self.asteriod_count):
            self.new_asteroid()

    def discovered(self):
        return self.star_icon != ord('?')

    def new_star(self):
        star_class = random.choice(Planet.star_classes.keys())
        star_temp = random.randrange(
                Planet.star_classes[star_class]['temp'][0],
                Planet.star_classes[star_class]['temp'][1])
        self.planets.append( {
            "planet_class" : "star",
            "star_class"   : star_class,
            "star_temp"    : star_temp,
            "position_x"   : 0,
            "position_y"   : 0,
            "diameter"     : 50,
            "seed"         : random.randrange(1,1000000),
            "name"         : self.galaxy.next_name(),
        } )

    def new_asteroid(self):
        self.asteroids.append( {
            "planet_class" : "asteroid",
            "position_x"   : random.randrange(-1000,1001),
            "position_y"   : random.randrange(-1000,1001),
            "diameter"     : random.randrange(5, 8),
            "seed"         : random.randrange(1,1000000),
            "name"         : "Asteroid",
        } )

    def new_planet(self):
        self.planets.append( {
            "planet_class" : Planet.classes[ random.randrange(0, len(Planet.classes)) ],
            "position_x"   : random.randrange(-1000,1001),
            "position_y"   : random.randrange(-1000,1001),
            "diameter"     : random.randrange(18, self.galaxy.screen_height),
            "seed"         : random.randrange(1,1000000),
            "name"         : self.galaxy.next_name(),
        } )

    def __repr__(self):
        return repr({ "posx": self.galaxy_position_x, "posy": self.galaxy_position_y, "seed": self.seed, "planet_count": self.planet_count, "nebula_background": self.nebula_background, "planets": self.planets })

    def print_planet_loading_icon(self, console, icon, color, offset=0, count=0, line=0):
        center_height = self.screen_height/2
        center_width = self.screen_width/2
        libtcod.console_put_char_ex(console, center_width-((count+2)/2)+offset, center_height+4+line, icon, color, libtcod.black)
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
            if planet['planet_class'] == "star":
                self.star_icon = icon
                self.star_color = color
            self.print_planet_loading_icon(console, icon, color, offset=index, count=len(self.planets))

        # self.loading_message("Mapping Asteroids", console)
        for index, asteroid in enumerate(self.asteroids):
            icon, color, asteroid_count = sector.add_asteroid(
                planet_class=asteroid['planet_class'],
                position_x=asteroid['position_x'],
                position_y=asteroid['position_y'],
                diameter=asteroid['diameter'],
                seed=asteroid['seed'],
                name=asteroid['name'],
            )
            self.print_planet_loading_icon(console, icon, color, offset=index, count=len(self.asteroids), line=1)

        self.loading_message("Reading Background Radiation", console)
        starfield = Starfield(sector, max_stars=50)
        nebula = Nebula(sector, r_factor=self.nebula_background[0], g_factor=self.nebula_background[1], b_factor=self.nebula_background[2], seed=self.nebula_seed)

        return sector, starfield, nebula
