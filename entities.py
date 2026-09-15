import pygame
#side note: rects only work with integers
from particle import *
import math
import random
from spark import *

class PhysicsEntity:
	def __init__(self, game, e_type, pos, size):
		self.game = game 
		self.type = e_type
		self.pos = list(pos) #using a list as position can change
		self.size = size
		self.velocity = [0, 0] #rate of change of position
		self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

		self.action = ''
		self.anim_offset = (-3, -3)
		self.flip = False
		self.set_action('idle')


	def rect(self):
		return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

	def set_action(self, action):
		if action != self.action:
			self.action = action
			self.animation = self.game.assets[self.type + '/' + self.action].copy() #Animation state management


	def update(self, tilemap, movement=(0, 0)):
		self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

		#Using vector mathematics
		frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1]) #vector that represents how much the entity should be moved within this frame 
		
		self.pos[0] += frame_movement[0] 
		#handling collision for x-axis
		entity_rect = self.rect()
		for rect in tilemap.physics_rects_around(self.pos):
			if entity_rect.colliderect(rect): #Collision Detection
				if frame_movement[0] > 0: #if moving right and collide
					entity_rect.right = rect.left
					self.collisions['right'] = True
				if frame_movement[0] < 0:
					entity_rect.left = rect.right 
					self.collisions['left'] = True
				self.pos[0] = entity_rect.x #updating player's position


		self.pos[1] += frame_movement[1]
		#handling collison for y-axis
		entity_rect = self.rect()
		for rect in tilemap.physics_rects_around(self.pos):
			if entity_rect.colliderect(rect):
				if frame_movement[1] > 0: #if moving up and collide
					entity_rect.bottom = rect.top
					self.collisions['down'] = True
				if frame_movement[1] < 0:
					entity_rect.top = rect.bottom 
					self.collisions['up'] = True
				self.pos[1] = entity_rect.y #updating player's position

		if movement[0] > 0: # moving right
			self.flip = False
		if movement [0] < 0:
			self.flip = True # moving left

		self.velocity[1] = min(5, self.velocity[1] + 0.1) #will only take 5 and under

		if self.collisions['down'] or self.collisions['up']: #y-axis
			self.velocity[1] = 0

		self.animation.update()


	def render(self, surf, offset = (0,0)):
		#surf.blit(self.game.assets['player'], (self.pos[0] - offset[0], self.pos[1] - offset[1])) 
		surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1])) #Sprite transformations

class Enemy(PhysicsEntity): #Using inheritance 
	def __init__(self, game, pos, size):
		super().__init__(game, 'enemy', pos, size)

		self.walking = 0

	def update(self, tilemap, movement=(0,0)):
		if self.walking:
			#making it so chicken can't walk off the edge
			if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)):
				if (self.collisions['right'] or self.collisions['left']): #if walking into a wall walk the other way
					self.flip = not self.flip
				else:
					movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
			else:
				self.flip = not self.flip
			self.walking = max(0, self.walking - 1) 
			#making it so chicken can only shoot when stationary
			if not self.walking:
				dis = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
				if (abs(dis[1]) < 16): #if y-axis distance between cat and chicken is < 16 pixels
					if (self.flip and dis[0] < 0) :
						self.game.sfx['shoot'].play()
						self.game.projectiles.append([[self.rect().centerx - 7, self.rect().centery], -1.5, 0])
						for i in range(4):
							self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5 + math.pi, 2 +  random.random())) #face left
					if (not self.flip and dis[0] > 0): #if player is to the right
						self.game.projectiles.append([[self.rect().centerx + 7, self.rect().centery], 1.5, 0])
						for i in range(4):
								self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5, 2 +  random.random())) #face right, using Boolean Logic
		elif random.random() < 0.01:
			self.walking = random.randint(30, 120)

		super().update(tilemap, movement=movement)

		if movement[0] != 0: #making sure it has the walk animation when walking
			self.set_action('run')
		else:
			self.set_action('idle')

		#killing enemies by dashing
		if abs(self.game.player.dashing) >= 50: #whilst player is dashing
			if self.rect().colliderect(self.game.player.rect()): #if rect of enemy collides with rect of player
				self.game.screenshake = max(16, self.game.screenshake)
				self.game.sfx['hit'].play()
				for i in range(30):
							angle = random.random() * math.pi * 2
							speed = random.random() * 5
							self.game.sparks.append(Spark(self.rect().center, angle, 2 +  random.random()))
							self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7))) #Using Trigonometry
				self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
				self.game.sparks.append(Spark(self.rect().center, math.pi, + random.random()))
				return True

	def render(self, surf, offset=(0,0)): #chickens to hold a gun
		super().render(surf, offset=offset)

		if self.flip:
			surf.blit(pygame.transform.flip(self.game.assets['gun'], True, False), (self.rect().centerx - 1 - self.game.assets['gun'].get_width() - offset[0], self.rect().centery - offset[1]))
		else:
			surf.blit(self.game.assets['gun'], (self.rect().centerx + 1 - offset[0], self.rect().centery - offset[1]))

class Player(PhysicsEntity): #Using Polymorphism
	def __init__(self, game, pos, size):
		super().__init__(game, 'player', pos, size)
		self.air_time = 0
		self.jumps = 2 #player can only jump twice consecutively
		self.wall_slide = False
		self.last_movement = [0, 0]
		self.dashing = 0


	def update(self, tilemap, movement=(0, 0)):
		super().update(tilemap, movement=movement)

		self.last_movement = movement
		
		self.air_time += 1
		#player dies when falling off the edge
		if self.air_time > 120:
			self.game.dead = 1

		if self.collisions['down']:
			self.air_time = 0
			self.jumps = 2 # gain your jump back once you hit the floor 

		self.wall_slide = False
		if (self.collisions['right'] or self.collisions['left']) and self.air_time > 4: #if we hit the wall on either side & airtime>4
			self.wall_slide = True
			self.velocity[1] = min(self.velocity[1], 0.5) #capping downwards velocity at 0.5
			if self.collisions['right']: #which direction to keep animation correct
				self.flip = False
			else:
				self.flip = True
			self.set_action('wall_slide')

		if not self.wall_slide:
			if self.air_time > 4:
				self.set_action('jump')
			elif movement[0] != 0:
				self.set_action('run')
			else:
				self.set_action('idle')


			
			#adding particles when player dashes
		if abs(self.dashing) in {60, 50}: #burst of particles
			for i in range(20):
				angle = random.random() * math.pi * 2
				speed = random.random() * 0.5 + 0.5
				pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed] #cosine for x axis and sin for y axis. using this helps particles appear as a circle and flows correctly
				self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity = pvelocity, frame=random.randint(0, 7))) #Using random number generator 

		if self.dashing > 0:
			self.dashing = max(0, self.dashing - 1) #manage dashing value to 0
		if self.dashing < 0:
			self.dashing = min(0, self.dashing + 1)
		if abs(self.dashing) > 50: #stream of particles
			self.velocity[0] = abs(self.dashing) / self.dashing * 8 
			if abs(self.dashing) == 51:
				self.velocity[0] *= 0.1
			pvelocity = [abs(self.dashing) / self.dashing * random.random() * 3, 0]
			self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity = pvelocity, frame=random.randint(0, 7)))

		if self.velocity[0] > 0: #keeping velocity 0 
			self.velocity[0] = max(self.velocity[0] - 0.1, 0) 
		else:
			self.velocity[0] = min(self.velocity[0] + 0.1, 0)

	def render(self, surf, offset=(0, 0)): #making player invisible when we dash
		if abs(self.dashing) <= 50:
			super().render(surf, offset=offset)	

	def jump(self):
		if self.wall_slide:
			if self.flip and self.last_movement[0] < 0:
				self.velocity[0] = 3.5
				self.velocity[1] = -2.5
				self.air_time = 5
				self.jumps = max(0, self.jumps -1) #the wall slide uses up jumps
				return True
			elif not self.flip and self.last_movement[0] > 0:
				self.velocity[0] = -3.5
				self.velocity[1] = -2.5
				self.air_time = 5
				self.jumps = max(0, self.jumps -1)
				return True

		elif self.jumps:
			self.velocity[1] = -3
			self.jumps -= 1
			self.air_time = 5
			return True

	def dash(self): #how much we wna dash & which direction
		if not self.dashing:
			if self.flip:
				self.dashing = -60
			else:
				self.dashing = 60