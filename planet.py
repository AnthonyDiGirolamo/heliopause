import pprint
pp = pprint.PrettyPrinter(indent=4, width=200).pprint
import math
import sys
import random
import collections

import libtcodpy as libtcod

class Planet:
    def __init__(self, sector, planet_class='terran', position_x=-30, position_y=30, diameter=60, seed=3849058430):
        self.planet_class = planet_class
        self.seed = seed
        self.sector = sector
        self.sector_position_x = position_x
        self.sector_position_y = position_y
        self.width = diameter
        if (self.width % 2) != 0:
            self.width += 1
        self.height = self.width
        self.rotation_index = 0

        # Classes:
        #     arid
        #     artic
        #     barren
        #     desert
        #     gas giant
        #     junlge
        #     lava
        #     ocean
        #     terran
        #     tundra
        #TODO: clouds / atmosphere

        if self.planet_class == 'terran':
            # Earthlike colormap
            self.height_colormap = collections.deque( libtcod.color_gen_map(
                [ libtcod.Color(10,10,40), libtcod.Color(30,30,170),
                  libtcod.Color(114, 150, 71), libtcod.Color(80,120,10),
                  libtcod.Color(17,109,7), libtcod.Color(120,220,120),
                  libtcod.Color(208,208,239), libtcod.Color(255,255,255)],
                [ 0, 30, 34, 80, 90, 200, 210, 255]
            ))
            self.noise_dx = 0.0
            self.noise_dy = 0.0
            self.noise_dz = 0.0
            self.noise_octaves = 4.0
            self.noise_zoom = 1.0
            self.noise_hurst = libtcod.NOISE_DEFAULT_HURST
            self.noise_lacunarity = libtcod.NOISE_DEFAULT_LACUNARITY

        elif self.planet_class == 'star':
            # Star colormap
            self.height_colormap = collections.deque( libtcod.color_gen_map(
                [ libtcod.Color(255, 222, 0), libtcod.Color(232, 112, 26), libtcod.Color(255, 222, 0), libtcod.Color(232, 112, 26), libtcod.Color(255, 222, 0)],
                [ 0, 64, 128, 192, 255] ))
            self.noise_dx = 0.0
            self.noise_dy = 0.0
            self.noise_dz = 0.0
            self.noise_octaves = 4.0
            self.noise_zoom = 4.0
            self.noise_hurst = libtcod.NOISE_DEFAULT_HURST
            self.noise_lacunarity = libtcod.NOISE_DEFAULT_LACUNARITY

        self.heightmap_width = self.width * 2
        self.heightmap_height = self.height

        # self.char_shades = ['.',':','!','*','o','e','&','#','%','@']
        self.shades = [i/10.0 for i in range(10, -1, -1)]

        self.build_circle_mask()
        self.build_heightmap()
        self.build_atmosphere()
        self.build_sprite()

    def spherical_noise(self, noise_dx=0.0, noise_dy=0.0, noise_dz=0.0, noise_octaves=4.0, noise_zoom=1.0, noise_hurst=libtcod.NOISE_DEFAULT_HURST, noise_lacunarity=libtcod.NOISE_DEFAULT_LACUNARITY, seed=None):
        self.rnd = libtcod.random_new_from_seed(self.seed) if seed is None else libtcod.random_new_from_seed(seed)

        noise = libtcod.noise_new(3, noise_hurst, noise_lacunarity, self.rnd)
        hm = libtcod.heightmap_new(self.heightmap_width, self.heightmap_height)

        noise_dx += 0.01
        noise_dy += 0.01
        noise_dz += 0.01

        pi_times_two = 2 * math.pi
        pi_div_two = math.pi / 2.0

        theta = 0.0
        phi = pi_div_two * -1.0
        x = 0
        y = 0

        while phi <= pi_div_two:
            while theta <= pi_times_two:
                f = [
                    noise_zoom * math.cos(phi) * math.cos(theta),
                    noise_zoom * math.cos(phi) * math.sin(theta),
                    noise_zoom * math.sin(phi),
                ]
                value = libtcod.noise_get_fbm(noise, f, noise_octaves, libtcod.NOISE_PERLIN)
                # print((x, y, value))
                libtcod.heightmap_set_value(hm, x, y, value)
                theta += (pi_times_two / self.heightmap_width)
                x += 1
            phi += (math.pi / (self.heightmap_height-1))
            y += 1
            x = 0
            theta = 0.0
        return hm

    def build_atmosphere(self):
        if self.planet_class == 'terran':
            atmosphere = self.spherical_noise(
                    noise_dx=10.0,
                    noise_dy=10.0,
                    noise_dz=10.0,
                    noise_octaves=4.0,
                    noise_zoom=2.0,
                    noise_hurst=self.noise_hurst,
                    noise_lacunarity=self.noise_lacunarity )

            libtcod.heightmap_normalize(atmosphere, 0, 1.0)
            libtcod.heightmap_add(atmosphere,0.30)
            libtcod.heightmap_clamp(atmosphere,0.0,1.0)
            self.atmosphere = atmosphere
        else:
            self.atmosphere = None

    def build_heightmap(self):
        hm = self.spherical_noise( self.noise_dx, self.noise_dy, self.noise_dz, self.noise_octaves, self.noise_zoom, self.noise_hurst, self.noise_lacunarity )

        if self.planet_class == 'terran':
            libtcod.heightmap_normalize(hm, 0, 1.0)
            libtcod.heightmap_add(hm,-0.55)
            libtcod.heightmap_clamp(hm,0.0,1.0)
            libtcod.heightmap_rain_erosion(hm,1000,0.46,0.12,self.rnd)

        libtcod.heightmap_normalize(hm, 0, 255)
        self.heightmap = hm

        # # self.rnd=libtcod.random_new_from_seed(1094911894)
        # self.rnd=libtcod.random_get_instance()
        # # 3x3 kernel for smoothing operations
        # smoothKernelSize=9
        # smoothKernelDx=[-1,0,1,-1,0,1,-1,0,1]
        # smoothKernelDy=[-1,-1,-1,0,0,0,1,1,1]
        # smoothKernelWeight=[1.0,2.0,1.0,2.0,20.0,2.0,1.0,2.0,1.0]

        # hm=libtcod.heightmap_new(self.heightmap_width, self.heightmap_height)
        # coef=[0.11,0.22,-0.22,0.18,]
        # tmp =libtcod.heightmap_new(self.heightmap_width, self.heightmap_height)
        # libtcod.heightmap_add_voronoi(tmp,100,4,coef,self.rnd)
        # libtcod.heightmap_normalize(tmp)
        # libtcod.heightmap_add_hm(hm,tmp,hm)
        # libtcod.heightmap_delete(tmp)
        # # self.addHill(hm,40,11.4,0.31,0.09)
        # libtcod.heightmap_add(hm,-0.2)
        # libtcod.heightmap_clamp(hm,0.0,1.0)
        # smoothKernelWeight[4] = 20
        # for i in range(2,-1,-1) :
        #     libtcod.heightmap_kernel_transform(hm,smoothKernelSize,smoothKernelDx,smoothKernelDy,smoothKernelWeight,0,0.86)
        # libtcod.heightmap_rain_erosion(hm,1000,0.46,0.12,self.rnd)
        # libtcod.heightmap_normalize(hm,0,255)
        # self.heightmap = hm
        # # print(repr(libtcod.heightmap_get_minmax(self.heightmap)))

    def normalize(self, v):
        len = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
        return (v[0]/len, v[1]/len, v[2]/len)

    def dot(self, x,y):
        d = x[0]*y[0] + x[1]*y[1] + x[2]*y[2]
        return -d if d < 0 else 0

    def draw_sphere(self, r, k, ambient, light):
        self.circle_mask = []
        for i in range(int(math.floor(-r)), int(math.ceil(r))):
            x = i + 0.5
            col = []

            for j in range(int(math.floor(-1*r)), int(math.ceil(1*r))):
                # y = j/2 + 0.5
                y = j + 0.5
                if x*x + y*y <= r*r:
                    vec = self.normalize((x,y,math.sqrt(r*r - x*x - y*y)))
                    b = self.dot(light,vec)**k + ambient
                    intensity = int((1-b)*(len(self.shades)-1))
                    col.append( self.shades[intensity] if 0 <= intensity < len(self.shades) else self.shades[0] )
                    # sys.stdout.write(self.char_shades[intensity] if 0 <= intensity < len(self.char_shades) else self.char_shades[0])
                else:
                    col.append(0)
                    # sys.stdout.write(' ')
            # sys.stdout.write("\n")

            self.circle_mask.append(col)
        # pp(self.circle_mask)

    def build_circle_mask(self):
        if self.planet_class == 'star':
            light = self.normalize((10,10,-50))
            self.draw_sphere(self.width/2, 0.5, 0.1, light)
        else:
            light = self.normalize((20,20,-50))
            self.draw_sphere(self.width/2, 0.5, 0.1, light)

    def blend_colors(self, r1, g1, b1, r2, g2, b2, alpha):
        return ( int(alpha * r1 + (1-alpha) * r2),
                 int(alpha * g1 + (1-alpha) * g2),
                 int(alpha * b1 + (1-alpha) * b2) )

    def build_sprite(self):
        self.sprite = []
        for x in range(0, self.width):
            column = []
            for y in range(0, self.height):
                r, g, b = self.blend_layers(x, y)
                column.append( [r, g, b] )
            self.sprite.append(column)

    def blend_layers(self, x, y, terrain_rotation=0, atmosphere_rotation=0):
        terrain_color = int(libtcod.heightmap_get_value(self.heightmap, ((x+terrain_rotation) % self.heightmap_width), y))
        if terrain_color > 255:
            terrain_color = 255
        r = self.height_colormap[terrain_color][0]
        g = self.height_colormap[terrain_color][1]
        b = self.height_colormap[terrain_color][2]
        if self.atmosphere:
            cloud_cover = libtcod.heightmap_get_value(self.atmosphere, ((x+atmosphere_rotation) % self.heightmap_width), y)
            r, g, b = self.blend_colors(r, g, b, 255, 255, 255, cloud_cover)
        if self.circle_mask[x][y] < 1.0:
            r, g, b = self.blend_colors(r, g, b, 0, 0, 0, self.circle_mask[x][y])
        return [r, g, b]

    def draw(self):
        feature_left         = self.sector_position_x
        feature_top          = self.sector_position_y
        feature_right        = self.sector_position_x + self.width
        feature_bottom       = self.sector_position_y + self.height

        startingx = int(self.sector_position_x - math.floor(self.sector.visible_space_left))
        startingy = int(self.sector_position_y - math.floor(self.sector.visible_space_bottom))
        endingx = startingx + self.width
        endingy = startingy - self.height

        startingx = max([0, startingx])
        startingy = min([self.sector.screen_height-1,  startingy])
        endingx = min([self.sector.screen_width, endingx])
        endingy = max([-1, endingy])

        start_maskx = 0
        if startingx == 0:
            start_maskx += self.width - endingx
        maskx = start_maskx

        start_masky = 0
        if startingy == self.sector.screen_height-1:
            start_masky += self.height - (startingy - endingy)
        masky = start_masky

        for y in range(startingy, endingy, -1):
            for x in range(startingx, endingx):
                if self.circle_mask[maskx][masky]:
                    if self.planet_class == 'star':
                        r, g, b = self.blend_layers(maskx, masky, terrain_rotation=0, atmosphere_rotation=self.rotation_index)
                    else:
                        r, g, b = self.sprite[maskx][masky][0], self.sprite[maskx][masky][1], self.sprite[maskx][masky][2]

                    self.sector.buffer.set(x, self.sector.mirror_y_coordinate(y), r, g, b, r, g, b, ord('@') )
                maskx += 1
            maskx = start_maskx
            masky += 1

        if self.planet_class == 'star':
            self.height_colormap.rotate(1)
        else:
            self.rotation_index += 1
            if self.rotation_index >= self.heightmap_width:
                self.rotation_index = 0

