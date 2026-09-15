import pygame
import sys
from database import get_leaderboard, create_connection
from FelineFury import Button

class LeaderboardScreen:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 480), pygame.RESIZABLE)
        font_size = self.screen.get_width() // 20
        self.main_font = pygame.font.SysFont("Arial", font_size)
        self.small_font = pygame.font.SysFont("Arial", 18)
        self.title_font = pygame.font.SysFont("Arial", 24)
        pygame.display.set_caption('Feline Fury - Leaderboard')
        
        # Load button image
        button_surface = pygame.image.load('resources/images/button.png')
        button_surface = pygame.transform.scale(button_surface, (120, 40))
        
        # Create level buttons (1-5)
        self.level_buttons = []
        button_y = 80
        for i in range(1, 6):
            button = Button(button_surface, 100, button_y, f"Level {i}")
            self.level_buttons.append(button)
            button_y += 50
        
        # Back button
        back_button_surface = pygame.transform.scale(
            pygame.image.load('resources/images/button.png'), (120, 40)
        )
        self.back_button = Button(back_button_surface, 100, 420, "Back")
        
        self.selected_level = None
        self.leaderboard_data = []
    
    def get_leaderboard_with_usernames(self, level):
        """Get leaderboard data with usernames joined from users table"""
        conn = create_connection()
        if not conn:
            return []
        
        cursor = conn.cursor()
        try:
            cursor.execute("USE user_auth")
            cursor.execute("""
                SELECT users.username, leaderboard.time, leaderboard.level 
                FROM leaderboard
                INNER JOIN users ON leaderboard.user_id = users.id 
                WHERE leaderboard.level = %s
                ORDER BY leaderboard.time ASC
                LIMIT 10
            """, (level,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'username': row[0],
                    'time': row[1],
                    'level': row[2]
                })
            return results
            
        except Exception as e:
            print(f"Error fetching leaderboard: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    def format_time(self, milliseconds):
        """Convert milliseconds to MM:SS:mmm format"""
        millis = milliseconds % 1000
        seconds = int(milliseconds / 1000 % 60)
        minutes = int(milliseconds / 60000 % 24)
        return f'{minutes:02d}:{seconds:02d}:{millis:03d}'
    
    def draw_leaderboard(self):
        """Draw the leaderboard table"""
        if not self.leaderboard_data:
            no_data_text = self.small_font.render("No scores yet!", True, (0, 0, 0))
            self.screen.blit(no_data_text, (300, 200))
            return
        
        # Draw title
        title_text = self.title_font.render(f"Level {self.selected_level} Leaderboard", True, (0, 0, 0))
        self.screen.blit(title_text, (250, 50))
        
        # Draw headers
        rank_header = self.small_font.render("Rank", True, (0, 0, 0))
        username_header = self.small_font.render("Username", True, (0, 0, 0))
        time_header = self.small_font.render("Time", True, (0, 0, 0))
        
        self.screen.blit(rank_header, (200, 90))
        self.screen.blit(username_header, (280, 90))
        self.screen.blit(time_header, (420, 90))
        
        # Draw line under headers
        pygame.draw.line(self.screen, (0, 0, 0), (200, 110), (550, 110), 2)
        
        # Draw leaderboard entries
        y_pos = 125
        for idx, entry in enumerate(self.leaderboard_data, 1):
            rank_text = self.small_font.render(f"{idx}", True, (0, 0, 0))
            username_text = self.small_font.render(entry['username'], True, (0, 0, 0))
            time_text = self.small_font.render(self.format_time(entry['time']), True, (0, 0, 0))
            
            self.screen.blit(rank_text, (210, y_pos))
            self.screen.blit(username_text, (280, y_pos))
            self.screen.blit(time_text, (420, y_pos))
            
            y_pos += 30
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            self.screen.fill((244, 194, 194))  # Pink background
            
            # Draw title if no level selected
            if self.selected_level is None:
                title = self.main_font.render("Select a Level", True, (0, 0, 0))
                self.screen.blit(title, (self.screen.get_width() // 2 - title.get_width() // 2, 20))
            
            # Draw level buttons
            for button in self.level_buttons:
                button.update()
            
            # Draw back button
            self.back_button.update()
            
            # Draw leaderboard if level is selected
            if self.selected_level is not None:
                self.draw_leaderboard()
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Check level button clicks (levels 1-5)
                    for idx, button in enumerate(self.level_buttons):
                        if button.rect.collidepoint(mouse_pos):
                            self.selected_level = idx + 1  # Display level 1-5
                            self.leaderboard_data = self.get_leaderboard_with_usernames(idx + 1)  # Query using 1-5
                    
                    # Check back button
                    if self.back_button.rect.collidepoint(mouse_pos):
                        return  # Return to caller (main menu)
            
            pygame.display.update()
            clock.tick(60)

def main():
    """Entry point for leaderboard screen"""
    leaderboard = LeaderboardScreen()
    leaderboard.run()

if __name__ == "__main__":
    main()