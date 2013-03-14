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
		
class BaitAbility (Ability):
	action_time = 1000000000
	
	def use (self):
		bait = towers.Bait(self.state, self.x, self.y)
		self.state.entities.append(bait)
		def rollback ():
			bait.die()
		self.state.timers.start_run_once(self.action_time, rollback)
			
	def render (self):
		pass
