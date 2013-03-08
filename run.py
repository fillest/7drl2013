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


testc = [tcod.Color(255, 255, 255)]
def cb ():
	testc[0] = tcod.Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
t = util.Timer(1000, cb).start()

timers = [t]


class Enemy (object):
	def __init__ (self, x, y):
		self.x = x
		self.y = y

		timers.append(util.Timer(500, self._move).start())

	def _move (self):
		self.x = util.clamp(self.x + random.randint(-1, 1), 1, 10)
		self.y = util.clamp(self.y + random.randint(-1, 1), 1, 10)

	def update (self):
		pass

	def render (self):
		tcod.console_put_char(0, self.x, self.y, '@', tcod.BKGND_NONE)
		tcod.console_set_char_foreground(0, self.x, self.y, testc[0])

enemies = []
enemies.append(Enemy(1, 1))
enemies.append(Enemy(1, 15))

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
	timers.append(util.Timer(20, update_missile).start())
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