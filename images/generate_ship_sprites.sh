#!/bin/bash
# for angle in `seq 0 10 350`
# do
#   convert \
#     -size 16x16 xc:blue -fill white -stroke black -strokewidth 1.5 \
#     -draw "stroke-linecap round affine `./affine_rotate -$angle 7,7, 7,7`
#         polygon 2,1 15,7 2,13, 5,7" \
#     -fuzz 55% \
#     -fill blue \
#       -draw 'color 0,0 floodfill' \
#       -draw 'color 0,15 floodfill' \
#       -draw 'color 15,0 floodfill' \
#       -draw 'color 15,15 floodfill' \
#     `if (( $angle < 100 ))
#     then
#       echo ship_0$angle.png
#     else
#       echo ship_$angle.png
#     fi`
# done

# mv ship_00.png ship_000.png

for angle in `seq -w 0 10 350`
do
  convert \
    -alpha on \
    -background transparent \
    -rotate -$angle \
    -gravity NorthWest \
    -crop 16x16+0+0 \
    rocket.png rocket_$angle.png
    # -transparent-color blue \
    # -fuzz 0 -fill blue \
    #   -draw 'color 0,0 floodfill' \
    #   -draw 'color 0,15 floodfill' \
    #   -draw 'color 15,0 floodfill' \
    #   -draw 'color 15,15 floodfill' \
    # -distort ScaleRotateTranslate -$angle \
done

