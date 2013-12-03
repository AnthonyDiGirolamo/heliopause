import libtcodpy as libtcod

class Nebula:
    def __init__(self, sector, r_factor=0.1, g_factor=0.1, b_factor=0.1, seed=95837203):
        self.sector = sector

        self.starting_left = 0 - self.sector.screen_width/2
        self.starting_top  = 0 + self.sector.screen_height/2

        self.r_factor = r_factor
        self.g_factor = g_factor
        self.b_factor = b_factor

        self.noise_zoom = 6.0
        self.noise_octaves = 4.0

        self.r_rand = libtcod.random_new_from_seed(seed)
        self.g_rand = libtcod.random_new_from_seed(seed+1)
        self.b_rand = libtcod.random_new_from_seed(seed+2)

        self.r_noise = libtcod.noise_new(2, libtcod.NOISE_DEFAULT_HURST, libtcod.NOISE_DEFAULT_LACUNARITY, self.r_rand)
        self.g_noise = libtcod.noise_new(2, libtcod.NOISE_DEFAULT_HURST, libtcod.NOISE_DEFAULT_LACUNARITY, self.g_rand)
        self.b_noise = libtcod.noise_new(2, libtcod.NOISE_DEFAULT_HURST, libtcod.NOISE_DEFAULT_LACUNARITY, self.b_rand)

        self.build_sector_nebula()

    def build_sector_nebula(self):
        self.grid = []
        for x in range(0, 1000):
            column = []
            for y in range(0, 1000):
                f = [self.noise_zoom * x / (2*self.sector.screen_width),
                     self.noise_zoom * y / (2*self.sector.screen_height)]
                value = 0.0
                value = libtcod.noise_get_fbm(self.r_noise, f, self.noise_octaves, libtcod.NOISE_SIMPLEX)
                r = int((value + 1.0) * self.r_factor * 255)
                value = libtcod.noise_get_fbm(self.g_noise, f, self.noise_octaves, libtcod.NOISE_SIMPLEX)
                g = int((value + 1.0) * self.g_factor * 255)
                value = libtcod.noise_get_fbm(self.b_noise, f, self.noise_octaves, libtcod.NOISE_SIMPLEX)
                b = int((value + 1.0) * self.b_factor * 255)
                column.append([r, g, b])
            self.grid.append(column)

    def draw(self):
        left = int(500 + (self.sector.visible_space_left*0.1))
        top = int(500 + (self.sector.visible_space_top*0.1))

        for y in range(0, self.sector.screen_height):
            for x in range(0, self.sector.screen_width):
                r, g, b = self.grid[left+x][top+y]
                self.sector.buffer.set_back(x, self.sector.mirror_y_coordinate(y), r, g, b)


