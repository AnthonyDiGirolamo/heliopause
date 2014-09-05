import libtcodpy as libtcod
import math
import pprint
pp = pprint.PrettyPrinter(indent=4, width=200).pprint

from particle import Particle, ThrustExhaust, BlueBullet

class Ship:
    def __init__(self, sector, posx=0.0, posy=0.0):
        self.sector = sector
        self.x = (self.sector.screen_width / 2) - 4
        self.y = (self.sector.screen_height / 2) - 4

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
        self.load_pointer_sprites()

    def icon(self):
        if 0 <= self.heading < 0.39269908169872414 or 5.8904862254808625 <= self.heading < 6.283185307179586:
            return 173
        elif 0.39269908169872414 <= self.heading < 1.1780972450961724:
            return 168
        elif 1.1780972450961724 <= self.heading < 1.9634954084936207:
            return 170
        elif 1.9634954084936207 <= self.heading < 2.748893571891069:
            return 167
        elif 2.748893571891069 <= self.heading < 3.5342917352885173:
            return 172
        elif 3.5342917352885173 <= self.heading < 4.319689898685966:
            return 166
        elif 4.319689898685966 <= self.heading < 5.105088062083414:
            return 171
        elif 5.105088062083414 <= self.heading < 5.8904862254808625:
            return 169
        else:
            return ord('>')

    def load_ship_sprites(self):
        sprite_size = 16
        console = libtcod.console_new(sprite_size, sprite_size)
        self.ship = []
        color_masks = [[0, 0, 255], [68,68,196], [66,66,193]]
        for angle in range(0, 360, 10):
            ship = libtcod.image_load('images/ship_{0}.png'.format(str(angle).zfill(3)))
            # libtcod.image_blit(ship, console, 8, 8, libtcod.BKGND_SET, 1.0, 1.0, 0)
            # libtcod.image_blit_rect(ship, console, 0, 0, -1, -1, libtcod.BKGND_SET)
            libtcod.image_blit_2x(ship, console, 0, 0)
            frame = []
            for y in range(0, sprite_size):
                row = []
                for x in range(0, sprite_size):
                    b = libtcod.console_get_char_background(console,x,y)
                    f = libtcod.console_get_char_foreground(console,x,y)
                    c = libtcod.console_get_char(console,x,y)
                    if c == 32:
                        f = b
                        c = 219
                    if [b[0], b[1], b[2]] in color_masks or [f[0], f[1], f[2]] in color_masks:
                        row.append( None )
                    elif [b[0], b[1], b[2]] == [0,0,0] and [f[0], f[1], f[2]] == [0,0,0]:
                        row.append( None )
                    else:
                        row.append( [b, f, c] )
                frame.append(row)
            self.ship.append(frame)

        libtcod.console_delete(console)

    def load_pointer_sprites(self):
        console = libtcod.console_new(32, 32)
        self.pointer = []
        color_masks = [[0, 0, 255], [68,68,196], [66,66,193]]
        for angle in range(0, 360, 10):
            pointer = libtcod.image_load('images/pointer_{0}.png'.format(str(angle).zfill(3)))
            # libtcod.image_blit(ship, console, 8, 8, libtcod.BKGND_SET, 1.0, 1.0, 0)
            # libtcod.image_blit_rect(ship, console, 0, 0, -1, -1, libtcod.BKGND_SET)
            libtcod.image_blit_2x(pointer, console, 0, 0)
            frame = []
            for y in range(0, 32):
                row = []
                for x in range(0, 32):
                    b = libtcod.console_get_char_background(console,x,y)
                    f = libtcod.console_get_char_foreground(console,x,y)
                    c = libtcod.console_get_char(console,x,y)
                    if c == 32:
                        f = b
                        c = 219
                    if [b[0], b[1], b[2]] in color_masks or [f[0], f[1], f[2]] in color_masks:
                        row.append( None )
                    elif [b[0], b[1], b[2]] == [0,0,0] and [f[0], f[1], f[2]] == [0,0,0]:
                        row.append( None )
                    else:
                        row.append( [b, f, c] )
                frame.append(row)
            self.pointer.append(frame)
        libtcod.console_delete(console)

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

        self.sector.add_particle(
            ThrustExhaust(
                sector               = self.sector,
                x                    = self.x+3+x_component*-2,
                y                    = self.y+4+y_component*-2,
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

    def about_face(self):
        if self.velocity > 0.0:
            self.velocity_angle, self.velocity_angle_opposite = self.velocity_angle_opposite, self.velocity_angle
            self.velocity_component_x *= -1.0
            self.velocity_component_y *= -1.0
            if self.heading < math.pi:
                self.heading += math.pi
            else:
                self.heading -= math.pi

    # \--,
    #  \  \--,
    #   \     \----,
    #    \          \---,
    #     X              ----
    #    /          /---`
    #   /     /----`
    #  /  /--`
    # /--`

    def draw(self):
        sprite_index = int(round(math.degrees(self.heading), -1)/10)
        if sprite_index > 35 or sprite_index < 0:
            sprite_index = 0

        ship = self.ship[sprite_index]

        self.update_location()

        threshold = 120*3
        # threshold = 0

        for y, line in enumerate(ship):
            for x, cell in enumerate(line):
                if cell != None:
                    b = cell[0]
                    f = cell[1]
                    c = cell[2]
                    if b[0] + b[1] + b[2] <= threshold:
                        b = self.sector.buffer.get_back(self.x + x, self.y + y)
                    if f[0] + f[1] + f[2] <= threshold:
                        f = self.sector.buffer.get_back(self.x + x, self.y + y)

                    self.sector.buffer.set(self.x + x, self.y + y, b[0], b[1], b[2], f[0], f[1], f[2], c)
                    # self.sector.buffer.set_fore(self.x + x, self.y + y, f[0], f[1], f[2], c)

    def fire_laser(self):
        x_component = math.cos(self.heading)
        y_component = math.sin(self.heading)
        self.sector.add_particle(
            BlueBullet(
                sector               = self.sector,
                x                    = self.x+3+x_component*3,
                y                    = self.y+4+y_component*3,
                velocity             = 3.0,
                angle                = self.heading,
                velocity_component_x = self.velocity_component_x,
                velocity_component_y = self.velocity_component_y
            )
        )

    def draw_target_arrow(self, angle):
        sprite_index = int(round(math.degrees(angle), -1)/10)
        if sprite_index > 35 or sprite_index < 0:
            sprite_index = 0

        pointer = self.pointer[sprite_index]
        startx = self.x-4
        starty = self.y-4

        for y, line in enumerate(pointer):
            for x, cell in enumerate(line):
                if cell != None:
                    b = cell[0]
                    f = cell[1]
                    c = cell[2]
                    self.sector.buffer.set(startx + x, starty + y, b[0], b[1], b[2], f[0], f[1], f[2], c)
