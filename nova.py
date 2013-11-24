#!/usr/bin/env python
# coding: utf-8

import libtcodpy as libtcod
import math
from random import randrange, choice

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

class Particle:
    def __init__(self, x, y, particle_type, index, colormap, charactermap, velocity=0.0, angle=0.0,
            velocity_component_x=0.0, velocity_component_y=0.0):
        self.x = x
        self.y = y
        self.sector_position_x = 0.0
        self.sector_position_y = 0.0
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

        self.sector_position_x += self.velocity_component_x
        self.sector_position_y += self.velocity_component_y

class Feature:
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

        self.sector_position_x = 0.0
        self.sector_position_y = 0.0

        self.deltav = 0.10
        self.turn_rate = math.radians(5.0)
        self.twopi = 2 * math.pi
        self.max_heading = self.twopi - self.turn_rate

        self.velocity_angle = 0.0
        self.velocity_angle_opposite = 180.0
        self.heading = 0.0
        self.velocity = 0.0
        self.velocity_component_x = 0.0
        self.velocity_component_y = 0.0

        # self.ship = [libtcod.image_load('images/ship_{0}.png'.format(str(angle).zfill(3))) for angle in range(0, 360, 10)]
        self.ship = [[[None, None, None, None, None, None, None, None], [None, None, [libtcod.Color(9,9,9), libtcod.Color(162,162,162), 232], None, None, None, None, None], [None, None, [libtcod.Color(0,0,0), libtcod.Color(205,205,205), 231], [libtcod.Color(237,237,237), libtcod.Color(61,61,61), 227], [libtcod.Color(30,30,30), libtcod.Color(218,218,218), 232], None, None, None], [None, None, None, [libtcod.Color(253,253,253), libtcod.Color(191,191,191), 232], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(246,246,246), libtcod.Color(118,118,118), 227], [libtcod.Color(191,191,191), libtcod.Color(0,0,0), 228], None], [None, None, [libtcod.Color(0,0,0), libtcod.Color(162,162,162), 229], [libtcod.Color(255,255,255), libtcod.Color(249,249,249), 226], [libtcod.Color(242,242,242), libtcod.Color(91,91,91), 229], [libtcod.Color(0,0,0), libtcod.Color(174,174,174), 228], None, None], [None, None, [libtcod.Color(205,205,205), libtcod.Color(14,14,14), 230], [libtcod.Color(20,20,20), libtcod.Color(203,203,203), 226], None, None, None, None], [None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None]], [[None, None, None, None, None, None, None, None], [None, [libtcod.Color(0,0,0), libtcod.Color(2,2,2), 229], None, None, None, None, None, None], [None, None, [libtcod.Color(219,219,219), libtcod.Color(34,34,34), 232], [libtcod.Color(254,254,254), libtcod.Color(47,47,47), 228], [libtcod.Color(196,196,196), libtcod.Color(0,0,0), 228], None, None, None], [None, None, None, [libtcod.Color(255,255,255), libtcod.Color(199,199,199), 232], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(253,253,253), libtcod.Color(208,208,208), 229], [libtcod.Color(0,0,0), libtcod.Color(164,164,164), 228], None], [None, None, None, [libtcod.Color(254,254,254), libtcod.Color(218,218,218), 226], [libtcod.Color(242,242,242), libtcod.Color(34,34,34), 229], None, None, None], [None, None, [libtcod.Color(0,0,0), libtcod.Color(149,149,149), 231], [libtcod.Color(74,74,74), libtcod.Color(255,255,255), 226], None, None, None, None], [None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None]], [[None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None], [None, [libtcod.Color(4,4,4), libtcod.Color(90,90,90), 227], [libtcod.Color(242,242,242), libtcod.Color(34,34,34), 228], [libtcod.Color(252,252,252), libtcod.Color(0,0,0), 228], [libtcod.Color(237,237,237), libtcod.Color(0,0,0), 228], [libtcod.Color(207,207,207), libtcod.Color(0,0,0), 228], [libtcod.Color(7,7,7), libtcod.Color(176,176,176), 232], None], [None, None, [libtcod.Color(0,0,0), libtcod.Color(222,222,222), 227], [libtcod.Color(255,255,255), libtcod.Color(217,217,217), 232], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(243,243,243), libtcod.Color(17,17,17), 229], None, None], [None, None, None, [libtcod.Color(182,182,182), libtcod.Color(255,255,255), 231], [libtcod.Color(243,243,243), libtcod.Color(12,12,12), 229], None, None, None], [None, None, None, [libtcod.Color(230,230,230), libtcod.Color(6,6,6), 229], None, None, None, None], [None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None]], [[None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None], [None, [libtcod.Color(31,31,31), libtcod.Color(191,191,191), 229], [libtcod.Color(220,220,220), libtcod.Color(0,0,0), 228], [libtcod.Color(246,246,246), libtcod.Color(0,0,0), 228], [libtcod.Color(255,255,255), libtcod.Color(11,11,11), 228], [libtcod.Color(246,246,246), libtcod.Color(84,84,84), 228], [libtcod.Color(0,0,0), libtcod.Color(137,137,137), 226], None], [None, None, [libtcod.Color(43,43,43), libtcod.Color(219,219,219), 228], [libtcod.Color(255,255,255), libtcod.Color(238,238,238), 232], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(80,80,80), libtcod.Color(255,255,255), 226], None, None], [None, None, None, [libtcod.Color(91,91,91), libtcod.Color(255,255,255), 231], [libtcod.Color(243,243,243), libtcod.Color(32,32,32), 229], None, None, None], [None, None, None, [libtcod.Color(39,39,39), libtcod.Color(229,229,229), 231], None, None, None, None], [None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None]], [[None, None, None, None, None, None, None, None], [None, None, None, None, None, None, [libtcod.Color(0,0,0), libtcod.Color(17,17,17), 232], None], [None, None, [libtcod.Color(21,21,21), libtcod.Color(163,163,163), 229], [libtcod.Color(240,240,240), libtcod.Color(0,0,0), 228], [libtcod.Color(232,232,232), libtcod.Color(100,100,100), 226], [libtcod.Color(229,229,229), libtcod.Color(42,42,42), 229], None, None], [None, [libtcod.Color(32,32,32), libtcod.Color(218,218,218), 227], [libtcod.Color(233,233,233), libtcod.Color(46,46,46), 232], [libtcod.Color(255,255,255), libtcod.Color(252,252,252), 232], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(22,22,22), libtcod.Color(207,207,207), 226], None, None], [None, None, None, [libtcod.Color(25,25,25), libtcod.Color(251,251,251), 231], [libtcod.Color(242,242,242), libtcod.Color(88,88,88), 229], None, None, None], [None, None, None, [libtcod.Color(0,0,0), libtcod.Color(181,181,181), 231], [libtcod.Color(36,36,36), libtcod.Color(228,228,228), 226], None, None, None], [None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None]], [[None, None, None, None, None, None, None, None], [None, None, None, None, None, [libtcod.Color(12,12,12), libtcod.Color(195,195,195), 232], None, None], [None, None, None, [libtcod.Color(236,236,236), libtcod.Color(33,33,33), 228], [libtcod.Color(255,255,255), libtcod.Color(207,207,207), 226], [libtcod.Color(213,213,213), libtcod.Color(0,0,0), 231], None, None], [None, [libtcod.Color(106,106,106), libtcod.Color(0,0,0), 226], [libtcod.Color(220,220,220), libtcod.Color(251,251,251), 231], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(255,255,255), libtcod.Color(254,254,254), 229], [libtcod.Color(0,0,1), libtcod.Color(100,100,100), 226], None, None], [None, None, None, [libtcod.Color(25,25,25), libtcod.Color(221,221,221), 231], [libtcod.Color(245,245,245), libtcod.Color(163,163,163), 229], None, None, None], [None, None, None, None, [libtcod.Color(236,236,236), libtcod.Color(32,32,32), 231], None, None, None], [None, None, None, None, [libtcod.Color(0,0,0), libtcod.Color(99,99,99), 226], None, None, None], [None, None, None, None, None, None, None, None]], [[None, None, None, None, None, None, None, None], [None, None, None, None, [libtcod.Color(25,25,25), libtcod.Color(238,238,238), 229], [libtcod.Color(120,120,120), libtcod.Color(0,0,0), 231], None, None], [None, None, None, [libtcod.Color(213,213,213), libtcod.Color(0,0,0), 226], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(7,7,7), libtcod.Color(65,65,65), 226], None, None], [None, [libtcod.Color(0,0,0), libtcod.Color(203,203,203), 229], [libtcod.Color(253,253,253), libtcod.Color(132,132,132), 226], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(255,255,255), libtcod.Color(251,251,251), 229], None, None, None], [None, [libtcod.Color(0,0,0), libtcod.Color(25,25,25), 227], [libtcod.Color(0,0,0), libtcod.Color(66,66,66), 228], [libtcod.Color(63,63,63), libtcod.Color(238,238,238), 227], [libtcod.Color(255,255,255), libtcod.Color(235,235,235), 231], None, None, None], [None, None, None, None, [libtcod.Color(195,195,195), libtcod.Color(0,0,0), 232], None, None, None], [None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None]], [[None, None, None, None, None, None, None, None], [None, None, None, None, [libtcod.Color(204,204,204), libtcod.Color(20,20,20), 226], None, None, None], [None, None, None, [libtcod.Color(243,243,243), libtcod.Color(14,14,14), 226], [libtcod.Color(255,255,255), libtcod.Color(223,223,223), 231], None, None, None], [None, None, [libtcod.Color(242,242,242), libtcod.Color(9,9,9), 226], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(253,253,253), libtcod.Color(243,243,243), 227], None, None, None], [None, [libtcod.Color(0,0,0), libtcod.Color(235,235,235), 227], [libtcod.Color(0,0,0), libtcod.Color(210,210,210), 228], [libtcod.Color(0,0,0), libtcod.Color(191,191,191), 228], [libtcod.Color(255,255,255), libtcod.Color(222,222,222), 232], None, None, None], [None, None, None, None, [libtcod.Color(0,0,0), libtcod.Color(229,229,229), 227], [libtcod.Color(72,72,72), libtcod.Color(0,0,0), 231], None, None], [None, None, None, None, None, [libtcod.Color(0,0,0), libtcod.Color(14,14,14), 226], None, None], [None, None, None, None, None, None, None, None]], [[None, None, None, None, [libtcod.Color(0,0,0), libtcod.Color(112,112,112), 232], None, None, None], [None, None, None, [libtcod.Color(0,0,0), libtcod.Color(208,208,208), 229], [libtcod.Color(234,234,234), libtcod.Color(0,0,0), 231], None, None, None], [None, None, None, [libtcod.Color(253,253,253), libtcod.Color(137,137,137), 226], [libtcod.Color(225,225,225), libtcod.Color(72,72,72), 227], None, None, None], [None, None, [libtcod.Color(212,212,212), libtcod.Color(0,0,0), 226], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(254,254,254), libtcod.Color(227,227,227), 227], None, None, None], [None, [libtcod.Color(21,21,21), libtcod.Color(195,195,195), 229], [libtcod.Color(51,51,51), libtcod.Color(254,254,254), 228], [libtcod.Color(0,0,0), libtcod.Color(208,208,208), 228], [libtcod.Color(253,253,253), libtcod.Color(122,122,122), 232], [libtcod.Color(137,137,137), libtcod.Color(0,0,0), 231], None, None], [None, None, None, None, None, [libtcod.Color(0,0,0), libtcod.Color(227,227,227), 226], None, None], [None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None]], [[None, None, None, [libtcod.Color(0,0,0), libtcod.Color(143,143,143), 229], None, None, None, None], [None, None, None, [libtcod.Color(59,59,59), libtcod.Color(247,247,247), 231], None, None, None, None], [None, None, None, [libtcod.Color(255,255,255), libtcod.Color(230,230,230), 226], [libtcod.Color(242,242,242), libtcod.Color(45,45,45), 231], None, None, None], [None, None, [libtcod.Color(30,30,30), libtcod.Color(236,236,236), 231], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(255,255,255), libtcod.Color(218,218,218), 227], None, None, None], [None, None, [libtcod.Color(252,252,252), libtcod.Color(182,182,182), 230], [libtcod.Color(0,0,0), libtcod.Color(220,220,220), 228], [libtcod.Color(222,222,222), libtcod.Color(0,0,0), 232], [libtcod.Color(226,226,226), libtcod.Color(14,14,14), 231], None, None], [None, [libtcod.Color(0,0,0), libtcod.Color(162,162,162), 227], None, None, None, [libtcod.Color(0,0,0), libtcod.Color(162,162,162), 227], None, None], [None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None]], [[None, None, None, None, None, None, None, None], [None, None, None, [libtcod.Color(225,225,225), libtcod.Color(0,0,0), 227], None, None, None, None], [None, None, [libtcod.Color(24,24,24), libtcod.Color(166,166,166), 229], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(194,194,194), libtcod.Color(17,17,17), 231], None, None, None], [None, None, [libtcod.Color(0,0,0), libtcod.Color(240,240,240), 231], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(255,255,255), libtcod.Color(222,222,222), 227], [libtcod.Color(0,0,0), libtcod.Color(160,160,160), 232], None, None], [None, None, [libtcod.Color(229,229,229), libtcod.Color(94,94,94), 226], [libtcod.Color(192,192,192), libtcod.Color(0,0,0), 229], [libtcod.Color(0,0,0), libtcod.Color(235,235,235), 228], [libtcod.Color(84,84,84), libtcod.Color(225,225,225), 230], None, None], [None, None, [libtcod.Color(11,11,11), libtcod.Color(227,227,227), 226], None, None, None, None, None], [None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None]], [[None, None, [libtcod.Color(0,0,0), libtcod.Color(23,23,23), 229], None, None, None, None, None], [None, None, [libtcod.Color(0,0,0), libtcod.Color(187,187,187), 231], [libtcod.Color(12,12,12), libtcod.Color(239,239,239), 232], None, None, None, None], [None, None, [libtcod.Color(0,0,0), libtcod.Color(223,223,223), 231], [libtcod.Color(255,255,255), libtcod.Color(238,238,238), 227], [libtcod.Color(8,8,8), libtcod.Color(237,237,237), 232], None, None, None], [None, None, [libtcod.Color(0,0,0), libtcod.Color(246,246,246), 231], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(255,255,255), libtcod.Color(237,237,237), 227], [libtcod.Color(4,4,4), libtcod.Color(236,236,236), 232], None, None], [None, None, [libtcod.Color(7,7,7), libtcod.Color(255,255,255), 231], [libtcod.Color(231,231,231), libtcod.Color(0,0,0), 229], [libtcod.Color(0,0,0), libtcod.Color(182,182,182), 228], [libtcod.Color(0,0,0), libtcod.Color(228,228,228), 228], [libtcod.Color(0,0,0), libtcod.Color(3,3,3), 226], None], [None, None, [libtcod.Color(48,48,48), libtcod.Color(229,229,229), 227], None, None, None, None, None], [None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None]], [[None, None, None, None, None, None, None, None], [None, None, [libtcod.Color(159,159,159), libtcod.Color(0,0,0), 227], None, None, None, None, None], [None, None, [libtcod.Color(44,44,44), libtcod.Color(255,255,255), 231], [libtcod.Color(255,255,255), libtcod.Color(164,164,164), 227], [libtcod.Color(10,10,10), libtcod.Color(223,223,223), 232], None, None, None], [None, None, [libtcod.Color(0,0,0), libtcod.Color(253,253,253), 231], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(255,255,255), libtcod.Color(252,252,252), 227], [libtcod.Color(196,196,196), libtcod.Color(0,0,0), 227], None, None], [None, None, [libtcod.Color(0,0,0), libtcod.Color(235,235,235), 231], [libtcod.Color(249,249,249), libtcod.Color(86,86,86), 229], [libtcod.Color(0,0,0), libtcod.Color(91,91,91), 228], [libtcod.Color(8,8,8), libtcod.Color(53,53,53), 226], None, None], [None, None, [libtcod.Color(0,0,0), libtcod.Color(201,201,201), 231], [libtcod.Color(0,0,0), libtcod.Color(184,184,184), 226], None, None, None, None], [None, None, [libtcod.Color(0,0,0), libtcod.Color(93,93,93), 227], None, None, None, None, None], [None, None, None, None, None, None, None, None]], [[None, None, None, None, None, None, None, None], [None, [libtcod.Color(0,0,0), libtcod.Color(19,19,19), 231], [libtcod.Color(14,14,14), libtcod.Color(195,195,195), 232], None, None, None, None, None], [None, None, [libtcod.Color(249,249,249), libtcod.Color(187,187,187), 232], [libtcod.Color(239,239,239), libtcod.Color(66,66,66), 227], [libtcod.Color(29,29,29), libtcod.Color(218,218,218), 232], None, None, None], [None, None, [libtcod.Color(50,50,50), libtcod.Color(254,254,254), 231], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(255,255,255), libtcod.Color(248,248,248), 229], [libtcod.Color(220,220,220), libtcod.Color(129,129,129), 231], [libtcod.Color(0,0,0), libtcod.Color(60,60,60), 232], None], [None, None, [libtcod.Color(0,0,0), libtcod.Color(194,194,194), 231], [libtcod.Color(254,254,254), libtcod.Color(190,190,190), 229], None, None, None, None], [None, None, None, [libtcod.Color(236,236,236), libtcod.Color(23,23,23), 231], None, None, None, None], [None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None]], [[None, None, None, None, None, None, None, None], [None, [libtcod.Color(19,19,19), libtcod.Color(0,0,0), 228], None, None, None, None, None, None], [None, [libtcod.Color(14,14,14), libtcod.Color(195,195,195), 227], [libtcod.Color(249,249,249), libtcod.Color(187,187,187), 227], [libtcod.Color(254,254,254), libtcod.Color(50,50,50), 228], [libtcod.Color(194,194,194), libtcod.Color(0,0,0), 228], None, None, None], [None, None, [libtcod.Color(239,239,239), libtcod.Color(66,66,66), 232], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(254,254,254), libtcod.Color(190,190,190), 229], [libtcod.Color(23,23,23), libtcod.Color(236,236,236), 228], None, None], [None, None, [libtcod.Color(29,29,29), libtcod.Color(218,218,218), 227], [libtcod.Color(255,255,255), libtcod.Color(248,248,248), 229], None, None, None, None], [None, None, None, [libtcod.Color(129,129,129), libtcod.Color(220,220,220), 228], None, None, None, None], [None, None, None, [libtcod.Color(0,0,0), libtcod.Color(60,60,60), 227], None, None, None, None], [None, None, None, None, None, None, None, None]], [[None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None], [None, [libtcod.Color(159,159,159), libtcod.Color(0,0,0), 232], [libtcod.Color(255,255,255), libtcod.Color(44,44,44), 228], [libtcod.Color(253,253,253), libtcod.Color(0,0,0), 228], [libtcod.Color(235,235,235), libtcod.Color(0,0,0), 228], [libtcod.Color(201,201,201), libtcod.Color(0,0,0), 228], [libtcod.Color(0,0,0), libtcod.Color(93,93,93), 232], None], [None, None, [libtcod.Color(255,255,255), libtcod.Color(164,164,164), 232], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(249,249,249), libtcod.Color(86,86,86), 229], [libtcod.Color(0,0,0), libtcod.Color(184,184,184), 226], None, None], [None, None, [libtcod.Color(10,10,10), libtcod.Color(223,223,223), 227], [libtcod.Color(255,255,255), libtcod.Color(252,252,252), 232], [libtcod.Color(91,91,91), libtcod.Color(0,0,0), 231], None, None, None], [None, None, None, [libtcod.Color(196,196,196), libtcod.Color(0,0,0), 232], [libtcod.Color(8,8,8), libtcod.Color(53,53,53), 226], None, None, None], [None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None]], [[None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None], [[libtcod.Color(0,0,0), libtcod.Color(23,23,23), 229], [libtcod.Color(187,187,187), libtcod.Color(0,0,0), 228], [libtcod.Color(223,223,223), libtcod.Color(0,0,0), 228], [libtcod.Color(246,246,246), libtcod.Color(0,0,0), 228], [libtcod.Color(255,255,255), libtcod.Color(7,7,7), 228], [libtcod.Color(48,48,48), libtcod.Color(229,229,229), 232], None, None], [None, [libtcod.Color(12,12,12), libtcod.Color(239,239,239), 227], [libtcod.Color(255,255,255), libtcod.Color(238,238,238), 232], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(231,231,231), libtcod.Color(0,0,0), 229], None, None, None], [None, None, [libtcod.Color(8,8,8), libtcod.Color(237,237,237), 227], [libtcod.Color(255,255,255), libtcod.Color(237,237,237), 232], [libtcod.Color(182,182,182), libtcod.Color(0,0,0), 231], None, None, None], [None, None, None, [libtcod.Color(4,4,4), libtcod.Color(236,236,236), 227], [libtcod.Color(228,228,228), libtcod.Color(0,0,0), 231], None, None, None], [None, None, None, None, [libtcod.Color(0,0,0), libtcod.Color(3,3,3), 226], None, None, None], [None, None, None, None, None, None, None, None]], [[None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None], [None, None, [libtcod.Color(24,24,24), libtcod.Color(166,166,166), 229], [libtcod.Color(240,240,240), libtcod.Color(0,0,0), 228], [libtcod.Color(229,229,229), libtcod.Color(94,94,94), 226], [libtcod.Color(11,11,11), libtcod.Color(227,227,227), 226], None, None], [None, [libtcod.Color(225,225,225), libtcod.Color(0,0,0), 232], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(192,192,192), libtcod.Color(0,0,0), 229], None, None, None], [None, None, [libtcod.Color(17,17,17), libtcod.Color(194,194,194), 228], [libtcod.Color(255,255,255), libtcod.Color(222,222,222), 232], [libtcod.Color(235,235,235), libtcod.Color(0,0,0), 231], None, None, None], [None, None, None, [libtcod.Color(0,0,0), libtcod.Color(160,160,160), 227], [libtcod.Color(84,84,84), libtcod.Color(225,225,225), 230], None, None, None], [None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None]], [[None, None, None, None, None, None, None, None], [None, None, None, None, None, [libtcod.Color(0,0,0), libtcod.Color(162,162,162), 232], None, None], [None, None, None, [libtcod.Color(236,236,236), libtcod.Color(30,30,30), 228], [libtcod.Color(252,252,252), libtcod.Color(182,182,182), 230], None, None, None], [[libtcod.Color(0,0,0), libtcod.Color(143,143,143), 229], [libtcod.Color(247,247,247), libtcod.Color(59,59,59), 228], [libtcod.Color(255,255,255), libtcod.Color(230,230,230), 226], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(220,220,220), libtcod.Color(0,0,0), 231], None, None, None], [None, None, [libtcod.Color(45,45,45), libtcod.Color(242,242,242), 228], [libtcod.Color(255,255,255), libtcod.Color(218,218,218), 232], [libtcod.Color(222,222,222), libtcod.Color(0,0,0), 227], None, None, None], [None, None, None, None, [libtcod.Color(14,14,14), libtcod.Color(226,226,226), 228], [libtcod.Color(0,0,0), libtcod.Color(162,162,162), 232], None, None], [None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None]], [[None, None, None, None, None, None, None, None], [None, None, None, None, [libtcod.Color(21,21,21), libtcod.Color(195,195,195), 229], None, None, None], [None, None, None, [libtcod.Color(212,212,212), libtcod.Color(0,0,0), 226], [libtcod.Color(254,254,254), libtcod.Color(51,51,51), 231], None, None, None], [None, [libtcod.Color(0,0,0), libtcod.Color(208,208,208), 229], [libtcod.Color(253,253,253), libtcod.Color(137,137,137), 226], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(208,208,208), libtcod.Color(0,0,0), 231], None, None, None], [[libtcod.Color(0,0,0), libtcod.Color(112,112,112), 227], [libtcod.Color(0,0,0), libtcod.Color(234,234,234), 228], [libtcod.Color(225,225,225), libtcod.Color(72,72,72), 232], [libtcod.Color(254,254,254), libtcod.Color(227,227,227), 232], [libtcod.Color(253,253,253), libtcod.Color(122,122,122), 227], None, None, None], [None, None, None, None, [libtcod.Color(0,0,0), libtcod.Color(137,137,137), 228], [libtcod.Color(0,0,0), libtcod.Color(227,227,227), 226], None, None], [None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None]], [[None, None, None, None, None, None, None, None], [None, None, None, None, [libtcod.Color(0,0,0), libtcod.Color(235,235,235), 232], None, None, None], [None, None, None, [libtcod.Color(242,242,242), libtcod.Color(9,9,9), 226], [libtcod.Color(210,210,210), libtcod.Color(0,0,0), 231], None, None, None], [None, None, [libtcod.Color(243,243,243), libtcod.Color(14,14,14), 226], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(191,191,191), libtcod.Color(0,0,0), 231], None, None, None], [None, [libtcod.Color(204,204,204), libtcod.Color(20,20,20), 226], [libtcod.Color(223,223,223), libtcod.Color(255,255,255), 228], [libtcod.Color(253,253,253), libtcod.Color(243,243,243), 232], [libtcod.Color(255,255,255), libtcod.Color(222,222,222), 227], [libtcod.Color(0,0,0), libtcod.Color(229,229,229), 232], None, None], [None, None, None, None, None, [libtcod.Color(0,0,0), libtcod.Color(72,72,72), 228], [libtcod.Color(0,0,0), libtcod.Color(14,14,14), 226], None], [None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None]], [[None, None, None, None, None, None, None, None], [None, None, None, [libtcod.Color(0,0,0), libtcod.Color(203,203,203), 229], [libtcod.Color(0,0,0), libtcod.Color(25,25,25), 232], None, None, None], [None, None, None, [libtcod.Color(253,253,253), libtcod.Color(132,132,132), 226], [libtcod.Color(66,66,66), libtcod.Color(0,0,0), 231], None, None, None], [None, None, [libtcod.Color(213,213,213), libtcod.Color(0,0,0), 226], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(63,63,63), libtcod.Color(238,238,238), 232], None, None, None], [None, [libtcod.Color(25,25,25), libtcod.Color(238,238,238), 229], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(255,255,255), libtcod.Color(251,251,251), 229], [libtcod.Color(235,235,235), libtcod.Color(255,255,255), 228], [libtcod.Color(195,195,195), libtcod.Color(0,0,0), 227], None, None], [None, [libtcod.Color(0,0,0), libtcod.Color(120,120,120), 228], [libtcod.Color(7,7,7), libtcod.Color(65,65,65), 226], None, None, None, None, None], [None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None]], [[None, None, None, None, None, None, None, None], [None, None, None, [libtcod.Color(106,106,106), libtcod.Color(0,0,0), 226], None, None, None, None], [None, None, None, [libtcod.Color(251,251,251), libtcod.Color(220,220,220), 228], None, None, None, None], [None, None, [libtcod.Color(33,33,33), libtcod.Color(236,236,236), 231], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(221,221,221), libtcod.Color(25,25,25), 228], None, None, None], [None, None, [libtcod.Color(255,255,255), libtcod.Color(207,207,207), 226], [libtcod.Color(255,255,255), libtcod.Color(254,254,254), 229], [libtcod.Color(245,245,245), libtcod.Color(163,163,163), 229], [libtcod.Color(32,32,32), libtcod.Color(236,236,236), 228], [libtcod.Color(0,0,0), libtcod.Color(99,99,99), 226], None], [None, [libtcod.Color(12,12,12), libtcod.Color(195,195,195), 227], [libtcod.Color(0,0,0), libtcod.Color(213,213,213), 228], [libtcod.Color(0,0,1), libtcod.Color(100,100,100), 226], None, None, None, None], [None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None]], [[None, None, None, None, None, None, None, None], [None, None, None, [libtcod.Color(32,32,32), libtcod.Color(218,218,218), 232], None, None, None, None], [None, None, [libtcod.Color(21,21,21), libtcod.Color(163,163,163), 229], [libtcod.Color(233,233,233), libtcod.Color(46,46,46), 227], None, None, None, None], [None, None, [libtcod.Color(0,0,0), libtcod.Color(240,240,240), 231], [libtcod.Color(255,255,255), libtcod.Color(252,252,252), 227], [libtcod.Color(251,251,251), libtcod.Color(25,25,25), 228], [libtcod.Color(181,181,181), libtcod.Color(0,0,0), 228], None, None], [None, None, [libtcod.Color(232,232,232), libtcod.Color(100,100,100), 226], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(242,242,242), libtcod.Color(88,88,88), 229], [libtcod.Color(36,36,36), libtcod.Color(228,228,228), 226], None, None], [None, None, [libtcod.Color(229,229,229), libtcod.Color(42,42,42), 229], [libtcod.Color(22,22,22), libtcod.Color(207,207,207), 226], None, None, None, None], [None, [libtcod.Color(0,0,0), libtcod.Color(17,17,17), 227], None, None, None, None, None, None], [None, None, None, None, None, None, None, None]], [[None, None, None, None, None, None, None, None], [None, None, [libtcod.Color(31,31,31), libtcod.Color(191,191,191), 229], None, None, None, None, None], [None, None, [libtcod.Color(0,0,0), libtcod.Color(220,220,220), 231], [libtcod.Color(219,219,219), libtcod.Color(43,43,43), 231], None, None, None, None], [None, None, [libtcod.Color(0,0,0), libtcod.Color(246,246,246), 231], [libtcod.Color(255,255,255), libtcod.Color(238,238,238), 227], [libtcod.Color(255,255,255), libtcod.Color(91,91,91), 228], [libtcod.Color(229,229,229), libtcod.Color(39,39,39), 228], None, None], [None, None, [libtcod.Color(11,11,11), libtcod.Color(255,255,255), 231], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(243,243,243), libtcod.Color(32,32,32), 229], None, None, None], [None, None, [libtcod.Color(84,84,84), libtcod.Color(246,246,246), 231], [libtcod.Color(80,80,80), libtcod.Color(255,255,255), 226], None, None, None, None], [None, None, [libtcod.Color(0,0,0), libtcod.Color(137,137,137), 226], None, None, None, None, None], [None, None, None, None, None, None, None, None]], [[None, None, None, None, None, None, None, None], [None, None, [libtcod.Color(4,4,4), libtcod.Color(90,90,90), 232], None, None, None, None, None], [None, None, [libtcod.Color(34,34,34), libtcod.Color(242,242,242), 231], [libtcod.Color(0,0,0), libtcod.Color(222,222,222), 232], None, None, None, None], [None, None, [libtcod.Color(0,0,0), libtcod.Color(252,252,252), 231], [libtcod.Color(255,255,255), libtcod.Color(217,217,217), 227], [libtcod.Color(255,255,255), libtcod.Color(182,182,182), 228], [libtcod.Color(230,230,230), libtcod.Color(6,6,6), 229], None, None], [None, None, [libtcod.Color(0,0,0), libtcod.Color(237,237,237), 231], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(243,243,243), libtcod.Color(12,12,12), 229], None, None, None], [None, None, [libtcod.Color(0,0,0), libtcod.Color(207,207,207), 231], [libtcod.Color(243,243,243), libtcod.Color(17,17,17), 229], None, None, None, None], [None, None, [libtcod.Color(7,7,7), libtcod.Color(176,176,176), 227], None, None, None, None, None], [None, None, None, None, None, None, None, None]], [[None, None, None, None, None, None, None, None], [None, [libtcod.Color(0,0,0), libtcod.Color(2,2,2), 229], None, None, None, None, None, None], [None, None, [libtcod.Color(219,219,219), libtcod.Color(34,34,34), 227], None, None, [libtcod.Color(149,149,149), libtcod.Color(0,0,0), 228], None, None], [None, None, [libtcod.Color(47,47,47), libtcod.Color(254,254,254), 231], [libtcod.Color(255,255,255), libtcod.Color(199,199,199), 227], [libtcod.Color(254,254,254), libtcod.Color(218,218,218), 226], [libtcod.Color(74,74,74), libtcod.Color(255,255,255), 226], None, None], [None, None, [libtcod.Color(0,0,0), libtcod.Color(196,196,196), 231], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(242,242,242), libtcod.Color(34,34,34), 229], None, None, None], [None, None, None, [libtcod.Color(253,253,253), libtcod.Color(208,208,208), 229], None, None, None, None], [None, None, None, [libtcod.Color(164,164,164), libtcod.Color(0,0,0), 231], None, None, None, None], [None, None, None, None, None, None, None, None]], [[None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None], [None, [libtcod.Color(9,9,9), libtcod.Color(162,162,162), 227], [libtcod.Color(205,205,205), libtcod.Color(0,0,0), 228], None, [libtcod.Color(0,0,0), libtcod.Color(162,162,162), 229], [libtcod.Color(205,205,205), libtcod.Color(14,14,14), 230], None, None], [None, None, [libtcod.Color(237,237,237), libtcod.Color(61,61,61), 232], [libtcod.Color(253,253,253), libtcod.Color(191,191,191), 227], [libtcod.Color(255,255,255), libtcod.Color(249,249,249), 226], [libtcod.Color(20,20,20), libtcod.Color(203,203,203), 226], None, None], [None, None, [libtcod.Color(30,30,30), libtcod.Color(218,218,218), 227], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(242,242,242), libtcod.Color(91,91,91), 229], None, None, None], [None, None, None, [libtcod.Color(246,246,246), libtcod.Color(118,118,118), 232], [libtcod.Color(174,174,174), libtcod.Color(0,0,0), 231], None, None, None], [None, None, None, [libtcod.Color(0,0,0), libtcod.Color(191,191,191), 231], None, None, None, None], [None, None, None, None, None, None, None, None]], [[None, None, None, None, None, None, None, None], [None, None, None, None, None, [libtcod.Color(0,0,0), libtcod.Color(2,2,2), 229], None, None], [None, [libtcod.Color(0,0,0), libtcod.Color(195,195,195), 229], [libtcod.Color(0,0,2), libtcod.Color(103,103,103), 232], None, [libtcod.Color(52,52,52), libtcod.Color(251,251,251), 229], [libtcod.Color(204,204,204), libtcod.Color(0,0,0), 231], None, None], [None, None, [libtcod.Color(254,254,254), libtcod.Color(160,160,160), 232], [libtcod.Color(255,255,255), libtcod.Color(208,208,208), 228], [libtcod.Color(255,255,255), libtcod.Color(254,254,254), 229], [libtcod.Color(0,0,2), libtcod.Color(94,94,94), 226], None, None], [None, None, [libtcod.Color(11,11,11), libtcod.Color(222,222,222), 227], [libtcod.Color(255,255,255), libtcod.Color(252,252,252), 232], [libtcod.Color(245,245,245), libtcod.Color(166,166,166), 229], None, None, None], [None, None, None, [libtcod.Color(200,200,200), libtcod.Color(0,0,0), 232], [libtcod.Color(253,253,253), libtcod.Color(36,36,36), 231], None, None, None], [None, None, None, None, [libtcod.Color(164,164,164), libtcod.Color(0,0,0), 231], None, None, None], [None, None, None, None, None, None, None, None]], [[None, None, None, None, None, None, None, None], [None, None, None, None, None, [libtcod.Color(4,4,4), libtcod.Color(90,90,90), 232], None, None], [[libtcod.Color(0,0,0), libtcod.Color(0,0,2), 227], None, None, None, [libtcod.Color(235,235,235), libtcod.Color(0,0,0), 226], [libtcod.Color(4,4,4), libtcod.Color(54,54,54), 226], None, None], [None, [libtcod.Color(2,2,2), libtcod.Color(235,235,235), 227], [libtcod.Color(237,237,237), libtcod.Color(198,198,198), 227], [libtcod.Color(242,242,242), libtcod.Color(166,166,166), 226], [libtcod.Color(255,255,255), libtcod.Color(250,250,250), 229], None, None, None], [None, None, [libtcod.Color(6,6,6), libtcod.Color(237,237,237), 227], [libtcod.Color(255,255,255), libtcod.Color(237,237,237), 232], [libtcod.Color(255,255,255), libtcod.Color(237,237,237), 231], None, None, None], [None, None, None, [libtcod.Color(10,10,10), libtcod.Color(238,238,238), 227], [libtcod.Color(247,247,247), libtcod.Color(207,207,207), 231], None, None, None], [None, None, None, None, [libtcod.Color(14,14,14), libtcod.Color(176,176,176), 227], None, None, None], [None, None, None, None, None, None, None, None]], [[None, None, None, None, None, None, None, None], [None, None, None, None, [libtcod.Color(31,31,31), libtcod.Color(191,191,191), 229], None, None, None], [None, None, None, None, [libtcod.Color(242,242,242), libtcod.Color(198,198,198), 228], None, None, None], [None, [libtcod.Color(8,8,8), libtcod.Color(203,203,203), 229], [libtcod.Color(255,255,255), libtcod.Color(66,66,66), 228], [libtcod.Color(249,249,249), libtcod.Color(104,104,104), 226], [libtcod.Color(253,253,253), libtcod.Color(242,242,242), 227], None, None, None], [None, None, [libtcod.Color(16,16,16), libtcod.Color(192,192,192), 228], [libtcod.Color(255,255,255), libtcod.Color(223,223,223), 232], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], None, None, None], [None, None, None, [libtcod.Color(0,0,0), libtcod.Color(164,164,164), 227], [libtcod.Color(249,249,249), libtcod.Color(76,76,76), 232], [libtcod.Color(84,84,84), libtcod.Color(0,0,0), 231], None, None], [None, None, None, None, None, [libtcod.Color(0,0,0), libtcod.Color(137,137,137), 226], None, None], [None, None, None, None, None, None, None, None]], [[None, None, None, None, None, None, None, None], [None, None, None, None, [libtcod.Color(32,32,32), libtcod.Color(218,218,218), 232], None, None, None], [None, None, None, [libtcod.Color(15,15,15), libtcod.Color(190,190,190), 229], [libtcod.Color(224,224,224), libtcod.Color(64,64,64), 227], None, None, None], [None, [libtcod.Color(20,20,20), libtcod.Color(150,150,150), 229], [libtcod.Color(230,230,230), libtcod.Color(0,0,0), 228], [libtcod.Color(253,253,253), libtcod.Color(50,50,50), 226], [libtcod.Color(254,254,254), libtcod.Color(226,226,226), 227], None, None, None], [None, None, [libtcod.Color(44,44,44), libtcod.Color(241,241,241), 228], [libtcod.Color(255,255,255), libtcod.Color(218,218,218), 232], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(143,143,143), libtcod.Color(0,0,0), 231], None, None], [None, None, None, None, [libtcod.Color(21,21,21), libtcod.Color(231,231,231), 228], [libtcod.Color(217,217,217), libtcod.Color(10,10,10), 231], None, None], [None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None]], [[None, None, None, None, None, None, None, None], [None, None, None, [libtcod.Color(20,20,20), libtcod.Color(150,150,150), 229], None, None, None, None], [None, None, None, [libtcod.Color(0,0,0), libtcod.Color(230,230,230), 231], [libtcod.Color(241,241,241), libtcod.Color(44,44,44), 231], None, None, None], [None, None, [libtcod.Color(15,15,15), libtcod.Color(190,190,190), 229], [libtcod.Color(253,253,253), libtcod.Color(50,50,50), 226], [libtcod.Color(255,255,255), libtcod.Color(218,218,218), 227], None, None, None], [None, [libtcod.Color(32,32,32), libtcod.Color(218,218,218), 227], [libtcod.Color(224,224,224), libtcod.Color(64,64,64), 232], [libtcod.Color(254,254,254), libtcod.Color(226,226,226), 232], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(231,231,231), libtcod.Color(21,21,21), 231], None, None], [None, None, None, None, [libtcod.Color(0,0,0), libtcod.Color(143,143,143), 228], [libtcod.Color(10,10,10), libtcod.Color(217,217,217), 228], None, None], [None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None]], [[None, None, None, None, None, None, None, None], [None, None, None, [libtcod.Color(8,8,8), libtcod.Color(203,203,203), 229], None, None, None, None], [None, None, None, [libtcod.Color(66,66,66), libtcod.Color(255,255,255), 231], [libtcod.Color(192,192,192), libtcod.Color(16,16,16), 231], None, None, None], [None, None, None, [libtcod.Color(249,249,249), libtcod.Color(104,104,104), 226], [libtcod.Color(255,255,255), libtcod.Color(223,223,223), 227], [libtcod.Color(0,0,0), libtcod.Color(164,164,164), 232], None, None], [None, [libtcod.Color(31,31,31), libtcod.Color(191,191,191), 229], [libtcod.Color(198,198,198), libtcod.Color(242,242,242), 231], [libtcod.Color(253,253,253), libtcod.Color(242,242,242), 232], [libtcod.Color(255,255,255), libtcod.Color(255,255,255), 219], [libtcod.Color(249,249,249), libtcod.Color(76,76,76), 227], None, None], [None, None, None, None, None, [libtcod.Color(0,0,0), libtcod.Color(84,84,84), 228], [libtcod.Color(0,0,0), libtcod.Color(137,137,137), 226], None], [None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None]], [[None, None, [libtcod.Color(0,0,0), libtcod.Color(0,0,2), 232], None, None, None, None, None], [None, None, None, [libtcod.Color(2,2,2), libtcod.Color(235,235,235), 232], None, None, None, None], [None, None, None, [libtcod.Color(237,237,237), libtcod.Color(198,198,198), 232], [libtcod.Color(6,6,6), libtcod.Color(237,237,237), 232], None, None, None], [None, None, None, [libtcod.Color(242,242,242), libtcod.Color(166,166,166), 226], [libtcod.Color(255,255,255), libtcod.Color(237,237,237), 227], [libtcod.Color(10,10,10), libtcod.Color(238,238,238), 232], None, None], [None, None, [libtcod.Color(235,235,235), libtcod.Color(0,0,0), 226], [libtcod.Color(255,255,255), libtcod.Color(250,250,250), 229], [libtcod.Color(237,237,237), libtcod.Color(255,255,255), 228], [libtcod.Color(207,207,207), libtcod.Color(247,247,247), 228], [libtcod.Color(14,14,14), libtcod.Color(176,176,176), 232], None], [None, [libtcod.Color(4,4,4), libtcod.Color(90,90,90), 227], [libtcod.Color(4,4,4), libtcod.Color(54,54,54), 226], None, None, None, None, None], [None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None]], [[None, None, None, None, None, None, None, None], [None, None, [libtcod.Color(0,0,0), libtcod.Color(195,195,195), 229], None, None, None, None, None], [None, None, [libtcod.Color(0,0,2), libtcod.Color(103,103,103), 227], [libtcod.Color(254,254,254), libtcod.Color(160,160,160), 227], [libtcod.Color(11,11,11), libtcod.Color(222,222,222), 232], None, None, None], [None, None, None, [libtcod.Color(208,208,208), libtcod.Color(255,255,255), 231], [libtcod.Color(255,255,255), libtcod.Color(252,252,252), 227], [libtcod.Color(200,200,200), libtcod.Color(0,0,0), 227], None, None], [None, None, [libtcod.Color(52,52,52), libtcod.Color(251,251,251), 229], [libtcod.Color(255,255,255), libtcod.Color(254,254,254), 229], [libtcod.Color(245,245,245), libtcod.Color(166,166,166), 229], [libtcod.Color(36,36,36), libtcod.Color(253,253,253), 228], [libtcod.Color(0,0,0), libtcod.Color(164,164,164), 228], None], [None, [libtcod.Color(0,0,0), libtcod.Color(2,2,2), 229], [libtcod.Color(0,0,0), libtcod.Color(204,204,204), 228], [libtcod.Color(0,0,2), libtcod.Color(94,94,94), 226], None, None, None, None], [None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None]]]

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

    def update_location(self):
        if self.velocity > 0.0:
            self.sector_position_x += self.velocity_component_x
            self.sector_position_y += self.velocity_component_y

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

        if self.velocity < 0.09:
            self.velocity = 0.0
        elif self.velocity > 3.0:
            self.velocity = 3.0

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

    # \--,
    #  \  \--,
    #   \     \----,
    #    \          \---,
    #     X              ----
    #    /          /---`
    #   /     /----`
    #  /  /--`
    # /--`

    def draw(self):
        sprite_index = int(round(math.degrees(self.heading), -1)/10)
        if sprite_index > 35 or sprite_index < 0:
            sprite_index = 0

        ship = self.ship[sprite_index]
        # libtcod.image_set_key_color(ship, libtcod.blue)

        # libtcod.image_blit(ship, con, self.x+4, self.y+4, libtcod.BKGND_SET, 1.0, 1.0, 0)
        # libtcod.image_blit_rect(ship, con, self.x-4, self.y-4, -1, -1, libtcod.BKGND_SET)

        self.update_location()

        # libtcod.image_blit_2x(ship, con, self.x, self.y)
        # libtcod.image_blit_2x(ship, ship_console, 0, 0)

        for y, line in enumerate(ship):
            for x, cell in enumerate(line):
                if cell != None:
                    b = cell[0]
                    f = cell[1]
                    c = cell[2]
                    buffer.set(self.x + x, self.y + y, b[0], b[1], b[2], f[0], f[1], f[2], c)

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
                buffer.set_fore(x+1, mirror_y_coordinate(y),   color[0], color[1], color[2], character)
                buffer.set_fore(x-1, mirror_y_coordinate(y),   color[0], color[1], color[2], character)
                buffer.set_fore(x,   mirror_y_coordinate(y+1), color[0], color[1], color[2], character)
                buffer.set_fore(x,   mirror_y_coordinate(y-1), color[0], color[1], color[2], character)
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

# buffer = ConsoleBuffer(width, height, back_r=0, back_g=0, back_b=0, fore_r=0, fore_g=0, fore_b=0, char=' ')
panel_buffer  = libtcod.ConsoleBuffer(HUD_WIDTH, HUD_HEIGHT, sector_background[0], sector_background[1], sector_background[2])

panel_console = libtcod.console_new(HUD_WIDTH, HUD_HEIGHT)

libtcod.console_set_default_foreground(panel_console, libtcod.white)
libtcod.console_set_default_background(panel_console, libtcod.black)

global buffer
buffer = libtcod.ConsoleBuffer(SCREEN_WIDTH, SCREEN_HEIGHT)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
libtcod.console_set_default_background(panel_console, sector_background)

# ship_console = libtcod.console_new(8, 8)
# libtcod.console_set_key_color(ship_console, libtcod.blue)

mouse = libtcod.Mouse()
key = libtcod.Key()

libtcod.console_set_keyboard_repeat(1, 10)

starfield = Starfield()
player_ship = Ship()

objects = [Feature()]

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

