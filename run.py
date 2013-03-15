#coding: utf-8
import sys
import os
import platform
if '32' in platform.architecture()[0]:
	os.chdir("libtcod32-1.5.2")
else:
	os.chdir("libtcod-1.5.2")
# sys.path.append("tcod-1.5.2/python") 
sys.path.append("python") 
import libtcodpy as tcod
import random
from random import randint
import util
import math
import towers
import enemies
import abilities

FPS_LIMIT = 60
WINDOW_TITLE = "TD RL"


tile_types = dict(
	grass = dict(
		sym = '.',
		color = tcod.darker_green,
	)
)

class state (object):
	pass

class Popup (object):
	width = 10
	height = 5
	x = 0
	y = 0
	text = None

	def __init__ (self):
		self.obj = tcod.console_new(self.width, self.height)
		tcod.console_set_default_foreground(self.obj, tcod.white)

		tcod.console_set_default_background(self.obj, tcod.Color(5, 5, 5))
		tcod.console_rect(self.obj, 0, 0, self.width, self.height, False, tcod.BKGND_SCREEN)

	def set_params (self, x, y, text):
		self.text = text
		self.x = x
		self.y = y

	def show (self):
		if self.text:
			tcod.console_print_ex(self.obj, 0, 0, tcod.BKGND_OVERLAY, tcod.LEFT, self.text)
			tcod.console_blit(self.obj, 0, 0, self.width, self.height, 0, self.x, self.y)
		tcod.console_clear(self.obj)
		self.text = None


class Map (object):
	def __init__ (self, w, h):
		assert w % 2 == 1, "heart is in the center of map"
		assert h % 2 == 1, "heart is in the center of map"
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
	os.putenv('SDL_VIDEO_CENTERED', '1')
	tcod.sys_set_fps(FPS_LIMIT)
	tcod.console_set_custom_font('data/fonts/dejavu16x16_gs_tc.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)
	tcod.console_init_root(60, 50, WINDOW_TITLE, False)
	

	# c1 = tcod.Color(255, 255, 255)
	# tcod.console_set_default_background(0, c1)
	# tcod.console_clear(0)


	state.timers = util.Timers()
	state.is_paused = False
	state.map = Map(41, 41)
	state.entities = entities = util.Entities()
	state.energy = 10


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
	state.enemy_i = 0
	
	def spawn_enemy_group (start_x, start_y, rows, cols):
		es = [random.choice([enemies.Wolf, enemies.Rat]) for _ in range(rows * cols)]
		
		y = start_y
		for c in range(cols):
			x = start_x
			for r in range(rows):
				entities.append(es[c + r](state, x, y))
				x += 1
			y += 1
	
	def spawn_enemy ():
		if random.random() >= 0.8:
			x, y = random.choice(map_sides)()
			rows = random.randint(1, 4)
			cols = random.randint(1, 4)
			spawn_enemy_group(x, y, rows, cols)

			state.enemy_i += rows * cols

		# x, y = random.choice(map_sides)()
		x, y = random.choice([(5,5), (6,5)])
		entities.append(enemies.Rat(state, x, y))
		
		if state.enemy_i > 4:
			x, y = random.choice(map_sides)()
			entities.append(enemies.Wolf(state, x, y))

			state.enemy_i += 1

		state.enemy_i += 1
	state.timers.start(500, spawn_enemy)


	#towers
	heart = towers.Heart(state, state.map.w // 2, state.map.h // 2)
	entities.append(heart)
	state.heart = heart

	towers.BasicTower(state, heart.x - 1, heart.y).put()
	towers.ResearchBuilding(state, heart.x + 1, heart.y).put()
	towers.IceTower(state, heart.x, heart.y - 1).put()
	towers.AoeTower(state, heart.x, heart.y + 1).put()


	#panel
	pan_w = 50
	pan_h = 6
	panel = tcod.console_new(pan_w, pan_h)
	tcod.console_set_default_foreground(panel, tcod.white)

	tcod.console_set_default_background(panel, tcod.Color(5, 5, 5))
	tcod.console_rect(panel, 0, 0, pan_w, pan_h, False, tcod.BKGND_SCREEN)
	# tcod.console_set_default_background(panel, tcod.black)

	popup = Popup()

	def map_to_entity (cx, cy):
		for e in state.entities:
			if (e.x, e.y) == (cx, cy):
				return e

	key = tcod.Key()
	mouse = tcod.Mouse()
	while not tcod.console_is_window_closed():
		#handle input
		ev = tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE, key, mouse) #TODO loop?
		if key.vk == tcod.KEY_ESCAPE:
			break
		elif key.vk == tcod.KEY_SPACE:
			if state.is_paused:
				state.timers.resume()
			else:
				state.timers.pause()
			state.is_paused = not state.is_paused

		entity_under_mouse = map_to_entity(mouse.cx, mouse.cy)
		if entity_under_mouse:
			px, py = mouse.cx, mouse.cy
			#if isinstance(entity_under_mouse, util.Building):
			popup.set_params(px, py, entity_under_mouse.__class__.__name__)

		if mouse.lbutton_pressed:
			print "left mouse, cell:", mouse.cx, mouse.cy

			e = map_to_entity(mouse.cx, mouse.cy)
			if not isinstance(e, towers.Building):
				# towers.ResearchTower(state, mouse.cx, mouse.cy).put()

				a = abilities.BaitAbility(None, state, mouse.cx, mouse.cy)
				a.use()
		elif mouse.rbutton_pressed:
			e = map_to_entity(mouse.cx, mouse.cy)
			if isinstance(e, towers.Tower):
				e.delete()

		for e in entities:
			if e.x == mouse.cx and e.y == mouse.cy:
				e.mouse_over = True
			else:
				e.mouse_over = False

		#update
		if not state.is_paused:
			state.timers.update()

		if not state.is_paused:
			for e in entities:
				e.update()

		#render
		tcod.console_clear(0)  #TODO dont use?

		state.map.render()

		for e in entities:
			e.render()

		if state.is_paused:
			tcod.console_print_ex(0, 0, 0, tcod.BKGND_NONE, tcod.LEFT, "paused")
		else:
			tcod.console_print_ex(0, 0, 0, tcod.BKGND_NONE, tcod.LEFT, " " * len("paused"))

		tcod.console_print_ex(0, 14, 0, tcod.BKGND_NONE, tcod.LEFT, "energy: %s" % state.energy)

		tcod.console_print_ex(panel, 0, 0, tcod.BKGND_NONE, tcod.LEFT, "123 The quick brown fox jumps over the lazy dog.")
		tcod.console_print_ex(panel, 0, 2, tcod.BKGND_NONE, tcod.LEFT, "Adviser: Eew! Rats.. I have musophobia, I told you.")
		# tcod.console_print_ex(panel, 0, 1, tcod.BKGND_NONE, tcod.LEFT, "Эх, чужд кайф, сплющь объём вши, грызя цент.")
		tcod.console_blit(panel, 0, 0, pan_w, pan_h, 0, 0, 43)
		popup.show()


		tcod.console_flush()

if __name__ == '__main__':
	run()
