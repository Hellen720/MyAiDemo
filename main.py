import random
import sys

import pygame


GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 30
SIDE_PANEL_WIDTH = 180
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE + SIDE_PANEL_WIDTH
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE
FPS = 60

DROP_EVENT = pygame.USEREVENT + 1
DROP_INTERVAL_MS = 500

BLACK = (20, 20, 20)
GRAY = (60, 60, 60)
WHITE = (230, 230, 230)


TETROMINOES = {
    "I": {
        "color": (0, 240, 240),
        "shapes": [
            [(0, 1), (1, 1), (2, 1), (3, 1)],
            [(2, 0), (2, 1), (2, 2), (2, 3)],
            [(0, 2), (1, 2), (2, 2), (3, 2)],
            [(1, 0), (1, 1), (1, 2), (1, 3)],
        ],
    },
    "O": {
        "color": (240, 240, 0),
        "shapes": [
            [(1, 0), (2, 0), (1, 1), (2, 1)],
            [(1, 0), (2, 0), (1, 1), (2, 1)],
            [(1, 0), (2, 0), (1, 1), (2, 1)],
            [(1, 0), (2, 0), (1, 1), (2, 1)],
        ],
    },
    "T": {
        "color": (160, 0, 240),
        "shapes": [
            [(1, 0), (0, 1), (1, 1), (2, 1)],
            [(1, 0), (1, 1), (2, 1), (1, 2)],
            [(0, 1), (1, 1), (2, 1), (1, 2)],
            [(1, 0), (0, 1), (1, 1), (1, 2)],
        ],
    },
    "S": {
        "color": (0, 240, 0),
        "shapes": [
            [(1, 0), (2, 0), (0, 1), (1, 1)],
            [(1, 0), (1, 1), (2, 1), (2, 2)],
            [(1, 1), (2, 1), (0, 2), (1, 2)],
            [(0, 0), (0, 1), (1, 1), (1, 2)],
        ],
    },
    "Z": {
        "color": (240, 0, 0),
        "shapes": [
            [(0, 0), (1, 0), (1, 1), (2, 1)],
            [(2, 0), (1, 1), (2, 1), (1, 2)],
            [(0, 1), (1, 1), (1, 2), (2, 2)],
            [(1, 0), (0, 1), (1, 1), (0, 2)],
        ],
    },
    "J": {
        "color": (0, 0, 240),
        "shapes": [
            [(0, 0), (0, 1), (1, 1), (2, 1)],
            [(1, 0), (2, 0), (1, 1), (1, 2)],
            [(0, 1), (1, 1), (2, 1), (2, 2)],
            [(1, 0), (1, 1), (0, 2), (1, 2)],
        ],
    },
    "L": {
        "color": (240, 160, 0),
        "shapes": [
            [(2, 0), (0, 1), (1, 1), (2, 1)],
            [(1, 0), (1, 1), (1, 2), (2, 2)],
            [(0, 1), (1, 1), (2, 1), (0, 2)],
            [(0, 0), (1, 0), (1, 1), (1, 2)],
        ],
    },
}


class Piece:
    def __init__(self, kind):
        self.kind = kind
        self.rotation = 0
        self.x = 3
        self.y = 0
        self.color = TETROMINOES[kind]["color"]

    @property
    def blocks(self):
        return TETROMINOES[self.kind]["shapes"][self.rotation]

    def rotated(self):
        p = Piece(self.kind)
        p.rotation = (self.rotation + 1) % 4
        p.x = self.x
        p.y = self.y
        return p


def create_board():
    return [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]


def random_piece():
    return Piece(random.choice(list(TETROMINOES.keys())))


def valid_position(board, piece, dx=0, dy=0):
    for bx, by in piece.blocks:
        x = piece.x + bx + dx
        y = piece.y + by + dy
        if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
            return False
        if y >= 0 and board[y][x] is not None:
            return False
    return True


def lock_piece(board, piece):
    for bx, by in piece.blocks:
        x = piece.x + bx
        y = piece.y + by
        if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
            board[y][x] = piece.color


def clear_lines(board):
    new_board = [row for row in board if any(cell is None for cell in row)]
    cleared = GRID_HEIGHT - len(new_board)
    while len(new_board) < GRID_HEIGHT:
        new_board.insert(0, [None for _ in range(GRID_WIDTH)])
    return new_board, cleared


def draw_cell(screen, x, y, color):
    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, GRAY, rect, 1)


def draw(screen, board, piece, score, level, lines):
    screen.fill(BLACK)

    for y, row in enumerate(board):
        for x, color in enumerate(row):
            if color is not None:
                draw_cell(screen, x, y, color)
            else:
                empty_rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, GRAY, empty_rect, 1)

    for bx, by in piece.blocks:
        x = piece.x + bx
        y = piece.y + by
        if y >= 0:
            draw_cell(screen, x, y, piece.color)

    pygame.draw.rect(
        screen,
        (35, 35, 35),
        pygame.Rect(GRID_WIDTH * CELL_SIZE, 0, SIDE_PANEL_WIDTH, SCREEN_HEIGHT),
    )
    font = pygame.font.SysFont("Arial", 24)
    small_font = pygame.font.SysFont("Arial", 20)

    screen.blit(font.render("Tetris", True, WHITE), (GRID_WIDTH * CELL_SIZE + 28, 30))
    screen.blit(small_font.render(f"Score: {score}", True, WHITE), (GRID_WIDTH * CELL_SIZE + 20, 90))
    screen.blit(small_font.render(f"Level: {level}", True, WHITE), (GRID_WIDTH * CELL_SIZE + 20, 130))
    screen.blit(small_font.render(f"Lines: {lines}", True, WHITE), (GRID_WIDTH * CELL_SIZE + 20, 170))

    screen.blit(small_font.render("Controls:", True, WHITE), (GRID_WIDTH * CELL_SIZE + 20, 240))
    screen.blit(small_font.render("A/D  Move", True, WHITE), (GRID_WIDTH * CELL_SIZE + 20, 275))
    screen.blit(small_font.render("W    Rotate", True, WHITE), (GRID_WIDTH * CELL_SIZE + 20, 305))
    screen.blit(small_font.render("S    Drop", True, WHITE), (GRID_WIDTH * CELL_SIZE + 20, 335))
    screen.blit(small_font.render("Q    Quit", True, WHITE), (GRID_WIDTH * CELL_SIZE + 20, 365))

    pygame.display.flip()


def main():
    pygame.init()
    pygame.display.set_caption("Python Tetris")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    board = create_board()
    current_piece = random_piece()
    score = 0
    total_lines = 0
    level = 1
    game_over = False

    pygame.time.set_timer(DROP_EVENT, DROP_INTERVAL_MS)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit(0)
                if game_over:
                    continue
                if event.key == pygame.K_a and valid_position(board, current_piece, dx=-1):
                    current_piece.x -= 1
                elif event.key == pygame.K_d and valid_position(board, current_piece, dx=1):
                    current_piece.x += 1
                elif event.key == pygame.K_s:
                    if valid_position(board, current_piece, dy=1):
                        current_piece.y += 1
                elif event.key == pygame.K_w:
                    rotated = current_piece.rotated()
                    if valid_position(board, rotated):
                        current_piece = rotated

            if event.type == DROP_EVENT and not game_over:
                if valid_position(board, current_piece, dy=1):
                    current_piece.y += 1
                else:
                    lock_piece(board, current_piece)
                    board, cleared = clear_lines(board)
                    if cleared:
                        total_lines += cleared
                        score += [0, 100, 300, 500, 800][cleared] * level
                        level = total_lines // 10 + 1
                        interval = max(100, DROP_INTERVAL_MS - (level - 1) * 30)
                        pygame.time.set_timer(DROP_EVENT, interval)

                    current_piece = random_piece()
                    if not valid_position(board, current_piece):
                        game_over = True

        draw(screen, board, current_piece, score, level, total_lines)

        if game_over:
            font = pygame.font.SysFont("Arial", 40)
            text = font.render("Game Over", True, (255, 80, 80))
            screen.blit(text, (65, SCREEN_HEIGHT // 2 - 20))
            pygame.display.flip()

        clock.tick(FPS)


if __name__ == "__main__":
    main()
