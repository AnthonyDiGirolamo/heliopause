import libtcodpy as libtcod
import math
from random import randrange
import time
import pprint
pp = pprint.PrettyPrinter(indent=4, width=200).pprint

from planet import Planet
from asteroid import Asteroid


class Sector:
    def __init__(self, screen_width, screen_height, buffer, background=libtcod.Color(0,0,0)):
        self.twopi = 2 * math.pi
        self.background = background
        # self.background = libtcod.Color(32,32,64)

        self.buffer = buffer
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.visible_space_left   = 0
        self.visible_space_top    = 0
        self.visible_space_right  = 0
        self.visible_space_bottom = 0

        self.planets = []
        self.asteroids = []

        self.particles = []

        self.selected_planet = None
        self.selected_asteroid = None
        self.selected_blink = 0

    def mirror_y_coordinate(self, y):
        return (self.screen_height- 1 - y)

    def add_planet(self, **keyword_args):
        self.planets.append(Planet(sector=self, **keyword_args))
        self.planet_distances = [None for p in self.planets]
        return [self.planets[-1].icon, self.planets[-1].icon_color, len(self.planets)]

    def add_asteroid(self, **keyword_args):
        self.asteroids.append(Asteroid(sector=self, **keyword_args))
        self.asteroid_distances = [None for p in self.asteroids]
        return [self.asteroids[-1].icon, self.asteroids[-1].icon_color, len(self.asteroids)]

    def update_visibility(self, player_sector_position_x, player_sector_position_y):
        self.visible_space_left   = player_sector_position_x - self.screen_width/2
        self.visible_space_top    = player_sector_position_y + self.screen_height/2
        self.visible_space_right  = self.visible_space_left + self.screen_width
        self.visible_space_bottom = self.visible_space_top - self.screen_height

    def clear_selected_planet(self):
        self.selected_planet = None

    def distance_from_center(self, ship):
        return math.sqrt(ship.sector_position_x**2 + ship.sector_position_y**2)

    def update_selected_planet_distance(self, ship):
        planet = self.get_selected_planet()
        if self.selected_planet is not None:
            self.planet_distances[self.selected_planet] = math.sqrt((ship.sector_position_x - planet.sector_position_x)**2.0 + (ship.sector_position_y - planet.sector_position_y)**2.0)
        elif self.selected_asteroid is not None:
            self.asteroid_distances[self.selected_asteroid] = math.sqrt((ship.sector_position_x - planet.sector_position_x)**2.0 + (ship.sector_position_y - planet.sector_position_y)**2.0)

        newx = planet.sector_position_x - ship.sector_position_x
        newy = planet.sector_position_y - ship.sector_position_y
        try:
            self.selected_planet_angle = math.atan(newy / newx)
        except:
            self.selected_planet_angle = 0.0

        if newx > 0.0 and newy < 0.0:
            self.selected_planet_angle += self.twopi
        elif newx < 0.0:
            self.selected_planet_angle += math.pi

    def get_selected_planet(self):
        if self.selected_planet is not None:
            return self.planets[self.selected_planet]
        elif self.selected_asteroid is not None:
            return self.asteroids[self.selected_asteroid]

    def selected_planet_distance(self):
        if self.selected_planet is not None:
            return self.planet_distances[self.selected_planet]
        elif self.selected_asteroid is not None:
            return self.asteroid_distances[self.selected_asteroid]

    def update_all_planet_distances(self, ship):
        self.planet_distances = [ math.sqrt((ship.sector_position_x - planet.sector_position_x)**2.0 + (ship.sector_position_y - planet.sector_position_y)**2.0) for planet in self.planets]
        self.asteroid_distances = [ math.sqrt((ship.sector_position_x - asteroid.sector_position_x)**2.0 + (ship.sector_position_y - asteroid.sector_position_y)**2.0) for asteroid in self.asteroids]

    def closest_planet(self, ship):
        self.update_all_planet_distances(ship)
        nearest_planet_index = 0
        smallest_distance = None
        for index, distance in enumerate(self.planet_distances):
            if smallest_distance is None or distance < smallest_distance:
                nearest_planet_index = index
                smallest_distance = distance
        return [nearest_planet_index, smallest_distance]

    def closest_asteroid(self, ship):
        self.update_all_planet_distances(ship)
        nearest_asteroid_index = 0
        smallest_distance = None
        for index, distance in enumerate(self.asteroid_distances):
            if smallest_distance is None or distance < smallest_distance:
                nearest_asteroid_index = index
                smallest_distance = distance
        return [nearest_asteroid_index, smallest_distance]

    def land_at_closest_planet(self, ship):
        landed = False
        message = None
        index, distance = self.closest_planet(ship)
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
        self.particles = [p for p in self.particles if p.on_screen]
        for particle in self.particles:
            if particle.on_screen:
                particle.x += deltax * 1.0
                particle.y += deltay * 1.0
                particle.index -= 1
                if particle.index < 0:
                    particle.index = 0
                    particle.on_screen = False

    def draw_minimap(self, buffer, width, height, ship):
        zoom = 1.0
        distance = 1000.0
        zoom = float(int(distance + max([ abs((ship.sector_position_x)), abs(ship.sector_position_y) ])) / int(distance))

        buffer.clear(self.background[0], self.background[1], self.background[2])

        size = int((width-3) / 2.0)
        size_reduction = (zoom*distance)/size

        for index, p in enumerate(self.asteroids + self.planets):
            x = size + 1 + int(p.sector_position_x / (size_reduction))
            y = size + 1 - int(p.sector_position_y / (size_reduction))
            if 0 < x < width-1 and 0 < y < height-1:
                buffer.set(x, y, 0, 0, 0, p.icon_color[0], p.icon_color[1], p.icon_color[2], p.icon)

        if self.selected_planet is not None:
            x = size + 1 + int(self.planets[self.selected_planet].sector_position_x / (size_reduction))
            y = size + 1 - int(self.planets[self.selected_planet].sector_position_y / (size_reduction))
            t = time.clock()
            if t > self.selected_blink + 0.5:
                if t > self.selected_blink + 1.0:
                    self.selected_blink = t
                buffer.set(x+1, y, 0, 0, 0, 0, 255, 0, 175)
                buffer.set(x-1, y, 0, 0, 0, 0, 255, 0, 174)

        x = size + 1 + int(ship.sector_position_x / (size_reduction))
        y = size + 1 - int(ship.sector_position_y / (size_reduction))
        if 0 < x < width-1 and 0 < y < height-1:
            buffer.set_fore(x, y, 255, 255, 255, ship.icon())

    def cycle_planet_target(self, ship):
        self.deselect_asteroid()

        if self.selected_planet == None:
            self.selected_planet = 0
        else:
            self.selected_planet += 1

        if self.selected_planet == len(self.planets):
            self.selected_planet = None

        if self.selected_planet is not None:
            for p in self.planets:
                p.selected = False
            self.planets[self.selected_planet].selected = True
            self.update_selected_planet_distance(ship)

    def deselect_planet(self):
        if self.selected_planet is not None:
            self.selected_planet = None
            for p in self.planets:
                p.selected = False

    def deselect_asteroid(self):
        if self.selected_asteroid is not None:
            self.selected_asteroid = None
            for p in self.asteroids:
                p.selected = False

    def cycle_target(self, ship):
        self.deselect_planet()

        if self.selected_asteroid == None:
            self.selected_asteroid = 0
        else:
            self.selected_asteroid += 1

        if self.selected_asteroid == len(self.asteroids):
            self.selected_asteroid = None

        if self.selected_asteroid is not None:
            for p in self.asteroids:
                p.selected = False
            self.asteroids[self.selected_asteroid].selected = True
            self.update_selected_planet_distance(ship)
            # self.update_selected_asteroid_distance(ship)

    def target_nearest_planet(self, ship):
        self.deselect_asteroid()
        self.selected_planet, distance = self.closest_planet(ship)
        self.planets[self.selected_planet].selected = True

    def target_nearest_asteroid(self, ship):
        self.deselect_planet()
        self.selected_asteroid, distance = self.closest_asteroid(ship)
        self.asteroids[self.selected_asteroid].selected = True

