import libtcodpy as tcod
import random
import math


class Entity (object):
	color = tcod.white
	sym = None

	def __init__ (self, state, x, y):
		self.x = x
		self.y = y
		self.state = state
		self.mouse_over = False

	def render (self):
		tcod.console_put_char(0, self.x, self.y, self.sym, tcod.BKGND_NONE)
		tcod.console_set_char_foreground(0, self.x, self.y, self.color)

	def update (self):
		pass


import enemies


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
		self.time_buf = 0

	def start (self):
		self.last_time = tcod.sys_elapsed_milli()
		return self

	def update (self):
		cur_time = tcod.sys_elapsed_milli()
		dt = cur_time - self.last_time
		self.last_time = cur_time
		self.time_buf += dt

		while self.time_buf >= self.interval:
			self.time_buf -= self.interval

			result = self.cb(*self.args)
			if result:
				return result

	def pause (self):
		cur_time = tcod.sys_elapsed_milli() #TODO paste
		dt = cur_time - self.last_time
		self.last_time = cur_time
		self.time_buf += dt

	def resume (self):
		self.last_time = tcod.sys_elapsed_milli()

	def reset (self):
		self.last_time = tcod.sys_elapsed_milli()
		self.time_buf = 0

class Timers (list):
	def start (self, interval, cb, args = None):
		timer = Timer(interval, cb, args)
		self.append(timer.start())
		return timer
	
	def update (self):
		for t in list(self):
			if t.update():
				self.remove(t)

	def pause (self):
		for t in self:
			t.pause()

	def resume (self):
		for t in self:
			t.resume()



class Entities (list):
	def enemies (self):
		for e in self:
			if isinstance(e, enemies.Enemy):
				yield e
