
# For this, I copy and pasted my code from game.py and made adjustments to save time instead of rewriting code to do the exact same thing

import pygame
import sys 
import random
import math
import os

from utility import * #imports all of utility.py
from entities import * #imports all of entities.py
from tilemap import * #imports all of tilemap.py
from clouds import * #imports all of clouds.py
from particle import * #imports all of particle.py
from spark import * #imports all of spark.py



class FinalLevel:
	
	def __init__(self):

		pygame.init() #initialises pygame

		pygame.display.set_caption('Feline Fury')
		self.screen = pygame.display.set_mode((640, 480), pygame.RESIZABLE) #self. makes it an attribute of the object (FinalLevel)

		self.display = pygame.Surface((320, 240)) 
		#pygame.surface generates an empty image of selected dimension, it's all black
		#making the numbers bigger makes the image smaller

		self.movement = [False, False] #Using lists

		#Using a dictionary
		self.assets = {
			'decor': load_images('/tiles/decor'),
			'grass': load_images('/tiles/grass'),
			'large_decor': load_images('/tiles/large_decor'),
			'stone': load_images('/tiles/stone'),
			'player' : load_image('/entities/cat2.png'),
			'background' : load_image('/background.png'),
			'clouds' : load_images('/clouds'),
			'player/idle' : Animation([load_image('/entities/player/cat_idle/cat_idle.png')], img_dur=4),
			'player/cat_left' : Animation(load_images('/entities/player/cat_left'), img_dur=4),
			'player/run' : Animation(load_images('/entities/player/cat_right'), img_dur=4),
			'player/jump' : Animation([load_image('/entities/cat2.png')], img_dur=4),
			'player/wall_slide' : Animation([load_image('/entities/cat2.png')], img_dur=4),
			'particle/leaf' : Animation(load_images('/particles/leaf'), img_dur=20, loop=False),
			'particle/particle' : Animation(load_images('/particles/particle'), img_dur=6, loop=False),
			}

		self.sfx = {
			'jump': pygame.mixer.Sound('resources/sfx/jump.wav'),
			'dash' : pygame.mixer.Sound('resources/sfx/dash.wav')
		}

		self.sfx['jump'].set_volume(0.5)
		self.sfx['dash'].set_volume(0.5)

		self.clouds = Clouds(self.assets['clouds'], count=16)

		self.player = Player(self, (50, 50), (8, 15)) #8 by 15 is its size, (50, 50) is its position

		self.tilemap = Tilemap(self, tile_size=16)
		
		self.load_celebration_level()

		self.screenshake = 0


	def load_celebration_level(self):
		self.tilemap.load('resources/maps/CelebrateLevel.json')

		pygame.mixer.music.fadeout(500) #fade music out

		#loading celebration music
		celebration_music = 'resources/celebrate.mp3'
		if os.path.exists(celebration_music):
			pygame.time.wait(550)
			pygame.mixer.music.load(celebration_music)
			pygame.mixer.music.set_volume(0.3)
			pygame.mixer.music.play(-1)

		#spawning leafs to fall out of trees
		self.leaf_spawners = []
		for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
			self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))

		#spawning player
		for spawner in self.tilemap.extract([('spawners', 0)]):
			self.player.pos = spawner['pos']
			self.player.air_time = 0

		#leaf falling 
		self.particles = []

		#spark effect
		self.sparks = []

		self.clock = pygame.time.Clock()
		self.font = pygame.freetype.SysFont(None, 18)
		self.font.origin = True

		self.scroll = [0,0]
		self.dead = 0


	def run(self):
	
		while True:
			
			self.display.blit(self.assets['background'], (0,0)) 

			self.screenshake = max(0, self.screenshake - 1)
			
            #respawn player after death
			if self.dead:
				self.dead += 1
				if self.dead >= 40:
					self.load_celebration_level()
			
			#CAMERA FOCUSING ON PLAYER
			self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0] )
			self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1] ) 
			
			#fixing camera being 'wobbly'
			render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

			for rect in self.leaf_spawners: #for loops
				if random.random() * 49999 < rect.width * rect.height:
					pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height) 
					self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))

			self.clouds.update()
			self.clouds.render(self.display, offset=render_scroll)

			self.tilemap.render(self.display, offset=render_scroll)
			
            #displaying celebration message
			celebration_text = "You've completed all levels!"
			self.font.render_to(self.display, (45, 40), celebration_text, pygame.Color('darkgreen'))

			if not self.dead:
				self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
				self.player.render(self.display, offset=render_scroll)
				
            #player dies when falling off the edge
			if self.player.air_time > 120:
				self.dead = 1

			for spark in self.sparks.copy():
				kill = spark.update()
				spark.render(self.display, offset=render_scroll)
				if kill:
					self.sparks.remove(spark)

			for particle in self.particles.copy():
				kill = particle.update()
				particle.render(self.display, offset=render_scroll)
				if particle.type == 'leaf':
					particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
				if kill:
					self.particles.remove(particle)

			for event in pygame.event.get(): #gets the input from windows so the window doesnt freeze
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit
				if event.type == pygame.KEYDOWN: #event type for a button press
					if event.key == pygame.K_a:
						self.movement[0] = True
					if event.key == pygame.K_d:
						self.movement[1] = True
					if event.key == pygame.K_SPACE: #jump
						if self.player.jump():
							self.sfx['jump'].play()
					if event.key == pygame.K_x:
						if self.player.dash():
							self.sfx['dash'].play()
					if event.key == pygame.K_ESCAPE: #press ESC to return to main menu
						pygame.mixer.music.fadeout(500)
						pygame.time.wait(500)
						pygame.quit()
						pygame.init()
						return
                 
				if event.type == pygame.KEYUP: #key lifted up instead of down
					if event.key == pygame.K_a:
						self.movement[0] = False
					if event.key == pygame.K_d:
						self.movement[1] = False

			screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
			self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), screenshake_offset) 			
			pygame.display.update() #updates display as by default screen is black
			self.clock.tick(60) #60 fps, frame rate control

FinalLevel().run()

