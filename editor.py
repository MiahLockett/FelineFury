import pygame
import sys 

from utility import * #imports all of utility.py
from tilemap import * #imports all of tilemap.py


RENDER_SCALE = 2.0

class Editor:
	def __init__(self):

		pygame.init() #initialises pygame

		pygame.display.set_caption('editor')
		self.screen = pygame.display.set_mode((640, 480)) #self. makes it an attribute of the object (Game)

		self.display = pygame.Surface((320, 240)) 
		#pygame.surface generates an empty image of selected dimension, it's all black
		#making the numbers bigger makes the image smaller

		
		self.clock = pygame.time.Clock()


		self.assets = {
			'decor': load_images('/tiles/decor'),
			'grass': load_images('/tiles/grass'),
			'large_decor': load_images('/tiles/large_decor'),
			'stone': load_images('/tiles/stone'),
			'spawners' : load_images('/tiles/spawners'),
			}

		#print(self.assets)

		self.movement = [False, False, False, False] #camera movement

		self.tilemap = Tilemap(self, tile_size=16)

		try:
			self.tilemap.load('resources/maps/6.json') #only load map if it exists
		except FileNotFoundError:
			pass

		self.scroll = [0,0]

		self.tile_list = list(self.assets) #converts assets into list of stated values
		self.tile_group = 0 #which tile
		self.tile_variant = 0 #which tile within that group

		self.clicking = False
		self.right_clicking = False
		self.shift = False
		self.ongrid = True


	def run(self):
		while True:
			
			self.display.fill((0, 0, 0))  #bg is black

			self.scroll[0] += (self.movement[1] - self.movement[0]) * 2
			self.scroll[1] += (self.movement[3] - self.movement[2]) * 2

			render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

			self.tilemap.render(self.display, offset=render_scroll)

			#showing which tile we have selected
			current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy() #copying as want to show it with an alpha
			current_tile_img.set_alpha(100) #sets so img is partially transparent so we can see whats behind it

			mpos = pygame.mouse.get_pos() #gives pixel coords of mouse with top left being 0,0
			mpos = (mpos[0] / RENDER_SCALE, mpos[1] / RENDER_SCALE)
			tile_pos = (int((mpos[0] + self.scroll[0]) // self.tilemap.tile_size), int((mpos[1] + self.scroll[1]) // self.tilemap.tile_size))


			if self.ongrid:
				self.display.blit(current_tile_img, (tile_pos[0] * self.tilemap.tile_size - self.scroll[0], tile_pos[1] * self.tilemap.tile_size - self.scroll[1])) #converts tile_pos back into pixel coords then adjusting by camera for rendering
			else:
				self.display.blit(current_tile_img, mpos)


			if self.clicking and self.ongrid:
				self.tilemap.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1])] = {'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': tile_pos}
			if self.right_clicking:
				tile_loc = str(tile_pos[0]) + ';' + str(tile_pos[1])
				if tile_loc in self.tilemap.tilemap:
					del self.tilemap.tilemap[tile_loc]
				for tile in self.tilemap.offgrid_tiles.copy():
					tile_img = self.assets[tile['type']][tile['variant']]
					tile_r = pygame.Rect(tile['pos'][0] - self.scroll[0], tile['pos'][1] - self.scroll[1], tile_img.get_width(), tile_img.get_height()) #converting world space into display space
					if tile_r.collidepoint(mpos): #if tile is colliding with my mouse
						self.tilemap.offgrid_tiles.remove(tile)

			self.display.blit(current_tile_img, (5, 5))
	

			for event in pygame.event.get(): #gets the input from windows so the window doesnt freeze
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit

				if event.type == pygame.MOUSEBUTTONDOWN:
					if event.button == 1: #left click
						self.clicking = True
						if not self.ongrid:
							self.tilemap.offgrid_tiles.append({'type' : self.tile_list[self.tile_group], 'variant' : self.tile_variant, 'pos' : (mpos[0] + self.scroll[0], mpos[1] + self.scroll[1])})
					if event.button == 3: #right click
						self.right_clicking = True

					if self.shift: #if pressing shift, scroll through variants
						if event.button == 4: #scroll up
							self.tile_variant = (self.tile_variant -1) % len(self.assets[self.tile_list[self.tile_group]]) #% helps loop
						if event.button == 5: #scroll down
							self.tile_variant = (self.tile_variant + 1) % len(self.assets[self.tile_list[self.tile_group]])
					else: #if not pressing shift, scroll through group
						if event.button == 4: #scroll up
							self.tile_group = (self.tile_group -1) % len(self.tile_list) #% helps loop
							self.tile_variant = 0
						if event.button == 5: #scroll down
							self.tile_group = (self.tile_group + 1) % len(self.tile_list)
							self.tile_variant = 0

				if event.type == pygame.MOUSEBUTTONUP:
					if event.button == 1:
						self.clicking = False
					if event.button == 3:
						self.right_clicking = False	

		
    					
				if event.type == pygame.KEYDOWN: #event type for a button press
					if event.key == pygame.K_a:#the w allows WASD to be used
						self.movement[0] = True
					if event.key == pygame.K_d:
						self.movement[1] = True
					if event.key == pygame.K_w:
						self.movement[2] = True
					if event.key == pygame.K_s:
						self.movement[3] = True
					if event.key == pygame.K_g:
						self.ongrid = not self.ongrid #if you press g it switches if its on grid or not
					if event.key == pygame.K_t:
					 	self.tilemap.autotile()
					if event.key == pygame.K_o:
						self.tilemap.save('new.json') #o key for saving map
					if event.key == pygame.K_LSHIFT:
						self.shift = True

				if event.type == pygame.KEYUP: #key lifted up instead of down
					if event.key == pygame.K_a:
						self.movement[0] = False
					if event.key == pygame.K_d:
						self.movement[1] = False
					if event.key == pygame.K_w:
						self.movement[2] = False
					if event.key == pygame.K_s:
						self.movement[3] = False
					if event.key == pygame.K_LSHIFT:
						self.shift = False	


			self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))			
			pygame.display.update() #updates display as by default screen is black
			self.clock.tick(60) #60 fps

Editor().run()