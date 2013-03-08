import libtcodpy as tcod


def clamp (value, min_value, max_value):
	return max(min(value, max_value), min_value)

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