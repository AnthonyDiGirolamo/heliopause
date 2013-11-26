# import pprint
# pp = pprint.PrettyPrinter(indent=4, width=200).pprint
import math
from random import randrange

import libtcodpy as libtcod

class Planet:
    def __init__(self, sector):
        self.sector = sector
        self.sector_position_x = randrange(-100, 100)
        self.sector_position_y = randrange(-100, 100)
        self.width = randrange(30, 50)
        if (self.width % 2) != 0:
            self.width += 1
        self.height = self.width

        # Earthlike colormap
        self.colormap = libtcod.color_gen_map(
            [ libtcod.Color(10,10,40), libtcod.Color(40,40,170),
              libtcod.Color(114, 150, 71), libtcod.Color(80,120,10),
              libtcod.Color(17,109,7), libtcod.Color(120,220,120),
              libtcod.Color(208,208,239), libtcod.Color(255,255,255)],
            [ 0, 30, 34, 80, 90, 200, 210, 255]
        )
        self.build_circle_mask()
        self.build_heightmap()

    def addHill(self, hm,nbHill,baseRadius,radiusVar,height) :
        for i in range(nbHill) :
            hillMinRadius=baseRadius*(1.0-radiusVar)
            hillMaxRadius=baseRadius*(1.0+radiusVar)
            radius = libtcod.random_get_float(self.rnd,hillMinRadius, hillMaxRadius)
            theta = libtcod.random_get_float(self.rnd,0.0, 6.283185) # between 0 and 2Pi
            dist = libtcod.random_get_float(self.rnd,0.0, float(min(self.width,self.height))/2 - radius)
            xh = int(self.width/2 + math.cos(theta) * dist)
            yh = int(self.height/2 + math.sin(theta) * dist)
            libtcod.heightmap_add_hill(hm,float(xh),float(yh),radius,height)

    def build_heightmap(self):
        # self.rnd=libtcod.random_new_from_seed(1094911894)
        self.rnd=libtcod.random_get_instance()
        # 3x3 kernel for smoothing operations
        smoothKernelSize=9
        smoothKernelDx=[-1,0,1,-1,0,1,-1,0,1]
        smoothKernelDy=[-1,-1,-1,0,0,0,1,1,1]
        smoothKernelWeight=[1.0,2.0,1.0,2.0,20.0,2.0,1.0,2.0,1.0]

        hm=libtcod.heightmap_new(self.width,self.height)
        coef=[0.11,0.22,-0.22,0.18,]
        tmp =libtcod.heightmap_new(self.width,self.height)
        libtcod.heightmap_add_voronoi(tmp,100,4,coef,self.rnd)
        libtcod.heightmap_normalize(tmp)
        libtcod.heightmap_add_hm(hm,tmp,hm)
        libtcod.heightmap_delete(tmp)
        # self.addHill(hm,40,11.4,0.31,0.09)
        libtcod.heightmap_add(hm,-0.2)
        libtcod.heightmap_clamp(hm,0.0,1.0)
        smoothKernelWeight[4] = 20
        for i in range(2,-1,-1) :
            libtcod.heightmap_kernel_transform(hm,smoothKernelSize,smoothKernelDx,smoothKernelDy,smoothKernelWeight,0,0.86)
        libtcod.heightmap_rain_erosion(hm,1000,0.46,0.12,self.rnd)
        libtcod.heightmap_normalize(hm,0,255)
        self.heightmap = hm
        # print(repr(libtcod.heightmap_get_minmax(self.heightmap)))

    def build_circle_mask(self):
        radius = self.width / 2
        self.circle_mask = []
        for x in range(-radius, radius+1):
            col = []
            for y in range(radius, -radius-1, -1):
                if float(x)**2.0 + float(y)**2.0 < float(radius)**2.0:
                    col.append(1)
                else:
                    col.append(0)
            self.circle_mask.append(col)
        # pp(self.circle_mask)

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

        maskx = 1
        if startingx == 0:
            maskx += self.width - endingx
        start_masky = 1
        if startingy == self.sector.screen_height-1:
            start_masky += self.height - (startingy - endingy)
        masky = start_masky
        for x in range(startingx, endingx):
            for y in range(startingy, endingy, -1):
                if self.circle_mask[maskx][masky]:
                    color = int(libtcod.heightmap_get_value(self.heightmap, maskx, masky))
                    if color > 255:
                        color = 255
                    self.sector.buffer.set(x, self.sector.mirror_y_coordinate(y),
                        self.colormap[color][0], self.colormap[color][1], self.colormap[color][2],
                        self.colormap[color][0], self.colormap[color][1], self.colormap[color][2], ord('@') )
                        # 128, 255, 128, ord('@') )
                masky += 1
            masky = start_masky
            maskx += 1

