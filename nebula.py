import random
import math
from random import randrange

import libtcodpy as libtcod

class Nebula:
    def __init__(self, sector, r_factor=0.40, g_factor=0.40, b_factor=0.75, seed=95837203, size=512):
        self.seed = randrange(1,10000) if seed is None else seed
        self.sector = sector

        self.parallax_speed = 0.1

        self.starting_left = 0 - self.sector.screen_width/2
        self.starting_top  = 0 + self.sector.screen_height/2

        self.r_factor = r_factor
        self.g_factor = g_factor
        self.b_factor = b_factor

        self.noise_zoom = 2.0
        self.noise_octaves = 4.0

        self.size = size

        self.r_rand = libtcod.random_new_from_seed(self.seed)
        self.g_rand = libtcod.random_new_from_seed(self.seed+1)
        self.b_rand = libtcod.random_new_from_seed(self.seed+2)
        self.c_rand = libtcod.random_new_from_seed(self.seed*2)
        self.s_rand = libtcod.random_new_from_seed(self.seed*3)

        self.r_noise = libtcod.noise_new(2, libtcod.NOISE_DEFAULT_HURST, libtcod.NOISE_DEFAULT_LACUNARITY, self.r_rand)
        self.g_noise = libtcod.noise_new(2, libtcod.NOISE_DEFAULT_HURST, libtcod.NOISE_DEFAULT_LACUNARITY, self.g_rand)
        self.b_noise = libtcod.noise_new(2, libtcod.NOISE_DEFAULT_HURST, libtcod.NOISE_DEFAULT_LACUNARITY, self.b_rand)
        self.c_noise = libtcod.noise_new(2, libtcod.NOISE_DEFAULT_HURST, libtcod.NOISE_DEFAULT_LACUNARITY, self.c_rand)
        self.s_noise = libtcod.noise_new(2, libtcod.NOISE_DEFAULT_HURST, libtcod.NOISE_DEFAULT_LACUNARITY, self.s_rand)

        self.grid = [[None for i in range(self.size)] for i in range(self.size)]
        self.last_top = None
        self.last_left = None

    def exponent_filter(self, value, cover=32, sharpness=0.995):
        # cover 0..255
        # sharpness 0.0..1.0
        c = value - (255 - cover)
        if c < 0:
            c = 0
        new_value = 255 - ((sharpness**c) * 255)
        return int(new_value)

    def blend_multiply(self, a, b):
        return ((a * b) >> 8)

    def get_color_value(self, value, factor=0.5):
        c = int((value + 1.0) * factor * 255)
        if c < 0:
            c = 0
        elif c > 255:
            c = 255
        return c

    def draw(self):
        self.left   = left   = int((self.size/2) + (self.sector.visible_space_left * self.parallax_speed))
        self.top    = top    = int((self.size/2) + (self.sector.visible_space_top * self.parallax_speed))
        self.right  = right  = left + self.sector.screen_width
        self.bottom = bottom = top + self.sector.screen_height

        if self.last_left != left or self.last_top != top:
            for y in range(0, self.sector.screen_height+2):
                self.grid[(left-1)%self.size][(top-1+y)%self.size] = None
                self.grid[(right)%self.size][(top-1+y)%self.size] = None
            for x in range(0, self.sector.screen_width+2):
                self.grid[(left-1+x)%self.size][(bottom)%self.size] = None
                self.grid[(left-1+x)%self.size][(top-1)%self.size] = None

        self.last_left = left
        self.last_top = top

        for y in range(0, self.sector.screen_height):
            for x in range(0, self.sector.screen_width):
                if self.grid[(left+x)%self.size][(top+y)%self.size] == None:
                    f = [9999 + self.noise_zoom * (left+x) / (2*self.sector.screen_width),
                         9999 + self.noise_zoom * (top+y)  / (2*self.sector.screen_height)]
                    r = self.get_color_value(libtcod.noise_get_fbm(self.r_noise, f, self.noise_octaves, libtcod.NOISE_SIMPLEX), self.r_factor)
                    g = self.get_color_value(libtcod.noise_get_fbm(self.g_noise, f, self.noise_octaves, libtcod.NOISE_SIMPLEX), self.g_factor)
                    b = self.get_color_value(libtcod.noise_get_fbm(self.b_noise, f, self.noise_octaves, libtcod.NOISE_SIMPLEX), self.b_factor)
                    c = self.exponent_filter( (libtcod.noise_get_fbm(self.c_noise, f, self.noise_octaves, libtcod.NOISE_SIMPLEX) + 1.0) * 255 )
                    self.grid[(left+x)%self.size][(top+y)%self.size] = [
                        self.blend_colors( self.blend_multiply(r,c), self.blend_multiply(g,c), self.blend_multiply(b,c),
                        self.sector.background[0], self.sector.background[1], self.sector.background[2], 0.5), None ]

                    f[0] *= 1000.0
                    f[1] *= 1000.0
                    star_value = libtcod.noise_get_fbm(self.s_noise, f, self.noise_octaves, libtcod.NOISE_SIMPLEX)
                    if 0.1 < star_value < 0.11:
                        r, g, b = self.grid[(left+x)%self.size][(top+y)%self.size][0]
                        rm = r * random.choice([1, 2, 3, 4, 5]) if r * 5 < 255 else 255
                        gm = g * random.choice([1, 2, 3, 4, 5]) if g * 5 < 255 else 255
                        bm = b * random.choice([1, 2, 3, 4, 5]) if b * 5 < 255 else 255
                        self.grid[(left+x)%self.size][(top+y)%self.size][1] = [rm, gm, bm]

                # Set the nebula background color
                r, g, b = self.grid[(left+x)%self.size][(top+y)%self.size][0]
                self.sector.buffer.set_back(x, self.sector.mirror_y_coordinate(y), r, g, b)

                # Create a Star
                if self.grid[(left+x)%self.size][(top+y)%self.size][1]:
                    rm, gm, bm = self.grid[(left+x)%self.size][(top+y)%self.size][1]
                    self.sector.buffer.set_fore(x, self.sector.mirror_y_coordinate(y), rm, gm, bm, ord('.'))

        # end draw

    def blend_colors(self, r1, g1, b1, r2, g2, b2, alpha):
        return [ int(alpha * r1 + (1-alpha) * r2),
                 int(alpha * g1 + (1-alpha) * g2),
                 int(alpha * b1 + (1-alpha) * b2) ]
