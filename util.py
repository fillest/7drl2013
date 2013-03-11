import libtcodpy as tcod
import random
import math


def clamp (value, min_value, max_value):
	return max(min(value, max_value), min_value)

def dist (x1, y1, x2, y2):
	return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

class Timer (object):
	def __init__ (self, interval, cb, args = None):
		self.cb = cb
		self.interval = interval
		self.last_time = None
		self.args = args if args else ()

	def start (self):
		self.last_time = tcod.sys_elapsed_milli()
		return self

	def update (self):
		cur_time = tcod.sys_elapsed_milli()
		#TODO buffering + dont forget pause
		#
		# last_time = cur_time
		#
		if cur_time - self.last_time >= self.interval:
			result = self.cb(*self.args)
			if result:
				return result
			self.last_time = cur_time

class Timers (list):
	def start (self, interval, cb, args = None):
		self.append(Timer(interval, cb, args).start())

class Entity (object):
	def __init__ (self, state, x, y, sym, color = tcod.white):
		self.x = x
		self.y = y
		self.sym = sym
		self.state = state
		self.color = color
		self.mouse_over = False

	def render (self):
		tcod.console_put_char(0, self.x, self.y, self.sym, tcod.BKGND_NONE)
		tcod.console_set_char_foreground(0, self.x, self.y, self.color)

	def update (self):
		pass

class Enemy (Entity):
	def __init__(self, *args):
		super(Enemy, self).__init__(*args)
		self.state.timers.start(500, self._move)

	def _move (self):
		# self.x = clamp(self.x + random.randint(-1, 1), 0, self.state.map.w - 1)
		# self.y = clamp(self.y + random.randint(-1, 1), 0, self.state.map.h - 1)

		tcod.line_init(self.x, self.y, self.state.heart.x, self.state.heart.y)
		x, y = tcod.line_step()
		if x is None:
			pass
		else:
			#TODO check x y for obstacle
			self.x = x
			self.y = y
