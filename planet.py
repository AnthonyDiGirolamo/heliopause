class Planet:
    def __init__(self, sector):
        self.sector = sector
        self.sector_position_x = -10
        self.sector_position_y = 10
        self.width = 20
        self.height = 20

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

        for x in range(startingx, endingx):
            for y in range(startingy, endingy, -1):
                self.sector.buffer.set_fore( x, self.sector.mirror_y_coordinate(y), 128, 255, 128, ord('@') )

