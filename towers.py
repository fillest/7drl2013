import util
import libtcodpy as tcod
import enemies
import operator


class Missile (util.Entity):
	sym = '*'
	color = tcod.white

class BasicMissile (Missile):
	color = tcod.yellow

class IceMissile (Missile):
	color = tcod.light_blue

class AoeMissile (Missile):
	color = tcod.red


class Building (util.Entity):
	sym = '@'
	max_hp = 1
	cost = 0

	def __init__ (self, *args):
		super(Building, self).__init__(*args)
		self.hp = self.max_hp

	def hurt (self, hp):
		self.hp -= hp

		if self.hp < 1:
			self.die()

	def hit (self, e):
		if e in self.state.entities:
			e.hurt(self.damage)
	
	def die (self):
		if self in self.state.entities:
			self.delete()

	def put (self):
		self.state.entities.append(self)
		self.state.energy -= self.cost
		return self

	def delete (self):
		self.state.entities.remove(self)
		self.state.energy += self.cost
		return self

class Heart (Building):
	sym = '&'
	color = tcod.darker_red
	max_hp = 20

	def delete (self):
		self.state.is_paused = True
		return super(Heart, self).delete()

class Bait (Building):
	sym = Heart.sym
	color = tcod.pink
	max_hp = 10

class Tower (Building):
	radius = 15
	max_hp = 10
	damage = 1
	missile = None

	def __init__ (self, *args):
		super(Tower, self).__init__(*args)
		self.cooldown = False

	def update (self):
		if not self.cooldown:
			# dist_min = None
			# target = None
			# for e in self.state.entities.enemies():
			# 	d = util.dist(self.x, self.y, e.x, e.y)
			# 	if d < (self.radius + 1) and ((dist_min is None) or (d < dist_min)):
			# 		dist_min = d
			# 		target = e
			
			preferred_targets = []
			other_targets = []
			for e in self.state.entities.enemies():
				d = util.dist(self.x, self.y, e.x, e.y)
				if d < (self.radius + 1):
					if e in self.state.targets_towers:
						total_damage = sum([t.damage for t in self.state.targets_towers[e]])
						if total_damage < e.hp:
							preferred_targets.append((d, e))
						else:
							other_targets.append((d, e))
					else:
						preferred_targets.append((d, e))

			target = None
			if preferred_targets:
				_d, target = sorted(preferred_targets, key = operator.itemgetter(0))[0]
			elif other_targets:
				_d, target = sorted(other_targets, key = operator.itemgetter(0))[0]

			if target:
				self.state.targets_towers[target].append(self)
				self._shoot(target)

	def render (self):
		super(Tower, self).render()
		if self.mouse_over:
		# if True:
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

class BasicTower (Tower):
	color = tcod.dark_green
	missile = BasicMissile
	cost = 1

class ResearchBuilding (Building):
	color = tcod.dark_sepia
	cost = 1

	def __init__ (self, *args):
		super(ResearchBuilding, self).__init__(*args)
		self.timer = self.state.timers.start(1000, self._research)

	def _research (self):
		pass

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
	cost = 2

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
	cost = 1

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
		elif getattr(self, 'rollback_timer', False):
			self.rollback_timer.reset()
