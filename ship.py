import libtcodpy as libtcod
import math
import pprint
pp = pprint.PrettyPrinter(indent=4, width=200).pprint

from particle import Particle, ThrustExhaust, BlueBullet
from ship_editor import ShipEditor

class Ship:
    sprite_index_heading = [a for a in range(0, 360, 10)]

    def __init__(self, sector, posx=0.0, posy=0.0):
        self.sector = sector
        self.x = (self.sector.screen_width / 2) - 8
        self.y = (self.sector.screen_height / 2) - 8
        self.center_point = [self.x + 8, self.y + 8]

        self.sector_position_x = posx
        self.sector_position_y = posy

        self.deltav = 0.05
        self.turn_rate = math.radians(10.0)
        self.speed_limit = 6.0

        self.twopi = 2 * math.pi
        self.max_heading = self.twopi - self.turn_rate

        self.velocity_angle = 0.0
        self.velocity_angle_opposite = 180.0
        self.heading = 0.0
        self.velocity = 0.0
        self.velocity_component_x = 0.0
        self.velocity_component_y = 0.0

        self.throttle_open = False
        self.turning_left  = False
        self.turning_right = False
        self.reversing     = False
        self.laser_firing  = False

        # self.ship = [libtcod.image_load('images/ship_{0}.png'.format(str(angle).zfill(3))) for angle in range(0, 360, 10)]
        self.load_ship_sprites()

    def icon(self, angle=None):
        if not angle:
            angle = self.heading
        if 0 <= angle < 0.39269908169872414 or 5.8904862254808625 <= angle < 6.283185307179586:
            return 173
        elif 0.39269908169872414 <= angle < 1.1780972450961724:
            return 168
        elif 1.1780972450961724 <= angle < 1.9634954084936207:
            return 170
        elif 1.9634954084936207 <= angle < 2.748893571891069:
            return 167
        elif 2.748893571891069 <= angle < 3.5342917352885173:
            return 172
        elif 3.5342917352885173 <= angle < 4.319689898685966:
            return 166
        elif 4.319689898685966 <= angle < 5.105088062083414:
            return 171
        elif 5.105088062083414 <= angle < 5.8904862254808625:
            return 169
        else:
            return ord('>')

    def load_ship_sprites(self):
        ship_editor = ShipEditor()
        ship_editor.generate_random_ship()
        self.ship_value = ship_editor.ship_value

        self.ship = []
        for angle in range(0, 360, 10):
            self.ship.append( ship_editor.load_frame(angle) )

        self.ship2x = []
        for angle in [0, 90, 180, 270]:
            self.ship2x.append( ship_editor.load_frame(angle, hq2x=True) )

        self.engine_locations = []
        for column in range(2, 5):
            for y in range(0, ship_editor.sprite_size):
                if self.ship[0][y][column]:
                    self.engine_locations.append([column, y])
            if self.engine_locations:
                break

        # pp(self.ship[0])
        # pp(self.engine_locations)

    def turn_left(self):
        self.heading += self.turn_rate
        if self.heading > self.max_heading:
            self.heading = 0.0

    def turn_right(self):
        self.heading -= self.turn_rate
        if self.heading < 0.0:
            self.heading = self.max_heading

    def update_location(self):
        if self.velocity > 0.0:
            self.sector_position_x += self.velocity_component_x
            self.sector_position_y += self.velocity_component_y

    def apply_thrust(self):
        velocity_vectorx = math.cos(self.velocity_angle) * self.velocity
        velocity_vectory = math.sin(self.velocity_angle) * self.velocity

        x_component = math.cos(self.heading)
        y_component = math.sin(self.heading)
        deltavx = x_component * self.deltav
        deltavy = y_component * self.deltav

        newx = velocity_vectorx + deltavx
        newy = velocity_vectory + deltavy
        self.velocity_component_x = newx
        self.velocity_component_y = newy

        # print(repr((newy,newx)))

        self.velocity = math.sqrt(newx**2 + newy**2)
        try:
            self.velocity_angle = math.atan(newy / newx)
        except:
            self.velocity_angle = 0.0

        if newx > 0.0 and newy < 0.0:
            self.velocity_angle += self.twopi
        elif newx < 0.0:
            self.velocity_angle += math.pi

        if self.velocity_angle > math.pi:
            self.velocity_angle_opposite = self.velocity_angle - math.pi
        else:
            self.velocity_angle_opposite = self.velocity_angle + math.pi

        if self.velocity < self.deltav:
            self.velocity = 0.0
        elif self.velocity > self.speed_limit:
            self.velocity = self.speed_limit

        for thrust_posx, thrust_posy in self.engine_locations:
            point = [float(self.x + thrust_posx), float(self.y + thrust_posy)]
            h = math.radians(Ship.sprite_index_heading[self.current_sprite_index()])
            temp_point = [ point[0]-self.center_point[0], point[1]-self.center_point[1]]
            temp_point = [ temp_point[0]*math.cos(h)-temp_point[1]*math.sin(h) , temp_point[0]*math.sin(h)+temp_point[1]*math.cos(h) ]
            temp_point = [ temp_point[0]+self.center_point[0] , temp_point[1]+self.center_point[1] ]

            if 2.748893571891069 <= self.heading < 3.5342917352885173:
                temp_point[0] -= 1.0
                temp_point[1] -= 1.0
            elif 1.1780972450961724 <= self.heading < 1.9634954084936207:
                temp_point[0] -= 1.0

            self.sector.add_particle(
                ThrustExhaust(
                    sector               = self.sector,
                    x                    = int(math.floor(temp_point[0])),
                    y                    = int(math.floor(temp_point[1])),
                    # x                    = self.x+3+x_component*-2,
                    # y                    = self.y+4+y_component*-2,
                    velocity             = 1.0,
                    angle                = self.heading - math.pi if self.heading > math.pi else self.heading + math.pi,
                    velocity_component_x = newx,
                    velocity_component_y = newy)
            )

    def reverse_direction(self):
        if self.velocity > 0.0:
            if not (self.velocity_angle_opposite - self.turn_rate*0.9) < self.heading < (self.velocity_angle_opposite + self.turn_rate*0.9):
                if self.heading > self.velocity_angle_opposite or self.heading < self.velocity_angle:
                    self.turn_right()
                else:
                    self.turn_left()

    def dead_stop(self):
        if self.velocity > 0.0:
            self.velocity = 0.0
            self.velocity_component_x = 0.0
            self.velocity_component_y = 0.0

    def face_system_center(self):
        try:
            a = math.acos((self.sector_position_x * 1 +
                self.sector_position_y * 0) / math.sqrt(self.sector_position_x**2 + self.sector_position_y**2))
        except:
            a = 0.0
        if self.sector_position_y < 0:
            a = (2*math.pi - a)

        self.heading = a

    def about_face(self):
        if self.velocity > 0.0:
            self.velocity_angle, self.velocity_angle_opposite = self.velocity_angle_opposite, self.velocity_angle
            self.velocity_component_x *= -1.0
            self.velocity_component_y *= -1.0
            if self.heading < math.pi:
                self.heading += math.pi
            else:
                self.heading -= math.pi

    def current_sprite_index(self):
        sprite_index = int(round(math.degrees(self.heading), -1)/10)
        if sprite_index > 35 or sprite_index < 0:
            sprite_index = 0
        return sprite_index

    def draw(self, startx=None, starty=None, hq2x=False):
        ship = self.ship[ self.current_sprite_index() ]
        if hq2x:
            ship = self.ship2x[int((self.current_sprite_index()*10)/90)]

        if not startx or not starty:
            startx = self.x
            starty = self.y

        self.update_location()

        for y, line in enumerate(ship):
            for x, cell in enumerate(line):
                if cell != None:
                    b = cell[0]
                    f = cell[1]
                    c = cell[2]
                    b = self.sector.buffer.get_back(startx + x, starty + y)
                    self.sector.buffer.set(startx + x, starty + y, b[0], b[1], b[2], f[0], f[1], f[2], c)

    def fire_laser(self):
        x_component = math.cos(self.heading)
        y_component = math.sin(self.heading)
        self.sector.add_particle(
            BlueBullet(
                sector               = self.sector,
                x                    = self.x+8+x_component*3,
                y                    = self.y+8+y_component*3,
                sector_position_x    = self.sector_position_x+3+x_component*3,
                sector_position_y    = self.sector_position_y+4+y_component*3,
                # velocity             = 1.0,
                angle                = self.heading,
                velocity_component_x = self.velocity_component_x,
                velocity_component_y = self.velocity_component_y
            )
        )

    def draw_target_arrow(self, angle):
        startx = self.center_point[0] + 10
        starty = self.center_point[1]

        temp_point = startx-self.center_point[0] , starty-self.center_point[1]
        temp_point = [ temp_point[0]*math.cos(-angle)-temp_point[1]*math.sin(-angle) , temp_point[0]*math.sin(-angle)+temp_point[1]*math.cos(-angle) ]
        temp_point = int(temp_point[0]+self.center_point[0]) , int(temp_point[1]+self.center_point[1])

        b = self.sector.buffer.get_back(temp_point[0], temp_point[1])
        self.sector.buffer.set(temp_point[0], temp_point[1], b[0], b[1], b[2], 0, 255, 0, self.icon(angle))

