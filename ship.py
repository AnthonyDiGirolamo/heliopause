import libtcodpy as libtcod
import math

from particle import Particle

# sector_background = libtcod.Color(32,32,64)
sector_background = libtcod.Color(0,0,0)

thrust_exhaust_index = 10
thrust_exhaust_colormap = libtcod.color_gen_map(
    [ sector_background, libtcod.Color(255, 144, 0),  libtcod.Color(255, 222, 0) ],
    [ 0,                 thrust_exhaust_index/2,      thrust_exhaust_index] )
thrust_exhaust_character_map = [176, 176, 176, 177, 177, 178, 178, 219, 219, 219]

laser_index = 20
laser_colormap = libtcod.color_gen_map(
    [ libtcod.Color(0, 144, 255),  libtcod.Color(0, 222, 255) ],
    [ 0,                           laser_index] )
laser_character_map = [4 for i in range(0, laser_index+1)]

class Ship:
    def __init__(self, sector):
        self.sector = sector
        self.x = (self.sector.screen_width / 2) - 4
        self.y = (self.sector.screen_height / 2) - 4

        self.sector_position_x = 0.0
        self.sector_position_y = 0.0

        self.deltav = 0.05
        self.turn_rate = math.radians(10.0)
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

    def load_ship_sprites(self):
        console = libtcod.console_new(16, 16)
        self.ship = []
        color_masks = [[0, 0, 255], [68,68,196], [66,66,193]]
        for angle in range(0, 360, 10):
            ship = libtcod.image_load('images/ship_{0}.png'.format(str(angle).zfill(3)))
            # libtcod.image_blit(ship, console, 8, 8, libtcod.BKGND_SET, 1.0, 1.0, 0)
            # libtcod.image_blit_rect(ship, console, 0, 0, -1, -1, libtcod.BKGND_SET)
            libtcod.image_blit_2x(ship, console, 0, 0)
            frame = []
            for y in range(0, 16):
                row = []
                for x in range(0, 16):
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
        elif self.velocity > 3.0:
            self.velocity = 3.0

        self.sector.add_particle(
            Particle( self.x+3+x_component*-2, self.y+4+y_component*-2,
                "thrust_exhaust",
                thrust_exhaust_index,
                thrust_exhaust_colormap,
                thrust_exhaust_character_map,
                1.0,
                self.heading - math.pi if self.heading > math.pi else self.heading + math.pi,
                newx, newy)
        )

    def reverse_direction(self):
        if self.velocity > 0.0:
            if not (self.velocity_angle_opposite - self.turn_rate*0.9) < self.heading < (self.velocity_angle_opposite + self.turn_rate*0.9):
                if self.heading > self.velocity_angle_opposite or self.heading < self.velocity_angle:
                    self.turn_right()
                else:
                    self.turn_left()

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

        for y, line in enumerate(ship):
            for x, cell in enumerate(line):
                if cell != None:
                    b = cell[0]
                    f = cell[1]
                    c = cell[2]
                    self.sector.buffer.set(self.x + x, self.y + y, b[0], b[1], b[2], f[0], f[1], f[2], c)
                    # self.sector.buffer.set_fore(self.x + x, self.y + y, f[0], f[1], f[2], c)

    def fire_laser(self):
        x_component = math.cos(self.heading)
        y_component = math.sin(self.heading)
        self.sector.add_particle(
            Particle(
                # self.x,
                self.x+3+x_component*3,
                self.y+4+y_component*3,
                # self.y-y_component*10,
                "laser",
                laser_index,
                laser_colormap,
                laser_character_map,
                3.0,
                self.heading,
                self.velocity_component_x,
                self.velocity_component_y
            )
        )

