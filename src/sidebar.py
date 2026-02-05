import pygame
from .const import *

class Sidebar:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.rect = pygame.Rect(width - 200, 0, 200, height) # Assume side panel is 200px
        self.font = pygame.font.SysFont('monospace', 14)
        self.title_font = pygame.font.SysFont('monospace', 24, bold=True)
    
    def show_bg(self):
        pygame.draw.rect(self.screen, (50, 50, 50), self.rect)
        
    def show_history(self, move_log):
        self.show_bg()
        
        # Title
        title = self.title_font.render("Move History", True, (255, 255, 255))
        self.screen.blit(title, (self.width - 190, 20))
        
        # Moves
        start_y = 60
        for i, record in enumerate(move_log[-20:]): # Show last 20 moves
            text = f"{i+1}. {record['notation']}"
            color = (200, 200, 200) if i % 2 == 0 else (255, 255, 255)
            lbl = self.font.render(text, True, color)
            self.screen.blit(lbl, (self.width - 190, start_y + i * 20))
