import math

class Particle:
    def __init__(self, x, y, particle_type, index, colormap, charactermap, velocity=0.0, angle=0.0,
            velocity_component_x=0.0, velocity_component_y=0.0):
        self.x = x
        self.y = y
        self.sector_position_x = 0.0
        self.sector_position_y = 0.0
        self.velocity = velocity
        self.angle = angle
        self.particle_type = particle_type
        self.index = index
        self.colormap = colormap
        self.charactermap = charactermap
        self.valid = True
        self.velocity_component_x = velocity_component_x
        self.velocity_component_y = velocity_component_y

    def update_position(self):
        if self.velocity > 0.0:
            self.x += math.cos(self.angle) * self.velocity
            self.y += math.sin(self.angle) * self.velocity

        self.x += self.velocity_component_x
        self.y += self.velocity_component_y

        self.sector_position_x += self.velocity_component_x
        self.sector_position_y += self.velocity_component_y

