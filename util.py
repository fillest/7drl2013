import libtcodpy as tcod
import random


def clamp (value, min_value, max_value):
	return max(min(value, max_value), min_value)

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
		#
		# last_time = cur_time
		#
		if cur_time - self.last_time >= self.interval:
			self.cb(*self.args)
			self.last_time = cur_time

class Enemy (object):
	def __init__ (self, state, x, y):
		self.x = x
		self.y = y

		state.timers.append(Timer(500, self._move).start())

	def _move (self):
		self.x = clamp(self.x + random.randint(-1, 1), 1, 10)
		self.y = clamp(self.y + random.randint(-1, 1), 1, 10)

	def update (self):
		pass

	def render (self):
		tcod.console_put_char(0, self.x, self.y, '@', tcod.BKGND_NONE)
		tcod.console_set_char_foreground(0, self.x, self.y, tcod.Color(255, 255, 255))
