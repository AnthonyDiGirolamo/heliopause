#!/usr/bin/env python
# coding: utf-8

import random
import math
import libtcodpy as libtcod
from PIL import Image

import pprint
pp = pprint.PrettyPrinter(indent=4, width=200).pprint

class ShipEditor:
    def __init__(self, ship_value=None, screen_width=106, screen_height=60):
        random.seed()
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.buffer = libtcod.ConsoleBuffer(self.screen_width, self.screen_height)
        self.console = libtcod.console_new(self.screen_width, self.screen_height)

        self.mouse = libtcod.Mouse()
        self.key = libtcod.Key()

        self.selected_character = 0
        self.sprite_size = 16

        self.ship_buffer = libtcod.ConsoleBuffer(self.sprite_size, self.sprite_size)
        self.ship_console = libtcod.console_new(self.sprite_size, self.sprite_size)

        self.sprite_drawing_left   = 16 + 1
        self.sprite_drawing_top    = 1
        self.sprite_drawing_right  = self.sprite_drawing_left + self.sprite_size
        self.sprite_drawing_bottom = self.sprite_drawing_top + self.sprite_size

        self.rotation_angle = 0

        self.presets = [
            0b1010011101000010001010111110111,
            0x2cd31bf7L,
            0x50783136L,
            0b10100010101010100011011001000110,
            0b11110110101111101000001011010101,
            0b11111101110110011110011111011110,
            0b1000011111101111111111001111110,
            0b10100001000010111110111001111110,
            0b100100001111111111001001110111,
            0b101110011000110111100110111111,
            0b10011010001100011110101011010010,
            0b10101001000100000010100100100000,
        ]

    def create_ship_image(self):
        self.ship_original_image = Image.new("RGBA", (16,16))
        pixels = self.ship_original_image.load()

        for i, cell in enumerate(self.ship_buffer):
            x = i%self.sprite_size
            y = int(i/self.sprite_size)
            back_r, back_g, back_b, fore_r, fore_g, fore_b, c = cell
            alpha = 255
            if c == 32:
                if back_r == 64 and back_b == 64 and back_b == 64:
                    alpha = 0
                pixels[x, y] = (back_r, back_g, back_b, alpha)
            else:
                pixels[x, y] = (fore_r, fore_g, fore_b, alpha)

        # self.ship_original_image.save("rship_test_000.png")

    def rotate(self, angle=0):
        if angle in [0, 90, 180, 270]:
            rotated_image = self.ship_original_image.rotate(angle, resample=Image.NEAREST)
        else:
            larger_image = self.ship_original_image.resize((self.sprite_size*4, self.sprite_size*4), resample=Image.NEAREST)
            r = larger_image.rotate(angle, resample=Image.BICUBIC)
            rotated_image = r.resize((16, 16), resample=Image.NEAREST)

            # rotated_image = self.ship_original_image.rotate(angle, resample=Image.BICUBIC)
            # rotated_image = self.ship_original_image.rotate(angle, resample=Image.BILINEAR)
            # rotated_image = self.ship_original_image.rotate(angle, resample=Image.NEAREST)

        # rotated_image.save("rship_test_045.png")

        rotated_pixels = rotated_image.load()

        for y in range(0, self.sprite_size):
            for x in range(0, self.sprite_size):
                self.ship_buffer.set(x, y, 64, 64, 64, 0, 0, 0, 32)
        for i, cell in enumerate(self.ship_buffer):
            x = i%self.sprite_size
            y = int(i/self.sprite_size)
            if rotated_pixels[x, y][3] > 0:
                self.ship_buffer.set_fore(x, y, rotated_pixels[x,y][0], rotated_pixels[x,y][1], rotated_pixels[x,y][2], 219)
                self.ship_buffer.set_back(x, y, rotated_pixels[x,y][0], rotated_pixels[x,y][1], rotated_pixels[x,y][2])

    def generate_random_ship(self, value=None):
        ship_frame = []
        ship_mask = [
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 1],
            [0, 0, 0, 0, 1,-1],
            [0, 0, 0, 1, 1,-1],
            [0, 0, 0, 1, 1,-1],
            [0, 0, 1, 1, 1,-1],
            [0, 1, 1, 1, 2, 2],
            [0, 1, 1, 1, 2, 2],
            [0, 1, 1, 1, 2, 2],
            [0, 1, 1, 1, 1,-1],
            [0, 0, 0, 1, 1, 1],
            [0, 0, 0, 0, 0, 0],
        ]

        if value:
            self.ship_value = value
        else:
            self.ship_value = random.getrandbits(32)
        print("Ship Value: {0}".format(hex(self.ship_value)))

        # Generate Colors
        self.ship_hue = []
        for i in range(0, 3):
            self.ship_hue.append( (float((self.ship_value >> i*10) & 0b1111111111) / 1023.0 ) * 360.0 )

        # Create a list of random bits
        random_bits = []
        bit_mask = 1
        for i in range(0, 32):
            random_bits.append( (self.ship_value & bit_mask) >> i )
            bit_mask <<= 1
        random_bits.reverse()

        positions = [ [x, y] for y, row in enumerate(ship_mask) for x, cell in enumerate(row) if cell > 0 ]
        # pp(ship_mask)
        # pp(random_bits)

        border_positions = [[5, 1]]
        for y, row in enumerate(ship_mask):
            for x, cell in enumerate(row):
                if cell > 0:
                    border_positions.append([x, y])
                    break
        border_positions.append([4, 10])
        border_positions.append([5, 10])

        for x, y in positions:
            if ship_mask[y][x] == 1:
                ship_mask[y][x] = int(random_bits.pop())
            elif ship_mask[y][x] == 2:
                ship_mask[y][x] = int(random_bits.pop())
                if ship_mask[y][x] == 0:
                    ship_mask[y][x] = -1

        for x, y in positions:
            if ship_mask[y][x] > 0:
                if ship_mask[y-1][x] == 0:
                    ship_mask[y-1][x] = -1

                if ship_mask[y+1][x] == 0:
                    ship_mask[y+1][x] = -1

                if ship_mask[y][x-1] == 0:
                    ship_mask[y][x-1] = -1

                if x+1 < 6 and ship_mask[y][x+1] == 0:
                    ship_mask[y][x+1] = -1

        # pp(ship_mask)
        self.generated_ship = ship_mask
        self.render_random_ship()

    def erase(self):
        for y in range(0, self.sprite_size):
            for x in range(0, self.sprite_size):
                xcoord = x
                ycoord = y
                self.ship_buffer.set(xcoord, ycoord, 64, 64, 64, 0, 0, 0, 32)


    def render_random_ship(self):
        self.erase()

        for y, row in enumerate(self.generated_ship):
            for x, cell in enumerate(row):
                body_color = libtcod.Color(0, 0, 255)

                hue = self.ship_hue[0]
                if 6 <= y < 12:
                    if 4 <= x < 8:
                        hue = self.ship_hue[1]
                    else:
                        hue = self.ship_hue[2]


                saturation = 0.6
                if 2 <= x < 4 or 8 <= x < 10:
                    saturation = 0.8
                elif 4 <= x < 8:
                    saturation = 1.0

                lightness = 0.6
                if 2 <= y < 4 or 8 <= y < 10:
                    lightness = 0.8
                elif 4 <= y < 8:
                    lightness = 1.0
                # lightness = 1 - (math.sqrt((x-7)**2 + (y-7)**2) / 10.0)
                libtcod.color_set_hsv(body_color, hue, saturation, lightness)

                # facing up
                # xcoord = 12-y
                # ycoord = x

                # rotated 90 cw (facing right)
                xcoord = 11-y+2
                ycoord = x+2

                xcoord_mirrored = xcoord
                ycoord_mirrored = 15 - ycoord
                if cell == -1:
                    self.ship_buffer.set_fore(xcoord, ycoord, 0, 0, 0, 219)
                    self.ship_buffer.set_fore(xcoord_mirrored, ycoord_mirrored, 0, 0, 0, 219)
                elif cell == 1:
                    self.ship_buffer.set_fore(xcoord, ycoord, body_color[0], body_color[1], body_color[2], 219)
                    self.ship_buffer.set_fore(xcoord_mirrored, ycoord_mirrored, body_color[0], body_color[1], body_color[2], 219)

                if cell in [-1, 1]:
                    self.ship_buffer.set_back(xcoord, ycoord, body_color[0], body_color[1], body_color[2])
                    self.ship_buffer.set_back(xcoord_mirrored, ycoord_mirrored, body_color[0], body_color[1], body_color[2])

        self.create_ship_image()
        self.rotation_angle = 0

    def fix_missing_border_pixels(self):
        for i, cell in enumerate(self.ship_buffer):
            x = i%self.sprite_size
            y = int(i/self.sprite_size)
            if 0 < x < self.sprite_size and 0 < y < self.sprite_size:
                neighbor_indexes = [
                    (x - 1) + (self.sprite_size * y),
                    (x + 1) + (self.sprite_size * y),
                    x + (self.sprite_size * (y - 1)),
                    x + (self.sprite_size * (y + 1)),
                ]
                back_r, back_g, back_b, fore_r, fore_g, fore_b, c = cell
                if c == 219 and (fore_r + fore_b + fore_g > 60) and (back_r + back_b + back_g > 60):
                    for j in neighbor_indexes:
                        xcoord = j%self.sprite_size
                        ycoord = int(j/self.sprite_size)
                        neighbor_cell = self.ship_buffer[j]
                        if neighbor_cell == [64, 64, 64, 0, 0, 0, 32]:
                            self.ship_buffer.set_fore(xcoord, ycoord, 0, 0, 0, 219)

    def load_frame(self, angle=None):
        if angle:
            self.rotate(angle)

        self.fix_missing_border_pixels()

        frame = [[] for i in range(0, self.sprite_size)]

        for i, cell in enumerate(self.ship_buffer):
            x = i%self.sprite_size
            y = int(i/self.sprite_size)
            back_r, back_g, back_b, fore_r, fore_g, fore_b, c = cell
            alpha = 255
            if c == 32:
                if back_r == 64 and back_b == 64 and back_g == 64:
                    alpha = 0
                frame[y].append( None )
            else:
                frame[y].append( [[back_r, back_b, back_b], [fore_r, fore_g, fore_b], c] )

        return frame

    def render_all(self):
        # Draw character select pallete
        for c in range(0, 256):
            b = [0, 0, 0]
            if c == self.selected_character:
                b = [128, 128, 128]
            self.buffer.set(c%self.sprite_size, int(c/self.sprite_size), b[0], b[1], b[2], 255, 255, 255, c)

        self.buffer.blit(self.console)

        libtcod.console_print_ex(self.console, 0, 17, libtcod.BKGND_SET, libtcod.LEFT,
            "Selected: {0}".format( self.selected_character ))

        libtcod.console_print_frame(self.console, self.sprite_size, 0, self.sprite_size+2, self.sprite_size+2, clear=False, flag=libtcod.BKGND_SET, fmt=0)


        self.ship_buffer.blit(self.ship_console)
        libtcod.console_blit(self.ship_console, 0, 0, self.sprite_size, self.sprite_size, self.console, self.sprite_drawing_left, self.sprite_drawing_top, 1.0, 1.0)

        libtcod.console_blit(self.console, 0, 0, self.screen_width, self.screen_height, 0, 0, 0)
        libtcod.console_flush()
        self.buffer.clear(0, 0, 0)

    def handle_keys(self):
        if self.key.pressed and self.key.vk == libtcod.KEY_ENTER and self.key.lalt:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        elif self.key.pressed and self.key.vk == libtcod.KEY_ESCAPE:
            return 1  #exit game

        elif self.key.pressed and self.key.vk == libtcod.KEY_LEFT:
            self.selected_character -= 1
            if self.selected_character < 0:
                self.selected_character = 255

        elif self.key.pressed and self.key.vk == libtcod.KEY_RIGHT:
            self.selected_character += 1
            if self.selected_character >255:
                self.selected_character = 0

        elif self.key.pressed:
            key_character = chr(self.key.c)
            if key_character == 'G':
                self.generate_random_ship()
            elif key_character == 'r':
                self.rotation_angle += 10
                if self.rotation_angle > 350:
                    self.rotation_angle = 0
                self.rotate(self.rotation_angle)
            elif key_character == 'b':
                self.fix_missing_border_pixels()
            elif key_character == 'C':
                self.erase()
            elif key_character == 'P':
                pp(self.load_frame(self.rotation_angle))
            elif key_character in [str(i) for i in range(1, 10)]:
                if int(key_character) < len(self.presets):
                    self.generate_random_ship(self.presets[int(key_character)])

        if self.mouse.lbutton_pressed:
            if self.mouse.cx < 16 and self.mouse.cy < 16:
                self.selected_character = self.mouse.cx+ self.mouse.cy*16
            elif self.sprite_drawing_left <= self.mouse.cx < self.sprite_drawing_right and \
                 self.sprite_drawing_top <= self.mouse.cy < self.sprite_drawing_bottom:
                xcoord = self.mouse.cx - self.sprite_drawing_left
                ycoord = self.mouse.cy - self.sprite_drawing_top
                pp(self.ship_buffer[ (xcoord) + (self.sprite_size * ycoord) ])
                self.ship_buffer.set_fore(xcoord, ycoord, 0, 0, 0, self.selected_character)

    def main_loop(self):
        self.generate_random_ship()

        while not libtcod.console_is_window_closed():
            libtcod.sys_check_for_event(libtcod.KEY_PRESSED|libtcod.KEY_RELEASED|libtcod.EVENT_MOUSE, self.key, self.mouse)

            self.render_all()

            player_action = self.handle_keys()
            if player_action == 1:
                break

if __name__ == '__main__':
    libtcod.sys_set_fps(30)
    libtcod.console_set_keyboard_repeat(1, 10)

    libtcod.console_set_custom_font('fonts/12x12_limited.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=16)

    game = ShipEditor()
    libtcod.console_init_root(game.screen_width, game.screen_height, 'Heliopause Ship Editor', False)
    game.main_loop()
