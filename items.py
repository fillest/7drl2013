import libtcodpy as tcod
import util

class Item (util. Entity):
	color = tcod.red
	sym = '$'
	
	def __init__ (self, *args):
		super(Item, self).__init__(*args)
		
	def pick_up (self):
		self.state.inventory.append(self)
		self.state.entities.remove(self)
		
class EnergyItem (Item):
	put_to_inventory = False
	
	def pick_up (self):
		self.state.energy += 1
		self.state.entities.remove(self)
