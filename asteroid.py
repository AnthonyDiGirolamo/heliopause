import math
import time
import random
import pprint
pp = pprint.PrettyPrinter(indent=4, width=200).pprint

import libtcodpy as libtcod

from planet import Planet
from particle import Particle, Fire, ThrustExhaust, BlueBullet, ExplosionFireBall

class Asteroid(Planet):
    def __init__(self, **kwargs):
        super(Asteroid, self).__init__(**kwargs)
        self.hp = self.width * 80
        self.velocity = random.random() / 10.0
        self.angle = random.randrange(359)
        self.distance_to_star = math.sqrt(self.sector_position_x**2 + self.sector_position_y**2)
        self.sector_position_x = math.cos(math.radians(self.angle)) * self.distance_to_star
        self.sector_position_y = math.sin(math.radians(self.angle)) * self.distance_to_star

    def update_position(self):
        if self.velocity > 0.0:
            self.angle += self.velocity
            if self.angle >= 360.0:
                self.angle = 0.0
            self.sector_position_x = math.cos(math.radians(self.angle)) * self.distance_to_star
            self.sector_position_y = math.sin(math.radians(self.angle)) * self.distance_to_star

    def draw(self):
        self.update_position()

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
                if self.circle_mask[maskx][masky]:
                    r, g, b = self.blend_layers(maskx, masky, terrain_rotation=self.terrain_rotation_index)
                    self.sector.buffer.set(x, self.sector.mirror_y_coordinate(y), r, g, b, r, g, b, ord(' ') )
                maskx += 1
            maskx = start_maskx
            masky += 1

        if self.selected and startingx < endingx and endingy < startingy:
            self.sector.buffer.set_fore(startingx,   self.sector.mirror_y_coordinate(startingy),   64, 255, 64, 201)#218
            # self.sector.buffer.set_fore(startingx+1, self.sector.mirror_y_coordinate(startingy),   64, 255, 64, 196)
            # self.sector.buffer.set_fore(startingx+2, self.sector.mirror_y_coordinate(startingy),   64, 255, 64, 196)
            # self.sector.buffer.set_fore(startingx,   self.sector.mirror_y_coordinate(startingy-1), 64, 255, 64, 179)
            # self.sector.buffer.set_fore(startingx,   self.sector.mirror_y_coordinate(startingy-2), 64, 255, 64, 179)

            self.sector.buffer.set_fore(endingx-1,   self.sector.mirror_y_coordinate(endingy+1),   64, 255, 64, 188)#217
            # self.sector.buffer.set_fore(endingx-1-1, self.sector.mirror_y_coordinate(endingy+1),   64, 255, 64, 196)
            # self.sector.buffer.set_fore(endingx-1-2, self.sector.mirror_y_coordinate(endingy+1),   64, 255, 64, 196)
            # self.sector.buffer.set_fore(endingx-1,   self.sector.mirror_y_coordinate(endingy+1+1), 64, 255, 64, 179)
            # self.sector.buffer.set_fore(endingx-1,   self.sector.mirror_y_coordinate(endingy+1+2), 64, 255, 64, 179)

            self.sector.buffer.set_fore(endingx-1,   self.sector.mirror_y_coordinate(startingy),   64, 255, 64, 187)#191
            # self.sector.buffer.set_fore(endingx-1-1, self.sector.mirror_y_coordinate(startingy),   64, 255, 64, 196)
            # self.sector.buffer.set_fore(endingx-1-2, self.sector.mirror_y_coordinate(startingy),   64, 255, 64, 196)
            # self.sector.buffer.set_fore(endingx-1,   self.sector.mirror_y_coordinate(startingy-1), 64, 255, 64, 179)
            # self.sector.buffer.set_fore(endingx-1,   self.sector.mirror_y_coordinate(startingy-2), 64, 255, 64, 179)

            self.sector.buffer.set_fore(startingx,   self.sector.mirror_y_coordinate(endingy+1),   64, 255, 64, 200)#192
            # self.sector.buffer.set_fore(startingx+1, self.sector.mirror_y_coordinate(endingy+1),   64, 255, 64, 196)
            # self.sector.buffer.set_fore(startingx+2, self.sector.mirror_y_coordinate(endingy+1),   64, 255, 64, 196)
            # self.sector.buffer.set_fore(startingx,   self.sector.mirror_y_coordinate(endingy+1+1), 64, 255, 64, 179)
            # self.sector.buffer.set_fore(startingx,   self.sector.mirror_y_coordinate(endingy+1+2), 64, 255, 64, 179)

        t = time.clock()
        if t > self.last_terrain_rotation + 0.5:
            self.last_terrain_rotation = t
            self.terrain_rotation_index += 1
            if self.terrain_rotation_index >= self.heightmap_width:
                self.terrain_rotation_index = 0

