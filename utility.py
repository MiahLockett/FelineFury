import pygame
import os



BASE_IMG_PATH = 'resources/images'

def load_image(path):
	img = pygame.image.load(BASE_IMG_PATH + path).convert() #.convert converts the internal representation of this image in pygame, making it more efficient for rendering
	img.set_colorkey((0, 0, 0)) #set_colorkey removes any background in the rgb colour states, and replaces it with transparency (my rgb colour is black)	
	#img.set_colorkey((255, 255, 255)) #white background
	#img = pygame.transform.scale(img, (100,50))
	return img

def load_images(path):
	images = [] 
	for img_name in sorted(os.listdir(BASE_IMG_PATH + path)): #os.listdir gives you all the files in the given path, reading files
		images.append(load_image(path + '/' + img_name))
	return images

class Animation:
	def __init__(self, images, img_dur=5, loop=True):
		self.images = images
		self.loop = loop
		self.img_duration = img_dur
		self.done = False
		self.frame = 0

		#renders images based on frame & loops ^^^

	def copy(self):
		return Animation(self.images, self.img_duration, self.loop)

	def update(self):
		if self.loop:
			self.frame = (self.frame + 1) % (self.img_duration * len(self.images)) #forces frame to loop until it reaches the end
		else:
			self.frame = min(self.frame + 1, self.img_duration * len(self.images) -1) #Frame based animation
			if self.frame >= self.img_duration * len(self.images) - 1:
				self.done = True


	def img(self):
		return self.images[int(self.frame / self.img_duration)] #dividing frame of the game by how long each img is supposed to show for
