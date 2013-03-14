import util
import libtcodpy as tcod
import towers


class Enemy (util.Entity):
	max_hp = 1
	speed = 1
	damage = 1

	def __init__ (self, *args):
		super(Enemy, self).__init__(*args)
		self.timer = self.state.timers.start(500 / self.speed, self._move)
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
				if e.x == x and e.y == y and isinstance(e, (towers.Tower, towers.Heart)):
					self.hit(e)
			
			self.x = x
			self.y = y
			
	def hit (self, e):
		if e in self.state.entities:
			print 'Enemy {0} hit the {1}. Damage: {2}'.format(self.__class__.__name__, e.__class__.__name__, self.damage)
			e.hurt(self.damage)
	
	def hurt (self, hp):
		self.hp -= hp
		if self.hp < 1:
			self.die()
	
	def die (self):
		if self in self.state.entities:
		    self.state.entities.remove(self)
		if self.timer in self.state.timers:
		    self.state.timers.remove(self.timer)
		
class Rat (Enemy):
	sym = 'r'
	color = tcod.lighter_sepia

class Wolf (Enemy):
	sym = 'w'
	color = tcod.lighter_grey
	max_hp = 2
	speed = 2