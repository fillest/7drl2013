import util
import towers

class Ability (util.Entity):
	action_time = 0
	
	def __init__ (self, target, *args):
		super(Ability, self).__init__(*args)
		self.target = target
	
	def use (self):
		self.state.entities.append(self)
		def rollback ():
			self.state.entities.remove(self)
		self.state.timers.start_run_once(self.action_time, rollback)	
		
class FakeHeartAbility (Ability):
	action_time = 1000000000
	
	def use (self):
		fake_heart = towers.FakeHeart(self.state, self.x, self.y)
		self.state.heart = fake_heart
		self.state.entities.append(fake_heart)
		def rollback ():
			fake_heart.die()
		self.state.timers.start_run_once(self.action_time, rollback)
			
	def render (self):
		pass
