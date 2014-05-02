#include <SDL.h>
#include <SDL_gfxPrimitives.h>
#include "libcustomrender.h"

void draw_line(SDL_Surface* surface, int x1, int y1, int x2, int y2) {
    printf("lineColor: %d %d %d %d\n", x1, y1, x2, y2);
    lineColor((SDL_Surface*) surface, (Sint16) x1, (Sint16) y1, (Sint16) x2, (Sint16) y2, (Uint32) 0);
    printf("draw done\n");
}

void testcprint(int number) {
  printf("print from c: %d\n", number);
}
