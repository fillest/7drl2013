import util

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
