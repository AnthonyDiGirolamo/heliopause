from random import randrange, choice
import math

class Starfield:
    def __init__(self, sector, max_stars):
        self.sector = sector
        self.max_stars = max_stars
        self.parallax_speeds = [0.3, 0.6, 1.0]
        # self.star_characters = [7, ord('*'), 15]
        self.star_characters = [ord('.'), 7]
        self.stars = [
            [float(randrange(0, self.sector.screen_width)), float(randrange(0, self.sector.screen_height)),
                choice(self.parallax_speeds), choice(self.star_characters)]
                    for i in range(0, self.max_stars) ]

    def __getitem__(self, index):
        return self.stars[index]

    def scroll(self, heading=0.0, velocity=0.0):
        deltax = math.cos(heading) * velocity * -1
        deltay = math.sin(heading) * velocity * -1

        for star in self.stars:
            star[0] += deltax * star[2]
            star[1] += deltay * star[2]
            if star[0] >= self.sector.screen_width-1:
                star[0] = 0
                star[1] = randrange(0, self.sector.screen_height-1)
                star[2] = choice(self.parallax_speeds)
            elif star[0] < 0:
                star[0] = self.sector.screen_width-1
                star[1] = randrange(0, self.sector.screen_height-1)
                star[2] = choice(self.parallax_speeds)
            elif star[1] >= self.sector.screen_height-1:
                star[0] = randrange(0, self.sector.screen_width-1)
                star[1] = 0
                star[2] = choice(self.parallax_speeds)
            elif star[1] < 0:
                star[0] = randrange(0, self.sector.screen_width-1)
                star[1] = self.sector.screen_height-1
                star[2] = choice(self.parallax_speeds)

