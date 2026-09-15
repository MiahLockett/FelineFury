import math
import pygame
#side note: math.pi * 2 creates a full circle

class Spark:
	def __init__(self, pos, angle, speed):
		self.pos = list(pos)
		self.angle = angle
		self.speed = speed

	def update(self):
		self.pos[0] += math.cos(self.angle) * self.speed
		self.pos[1] += math.sin(self.angle) * self.speed

		#it'll slow down as it moves and as it slows down it'll shrink so it smoothly disappears
		self.speed = max(0, self.speed - 0.1)
		return not self.speed #once speed is 0

	def render(self, surf, offset=(0,0)):
		render_points = [
			(self.pos[0] + math.cos(self.angle) * self.speed * 3 - offset[0], self.pos[1] + math.sin(self.angle) * self.speed * 3 - offset[1]), #keeps spark proportionate
			(self.pos[0] + math.cos(self.angle + math.pi * 0.5) * self.speed * 0.5 - offset[0], self.pos[1] + math.sin(self.angle + math.pi * 0.5) * self.speed * 0.5 - offset[1]), #spark to right or left
			(self.pos[0] + math.cos(self.angle + math.pi) * self.speed * 3 - offset[0], self.pos[1] + math.sin(self.angle + math.pi) * self.speed * 3 - offset[1]), 
			(self.pos[0] + math.cos(self.angle - math.pi * 0.5) * self.speed * 0.5 - offset[0], self.pos[1] + math.sin(self.angle - math.pi * 0.5) * self.speed * 0.5 - offset[1]), 
	
		]

		pygame.draw.polygon(surf, (255, 255, 255), render_points)