import sys
import os
os.chdir("libtcod-1.5.2")
# sys.path.append("tcod-1.5.2/python") 
sys.path.append("python") 
import libtcodpy as tcod
import random


tcod.sys_set_fps(60)
tcod.console_set_custom_font('data/fonts/dejavu16x16_gs_tc.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)
tcod.console_init_root(80, 50, 'TD RL', False)

# c1 = tcod.Color(255, 255, 255)
# tcod.console_set_default_background(0, c1)
# tcod.console_clear(0)


class color (object):
	grass = tcod.Color(50, 150, 50)

tile_types = dict(
	grass = dict(
		sym = '.',
		color = color.grass,
	)
)

world_map = [
	['grass'] * 60,
] * 40


class Timer (object):
	def __init__ (self, interval, cb, args = None):
		self.cb = cb
		self.interval = interval
		self.last_time = None
		self.args = args or ()

	def start (self):
		self.last_time = tcod.sys_elapsed_milli()
		return self

	def update (self):
		cur_time = tcod.sys_elapsed_milli()
		#
		# last_time = cur_time
		#
		if cur_time - self.last_time >= self.interval:
			self.cb(*self.args)
			self.last_time = cur_time

testc = [tcod.Color(255, 255, 255)]
def cb ():
	testc[0] = tcod.Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
t = Timer(1000, cb).start()

timers = [t]

def clamp (value, min_value, max_value):
	return max(min(value, max_value), min_value)

class Enemy (object):
	def __init__ (self, x, y):
		self.x = x
		self.y = y

		timers.append(Timer(500, self._move).start())

	def _move (self):
		self.x = clamp(self.x + random.randint(-1, 1), 1, 10)
		self.y = clamp(self.y + random.randint(-1, 1), 1, 10)

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
	timers.append(Timer(20, update_missile).start())
timers.append(Timer(1200, shoot, [enemies[0]]).start())
timers.append(Timer(1500, shoot, [enemies[1]]).start())


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
	tcod.console_set_char_foreground(0, 20, 20, tcod.Color(255, 255, 255))

	for t in timers:
		t.update()


	tcod.console_flush()