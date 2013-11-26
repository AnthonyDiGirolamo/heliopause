import pprint
pp = pprint.PrettyPrinter(indent=4, width=200).pprint
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
        self.rotation_index = 0

        # Earthlike colormap
        self.colormap = libtcod.color_gen_map(
            [ libtcod.Color(10,10,40), libtcod.Color(30,30,170),
              libtcod.Color(114, 150, 71), libtcod.Color(80,120,10),
              libtcod.Color(17,109,7), libtcod.Color(120,220,120),
              libtcod.Color(208,208,239), libtcod.Color(255,255,255)],
            [ 0, 30, 34, 80, 90, 200, 210, 255]
        )
        self.heightmap_width = self.width * 2 + 1
        self.heightmap_height = self.height + 1
        self.build_circle_mask()
        self.build_heightmap()

    def addHill(self, hm,nbHill,baseRadius,radiusVar,height) :
        for i in range(nbHill) :
            hillMinRadius=baseRadius*(1.0-radiusVar)
            hillMaxRadius=baseRadius*(1.0+radiusVar)
            radius = libtcod.random_get_float(self.rnd,hillMinRadius, hillMaxRadius)
            theta = libtcod.random_get_float(self.rnd,0.0, 6.283185) # between 0 and 2Pi
            dist = libtcod.random_get_float(self.rnd,0.0, float(min(self.heightmap_width,self.heightmap_height))/2 - radius)
            xh = int(self.heightmap_width/2 + math.cos(theta) * dist)
            yh = int(self.heightmap_height/2 + math.sin(theta) * dist)
            libtcod.heightmap_add_hill(hm,float(xh),float(yh),radius,height)

    def build_heightmap(self):
        # self.rnd=libtcod.random_new_from_seed(1094911894)
        self.rnd=libtcod.random_get_instance()
        # 3x3 kernel for smoothing operations
        smoothKernelSize=9
        smoothKernelDx=[-1,0,1,-1,0,1,-1,0,1]
        smoothKernelDy=[-1,-1,-1,0,0,0,1,1,1]
        smoothKernelWeight=[1.0,2.0,1.0,2.0,20.0,2.0,1.0,2.0,1.0]

        hm=libtcod.heightmap_new(self.heightmap_width, self.heightmap_height)
        coef=[0.11,0.22,-0.22,0.18,]
        tmp =libtcod.heightmap_new(self.heightmap_width, self.heightmap_height)
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
        circle_mask = []
        for y in range(radius, -radius-1, -1):
            col = []
            for x in range(-radius, radius+1):
                if float(x)**2.0 + float(y)**2.0 < float(radius)**2.0:
                    col.append(1)
                else:
                    col.append(0)
            circle_mask.append(col)

        self.circle_mask = []
        for y, row in enumerate(circle_mask):
            col = []
            for x, cell in enumerate(row):
                if x > 0 and y > 0 and x < len(row)-1 and y < len(circle_mask) - 1:
                    cell_sum = circle_mask[x-1][y-1] + circle_mask[x][y-1] + circle_mask[x+1][y-1] + circle_mask[x-1][y] + circle_mask[x][y] + circle_mask[x+1][y] + circle_mask[x-1][y+1] + circle_mask[x][y+1] + circle_mask[x+1][y+1]
                    if cell_sum <= 7 and cell_sum > 4:
                        col.append(2)
                    elif cell_sum > 6:
                        col.append(1)
                    else:
                        col.append(0)
                else:
                    col.append(0)
            self.circle_mask.append(col)
        # pp(self.circle_mask)

    def blend_colors(self, r1, g1, b1, r2, g2, b2, alpha):
        return ( int(alpha * r1 + (1-alpha) * r2),
                 int(alpha * g1 + (1-alpha) * g2),
                 int(alpha * b1 + (1-alpha) * b2) )

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

        maskx = 0
        if startingx == 0:
            maskx += self.width - endingx
        start_masky = 0
        if startingy == self.sector.screen_height-1:
            start_masky += self.height - (startingy - endingy)
        masky = start_masky
        for x in range(startingx, endingx):
            for y in range(startingy, endingy, -1):
                if self.circle_mask[maskx][masky]:
                    color = int(libtcod.heightmap_get_value(self.heightmap, maskx+self.rotation_index, masky))
                    if color > 255:
                        color = 255

                    r = self.colormap[color][0]
                    g = self.colormap[color][1]
                    b = self.colormap[color][2]
                    if self.circle_mask[maskx][masky] == 2:
                        r, g, b = self.blend_colors(r, g, b, 0, 0, 0, 0.5)

                    self.sector.buffer.set(x, self.sector.mirror_y_coordinate(y), r, g, b, r, g, b, ord('@') )
                    # 128, 255, 128, ord('@') )
                masky += 1
            masky = start_masky
            maskx += 1

        # self.rotation_index += 1
        # if self.rotation_index > self.width*2:
        #     self.rotation_index = 0

