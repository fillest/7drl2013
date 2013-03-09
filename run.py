#coding: utf-8
import sys
import os
os.chdir("libtcod-1.5.2")
# sys.path.append("tcod-1.5.2/python") 
sys.path.append("python") 
import libtcodpy as tcod
libtcod = tcod
import random
from random import randint
import util


tile_types = dict(
	grass = dict(
		sym = '.',
		color = tcod.darker_green,
	)
)

class state (object):
	pass

def run ():
	tcod.sys_set_fps(60)
	tcod.console_set_custom_font('data/fonts/dejavu16x16_gs_tc.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)
	tcod.console_init_root(80, 50, 'TD RL', False)

	# c1 = tcod.Color(255, 255, 255)
	# tcod.console_set_default_background(0, c1)
	# tcod.console_clear(0)


	w, h = 60, 40
	world_map = [
		['grass'] * w,
	] * h


	state.timers = util.Timers()
	state.is_paused = False


	entities = []

	#enemies
	def spawn_enemy ():
		x = random.choice(range(0, 3 + 1) + range(48, 50 + 1))
		y = random.choice(range(0, 3 + 1) + range(28, 30 + 1))
		entities.append(util.Enemy(state, x, y, 'r'))
	state.timers.start(1000, spawn_enemy)

	entities.append(util.Enemy(state, 1, 1, '@'))
	entities.append(util.Enemy(state, 1, 15, '@'))


	#towers
	class Tower (util.Entity):
		def __init__(self, *args):
			super(Tower, self).__init__(*args)
			self.targeted = set()

		def update (self):
			for e in entities:
				if isinstance(e, util.Enemy) and e not in self.targeted:
					self.targeted.add(e)
					state.timers.start(1200, self._shoot, [e])

		def _shoot (self, e):
			m = util.Entity(state, 20, 20, '*', tcod.yellow)
			entities.append(m)

			def update_missile ():
				tcod.line_init(m.x, m.y, e.x, e.y)
				x, y = tcod.line_step()
				if x is None:
					entities.remove(m)
					return True

				m.x = x
				m.y = y
			missile_speed = 20
			state.timers.start(missile_speed, update_missile)

	entities.append(Tower(state, 20, 20, '@', tcod.dark_green))


	#panel
	pan_w = 50
	pan_h = 10
	panel = tcod.console_new(pan_w, pan_h)
	tcod.console_set_default_foreground(panel, tcod.white)

	tcod.console_set_default_background(panel, tcod.Color(5, 5, 5))
	tcod.console_rect(panel, 0, 0, pan_w, pan_h, False, tcod.BKGND_SCREEN)
	# tcod.console_set_default_background(panel, tcod.black)


	key = tcod.Key()
	mouse = tcod.Mouse()
	while not tcod.console_is_window_closed():
		#handle input
		ev = tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE, key, mouse) #TODO loop?
		if key.vk == tcod.KEY_ESCAPE:
			break
		elif key.vk == tcod.KEY_SPACE:
			state.is_paused = not state.is_paused

			new_msg_lines = textwrap.wrap("hellokitten and fuck you", 5)


		if mouse.lbutton_pressed:
			print "left mouse, cell:", mouse.cx, mouse.cy

		#update
		if not state.is_paused:
			for t in list(state.timers):
				if t.update():
					state.timers.remove(t)

		for e in entities:
			e.update()

		#render
		for y, row in enumerate(world_map):
			for x, tile_type in enumerate(row):
				tcod.console_put_char(0, x + 1, y + 1, tile_types[tile_type]['sym'], tcod.BKGND_NONE)
				tcod.console_set_char_foreground(0, x + 1, y + 1, tile_types[tile_type]['color'])
				# tcod.console_put_char_ex(0, x + 1, y + 1, cell, color.grass, 0)

		for e in entities:
			e.render()

		tcod.console_print_ex(panel, 0, 0, libtcod.BKGND_NONE, libtcod.LEFT, "123 The quick brown fox jumps over the lazy dog.")
		# tcod.console_print_ex(panel, 0, 1, libtcod.BKGND_NONE, libtcod.LEFT, "Эх, чужд кайф, сплющь объём вши, грызя цент.")
		tcod.console_blit(panel, 0, 0, pan_w, pan_h, 0, 0, 40)


		tcod.console_flush()

if __name__ == '__main__':
	run()