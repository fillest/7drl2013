import sys
import os
os.chdir("libtcod-1.5.2")
# sys.path.append("libtcod-1.5.2/python") 
sys.path.append("python") 
import libtcodpy as libtcod


libtcod.sys_set_fps(60)
libtcod.console_init_root(80, 50, 'python/libtcod tutorial', False)

key = libtcod.Key()
mouse = libtcod.Mouse()
while not libtcod.console_is_window_closed():
	libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE, key, mouse)
	if key.vk == libtcod.KEY_ESCAPE:
		break

	if mouse.lbutton_pressed:
		print "left mouse, cell:", mouse.cx, mouse.cy

	libtcod.console_put_char(0, 1, 1, '@', libtcod.BKGND_NONE)

	libtcod.console_flush()