import math
import libtcodpy as libtcod

class Particle(object):
    def __init__(self, sector, x, y, sector_position_x=0.0, sector_position_y=0.0, velocity=0.0, angle=0.0, velocity_component_x=0.0, velocity_component_y=0.0):
        self.sector = sector
        self.x = x
        self.y = y
        self.sector_position_x = sector_position_x
        self.sector_position_y = sector_position_y
        self.velocity = velocity
        self.angle = angle
        self.valid = True
        self.velocity_component_x = velocity_component_x
        self.velocity_component_y = velocity_component_y

    def update_position(self):
        if self.velocity > 0.0:
            dx = math.cos(self.angle) * self.velocity
            dy = math.sin(self.angle) * self.velocity
            self.sector_position_x += dx
            self.sector_position_y += dy
            self.x += dx
            self.y += dy

        self.x += self.velocity_component_x
        self.y += self.velocity_component_y

        self.sector_position_x += self.velocity_component_x
        self.sector_position_y += self.velocity_component_y

    def draw(self):
        if self.valid:
            x = int(round(self.x))
            y = int(round(self.y))
            if x < 0 or \
               x > self.sector.screen_width-1 or \
               y < 0 or \
               y > self.sector.screen_height-1:
                self.valid = False
            else:
                self.draw_sprite(x, y)

    # def draw_sprite(self, x, y):
    #     color = self.colormap[self.index]
    #     character = self.charactermap[self.index]
    #     self.sector.buffer.set_fore(x, self.sector.mirror_y_coordinate(y),   color[0], color[1], color[2], character)


class ThrustExhaust(Particle):
    def __init__(self, **kwargs):
        self.bullet = False
        self.particle_type = 'thrust'
        self.index = 9
        self.colormap = libtcod.color_gen_map(
            [ kwargs.get('sector').background, libtcod.Color(255, 144, 0),  libtcod.Color(255, 222, 0) ],
            [ 0,                               self.index/2,                self.index] )
        self.charactermap = [176, 176, 176, 177, 177, 178, 178, 219, 219, 219]
        super(ThrustExhaust, self).__init__(**kwargs)

    def draw_sprite(self, x, y):
        color = self.colormap[self.index]
        character = self.charactermap[self.index]
        self.sector.buffer.set_fore(x,   self.sector.mirror_y_coordinate(y),   color[0], color[1], color[2], character)
        self.sector.buffer.set_fore(x,   self.sector.mirror_y_coordinate(y-1), color[0], color[1], color[2], character)
        self.sector.buffer.set_fore(x+1, self.sector.mirror_y_coordinate(y),   color[0], color[1], color[2], character)
        self.sector.buffer.set_fore(x+1, self.sector.mirror_y_coordinate(y-1), color[0], color[1], color[2], character)


class BlueBullet(Particle):
    def __init__(self, **kwargs):
        self.damage = 10
        self.bullet = True
        self.particle_type = 'bullet'
        self.index = 20
        self.colormap = libtcod.color_gen_map(
            [ libtcod.Color(0, 144, 255),  libtcod.Color(0, 222, 255) ],
            [ 0,                           self.index ] )
        self.charactermap = [4 for i in range(0, self.index+1)]
        super(BlueBullet, self).__init__(velocity=2.0, **kwargs)

    def draw_sprite(self, x, y):
        color = self.colormap[self.index]
        character = self.charactermap[self.index]
        self.sector.buffer.set_fore(x, self.sector.mirror_y_coordinate(y),   color[0], color[1], color[2], character)

class ExplosionFireBall(Particle):
    def __init__(self, **kwargs):
        self.bullet = False
        self.particle_type = 'explosion_fire_ball'
        self.index = 7
        self.colormap = libtcod.color_gen_map(
            [ kwargs.get('sector').background, libtcod.Color(255, 128, 128),  libtcod.Color(255, 222, 222) ],
            [ 0,                               self.index/2,                self.index] )
        self.charactermap = [176, 176, 177, 177, 178, 178, 219, 219, 219]
        super(ExplosionFireBall, self).__init__(**kwargs)

    def draw_sprite(self, x, y):
        i = self.index if self.index > 0 else 0
        color = self.colormap[i]
        character = self.charactermap[i]
        self.sector.buffer.set_fore(x,   self.sector.mirror_y_coordinate(y),   color[0], color[1], color[2], character)
        self.sector.buffer.set_fore(x,   self.sector.mirror_y_coordinate(y-1), color[0], color[1], color[2], character)
        self.sector.buffer.set_fore(x,   self.sector.mirror_y_coordinate(y+1), color[0], color[1], color[2], character)
        self.sector.buffer.set_fore(x+1, self.sector.mirror_y_coordinate(y),   color[0], color[1], color[2], character)
        self.sector.buffer.set_fore(x-1, self.sector.mirror_y_coordinate(y), color[0], color[1], color[2], character)

