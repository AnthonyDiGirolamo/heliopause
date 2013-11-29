import pprint
pp = pprint.PrettyPrinter(indent=4, width=200).pprint
import math
import sys
import random
import collections
import time

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

        self.terrain_rotation_index = 0
        self.atmosphere_rotation_index = 0
        self.last_terrain_rotation = 0.0
        self.last_atmosphere_rotation = 0.0

        self.selected = False

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

        self.noise_dx = 0.0
        self.noise_dy = 0.0
        self.noise_dz = 0.0
        self.noise_hurst = libtcod.NOISE_DEFAULT_HURST
        self.noise_lacunarity = libtcod.NOISE_DEFAULT_LACUNARITY

        if self.planet_class == 'terran':
            self.height_colormap = collections.deque( libtcod.color_gen_map(
                [ libtcod.Color(39,  62,  90),
                  libtcod.Color(50,  72,  88),
                  libtcod.Color(116, 184, 164),
                  libtcod.Color(142, 163, 164),
                  libtcod.Color(71,  97,  81),
                  libtcod.Color(149, 138, 115),
                  libtcod.Color(199, 197, 150),
                  libtcod.Color(220, 197, 173)],
                [ 0, 15, 70, 80, 90, 200, 233, 255]
            ))
            self.noise_octaves = 6.0
            self.noise_zoom = 1.0

        elif self.planet_class == 'ocean':
            self.height_colormap = collections.deque( libtcod.color_gen_map(
                [
                  libtcod.Color(13,  44,  53),
                  libtcod.Color(18,  51,  57),
                  libtcod.Color(16,  70,  63),
                  libtcod.Color(31,  106, 100),
                  libtcod.Color(92,  198, 169),
                  libtcod.Color(170, 211, 142),
                  libtcod.Color(78,  144, 72),
                  libtcod.Color(24,  55,  23),
                ],
                [0, 40, 80, 130, 150, 160, 180, 200]
            ))
            self.noise_octaves = 6.0
            self.noise_zoom = 1.0

        elif self.planet_class == 'jungle':
            self.height_colormap = collections.deque( libtcod.color_gen_map(
                [
                  libtcod.Color(29,  53,  112),
                  libtcod.Color(69,  137, 200),
                  libtcod.Color(61,  86,  34),
                  libtcod.Color(42,  72,  38),
                  libtcod.Color(52,  103, 35),
                  libtcod.Color(29,  47,  18),
                  libtcod.Color(75,  118, 33),
                  libtcod.Color(100, 173, 22),
                  # libtcod.Color(61,  71,  33),
                  # libtcod.Color(141, 132, 56),
                ],
                [0, 60, 80, 110, 150, 205, 235, 255]
            ))
            self.noise_octaves = 6.0
            self.noise_zoom = 3.0

        elif self.planet_class == 'lava':
            self.height_colormap = collections.deque( libtcod.color_gen_map(
                [
                  libtcod.Color(255, 151, 19),
                  libtcod.Color(255, 52,  0),
                  libtcod.Color(91,  31,  12),
                  libtcod.Color(31,  21,  11),
                  libtcod.Color(56,  44,  21),
                  libtcod.Color(0,   0,   0),
                  libtcod.Color(62,  19,  15),
                  libtcod.Color(94,  65,  35),
                ],
                [0, 60, 80, 110, 150, 205, 235, 255]
            ))
            self.noise_octaves = 6.0
            self.noise_zoom = 6.0

        elif self.planet_class == 'tundra':
            self.height_colormap = collections.deque( libtcod.color_gen_map(
                [
                  libtcod.Color(121, 183, 170),
                  libtcod.Color(167, 206, 174),
                  libtcod.Color(145, 150, 117),
                  libtcod.Color(110, 116, 93),
                  libtcod.Color(167, 157, 109),
                  libtcod.Color(86,  111, 95),
                  libtcod.Color(210, 199, 132),
                  libtcod.Color(255, 255, 200),
                ],
                [0, 60, 75, 105, 140, 200, 235, 255]
            ))
            self.noise_octaves = 6.0
            self.noise_zoom = 2.0

        elif self.planet_class == 'star':
            star_colors = random.choice([
                [libtcod.Color(255, 222, 0), libtcod.Color(232, 112, 26)],
                [libtcod.Color(211, 230, 255), libtcod.Color(128, 181, 255)],
            ])

            self.height_colormap = collections.deque( libtcod.color_gen_map(
                star_colors * 2 + [star_colors[0]],
                [ 0, 64, 128, 192, 255] ))
            self.noise_octaves = 4.0
            self.noise_zoom = 4.0

        self.heightmap_width = self.width * 2
        self.heightmap_height = self.height

        self.detail_width = self.width * 2
        if self.detail_width > self.sector.screen_height * 1.25:
            self.detail_width = int(self.sector.screen_height * 1.25)
            if (self.detail_width % 2) != 0:
                self.detail_width += 1

        self.detail_heightmap_width = self.detail_width * 2
        self.detail_heightmap_height = self.detail_width

        # self.char_shades = ['.',':','!','*','o','e','&','#','%','@']
        self.shades = [i/10.0 for i in range(10, -1, -1)]

        self.circle_mask = self.build_circle_mask(self.width)
        self.heightmap = self.build_heightmap(self.heightmap_width, self.heightmap_height)
        self.atmosphere = self.build_atmosphere(self.heightmap_width, self.heightmap_height)
        self.build_sprite()

        self.detail_circle_mask = self.build_circle_mask(self.detail_width)
        self.detail_heightmap = self.build_heightmap(self.detail_heightmap_width, self.detail_heightmap_height)
        self.detail_atmosphere = self.build_atmosphere(self.detail_heightmap_width, self.detail_heightmap_height)


    def spherical_noise(self,
            noise_dx=0.0,
            noise_dy=0.0,
            noise_dz=0.0,
            noise_octaves=4.0,
            noise_zoom=1.0,
            noise_hurst=libtcod.NOISE_DEFAULT_HURST,
            noise_lacunarity=libtcod.NOISE_DEFAULT_LACUNARITY,
            width=None,
            height=None,
            seed=None):
        self.rnd = libtcod.random_new_from_seed(self.seed) if seed is None else libtcod.random_new_from_seed(seed)

        noise = libtcod.noise_new(3, noise_hurst, noise_lacunarity, self.rnd)
        hm = libtcod.heightmap_new(width, height)

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
                theta += (pi_times_two / width)
                x += 1
            phi += (math.pi / (height-1))
            y += 1
            x = 0
            theta = 0.0
        return hm

    def build_atmosphere(self, width, height):
        if self.planet_class in ['terran', 'ocean', 'jungle', 'tundra'] :
            atmosphere = self.spherical_noise(
                    noise_dx=10.0,
                    noise_dy=10.0,
                    noise_dz=10.0,
                    noise_octaves=4.0,
                    noise_zoom=2.0,
                    noise_hurst=self.noise_hurst,
                    noise_lacunarity=self.noise_lacunarity,
                    width=width,
                    height=height )

            libtcod.heightmap_normalize(atmosphere, 0, 1.0)
            libtcod.heightmap_add(atmosphere,0.30)
            libtcod.heightmap_clamp(atmosphere,0.0,1.0)
            return atmosphere
        else:
            return None

    def build_heightmap(self, width, height):
        hm = self.spherical_noise(
                self.noise_dx,
                self.noise_dy,
                self.noise_dz,
                self.noise_octaves,
                self.noise_zoom,
                self.noise_hurst,
                self.noise_lacunarity,
                width,
                height)

        if self.planet_class == 'terran':
            libtcod.heightmap_normalize(hm, 0, 1.0)
            libtcod.heightmap_add(hm,-0.40)
            libtcod.heightmap_clamp(hm,0.0,1.0)
            libtcod.heightmap_rain_erosion(hm,1000,0.46,0.12,self.rnd)
            libtcod.heightmap_normalize(hm, 0, 255)

        elif self.planet_class == 'ocean':
            libtcod.heightmap_normalize(hm, 0, 1.0)
            libtcod.heightmap_add(hm,-0.40)
            libtcod.heightmap_clamp(hm,0.0,1.0)
            libtcod.heightmap_rain_erosion(hm,3000,0.46,0.12,self.rnd)
            libtcod.heightmap_normalize(hm, 0, 200)

        elif self.planet_class == 'jungle':
            libtcod.heightmap_normalize(hm, 0, 1.0)
            libtcod.heightmap_add(hm,0.20)
            libtcod.heightmap_clamp(hm,0.0,1.0)
            libtcod.heightmap_rain_erosion(hm,3000,0.25,0.05,self.rnd)
            libtcod.heightmap_normalize(hm, 0, 255)

        elif self.planet_class == 'lava':
            libtcod.heightmap_normalize(hm, 0, 1.0)
            libtcod.heightmap_rain_erosion(hm,1000,0.65,0.05,self.rnd)
            libtcod.heightmap_normalize(hm, 0, 255)

        elif self.planet_class == 'tundra':
            libtcod.heightmap_normalize(hm, 0, 1.0)
            # libtcod.heightmap_add(hm,0.20)
            # libtcod.heightmap_clamp(hm,0.0,1.0)
            libtcod.heightmap_rain_erosion(hm,2000,0.45,0.05,self.rnd)
            libtcod.heightmap_normalize(hm, 0, 255)

        else:
            libtcod.heightmap_normalize(hm, 0, 255)

        return hm

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
        circle_mask = []
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

            circle_mask.append(col)
        # pp(self.circle_mask)
        return circle_mask

    def build_circle_mask(self, diameter=None):
        if diameter is None:
            diameter = self.width

        if self.planet_class == 'star':
            light = self.normalize((10,10,-50))
            return self.draw_sphere(diameter/2, 0.5, 0.1, light)
        else:
            light = self.normalize((20,20,-50))
            return self.draw_sphere(diameter/2, 0.5, 0.1, light)

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

    def blend_layers(self, x, y, terrain_rotation=0, atmosphere_rotation=0, circle_mask=None, heightmap=None, atmosphere=None, width=None):
        if width is None:
            width = self.heightmap_width
        if heightmap is None:
            heightmap = self.heightmap
        if atmosphere is None:
            atmosphere = self.atmosphere
        if circle_mask is None:
            circle_mask = self.circle_mask

        terrain_color = int(libtcod.heightmap_get_value(heightmap, ((x+terrain_rotation) % width), y))
        if terrain_color > 255:
            terrain_color = 255
        r = self.height_colormap[terrain_color][0]
        g = self.height_colormap[terrain_color][1]
        b = self.height_colormap[terrain_color][2]
        if self.atmosphere:
            cloud_cover = libtcod.heightmap_get_value(atmosphere, ((x+atmosphere_rotation) % width), y)
            r, g, b = self.blend_colors(r, g, b, 255, 255, 255, cloud_cover)
        if circle_mask[x][y] < 1.0:
            r, g, b = self.blend_colors(r, g, b, 0, 0, 0, circle_mask[x][y])
        return [r, g, b]

    def draw(self):
        feature_left         = self.sector_position_x - (self.width / 2)
        feature_top          = self.sector_position_y + (self.width / 2)
        feature_right        = feature_left + self.width
        feature_bottom       = feature_top  + self.height

        startingx = int(feature_left - math.floor(self.sector.visible_space_left))
        startingy = int(feature_top  - math.floor(self.sector.visible_space_bottom))
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
                if self.selected:
                    if ((y==startingy or y==endingy+1) and (x>endingx-5 or x<startingx+4)) or ((x==startingx or x==endingx-1) and (y>startingy-4 or y<endingy+5)):
                        self.sector.buffer.set(x, self.sector.mirror_y_coordinate(y), 0, 255, 0, 0, 255, 0, ord(' ') )

                if self.circle_mask[maskx][masky]:
                    if self.planet_class == 'star':
                        r, g, b = self.blend_layers(maskx, masky)
                    else:
                        r, g, b = self.sprite[maskx][masky][0], self.sprite[maskx][masky][1], self.sprite[maskx][masky][2]
                        # r, g, b = self.blend_layers(maskx, masky, terrain_rotation=self.terrain_rotation_index, atmosphere_rotation=self.atmosphere_rotation_index)

                    self.sector.buffer.set(x, self.sector.mirror_y_coordinate(y), r, g, b, r, g, b, ord(' ') )
                maskx += 1
            maskx = start_maskx
            masky += 1

        if self.planet_class == 'star':
            self.height_colormap.rotate(1)
        # else:
        #     t = time.clock()
        #     if t > self.last_terrain_rotation + 5.0:
        #         self.last_terrain_rotation = t
        #         self.terrain_rotation_index += 1
        #         if self.terrain_rotation_index >= self.heightmap_width:
        #             self.terrain_rotation_index = 0

        #     if t > self.last_atmosphere_rotation + 1.0:
        #         self.last_atmosphere_rotation = t
        #         self.atmosphere_rotation_index += 1
        #         if self.atmosphere_rotation_index >= self.heightmap_width:
        #             self.atmosphere_rotation_index = 0

    def render_detail(self):
        startingx = (self.sector.screen_width / 3) - (self.detail_width / 2)
        startingy = (self.sector.screen_height / 2) + (self.detail_width / 2)
        endingx   = startingx + self.detail_width
        endingy   = startingy - self.detail_width

        diffx = 0 - startingx
        startingx = max([0, startingx])

        diffy = abs(self.sector.screen_height-1 - startingy)
        startingy = min([self.sector.screen_height-1,  startingy])

        endingx = min([self.sector.screen_width, endingx])
        endingy = max([-1, endingy])

        start_maskx = 0
        if startingx == 0:
            start_maskx += diffx
        maskx = start_maskx

        start_masky = 0
        if startingy == self.sector.screen_height-1:
            start_masky += diffy
        masky = start_masky

        for y in range(startingy, endingy, -1):
            for x in range(startingx, endingx):
                if self.detail_circle_mask[maskx][masky]:
                    if self.planet_class == 'star':
                        r, g, b = self.blend_layers(maskx, masky,
                                terrain_rotation=0,
                                atmosphere_rotation=0,
                                circle_mask=self.detail_circle_mask,
                                heightmap=self.detail_heightmap,
                                atmosphere=self.detail_atmosphere,
                                width=self.detail_heightmap_width)
                    else:
                        r, g, b = self.blend_layers(maskx, masky,
                                terrain_rotation=self.terrain_rotation_index,
                                atmosphere_rotation=self.atmosphere_rotation_index,
                                circle_mask=self.detail_circle_mask,
                                heightmap=self.detail_heightmap,
                                atmosphere=self.detail_atmosphere,
                                width=self.detail_heightmap_width)

                    self.sector.buffer.set(x, self.sector.mirror_y_coordinate(y), r, g, b, r, g, b, ord(' ') )
                maskx += 1
            maskx = start_maskx
            masky += 1

        if self.planet_class == 'star':
            self.height_colormap.rotate(1)
        else:
            t = time.clock()
            if t > self.last_terrain_rotation + 1.0:
                self.last_terrain_rotation = t
                self.terrain_rotation_index += 1
                if self.terrain_rotation_index >= self.detail_heightmap_width:
                    self.terrain_rotation_index = 0

            if t > self.last_atmosphere_rotation + 0.2:
                self.last_atmosphere_rotation = t
                self.atmosphere_rotation_index += 1
                if self.atmosphere_rotation_index >= self.detail_heightmap_width:
                    self.atmosphere_rotation_index = 0

