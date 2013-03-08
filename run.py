import sys
import os
os.chdir("libtcod-1.5.2")
# sys.path.append("tcod-1.5.2/python") 
sys.path.append("python") 
import libtcodpy as tcod
import random
import util


tcod.sys_set_fps(60)
tcod.console_set_custom_font('data/fonts/dejavu16x16_gs_tc.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)
tcod.console_init_root(80, 50, 'TD RL', False)

# c1 = tcod.Color(255, 255, 255)
# tcod.console_set_default_background(0, c1)
# tcod.console_clear(0)


class color (object):
	grass = tcod.Color(50, 150, 50)
	white = tcod.Color(255, 255, 255)

tile_types = dict(
	grass = dict(
		sym = '.',
		color = color.grass,
	)
)

world_map = [
	['grass'] * 60,
] * 40


timers = []

class State (object):
	pass

state = State()
state.timers = timers

enemies = []
enemies.append(util.Enemy(state, 1, 1))
enemies.append(util.Enemy(state, 1, 15))

missiles = []
def shoot (e):
	m = [20, 20]
	missiles.append(m)

	def update_missile ():
		tcod.line_init(m[0], m[1], e.x, e.y)
		x, y = tcod.line_step()
		if x is None:
			# missiles.remove(m)
			return

		m[0] = x
		m[1] = y
	missile_speed = 20
	timers.append(util.Timer(missile_speed, update_missile).start())
timers.append(util.Timer(1200, shoot, [enemies[0]]).start())
timers.append(util.Timer(1500, shoot, [enemies[1]]).start())


key = tcod.Key()
mouse = tcod.Mouse()
while not tcod.console_is_window_closed():
	ev = tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE, key, mouse) #TODO loop?
	if key.vk == tcod.KEY_ESCAPE:
		break
	

	if mouse.lbutton_pressed:
		print "left mouse, cell:", mouse.cx, mouse.cy


	for y, row in enumerate(world_map):
		for x, tile_type in enumerate(row):
			tcod.console_put_char(0, x + 1, y + 1, tile_types[tile_type]['sym'], tcod.BKGND_NONE)
			tcod.console_set_char_foreground(0, x + 1, y + 1, tile_types[tile_type]['color'])
			# tcod.console_put_char_ex(0, x + 1, y + 1, cell, color.grass, 0)

	for m in missiles:
		x, y = m
		tcod.console_put_char(0, x, y, '*', tcod.BKGND_NONE)
		tcod.console_set_char_foreground(0, x, y, tcod.Color(255, 0, 0))

	for e in enemies:
		e.update()
		e.render()

	tcod.console_put_char(0, 20, 20, '@', tcod.BKGND_NONE)
	tcod.console_set_char_foreground(0, 20, 20, color.white)

	for t in timers:
		t.update()


	tcod.console_flush()