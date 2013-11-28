import libtcodpy as libtcod
import math
import pprint
pp = pprint.PrettyPrinter(indent=4, width=200).pprint

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
        self.add_planet(planet_class='star',   position_x=-50, position_y=0, diameter=30)
        self.add_planet(planet_class='terran', position_x=-17,   position_y=0, diameter=30)
        self.add_planet(planet_class='terran', position_x=30,  position_y=0, diameter=60)

        self.planet_distances = [None for p in self.planets]

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

    def update_planet_distances(self, shipx, shipy):
        self.planet_distances = [ math.sqrt((shipx - planet.sector_position_x)**2.0 + (shipy - planet.sector_position_y)**2.0) for planet in self.planets]

    def closest_planet(self, shipx, shipy):
        self.update_planet_distances(shipx, shipy)
        nearest_planet_index = 0
        smallest_distance = None
        for index, distance in enumerate(self.planet_distances):
            if smallest_distance is None or distance < smallest_distance:
                nearest_planet_index = index
                smallest_distance = distance
        return [nearest_planet_index, smallest_distance]

    def land_at_closest_planet(self, ship):
        landed = False
        message = None
        index, distance = self.closest_planet(ship.sector_position_x, ship.sector_position_y)
        planet = self.planets[index]
        if distance < 1.25*(planet.width/2.0):
            for p in self.planets:
                p.selected = False
            planet.selected = True
            if ship.velocity > 0.30:
                message = "{0} you are moving to fast to land at this planet".format(distance)
            else:
                message = "{0} landed".format(distance)
                landed = True
        else:
            message = "{0} there isn't a planet in landing range".format(distance)
        if landed:
            ship.velocity = 0.0
        return [landed, message]

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

