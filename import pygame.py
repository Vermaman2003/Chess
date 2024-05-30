import pygames
import time
import sys

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH, HEIGHT = 800, 800
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  # for animation
IMAGES = {}

# Initialize a dictionary of images
def loadImages():
    pieces = ['wp', 'bp', 'wn', 'bn', 'wb', 'bb', 'wR', 'bR', 'wN', 'bN', 'wB',
              'bB', 'wQ', 'bQ']
    for piece in pieces:
        IMAGES[piece] = pygame.image.load('images/' + piece + '.png')

# Handle player input
def handleInput(screen, board, validMoves, selectedPiece, gameOver):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            location = pygame.mouse.get_pos()
            col = location[0] // SQ_SIZE
            row = location[1] // SQ_SIZE
            if selectedPiece == None:
                piece = board[row][col]
                if piece != '--':
                    validMoves = getValidMoves(board, piece)
                    if len(validMoves) > 0:
                        selectedPiece = piece
                        screen.blit(IMAGES[piece], (col * SQ_SIZE, row * SQ_SIZE))
            else:
                piece = board[row][col]
                if piece == selectedPiece:
                    selectedPiece = None
                elif piece != '--' and piece in validMoves:
                    selectedPiece = None
                    makeMove(board, validMoves, row, col)
                    time.sleep(0.5)
                    gameOver = isGameOver(board)
                    if gameOver:
                        print("Game Over")
                        pygame.quit()
                        sys.exit()
    return screen, board, validMoves, selectedPiece, gameOver

# Determine valid moves for a piece
def getValidMoves(board, piece):
    moves = []
    if piece != '--':
        if piece[1] == 'p':  # pawn
            if piece[0] == 'w':
                for i in range(1, 3):
                    if not onBoard((piece[2] - i, piece[3] - 1)) or board[(piece[2] - i)][piece[3] - 1] != '--':
                        break
                    moves.append((piece[2] - i, piece[3] - 1))
                if onBoard((piece[2] - 2, piece[3] - 1)) and board[(piece[2] - 2)][piece[3] - 1] == '--' and board[(piece[2] - 1)][piece[3] - 1] == '--':
                    moves.append((piece[2] - 2, piece[3] - 1))
            elif piece[0] == 'b':
                for i in range(1, 3):
                    if not onBoard((piece[2] + i, piece[3] - 1)) or board[(piece[2] + i)][piece[3] - 1] != '--':
                        break
                    moves.append((piece[2] + i, piece[3] - 1))
                if onBoard((piece[2] + 2, piece[3] - 1)) and board[(piece[2] + 2)][piece[3] - 1] == '--' and board[(piece[2] + 1)][piece[3] - 1] == '--':
                    moves.append((piece[2] + 2, piece[3] - 1))
        elif piece[1] == 'r':  # rook
            moves = rookMoves(board, piece)
        elif piece[1] == 'n':  # knight
            moves = knightMoves(board, piece)
        elif piece[1] == 'b':  # bishop
            moves = bishopMoves(board, piece)
        elif piece[1] == 'q':  # queen
            moves = queenMoves(board, piece)
        elif piece[1] == 'k':  # king
            moves = kingMoves(board, piece)
    return moves

# Make a move on the board
def makeMove(board, validMoves, row, col):
    board[row][col] = board[selectedPiece[2]][selectedPiece[3]]
    board[selectedPiece[2]][selectedPiece[3]] = '--'
    selectedPiece = None
    for i in range(len(validMoves)):
        if validMoves[i][0] == row and validMoves[i][1] == col:
            validMoves.pop(i)
            break

# Check if game is over
def isGameOver(board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            if board[row][col][0] == 'w' and kingAlive(board, row, col):
                return False
    return True

# Check if king is alive
def kingAlive(board, row, col):
    if board[row][col][1] == 'k':
        return True
    return False

# Main game loop
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    board = initializeBoard()
    validMoves = []
    selectedPiece = None
    gameOver = False
    loadImages()
    while not gameOver:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen, board, validMoves, selectedPiece, gameOver = handleInput(screen, board, validMoves, selectedP
```p, gameOver)
clock.tick(MAX\_FPS)
pygame.display.flip()

```python
# Initialize the board
def initializeBoard():
    board = []
    for i in range(DIMENSION):
        row = []
        for j in range(DIMENSION):
            if (i + j) % 2 == 0:
                row.append('--')
            else:
                row.append('ww')
        board.append(row)
    board[0][0] = 'bp'
    board[0][1] = 'bp'
    board[0][2] = 'bp'
    board[0][3] = 'bp'
    board[0][4] = 'bp'
    board[0][5] = 'bp'
    board[0][6] = 'bp'
    board[0][7] = 'bp'
    board[1][0] = 'bn'
    board[1][1] = 'bb'
    board[1][2] = 'bq'
    board[1][3] = 'bk'
    board[1][4] = 'bb'
    board[1][5] = 'bn'
    board[1][6] = 'bp'
    board[1][7] = 'bp'
    board[6][0] = 'wn'
    board[6][1] = 'wb'
    board[6][2] = 'wq'
    board[6][3] = 'wk'
    board[6][4] = 'wb'
    board[6][5] = 'wn'
    board[6][6] = 'wp'
    board[6][7] = 'wp'
    board[7][0] = 'wp'
    board[7][1] = 'wp'
    board[7][2] = 'wp'
    board[7][3] = 'wp'
    board[7][4] = 'wp'
    board[7][5] = 'wp'
    board[7][6] = 'wp'
    board[7][7] = 'wp'
    return board

# Check if a square is on the board
def onBoard(location):
    if location[0] >= 0 and location[0] < DIMENSION and location[1] >= 0 and location[1] < DIMENSION:
        return True
    return False

# Main game loop
main()