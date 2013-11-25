import pprint
pp = pprint.PrettyPrinter(indent=4, width=120).pprint

class Planet:
    def __init__(self, sector):
        self.sector = sector
        self.sector_position_x = -10
        self.sector_position_y = 10
        self.width = 30
        self.height = self.width
        self.build_circle_mask()

    def build_circle_mask(self):
        radius = self.width / 2
        self.circle_mask = []
        for x in range(-radius, radius+1):
            col = []
            for y in range(radius, -radius-1, -1):
                if float(x)**2.0 + float(y)**2.0 < float(radius)**2.0:
                    col.append(1)
                else:
                    col.append(0)
            self.circle_mask.append(col)
        pp(self.circle_mask)

    def draw(self):
        feature_left         = self.sector_position_x
        feature_top          = self.sector_position_y
        feature_right        = self.sector_position_x + self.width
        feature_bottom       = self.sector_position_y + self.height

        startingx = int(self.sector_position_x - self.sector.visible_space_left)
        startingy = int(self.sector_position_y - self.sector.visible_space_bottom)
        endingx = startingx + self.width
        endingy = startingy - self.height

        startingx = int(max([0, startingx]))
        startingy = int(min([self.sector.screen_height-1,  startingy]))
        endingx = int(min([self.sector.screen_width, endingx]))
        endingy = int(max([-1, endingy]))

        row = 1
        if startingx == 0:
            row += self.width - endingx
        start_col = 1
        if startingy == self.sector.screen_height-1:
            start_col += self.height - (startingy - endingy)
        col = start_col
        for x in range(startingx, endingx):
            for y in range(startingy, endingy, -1):
                if self.circle_mask[row][col]:
                    self.sector.buffer.set_fore( x, self.sector.mirror_y_coordinate(y), 128, 255, 128, ord('@') )
                col += 1
            col = start_col
            row += 1

