nova-stories
============

A space exporation game written in python using libtcod

Compiling libtcod on osx
------------------------

  brew install sdl mercurial
  hg clone https://bitbucket.org/KillerX/libtcod_osx
  cd libtcod_osx
  make -f makefiles/makefile-osx

Copy the resulting libtcod.dylib to the nova directory and run python nova.py
