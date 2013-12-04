from random import randrange

import libtcodpy as libtcod

class Nebula:
    def __init__(self, sector, r_factor=0.4, g_factor=0.4, b_factor=0.4, seed=95837203, size=512):
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

        self.r_noise = libtcod.noise_new(2, libtcod.NOISE_DEFAULT_HURST, libtcod.NOISE_DEFAULT_LACUNARITY, self.r_rand)
        self.g_noise = libtcod.noise_new(2, libtcod.NOISE_DEFAULT_HURST, libtcod.NOISE_DEFAULT_LACUNARITY, self.g_rand)
        self.b_noise = libtcod.noise_new(2, libtcod.NOISE_DEFAULT_HURST, libtcod.NOISE_DEFAULT_LACUNARITY, self.b_rand)
        self.c_noise = libtcod.noise_new(2, libtcod.NOISE_DEFAULT_HURST, libtcod.NOISE_DEFAULT_LACUNARITY, self.c_rand)

        self.build_sector_nebula()

    # cover 0..255
    # sharpness 0.0..1.0
    def exponent_filter(self, value, cover=32, sharpness=0.995):
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

    def build_sector_nebula(self):
        self.grid = []
        for x in range(0, self.size):
            column = []
            for y in range(0, self.size):
                f = [self.noise_zoom * x / (2*self.sector.screen_width),
                     self.noise_zoom * y / (2*self.sector.screen_height)]
                r = self.get_color_value(libtcod.noise_get_fbm(self.r_noise, f, self.noise_octaves, libtcod.NOISE_SIMPLEX), self.r_factor)
                g = self.get_color_value(libtcod.noise_get_fbm(self.g_noise, f, self.noise_octaves, libtcod.NOISE_SIMPLEX), self.g_factor)
                b = self.get_color_value(libtcod.noise_get_fbm(self.b_noise, f, self.noise_octaves, libtcod.NOISE_SIMPLEX), self.b_factor)
                c = self.exponent_filter( (libtcod.noise_get_fbm(self.c_noise, f, self.noise_octaves, libtcod.NOISE_SIMPLEX) + 1.0) * 255 )
                # column.append([c, c, c])
                # column.append([r, g, b])
                column.append([self.blend_multiply(r,c), self.blend_multiply(g,c), self.blend_multiply(b,c)])
            self.grid.append(column)

    def draw(self):
        left = int((self.size/2) + (self.sector.visible_space_left * self.parallax_speed))
        top = int((self.size/2) + (self.sector.visible_space_top * self.parallax_speed))

        for y in range(0, self.sector.screen_height):
            for x in range(0, self.sector.screen_width):
                r, g, b = self.grid[(left+x)%self.size][(top+y)%self.size]
                self.sector.buffer.set_back(x, self.sector.mirror_y_coordinate(y), r, g, b)


