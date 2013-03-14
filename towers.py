import util
import libtcodpy as tcod
import enemies


class BasicMissile (util.Entity):
	sym = '*'
	color = tcod.yellow

class IceMissile (util.Entity):
	sym = '*'
	color = tcod.light_blue

class AoeMissile (util.Entity):
	sym = '*'
	color = tcod.red


class Heart (util.Entity):
	sym = '&'
	color = tcod.darker_red
	max_hp = 10
	
	def __init__ (self, *args):
		super(Heart, self).__init__(*args)
		self.hp = self.max_hp
		self.state.hearts.append(self)
	
	def hurt (self, hp):
		self.hp -= hp
		if self.hp < 1:
			self.die()
	
	def die (self):
		if self in self.state.entities:
			self.state.entities.remove(self)
		if self in self.state.hearts:
			self.state.hearts.remove(self)
			
class FakeHeart (Heart):
	color = tcod.blue
	
	def die (self):
		def _next_heart ():
			for h in self.state.hearts:
				if isinstance(h, FakeHeart):
					return h
			return self.state.hearts[0] # TODO Maybe IndexError
		
		if self in self.state.hearts:
			self.state.hearts.remove(self)
		
		self.state.heart = _next_heart()
		super(FakeHeart, self).die()

class Tower (util.Entity):
	sym = '@'
	radius = 15
	max_hp = 10
	damage = 1
	missile = None

	def __init__ (self, *args):
		super(Tower, self).__init__(*args)
		self.cooldown = False
		self.hp = self.max_hp

	def update (self):
		if not self.cooldown:
			dist_min = None
			target = None
			for e in self.state.entities:
				if isinstance(e, enemies.Enemy):
					d = util.dist(self.x, self.y, e.x, e.y)
					if d < (self.radius + 1) and ((dist_min is None) or (d < dist_min)):
						dist_min = d
						target = e
			
			if target:
				self._shoot(target)

	def render (self):
		super(Tower, self).render()
		# if self.mouse_over:
		if True:
			for x in range(self.x - (self.radius + 1), self.x + (self.radius + 1)):
				for y in range(self.y - (self.radius + 1), self.y + (self.radius + 1)):
					if util.dist(self.x, self.y, x, y) < (self.radius + 1):
						tcod.console_set_char_background(0, x, y, tcod.Color(*[15]*3), flag = tcod.BKGND_SET) 

	def _shoot (self, e):
		self.cooldown = True
		def clear_cd ():
			self.cooldown = False
		self.state.timers.start_run_once(1000, clear_cd)

		m = self.missile(self.state, self.x, self.y)
		self.state.entities.append(m)
		
		missile_speed = 20
		self.state.timers.start(missile_speed, self.update_missile, [m, e])

	def update_missile (self, m, e):
		tcod.line_init(m.x, m.y, e.x, e.y)
		x, y = tcod.line_step()
		if x is None:
			self.state.entities.remove(m)
			
			self.hit(e)

			return util.STOP
		else:
			m.x = x
			m.y = y

	def hit (self, e):
		if e in self.state.entities:
			e.hurt(self.damage)
	
	def hurt (self, hp):
		self.hp -= hp
		if self.hp < 1:
			self.die()
		
	def die (self):
		if self in self.state.entities:
			self.state.entities.remove(self)

class BasicTower (Tower):
	color = tcod.dark_green
	missile = BasicMissile

class AoeExplosion (util.Entity):
	sym = '*'
	color = tcod.dark_red

	def __init__ (self, radius, *args):
		super(AoeExplosion, self).__init__(*args)
		self.radius = radius

	def render (self):
		for x in range(self.x - self.radius, self.x + self.radius):
			for y in range(self.y - self.radius, self.y + self.radius):
				tcod.console_put_char(0, x, y, self.sym, tcod.BKGND_NONE)
				tcod.console_set_char_foreground(0, x, y, self.color)

class AoeTower (Tower):
	color = tcod.dark_orange
	missile = AoeMissile

	def hit (self, target):
		radius = 2
		for x in range(target.x - radius, target.x + radius):
			for y in range(target.y - radius, target.y + radius):
				for e in self.state.entities.enemies():
					if (e.x, e.y) == (x, y):
						if e in self.state.entities: #TODO copypaste
							e.hurt(self.damage)

		e = AoeExplosion(radius, self.state, target.x, target.y)
		self.state.entities.append(e)
		self.state.timers.start_run_once(70, lambda: self.state.entities.remove(e))

class IceTower (Tower):
	damage = 0.2
	color = tcod.dark_blue
	missile = IceMissile

	def hit (self, target):
		target.hurt(self.damage)
		
		if not getattr(target, 'is_debuffed', False):
			old_speed = target.timer.interval
			target.timer.interval *= 3
			target.timer.time_buf *= 3
			target.is_debuffed = True
			def rollback ():
				target.timer.interval = old_speed
				target.timer.time_buf /= 3
				target.is_debuffed = False
			self.rollback_timer = self.state.timers.start_run_once(1000, rollback)
		else:
			self.rollback_timer.reset()
