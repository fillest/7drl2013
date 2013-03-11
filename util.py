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

class BasicMissile (Entity):
	sym = '*'
	color = tcod.yellow

class Enemy (Entity):
	max_hp = 1

	def __init__(self, *args):
		super(Enemy, self).__init__(*args)
		self.state.timers.start(500, self._move)
		self.hp = self.max_hp

	def _move (self):
		# self.x = clamp(self.x + random.randint(-1, 1), 0, self.state.map.w - 1)
		# self.y = clamp(self.y + random.randint(-1, 1), 0, self.state.map.h - 1)

		tcod.line_init(self.x, self.y, self.state.heart.x, self.state.heart.y)
		x, y = tcod.line_step()
		if x is None:
			pass
		else:
			for e in self.state.entities:
				if e.x == x and e.y == y and isinstance(e, (Tower, Heart)):
					return
			
			self.x = x
			self.y = y

class Rat (Enemy):
	sym = 'r'
	color = tcod.lighter_sepia

class Wolf (Enemy):
	sym = 'w'
	color = tcod.lighter_grey
	max_hp = 2

class Heart (Entity):
	sym = '&'
	color = tcod.darker_red

class Tower (Entity):
	sym = '@'
	color = tcod.dark_green

	def __init__(self, *args):
		super(Tower, self).__init__(*args)
		self.cooldown = False
		self.radius = 10 + 1

	def update (self):
		if not self.cooldown:
			dist_min = 9000
			target = None
			for e in self.state.entities:
				if isinstance(e, Enemy):
					d = dist(self.x, self.y, e.x, e.y)
					if d < self.radius and d < dist_min:
						dist_min = d
						target = e
			
			if target:
				self._shoot(target)

	def render (self):
		super(Tower, self).render()
		# if self.mouse_over:
		if True:
			for x in range(self.x - self.radius, self.x + self.radius):
				for y in range(self.y - self.radius, self.y + self.radius):
					if dist(self.x, self.y, x, y) < self.radius:
						tcod.console_set_char_background(0, x, y, tcod.Color(*[15]*3), flag = tcod.BKGND_SET) 

	def _shoot (self, e):
		self.cooldown = True
		def clear_cd ():
			self.cooldown = False
			return True
		self.state.timers.start(1000, clear_cd)

		m = BasicMissile(self.state, self.x, self.y)
		self.state.entities.append(m)
		
		missile_speed = 20
		self.state.timers.start(missile_speed, self.update_missile, [m, e])

	def update_missile (self, m, e):
		tcod.line_init(m.x, m.y, e.x, e.y)
		x, y = tcod.line_step()
		if x is None:
			self.state.entities.remove(m)

			if e in self.state.entities:
				e.hp -= 1
				if e.hp < 1:
					self.state.entities.remove(e)
			
			return True
		else:
			m.x = x
			m.y = y
