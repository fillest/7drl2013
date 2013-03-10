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
import math


tile_types = dict(
	grass = dict(
		sym = '.',
		color = tcod.darker_green,
	)
)

class state (object):
	pass

class Map (object):
	def __init__ (self, w, h):
		assert w % 2 == 1
		assert h % 2 == 1
		self.w = w
		self.h = h

		self.tiles = [
			['grass'] * w,
		] * h

	def render (self):
		for y, row in enumerate(self.tiles):
			for x, tile_type in enumerate(row):
				tcod.console_put_char(0, x, y, tile_types[tile_type]['sym'], tcod.BKGND_NONE)
				tcod.console_set_char_foreground(0, x, y, tile_types[tile_type]['color'])
				# tcod.console_put_char_ex(0, x + 1, y + 1, cell, color.grass, 0)

def run ():
	tcod.sys_set_fps(60)
	tcod.console_set_custom_font('data/fonts/dejavu16x16_gs_tc.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)
	tcod.console_init_root(80, 50, 'TD RL', False)

	# c1 = tcod.Color(255, 255, 255)
	# tcod.console_set_default_background(0, c1)
	# tcod.console_clear(0)


	state.timers = util.Timers()
	state.is_paused = False
	state.map = Map(41, 41)
	entities = []


	#enemies
	map_sides = [
		#top
		lambda: (randint(0, state.map.w - 1), 0),
		#bottom
		lambda: (randint(0, state.map.w - 1), state.map.h - 1),
		#left
		lambda: (0, randint(0, state.map.h - 1)),
		#right				
		lambda: (state.map.w - 1, randint(0, state.map.h - 1)),			
	]
	def spawn_enemy ():
		x, y = random.choice(map_sides)()
		entities.append(util.Enemy(state, x, y, 'r'))
	state.timers.start(500, spawn_enemy)


	#towers
	class Tower (util.Entity):
		def __init__(self, *args):
			super(Tower, self).__init__(*args)
			self.cooldown = False

		def update (self):
			if not self.cooldown:
				dist_min = 9000
				target = None
				for e in entities:
					if isinstance(e, util.Enemy):
						dist = util.dist(self.x, self.y, e.x, e.y)
						if dist < dist_min:
							dist_min = dist
							target = e
				
				if target:
					self._shoot(target)

		def _shoot (self, e):
			self.cooldown = True
			def clear_cd ():
				self.cooldown = False
				return True
			state.timers.start(1000, clear_cd)

			m = util.Entity(state, self.x, self.y, '*', tcod.yellow)
			entities.append(m)

			def update_missile ():
				tcod.line_init(m.x, m.y, e.x, e.y)
				x, y = tcod.line_step()
				if x is None:
					entities.remove(m)

					if e in entities:
						entities.remove(e)
					
					return True
				else:
					m.x = x
					m.y = y
			missile_speed = 20
			state.timers.start(missile_speed, update_missile)

	heart = util.Entity(state, state.map.w // 2, state.map.h // 2, 'O', tcod.darker_red)
	entities.append(heart)

	entities.append(Tower(state, heart.x - 1, heart.y, '@', tcod.dark_green))
	entities.append(Tower(state, heart.x + 1, heart.y, '@', tcod.dark_green))
	entities.append(Tower(state, heart.x, heart.y - 1, '@', tcod.dark_green))
	entities.append(Tower(state, heart.x, heart.y + 1, '@', tcod.dark_green))


	#panel
	pan_w = 50
	pan_h = 6
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
			#TODO after log pause shoots two times -- its now remade but seems timer+pause is buggy

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
		state.map.render()

		for e in entities:
			e.render()

		if state.is_paused:
			tcod.console_print_ex(0, 0, 0, libtcod.BKGND_NONE, libtcod.LEFT, "paused")
		else:
			tcod.console_print_ex(0, 0, 0, libtcod.BKGND_NONE, libtcod.LEFT, " " * 10)

		tcod.console_print_ex(panel, 0, 0, libtcod.BKGND_NONE, libtcod.LEFT, "123 The quick brown fox jumps over the lazy dog.")
		# tcod.console_print_ex(panel, 0, 1, libtcod.BKGND_NONE, libtcod.LEFT, "Эх, чужд кайф, сплющь объём вши, грызя цент.")
		tcod.console_blit(panel, 0, 0, pan_w, pan_h, 0, 0, 43)


		tcod.console_flush()

if __name__ == '__main__':
	run()