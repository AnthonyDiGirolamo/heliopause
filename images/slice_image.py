#!/usr/bin/env python
# coding: utf-8
import os

os.system("convert -crop 6x6@ +repage +adjoin shuttle3.png shuttle_%d.png")

angle = 90
for i in range(0, 36):
    os.system("mv -v shuttle_{}.png shuttle_{}.png".format(i, str(angle).zfill(3)))
    angle -= 10
    if angle < 0:
        angle = 350

# for x in range(0,144,24):
#     for y in range(0,144,24):
#         os.system("convert -gravity NorthWest -crop 24x24+{0}+{1} +repage +adjoin shuttle2.png shuttle_{2}.png".format(x, y, str(angle).zfill(3)))
#         angle -= 10
#         if angle < 0:
#             angle = 350
