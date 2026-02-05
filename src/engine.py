import copy
import pandas as pd
import datetime
import os
from .const import *
from .board import Board
from .pieces import Piece, Pawn, King, Queen, Rook, Bishop, Knight

class Engine:
    def __init__(self):
        self.board = Board()
        self.next_player = 'white'
        self.hovered_sqr = None
        self.move_log = []
        self.game_active = True
        self.start_time = datetime.datetime.now()
        
    def next_turn(self):
        self.next_player = 'white' if self.next_player == 'black' else 'black'

    def valid_move(self, piece, move):
        return self.board.valid_move(piece, move)


    def move(self, piece, move):
        if not self.game_active: return
        self.board.move(piece, move)
        self.log_move(piece, move)
        self.next_turn()

    def log_move(self, piece, move):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record = {
            'timestamp': timestamp,
            'player': piece.color,
            'piece': piece.name,
            'initial_pos': f"{move.initial.col},{move.initial.row}",
            'final_pos': f"{move.final.col},{move.final.row}",
            'notation': self.get_notation(piece, move)
        }
        self.move_log.append(record)

    def get_notation(self, piece, move):
        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        r_map = {0:8, 1:7, 2:6, 3:5, 4:4, 5:3, 6:2, 7:1}
        
        file_start = files[move.initial.col]
        rank_start = r_map[move.initial.row]
        file_end = files[move.final.col]
        rank_end = r_map[move.final.row]
        
        p_char = ''
        if isinstance(piece, Knight): p_char = 'N'
        elif isinstance(piece, Bishop): p_char = 'B'
        elif isinstance(piece, Rook): p_char = 'R'
        elif isinstance(piece, Queen): p_char = 'Q'
        elif isinstance(piece, King): p_char = 'K'
        
        return f"{p_char}{file_start}{rank_start}-{file_end}{rank_end}"

    def save_log(self, filename='game_log.csv'):
        df = pd.DataFrame(self.move_log)
        if os.path.exists(filename):
            df.to_csv(filename, mode='a', header=False, index=False)
        else:
            df.to_csv(filename, index=False)

    # Core Logic
    def calculate_moves(self, piece, row, col, check_for_checks=True):
        """
        1. Generate all pseudo-legal moves using piece-specific logic.
        2. If check_for_checks is True, filter out moves that leave King in check.
        """
        piece.clear_moves()
        piece.get_moves(self.board, row, col)
        
        if check_for_checks:
            valid_moves = []
            for move in piece.moves:
                if not self.in_check(piece, move):
                    valid_moves.append(move)
            piece.moves = valid_moves

    def in_check(self, piece, move):
        """
        Determines if making 'move' with 'piece' leaves the current player's King in check.
        """
        # Create a temp board state
        temp_board = copy.deepcopy(self.board)
        # Find the piece on the temp board
        temp_piece = temp_board.squares[move.initial.row][move.initial.col].piece
        
        # Execute move on temp board
        temp_board.move(temp_piece, move, testing=True)
        
        return self.is_king_attacked(temp_board, piece.color)

    def is_king_attacked(self, board, color):
        # Locate King
        king_pos = None
        for r in range(ROWS):
            for c in range(COLS):
                if board.squares[r][c].has_team_piece(color) and isinstance(board.squares[r][c].piece, King):
                    king_pos = (r, c)
                    break
        if not king_pos: return False

        # Check all enemy pieces to see if they can attack King
        enemy_color = 'black' if color == 'white' else 'white'
        
        for r in range(ROWS):
            for c in range(COLS):
                if board.squares[r][c].has_team_piece(enemy_color):
                    enemy_piece = board.squares[r][c].piece
                    # We need pseudo-legal moves for the enemy
                    enemy_piece.clear_moves()
                    enemy_piece.get_moves(board, r, c)
                    
                    for m in enemy_piece.moves:
                        if m.final.row == king_pos[0] and m.final.col == king_pos[1]:
                            return True
        return False
