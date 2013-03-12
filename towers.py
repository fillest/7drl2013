import util
import libtcodpy as tcod
import enemies

class BasicMissile (util.Entity):
	sym = '*'
	color = tcod.yellow

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


class Heart (util.Entity):
	sym = '&'
	color = tcod.darker_red
	max_hp = 10
	
	def __init__ (self, *args):
		super(Heart, self).__init__(*args)
		self.hp = self.max_hp
	
	def hurt (self, hp):
		self.hp -= hp
		if self.hp < 1:
			self.die()
	
	def die (self):
		self.state.entities.remove(self)

class Tower (util.Entity):
	sym = '@'
	radius = 10
	max_hp = 10
	damage = 1

	def __init__ (self, *args):
		super(Tower, self).__init__(*args)
		self.cooldown = False
		self.hp = self.max_hp

	def update (self):
		if not self.cooldown:
			dist_min = 9000
			target = None
			for e in self.state.entities:
				if isinstance(e, enemies.Enemy):
					d = util.dist(self.x, self.y, e.x, e.y)
					if d < (self.radius + 1) and d < dist_min:
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
			
			self.hit(e)

			return True
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
		self.state.entities.remove(self)

class BasicTower (Tower):
	color = tcod.dark_green

class AoeTower (Tower):
	color = tcod.dark_orange

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
		self.state.timers.start(70, lambda: self.state.entities.remove(e) or True)