import pygame
import sys
from login import main as login_main

pygame.init()
screen = pygame.display.set_mode((640,480), pygame.RESIZABLE)
font_size = screen.get_width() // 20
main_font = pygame.font.SysFont("Arial", font_size)
pygame.display.set_caption('Feline Fury')

class Button(): #Object Oriented Programming (OOP)
	def __init__(self, image, x_pos, y_pos, text_input):
		self.image = image
		self.x_pos = x_pos
		self.y_pos = y_pos
		self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
		self.text_input = text_input
		self.text = main_font.render(self.text_input, True, "white")
		self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

	def update(self):
		screen.blit(self.image, self.rect)
		screen.blit(self.text, self.text_rect)

	def check4Input1(self, pos): #checks if the mouse pos coords are within the bounds of the button play
		if pos[0] in range(self.rect.left, self.rect.right) and pos[1] in range(self.rect.top, self.rect.bottom):
			login_success, id_value = login_main()  # Call the login screensave_time(self.id_value, current_time)
			if login_success:
				from game import Game
				game = Game(id_value)
				game.run() 

	def check4Input2(self, pos): #checks if the mouse pos coords are within the bounds of the button quit
		if pos[0] in range(self.rect.left, self.rect.right) and pos[1] in range(self.rect.top, self.rect.bottom):
			pygame.quit()

	def check4Input3(self, pos):  #leaderboard button handler
		if pos[0] in range(self.rect.left, self.rect.right) and pos[1] in range(self.rect.top, self.rect.bottom):
			from leaderboard_screen import main as leaderboard_main
			leaderboard_main()

if __name__ == "__main__":

	Playbutton_surface = pygame.image.load('resources/images/button.png')
	Playbutton_surface = pygame.transform.scale(Playbutton_surface, (200, 50))

	Quitbutton_surface = pygame.image.load('resources/images/button.png')
	Quitbutton_surface = pygame.transform.scale(Quitbutton_surface, (200, 50))

	Leaderboardbutton_surface = pygame.image.load('resources/images/button.png') 
	Leaderboardbutton_surface = pygame.transform.scale(Leaderboardbutton_surface, (200, 50))

	button1 = Button(Playbutton_surface, screen.get_width() / 2 , 140, "Play")
	button2 = Button(Quitbutton_surface, screen.get_width() / 2, 260, "Quit")
	button3 = Button(Leaderboardbutton_surface, screen.get_width() / 2, 200, "Leaderboard")

	pygame.mixer.music.load('resources/mainmenu.mp3')
	pygame.mixer.music.set_volume(0.2)
	pygame.mixer.music.play(-1)

	while True: #while loops


		for event in pygame.event.get(): #event handling
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.MOUSEBUTTONDOWN:
				button1.check4Input1(pygame.mouse.get_pos())
				button2.check4Input2(pygame.mouse.get_pos())
				button3.check4Input3(pygame.mouse.get_pos()) 

			screen.fill("pink")

			button1.update()
			button2.update()
			button3.update()

			pygame.display.update()