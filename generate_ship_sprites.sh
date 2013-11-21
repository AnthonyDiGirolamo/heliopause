#!/bin/bash
for angle in `seq -w 0 10 350`
do
  convert -alpha set -background black -rotate -$angle -gravity NorthWest -crop 16x16+0+0 ship.png ship_$angle.png
done
