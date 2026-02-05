import pygame
import sys

from .const import *
from .engine import Engine
from .sidebar import Sidebar
from .square import Square
from .move import Move
from .dragger import Dragger
from .config import Config

class Main:

    def __init__(self):
        pygame.init()
        # Increase width for sidebar
        self.sidebar_width = 200
        self.screen_width = WIDTH + self.sidebar_width
        self.screen_height = HEIGHT
        
        self.screen = pygame.display.set_mode( (self.screen_width, self.screen_height) )
        pygame.display.set_caption('Chess')
        
        self.engine = Engine()
        self.dragger = Dragger()
        self.config = Config()
        self.sidebar = Sidebar(self.screen, self.screen_width, self.screen_height)

    def mainloop(self):
        
        screen = self.screen
        engine = self.engine
        board = self.engine.board
        dragger = self.dragger
        
        while True:
            # show methods
            self.show_bg(screen)
            self.show_last_move(screen)
            self.show_moves(screen)
            self.show_pieces(screen)
            self.show_hover(screen)
            
            # Show Sidebar
            self.sidebar.show_history(engine.move_log)

            if dragger.dragging:
                dragger.update_blit(screen)

            for event in pygame.event.get():

                # click
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if click is on board
                    if event.pos[0] < WIDTH:
                        dragger.update_mouse(event.pos)

                        clicked_row = dragger.mouseY // SQSIZE
                        clicked_col = dragger.mouseX // SQSIZE

                        # if clicked square has a piece ?
                        if board.squares[clicked_row][clicked_col].has_piece():
                            piece = board.squares[clicked_row][clicked_col].piece
                            # valid piece (color) ?
                            if piece.color == engine.next_player:
                                # Use Engine to calculate moves
                                engine.calculate_moves(piece, clicked_row, clicked_col)
                                
                                dragger.save_initial(event.pos)
                                dragger.drag_piece(piece)
                                # show methods 
                                self.show_bg(screen)
                                self.show_last_move(screen)
                                self.show_moves(screen)
                                self.show_pieces(screen)
                                self.sidebar.show_history(engine.move_log)
                
                # mouse motion
                elif event.type == pygame.MOUSEMOTION:
                    if event.pos[0] < WIDTH:
                        motion_row = event.pos[1] // SQSIZE
                        motion_col = event.pos[0] // SQSIZE

                        self.set_hover(motion_row, motion_col)

                        if dragger.dragging:
                            dragger.update_mouse(event.pos)
                            # show methods
                            self.show_bg(screen)
                            self.show_last_move(screen)
                            self.show_moves(screen)
                            self.show_pieces(screen)
                            self.show_hover(screen)
                            self.sidebar.show_history(engine.move_log)
                            dragger.update_blit(screen)
                
                # click release
                elif event.type == pygame.MOUSEBUTTONUP:
                    
                    if dragger.dragging:
                        dragger.update_mouse(event.pos)

                        released_row = dragger.mouseY // SQSIZE
                        released_col = dragger.mouseX // SQSIZE

                        # create possible move
                        initial = Square(dragger.initial_row, dragger.initial_col)
                        final = Square(released_row, released_col)
                        move = Move(initial, final)

                        # valid move ?
                        if engine.valid_move(dragger.piece, move):
                            # normal capture
                            captured = board.squares[released_row][released_col].has_piece()
                            
                            # Execute move via Engine
                            engine.move(dragger.piece, move)
                            
                            board.set_true_en_passant(dragger.piece)                            

                            # sounds
                            self.play_sound(captured)
                            
                            # show methods
                            self.show_bg(screen)
                            self.show_last_move(screen)
                            self.show_pieces(screen)
                            self.sidebar.show_history(engine.move_log)
                    
                    dragger.undrag_piece()
                
                # key press
                elif event.type == pygame.KEYDOWN:
                    
                    # changing themes
                    if event.key == pygame.K_t:
                        self.change_theme()

                     # changing themes
                    if event.key == pygame.K_r:
                        engine.reset() # This needs implementation in Engine if we want reset
                        engine = self.engine
                        board = self.engine.board
                        dragger = self.dragger
                    
                    # AI Move (Test)
                    if event.key == pygame.K_a:
                        engine.ai_move()
                        self.show_pieces(screen)

                # quit application
                elif event.type == pygame.QUIT:
                    engine.save_log() # Save log on exit
                    pygame.quit()
                    sys.exit()
            
            pygame.display.update()

    # Rendering helpers (moved/adapted from Game)
    def show_bg(self, surface):
        theme = self.config.theme
        for row in range(ROWS):
            for col in range(COLS):
                color = theme.bg.light if (row + col) % 2 == 0 else theme.bg.dark
                rect = (col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect)
                
                if col == 0:
                    color = theme.bg.dark if row % 2 == 0 else theme.bg.light
                    lbl = self.config.font.render(str(ROWS-row), 1, color)
                    surface.blit(lbl, (5, 5 + row * SQSIZE))
                if row == 7:
                    color = theme.bg.dark if (row + col) % 2 == 0 else theme.bg.light
                    lbl = self.config.font.render(Square.get_alphacol(col), 1, color)
                    surface.blit(lbl, (col * SQSIZE + SQSIZE - 20, HEIGHT - 20))

    def show_pieces(self, surface):
        board = self.engine.board
        for row in range(ROWS):
            for col in range(COLS):
                if board.squares[row][col].has_piece():
                    piece = board.squares[row][col].piece
                    if piece is not self.dragger.piece:
                        piece.set_texture(size=80)
                        img = pygame.image.load(piece.texture)
                        img_center = col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2
                        piece.texture_rect = img.get_rect(center=img_center)
                        surface.blit(img, piece.texture_rect)

    def show_moves(self, surface):
        theme = self.config.theme
        if self.dragger.dragging:
            piece = self.dragger.piece
            for move in piece.moves:
                color = theme.moves.light if (move.final.row + move.final.col) % 2 == 0 else theme.moves.dark
                rect = (move.final.col * SQSIZE, move.final.row * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect)

    def show_last_move(self, surface):
        theme = self.config.theme
        if self.engine.board.last_move:
            initial = self.engine.board.last_move.initial
            final = self.engine.board.last_move.final
            for pos in [initial, final]:
                color = theme.trace.light if (pos.row + pos.col) % 2 == 0 else theme.trace.dark
                rect = (pos.col * SQSIZE, pos.row * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect)

    def show_hover(self, surface):
        if self.engine.hovered_sqr:
            color = (180, 180, 180)
            rect = (self.engine.hovered_sqr.col * SQSIZE, self.engine.hovered_sqr.row * SQSIZE, SQSIZE, SQSIZE)
            pygame.draw.rect(surface, color, rect, width=3)

    def set_hover(self, row, col):
        if 0 <= row < ROWS and 0 <= col < COLS:
            self.engine.hovered_sqr = self.engine.board.squares[row][col]
        else:
            self.engine.hovered_sqr = None

    def change_theme(self):
        self.config.change_theme()

    def play_sound(self, captured=False):
        if captured:
            self.config.capture_sound.play()
        else:
            self.config.move_sound.play()
