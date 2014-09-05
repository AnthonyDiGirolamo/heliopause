#!/bin/bash
# Ship Sprite
# Arrow Shape
# polygon 2,1 15,7 2,13, 5,7" \
# Tiefighter Shape
# polygon 3,1 15,5 7,7 15,9 3,13, 1,7" \
for angle in `seq 0 10 350`
do
  convert \
    -size 16x16 xc:blue -fill white -stroke black -strokewidth 1.5 \
    -draw "stroke-linecap round affine `./affine_rotate -$angle 7,7, 7,7`
        polygon 2,1 15,7 2,13, 5,7" \
    -fuzz 55% \
    -fill blue \
      -draw 'color 0,0 floodfill' \
      -draw 'color 0,15 floodfill' \
      -draw 'color 15,0 floodfill' \
      -draw 'color 15,15 floodfill' \
    `if (( $angle < 100 ))
    then
      echo ship_0$angle.png
    else
      echo ship_$angle.png
    fi`
done
mv ship_00.png ship_000.png

# Pointer Sprite
for angle in `seq 0 10 350`
do
  convert \
    -size 32x32 xc:blue -fill red -stroke black -strokewidth 1.5 \
    -draw "stroke-linecap round affine `./affine_rotate -$angle 15,15, 15,15`
        polygon 31,15 24,12 24,18 31,15" \
    -fuzz 55% \
    -fill blue \
      -draw 'color 0,0 floodfill' \
      -draw 'color 0,31 floodfill' \
      -draw 'color 31,0 floodfill' \
      -draw 'color 31,31 floodfill' \
    `if (( $angle < 100 ))
    then
      echo pointer_0$angle.png
    else
      echo pointer_$angle.png
    fi`
done
mv pointer_00.png pointer_000.png

# Test Image Rotation
# for angle in `seq -w 0 10 350`
# do
#   convert \
#     -alpha on \
#     -background transparent \
#     -rotate -$angle \
#     -gravity NorthWest \
#     -crop 16x16+0+0 \
#     rocket.png rocket_$angle.png
#     # -transparent-color blue \
#     # -fuzz 0 -fill blue \
#     #   -draw 'color 0,0 floodfill' \
#     #   -draw 'color 0,15 floodfill' \
#     #   -draw 'color 15,0 floodfill' \
#     #   -draw 'color 15,15 floodfill' \
#     # -distort ScaleRotateTranslate -$angle \
# done

