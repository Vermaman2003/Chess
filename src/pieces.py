import os

class Piece:
    def __init__(self, name, color, value, texture=None, texture_rect=None):
        self.name = name
        self.color = color
        value_sign = 1 if color == 'white' else -1
        self.value = value * value_sign
        self.moves = []
        self.moved = False
        self.texture = texture
        self.set_texture()
        self.texture_rect = texture_rect

    def set_texture(self, size=80):
        self.texture = os.path.join(
            f'assets/images/imgs-{size}px/{self.color}_{self.name}.png')

    def add_move(self, move):
        self.moves.append(move)

    def clear_moves(self):
        self.moves = []

    def get_moves(self, board, row, col):
        """
        Abstract method to be implemented by subclasses.
        Populates self.moves with valid moves from (row, col).
        """
        raise NotImplementedError

class Pawn(Piece):
    def __init__(self, color):
        self.dir = -1 if color == 'white' else 1
        self.en_passant = False
        super().__init__('pawn', color, 1.0)

    def get_moves(self, board, row, col):
        from .move import Move
        from .square import Square
        
        # steps
        steps = 1 if self.moved else 2

        # vertical moves
        start = row + self.dir
        end = row + (self.dir * (1 + steps))
        
        for possible_move_row in range(start, end, self.dir):
            if Square.in_range(possible_move_row):
                if board.squares[possible_move_row][col].isempty():
                    initial = Square(row, col)
                    final = Square(possible_move_row, col)
                    move = Move(initial, final)
                    self.add_move(move)
                else: 
                    break # blocked
            else: 
                break

        # diagonal moves
        possible_move_row = row + self.dir
        possible_move_cols = [col-1, col+1]
        for possible_move_col in possible_move_cols:
            if Square.in_range(possible_move_row, possible_move_col):
                if board.squares[possible_move_row][possible_move_col].has_enemy_piece(self.color):
                    initial = Square(row, col)
                    final_piece = board.squares[possible_move_row][possible_move_col].piece
                    final = Square(possible_move_row, possible_move_col, final_piece)
                    move = Move(initial, final)
                    self.add_move(move)

        # en passant (logic kept similar to original but needs board awareness)
        r = 3 if self.color == 'white' else 4
        fr = 2 if self.color == 'white' else 5
        
        # left en passant
        if Square.in_range(col-1) and row == r:
            if board.squares[row][col-1].has_enemy_piece(self.color):
                p = board.squares[row][col-1].piece
                if isinstance(p, Pawn):
                    if p.en_passant:
                        initial = Square(row, col)
                        final = Square(fr, col-1, p)
                        move = Move(initial, final)
                        self.add_move(move)
        
        # right en passant
        if Square.in_range(col+1) and row == r:
            if board.squares[row][col+1].has_enemy_piece(self.color):
                p = board.squares[row][col+1].piece
                if isinstance(p, Pawn):
                    if p.en_passant:
                        initial = Square(row, col)
                        final = Square(fr, col+1, p)
                        move = Move(initial, final)
                        self.add_move(move)

class Knight(Piece):
    def __init__(self, color):
        super().__init__('knight', color, 3.0)

    def get_moves(self, board, row, col):
        from .move import Move
        from .square import Square

        possible_moves = [
            (row-2, col+1), (row-1, col+2), (row+1, col+2), (row+2, col+1),
            (row+2, col-1), (row+1, col-2), (row-1, col-2), (row-2, col-1),
        ]

        for possible_move in possible_moves:
            possible_move_row, possible_move_col = possible_move
            if Square.in_range(possible_move_row, possible_move_col):
                if board.squares[possible_move_row][possible_move_col].isempty_or_enemy(self.color):
                    initial = Square(row, col)
                    final_piece = board.squares[possible_move_row][possible_move_col].piece
                    final = Square(possible_move_row, possible_move_col, final_piece)
                    move = Move(initial, final)
                    self.add_move(move)

class Bishop(Piece):
    def __init__(self, color):
        super().__init__('bishop', color, 3.001)

    def get_moves(self, board, row, col):
        self.straightline_moves(board, row, col, [
            (-1, 1), (-1, -1), (1, 1), (1, -1)
        ])

    def straightline_moves(self, board, row, col, incrs):
        from .move import Move
        from .square import Square
        for incr in incrs:
            row_incr, col_incr = incr
            possible_move_row = row + row_incr
            possible_move_col = col + col_incr

            while True:
                if Square.in_range(possible_move_row, possible_move_col):
                    initial = Square(row, col)
                    final_piece = board.squares[possible_move_row][possible_move_col].piece
                    final = Square(possible_move_row, possible_move_col, final_piece)
                    move = Move(initial, final)

                    if board.squares[possible_move_row][possible_move_col].isempty():
                        self.add_move(move)
                    elif board.squares[possible_move_row][possible_move_col].has_enemy_piece(self.color):
                        self.add_move(move)
                        break
                    elif board.squares[possible_move_row][possible_move_col].has_team_piece(self.color):
                        break
                else: break

                possible_move_row += row_incr
                possible_move_col += col_incr

class Rook(Piece):
    def __init__(self, color):
        super().__init__('rook', color, 5.0)

    def get_moves(self, board, row, col):
        # We need access to straightline_moves, which I put in Bishop.
        # Ideally, it should be in Piece or a mixin.
        # For now, I'll copy or implement a shared method.
        # Actually I will add it to Piece class in a fix-up or just duplicate for now to be safe,
        # but better design is to put it in Piece.
        # I'll rely on the one I define below for Queen/Rook.
        self._straightline_moves(board, row, col, [
            (-1, 0), (0, 1), (1, 0), (0, -1)
        ])

    def _straightline_moves(self, board, row, col, incrs):
        from .move import Move
        from .square import Square
        for incr in incrs:
            row_incr, col_incr = incr
            possible_move_row = row + row_incr
            possible_move_col = col + col_incr

            while True:
                if Square.in_range(possible_move_row, possible_move_col):
                    initial = Square(row, col)
                    final_piece = board.squares[possible_move_row][possible_move_col].piece
                    final = Square(possible_move_row, possible_move_col, final_piece)
                    move = Move(initial, final)

                    if board.squares[possible_move_row][possible_move_col].isempty():
                        self.add_move(move)
                    elif board.squares[possible_move_row][possible_move_col].has_enemy_piece(self.color):
                        self.add_move(move)
                        break
                    elif board.squares[possible_move_row][possible_move_col].has_team_piece(self.color):
                        break
                else: break

                possible_move_row += row_incr
                possible_move_col += col_incr

class Queen(Piece):
    def __init__(self, color):
        super().__init__('queen', color, 9.0)

    def get_moves(self, board, row, col):
        self._straightline_moves(board, row, col, [
            (-1, 1), (-1, -1), (1, 1), (1, -1),
            (-1, 0), (0, 1), (1, 0), (0, -1)
        ])

    def _straightline_moves(self, board, row, col, incrs):
        # Same helper as Rook/Bishop
        from .move import Move
        from .square import Square
        for incr in incrs:
            row_incr, col_incr = incr
            possible_move_row = row + row_incr
            possible_move_col = col + col_incr

            while True:
                if Square.in_range(possible_move_row, possible_move_col):
                    initial = Square(row, col)
                    final_piece = board.squares[possible_move_row][possible_move_col].piece
                    final = Square(possible_move_row, possible_move_col, final_piece)
                    move = Move(initial, final)

                    if board.squares[possible_move_row][possible_move_col].isempty():
                        self.add_move(move)
                    elif board.squares[possible_move_row][possible_move_col].has_enemy_piece(self.color):
                        self.add_move(move)
                        break
                    elif board.squares[possible_move_row][possible_move_col].has_team_piece(self.color):
                        break
                else: break

                possible_move_row += row_incr
                possible_move_col += col_incr

class King(Piece):
    def __init__(self, color):
        self.left_rook = None
        self.right_rook = None
        super().__init__('king', color, 10000.0)

    def get_moves(self, board, row, col):
        from .move import Move
        from .square import Square
        
        adjs = [
            (row-1, col+0), (row-1, col+1), (row+0, col+1), (row+1, col+1),
            (row+1, col+0), (row+1, col-1), (row+0, col-1), (row-1, col-1),
        ]

        # normal moves
        for possible_move in adjs:
            possible_move_row, possible_move_col = possible_move
            if Square.in_range(possible_move_row, possible_move_col):
                if board.squares[possible_move_row][possible_move_col].isempty_or_enemy(self.color):
                    initial = Square(row, col)
                    final = Square(possible_move_row, possible_move_col) 
                    move = Move(initial, final)
                    self.add_move(move)

        # castling moves
        if not self.moved:
            # Queen castling
            left_rook = board.squares[row][0].piece
            if isinstance(left_rook, Rook):
                if not left_rook.moved:
                    for c in range(1, 4):
                        if board.squares[row][c].has_piece():
                            break
                        if c == 3:
                            self.left_rook = left_rook
                            initial = Square(row, 0)
                            final = Square(row, 3)
                            moveR = Move(initial, final)
                            initial = Square(row, col)
                            final = Square(row, 2)
                            moveK = Move(initial, final)
                            
                            # Note: check validation is handled in Engine or Board
                            left_rook.add_move(moveR)
                            self.add_move(moveK)

            # King castling
            right_rook = board.squares[row][7].piece
            if isinstance(right_rook, Rook):
                if not right_rook.moved:
                    for c in range(5, 7):
                        if board.squares[row][c].has_piece():
                            break
                        if c == 6:
                            self.right_rook = right_rook
                            initial = Square(row, 7)
                            final = Square(row, 5)
                            moveR = Move(initial, final)
                            initial = Square(row, col)
                            final = Square(row, 6)
                            moveK = Move(initial, final)
                            
                            right_rook.add_move(moveR)
                            self.add_move(moveK)
