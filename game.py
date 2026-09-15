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
from database import * #imports all of database.py
from DatabaseConnection import * #imports all of DatabaseConnection.py



class Game:
	
	def __init__(self, id_value: int): #Using encapsulation by using self to create instance attributes
		self.id_value = id_value

		pygame.init() #initialises pygame

		pygame.display.set_caption('Feline Fury')
		self.screen = pygame.display.set_mode((640, 480), pygame.RESIZABLE) #self. makes it an attribute of the object (Game)

		self.display = pygame.Surface((320, 240)) 
		#pygame.surface generates an empty image of selected dimension, it's all black
		#making the numbers bigger makes the image smaller
		#Begin usering pygame rendering

		

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
			'enemy/idle' : Animation(load_images('/entities/enemy/idle'), img_dur=50),
			'enemy/run' : Animation(load_images('/entities/enemy/run'), img_dur=6),		
			'gun' :	load_image('/gun.png'),
			'projectile' : load_image('/projectile.png'),
			}

		#print(self.assets)

		self.sfx = {
			'jump': pygame.mixer.Sound('resources/sfx/jump.wav'),
			'shoot': pygame.mixer.Sound('resources/sfx/shoot.wav'),
			'hit' : pygame.mixer.Sound('resources/sfx/hit.wav'),
			'dash' : pygame.mixer.Sound('resources/sfx/dash.wav')
		}

		self.sfx['jump'].set_volume(0.5)
		self.sfx['shoot'].set_volume(0.5)
		self.sfx['hit'].set_volume(0.7)
		self.sfx['dash'].set_volume(0.5)

		self.clouds = Clouds(self.assets['clouds'], count=16)

		self.player = Player(self, (50, 50), (8, 15)) #8 by 15 is its size, (50, 50) is its position

		self.tilemap = Tilemap(self, tile_size=16)
		
		self.music_tracks = {
		0: 'resources/level1.mp3',
		1 : 'resources/level2.mp3',
		2: 'resources/level3.mp3',
		3 : 'resources/level4.mp3',
		4 : 'resources/level5.mp3',
		'default' : 'resources/level1.mp3' #fallback music
		}

		self.level = 0
		self.load_level(self.level)

		self.music = 0

		self.screenshake = 0


	def save_time(self, level_time):
		user_id = self.id_value



	def load_level(self, map_id):
		self.tilemap.load('resources/maps/' + str(map_id) + '.json')

		pygame.mixer.music.fadeout(500) #fade music out

		#loading new music for each level
		music_file = self.music_tracks.get(map_id)
		if music_file and os.path.exists(music_file): #using os.path,exists() is used for file operation
			pygame.time.wait(550)
			pygame.mixer.music.load(music_file)
			pygame.mixer.music.set_volume(0.2)
			pygame.mixer.music.play(-1)
		else:
			pygame.time.wait(550)
			pygame.mixer.music.load(self.music_tracks['default'])
			pygame.mixer.music.set_volume(0.2)
			pygame.mixer.music.play(-1)

		   # RESET THE TIMER:
		self.level_start_time = pygame.time.get_ticks()  # Store when the level started
		self.level_completed = False

			#spawning leafs to fall out of trees
		self.leaf_spawners = []
		for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
			self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))
		print(self.leaf_spawners)	

		#spawning enemies
		self.enemies = []
		for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
			if spawner['variant'] == 0:
				self.player.pos = spawner['pos']
				self.player.air_time = 0
			else:
				self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))	

		#bullets for the gun
		self.projectiles = []

		#leaf falling 
		self.particles = []

		#spark effect for when you are shot
		self.sparks = []

		self.clock = pygame.time.Clock()
		self.font = pygame.freetype.SysFont(None, 20)
		self.font.origin = True


		self.scroll = [0,0]
		self.dead = 0
		self.transition = -30 #initial transition for moving onto level



	def run(self):
	
		while True:
			
			self.display.blit(self.assets['background'], (0,0)) 

			self.screenshake = max(0, self.screenshake - 1)

			#adding timer - asked AI for help on what logic to use (such as getting the full running time and taking away the level time)
			current_time = pygame.time.get_ticks() #since game began running
			if hasattr(self, 'level_start_time'): #hasattr returns true or false (so if level_start_time is same as pygame.time.get_tickets()), It is a method of type checking
				level_time = current_time - self.level_start_time #then the level_time is now the total running time minus the time of the last level
			else:
				level_time = current_time #otherwise the level_time is the same as total time it has been running
    
    		#calculating time
			millis = level_time % 1000
			seconds = int(level_time / 1000 % 60)
			minutes = int(level_time / 60000 % 24)
			#formatting how the stopwatch is displayed
			out = '{minutes:02d}:{seconds:02d}:{millis:03d}'.format(minutes=minutes, seconds=seconds, millis=millis) #String Formatting
			#displaying stopwatch
			#self.font.render_to(self.display, (10, 25), out, pygame.Color('darkgreen'))
			

			
			# THIS RUNS WHEN ALL CHICKENS HAVE BEEN KILLED SO YOU PROGRESS TO NEXT LEVEL
			#loading onto the next level
			if not len(self.enemies): #YOU HAVE TO KILL ALL THE ENEMIES TO MOVE ON
				self.transition += 1
				if self.transition > 30:
						# CODE HERE TO SAVE TIME AND USERNAME TO DATABASE
						save_time(self.id_value, level_time, self.level)

					
						#self.level = min(self.level + 1, len(os.listdir('resources/maps')))
						max_level = len(os.listdir('resources/maps')) - 2
						if self.level < max_level:
							self.level += 1
							self.load_level(self.level)
						else:
							# Load the celebration level instead of quitting
							pygame.mixer.music.fadeout(500)
							pygame.time.wait(500)
							pygame.quit()  # Fully quit pygame
							pygame.init()  # Reinitialize pygame
							from FinalLevel import FinalLevel
							final = FinalLevel()
							final.run()
							return
					
			


			if self.transition < 0: #conditional statement
				self.transition += 1

			#only have 1 life
			if self.dead:
				self.dead += 1
				if self.dead >= 40:
					self.load_level(self.level)

			#CO-ORDINATES: TOP LEFT IS 0,0 - DIFF FROM MATHS. RIGHT IS +X AND DOWN IS +Y
			
			#CAMERA FOCUSING ON PLAYER
			self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0] )  #taking where we want camera to be then subtracting what we have. All of this is being added to the scroll. SETS CAMERA TO WHERE WE WANT TO BE
			self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1] ) 
			
			#fixing camera being 'wobbly'
			render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

			for rect in self.leaf_spawners: #for loops
				if random.random() * 49999 < rect.width * rect.height: #by multiplying by a big number, it means the particles wont spawn every single frame
					pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height) 
					self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))

			self.clouds.update()
			self.clouds.render(self.display, offset=render_scroll)

			#displaying stopwatch
			self.font.render_to(self.display, (10, 25), out, pygame.Color('darkgreen'))

			self.tilemap.render(self.display, offset=render_scroll)

			for enemy in self.enemies.copy():
				kill = enemy.update(self.tilemap, (0,0))
				enemy.render(self.display, offset=render_scroll)
				if kill:
					# UNCOMMENT BELOW LINE TO MAKE GAME SAVE TIME ON KILL OF SINGLE CHICKEN
					#save_time(self.id_value, current_time, self.level)

					self.enemies.remove(enemy)

			if not self.dead:
				self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
				self.player.render(self.display, offset=render_scroll)	#allows player to render + update

			#print(self.tilemap.physics_rects_around(self.player.pos)) #allows to see the tiles around player

			# for the bullets I will use [[x,y], direction, timer]
			for projectile in self.projectiles.copy(): #event type checking
				projectile[0][0] += projectile[1]
				projectile[2] += 1
				img = self.assets['projectile']
				self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1])) #using / 2 centers img. 
				#making it disappear if it hits a wall
				if self.tilemap.solid_check(projectile[0]):
					self.projectiles.remove(projectile)
					for i in range(4):
						self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 +  random.random()))
				elif projectile[2] > 360: #if timer is greater than 360
					self.projectiles.remove(projectile)
				elif abs(self.player.dashing) < 50: #if it hits the player BUT if they are dashing they are invisible
					if self.player.rect().collidepoint(projectile[0]):
						self.projectiles.remove(projectile)
						self.dead += 1
						#when projectile hits player
						self.sfx['hit'].play()
						for i in range(30):
							angle = random.random() * math.pi * 2
							speed = random.random() * 5
							self.sparks.append(Spark(self.player.rect().center, angle, 2 +  random.random()))
							self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))


				for spark in self.sparks.copy():
					kill = spark.update()
					spark.render(self.display, offset=render_scroll)
					if kill:
						self.sparks.remove(spark)

			for particle in self.particles.copy():
				kill = particle.update()
				particle.render(self.display, offset=render_scroll)
				if particle.type == 'leaf':
					particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3 #using the sin function smoothly goes between -1 and 1 so the leaf has a more natural pattern
				if kill:
					self.particles.remove(particle)


			for event in pygame.event.get(): #gets the input from windows so the window doesnt freeze
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit
				if event.type == pygame.KEYDOWN: #event type for a button press
					if event.key == pygame.K_a:#the w allows WASD to be used
						self.movement[0] = True
					if event.key == pygame.K_d:
						self.movement[1] = True
					if event.key == pygame.K_SPACE: #jump
						if self.player.jump():
							self.sfx['jump'].play()
					if event.key == pygame.K_x:
						if self.player.dash(): #use x to dash to defeat enemies
							self.sfx['dash'].play()
                 
				if event.type == pygame.KEYUP: #key lifted up instead of down
					if event.key == pygame.K_a:
						self.movement[0] = False
					if event.key == pygame.K_d:
						self.movement[1] = False

		
			#creating the circle transition
			if self.transition:
				transition_surf = pygame.Surface(self.display.get_size())
				pygame.draw.circle(transition_surf, (255, 255, 255), (self.display.get_width() // 2, self.display.get_height() // 2), (30 - abs(self.transition)) * 8)
				transition_surf.set_colorkey((255, 255, 255))
				self.display.blit(transition_surf,(0, 0))

			screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
			self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), screenshake_offset) 			
			pygame.display.update() #updates display as by default screen is black
			self.clock.tick(60) #60 fps, frame rate control

#Game().run()