import libtcodpy as libtcod
import math

from planet import Planet


class Sector:
    def __init__(self, screen_width, screen_height, buffer):
        self.background = libtcod.Color(0,0,0)
        # self.background = libtcod.Color(32,32,64)

        self.buffer = buffer
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.visible_space_left   = 0
        self.visible_space_top    = 0
        self.visible_space_right  = 0
        self.visible_space_bottom = 0

        self.planets = []
        self.add_planet(planet_class='star', position_x=-50, position_y=15, radius=30)
        self.add_planet(planet_class='terran', position_x=0, position_y=20, radius=40)

        self.particles = []

    def mirror_y_coordinate(self, y):
        return (self.screen_height- 1 - y)

    def add_planet(self, **keyword_args):
        self.planets.append(Planet(sector=self, **keyword_args))

    def update_visibility(self, player_sector_position_x, player_sector_position_y):
        self.visible_space_left   = player_sector_position_x - self.screen_width/2
        self.visible_space_top    = player_sector_position_y + self.screen_height/2
        self.visible_space_right  = self.visible_space_left + self.screen_width
        self.visible_space_bottom = self.visible_space_top - self.screen_height

    def add_particle(self, particle):
        self.particles.append( particle )

    def update_particle_positions(self):
        for p in self.particles:
            p.update_position()

    def scroll_particles(self, heading=0.0, velocity=0.0):
        deltax = math.cos(heading) * velocity * -1
        deltay = math.sin(heading) * velocity * -1
        # remove particles which have faded
        self.particles = [p for p in self.particles if p.valid]
        for particle in self.particles:
            if particle.valid:
                particle.x += deltax * 1.0
                particle.y += deltay * 1.0
                particle.index -= 1
                if particle.index < 0:
                    particle.valid = False

