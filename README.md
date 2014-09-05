heliopause
==========

A text mode space exporation game in the spirit of [Escape Velocityi](http://en.wikipedia.org/wiki/Escape_Velocity_%28video_game%29) written in Python using [libtcod](http://doryen.eptalys.net/libtcod/).

[Video demo here](https://www.youtube.com/watch?v=XIpc9fwR4BU)

Screenshots
-----------

[![screenshot000.png](https://raw.github.com/AnthonyDiGirolamo/heliopause/master/screenshots/screenshot000.png)](https://raw.github.com/AnthonyDiGirolamo/heliopause/master/screenshots/screenshot000.png)

[![screenshot001.png](https://raw.github.com/AnthonyDiGirolamo/heliopause/master/screenshots/screenshot001.png)](https://raw.github.com/AnthonyDiGirolamo/heliopause/master/screenshots/screenshot001.png)

[![screenshot002.png](https://raw.github.com/AnthonyDiGirolamo/heliopause/master/screenshots/screenshot002.png)](https://raw.github.com/AnthonyDiGirolamo/heliopause/master/screenshots/screenshot002.png)

[![screenshot003.png](https://raw.github.com/AnthonyDiGirolamo/heliopause/master/screenshots/screenshot003.png)](https://raw.github.com/AnthonyDiGirolamo/heliopause/master/screenshots/screenshot003.png)

[![screenshot004.png](https://raw.github.com/AnthonyDiGirolamo/heliopause/master/screenshots/screenshot004.png)](https://raw.github.com/AnthonyDiGirolamo/heliopause/master/screenshots/screenshot004.png)

[![screenshot005.png](https://raw.github.com/AnthonyDiGirolamo/heliopause/master/screenshots/screenshot005.png)](https://raw.github.com/AnthonyDiGirolamo/heliopause/master/screenshots/screenshot005.png)

[![screenshot006.png](https://raw.github.com/AnthonyDiGirolamo/heliopause/master/screenshots/screenshot006.png)](https://raw.github.com/AnthonyDiGirolamo/heliopause/master/screenshots/screenshot006.png)

[![screenshot007.png](https://raw.github.com/AnthonyDiGirolamo/heliopause/master/screenshots/screenshot007.png)](https://raw.github.com/AnthonyDiGirolamo/heliopause/master/screenshots/screenshot007.png)

Compiling libtcod on osx
------------------------

    brew install sdl mercurial
    hg clone https://bitbucket.org/KillerX/libtcod_osx
    cd libtcod_osx
    make -f makefiles/makefile-osx

Copy the resulting libtcod.dylib to the heliopause directory and run `python heliopause.py`

