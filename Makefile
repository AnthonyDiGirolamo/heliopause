libcustomrender:
	gcc -shared -o libcustomrender.dylib  `sdl-config --cflags --libs` -lSDL_gfx libcustomrender.c
