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
        self.hp = self.width * 50
        self.velocity = random.random() / 10.0
        self.angle = random.randrange(359)
        self.distance_to_star = math.sqrt(self.sector_position_x**2 + self.sector_position_y**2)
        self.sector_position_x = math.cos(math.radians(self.angle)) * self.distance_to_star
        self.sector_position_y = math.sin(math.radians(self.angle)) * self.distance_to_star

    def check_for_collision(self):
        for p in self.sector.particles:
            if p.bullet:
                # pp("x: {} < {} < {}".format(self.sector_position_x, p.sector_position_x, self.sector_position_x+self.width))
                # pp("y: {} < {} < {}".format(self.sector_position_y, p.sector_position_y, self.sector_position_y+self.width))
                if self.sector_position_x < p.sector_position_x < self.sector_position_x+self.width and \
                   self.sector_position_y < p.sector_position_y < self.sector_position_y+self.width:
                    self.hp -= p.damage
                    if self.hp < 0:
                        for a in range(0, random.randrange(5, 15)):
                            self.sector.add_particle(
                                ExplosionFireBall(
                                    sector               = self.sector,
                                    x                    = p.x,
                                    y                    = p.y,
                                    sector_position_x    = p.sector_position_x,
                                    sector_position_y    = p.sector_position_y,
                                    angle                = random.randrange(0, 359),
                                    velocity             = random.random() * random.randrange(0,3)))
                        #TODO delete this asteroid
                    else:
                        self.sector.add_particle(
                            Fire(
                                sector               = self.sector,
                                x                    = p.x,
                                y                    = p.y,
                                sector_position_x    = p.sector_position_x,
                                sector_position_y    = p.sector_position_y))
                    # delete the bullet that hit
                    self.sector.particles.remove(p)

    def update_position(self):
        if self.velocity > 0.0:
            self.angle += self.velocity
            if self.angle >= 360.0:
                self.angle = 0.0
            self.sector_position_x = math.cos(math.radians(self.angle)) * self.distance_to_star
            self.sector_position_y = math.sin(math.radians(self.angle)) * self.distance_to_star

    def draw(self):
        self.check_for_collision()
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

        t = time.clock()
        if t > self.last_terrain_rotation + 0.5:
            self.last_terrain_rotation = t
            self.terrain_rotation_index += 1
            if self.terrain_rotation_index >= self.heightmap_width:
                self.terrain_rotation_index = 0

