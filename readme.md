# A game for 7DRL-2013

## About
This is a tower defence roguelike game for [7DRL-2013](http://roguebasin.roguelikedevelopment.org/index.php?title=7DRL_Challenge_2013). It is written in Python using [libtcod](http://doryen.eptalys.net/libtcod/).

[Retrospective](https://github.com/fillest/7drl2013/wiki/Retrospective)

## Running
Tested on Linux (Ubuntu) and Windows 7. The code should also run on Mac as well (I don't have a Mac system to test for the present, sorry) if you download and put libtcod binary distribution for Mac to the source directory and add appropriate OS check to *run.py* (see at the top of file).

### Windows
1. Install latest Python 2, e.g. http://www.python.org/ftp/python/2.7.4/python-2.7.4.msi (choose something like C:\Python27 for installation path)
1. Open the game code folder and double-click *run* (*run.py*)
1. If the game doesn't launch, try adding Python to Windows Path and launch again: http://superuser.com/questions/143119/how-to-add-python-to-the-windows-path/
1. If the game still doesn't run, please [create an issue](https://github.com/fillest/7drl2013/issues) or email me to *fsfeel AT gmail DOTCOM*

### Linux 
```bash
cd 7drl2013
python run.py
```

## How to play
### Keyboard shortcuts
* `space` - toggle pause
* `0` to `4` - choose tower type / ability
* `left mouse button` - put tower / pick up loot / use ability
* `right mouse button` - remove tower
* `esc` - exit

## License
See license.txt ([The MIT License](http://www.opensource.org/licenses/mit-license.php))
