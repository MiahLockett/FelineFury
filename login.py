import pygame
import sys
from database import init_database, signup_user, login_user

# Initialize Pygame
pygame.init()

# Constants for colour calculation
WIDTH, HEIGHT = 640, 480
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (100, 150, 255)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
PINK = (244, 194, 194)

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Login System")

# Fonts
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

class InputBox:
    def __init__(self, x, y, w, h, is_password=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = GRAY
        self.text = ''
        self.active = False
        self.is_password = is_password

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = BLUE if self.active else GRAY
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return True
            elif len(self.text) < 20:
                self.text += event.unicode
        return False

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, 2)
        display_text = '*' * len(self.text) if self.is_password else self.text
        txt_surface = small_font.render(display_text, True, BLACK)
        screen.blit(txt_surface, (self.rect.x + 5, self.rect.y + 10))

class Button:
    def __init__(self, x, y, w, h, text, color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover = False

    def draw(self, screen):
        color = tuple(min(c + 30, 255) for c in self.color) if self.hover else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        txt_surface = small_font.render(self.text, True, BLACK)
        txt_rect = txt_surface.get_rect(center=self.rect.center)
        screen.blit(txt_surface, txt_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

def main():
    # Initialize database
    init_database()
    
    clock = pygame.time.Clock()
    
    # UI elements
    username_box = InputBox(220, 150, 200, 40)
    password_box = InputBox(220, 210, 200, 40, is_password=True)
    login_btn = Button(200, 280, 100, 40, "Login", GREEN)
    signup_btn = Button(340, 280, 100, 40, "Sign Up", BLUE)
    
    message = ""
    message_color = BLACK
    login_successful = False
    
    running = True
    while running:
        screen.fill(PINK)
        
        # Draw title
        title = font.render("Login to play!", True, BLACK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Draw labels
        username_label = small_font.render("Username:", True, BLACK)
        password_label = small_font.render("Password:", True, BLACK)
        screen.blit(username_label, (220, 130))
        screen.blit(password_label, (220, 190))
        
        # Draw UI elements
        username_box.draw(screen)
        password_box.draw(screen)
        login_btn.draw(screen)
        signup_btn.draw(screen)
        
        # Draw message
        if message:
            msg_surface = small_font.render(message, True, message_color)
            screen.blit(msg_surface, (WIDTH//2 - msg_surface.get_width()//2, 350))
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return False  # Return False if user quits
            
            username_box.handle_event(event)
            password_box.handle_event(event)
            
            if login_btn.handle_event(event):
                if username_box.text and password_box.text:
                    success, msg, id_value = login_user(username_box.text, password_box.text)
                    message = msg
                    message_color = GREEN if success else RED
                    if success:
                        # Wait a moment to show success message
                        pygame.display.flip()
                        pygame.time.wait(1000)
                        return True, id_value  # Return True on successful login EDIT - ALSO RETURNING USERNAME
                else:
                    message = "Please fill all fields"
                    message_color = RED
            
            if signup_btn.handle_event(event):
                if username_box.text and password_box.text:
                    success, msg = signup_user(username_box.text, password_box.text)
                    message = msg
                    message_color = GREEN if success else RED
                    if success:
                        username_box.text = ""
                        password_box.text = ""
                else:
                    message = "Please fill all fields"
                    message_color = RED
        
        pygame.display.flip()
        clock.tick(60)
    
    return False, null  # Return False if loop ends without successful login

if __name__ == "__main__":
    main()