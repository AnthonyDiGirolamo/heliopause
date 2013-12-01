import libtcodpy as libtcod
import math
from random import randrange
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
        self.add_planet(planet_class='star',      position_x=0, position_y=0,       diameter=60)
        self.add_planet(planet_class='terran',    position_x=randrange(-1000,1001), position_y=randrange(-1000,1001), diameter=randrange(10, self.screen_height))
        self.add_planet(planet_class='ocean',     position_x=randrange(-1000,1001), position_y=randrange(-1000,1001), diameter=randrange(10, self.screen_height), seed=987213314)
        self.add_planet(planet_class='jungle',    position_x=randrange(-1000,1001), position_y=randrange(-1000,1001), diameter=randrange(10, self.screen_height), seed=876535609)
        self.add_planet(planet_class='lava',      position_x=randrange(-1000,1001), position_y=randrange(-1000,1001), diameter=randrange(10, self.screen_height), seed=567835322)
        self.add_planet(planet_class='tundra',    position_x=randrange(-1000,1001), position_y=randrange(-1000,1001), diameter=randrange(10, self.screen_height), seed=958492104)
        self.add_planet(planet_class='arid',      position_x=randrange(-1000,1001), position_y=randrange(-1000,1001), diameter=randrange(10, self.screen_height), seed=393859601)
        self.add_planet(planet_class='desert',    position_x=randrange(-1000,1001), position_y=randrange(-1000,1001), diameter=randrange(10, self.screen_height), seed=123753278)
        self.add_planet(planet_class='artic',     position_x=randrange(-1000,1001), position_y=randrange(-1000,1001), diameter=randrange(10, self.screen_height), seed=754367994)
        self.add_planet(planet_class='barren',    position_x=randrange(-1000,1001), position_y=randrange(-1000,1001), diameter=randrange(10, self.screen_height), seed=294958204)
        self.add_planet(planet_class='gas giant', position_x=randrange(-1000,1001), position_y=randrange(-1000,1001), diameter=randrange(10, self.screen_height), seed=294958204)

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
            if ship.velocity > 0.20:
                message = "You are moving to fast to land.".format(distance)
            else:
                landed = True
                planet.render_detail()
        else:
            message = "There isn't a planet in landing range."
        if landed:
            ship.velocity = 0.0
        return [landed, message, index]

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

    def draw_minimap(self, buffer, width, height, ship, zoom=1.0):
        buffer.clear(self.background[0], self.background[1], self.background[2])

        for p in self.planets:
            x = 11 + int(p.sector_position_x / 100.0)
            y = 11 - int(p.sector_position_y / 100.0)
            if 0 < x < width-1 and 0 < y < height-1:
                buffer.set_fore(x, y, p.icon_color[0], p.icon_color[1], p.icon_color[2], p.icon)

        x = 11 + int(ship.sector_position_x / 100.0)
        y = 11 - int(ship.sector_position_y / 100.0)
        if 0 < x < width-1 and 0 < y < height-1:
            if 0 <= ship.heading < 0.39269908169872414 or 5.8904862254808625 <= ship.heading < 6.283185307179586:
                ship_icon = 173
            elif 0.39269908169872414 <= ship.heading < 1.1780972450961724:
                ship_icon = 168
            elif 1.1780972450961724 <= ship.heading < 1.9634954084936207:
                ship_icon = 170
            elif 1.9634954084936207 <= ship.heading < 2.748893571891069:
                ship_icon = 167
            elif 2.748893571891069 <= ship.heading < 3.5342917352885173:
                ship_icon = 172
            elif 3.5342917352885173 <= ship.heading < 4.319689898685966:
                ship_icon = 166
            elif 4.319689898685966 <= ship.heading < 5.105088062083414:
                ship_icon = 171
            elif 5.105088062083414 <= ship.heading < 5.8904862254808625:
                ship_icon = 169
            else:
                ship_icon = ord('>')
            buffer.set_fore(x, y, 255, 255, 255, ship_icon)



