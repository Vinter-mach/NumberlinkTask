import pygame
import sys

# Инициализация Pygame
pygame.init()

# Размер окна и количество клеток
window_size = (600, 600)
rows, cols = 4, 4
cell_size = window_size[0] // rows

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# Настройка окна
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("Ввод чисел в клетки")

# Шрифт для отображения чисел
font = pygame.font.Font(None, 50)

# Сетка для чисел
grid = [[None for _ in range(cols)] for _ in range(rows)]

# Текущая активная клетка
active_cell = None

def draw_grid():
    for row in range(rows):
        for col in range(cols):
            rect = pygame.Rect(col * cell_size, row * cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, BLACK, rect, 2)

            # Если в клетке есть число, рисуем его
            if grid[row][col] is not None:
                text = font.render(str(grid[row][col]), True, BLACK)
                screen.blit(text, (col * cell_size + 20, row * cell_size + 10))

def handle_click(pos):
    global active_cell
    col = pos[0] // cell_size
    row = pos[1] // cell_size
    active_cell = (row, col)

def handle_key_press(key):
    if active_cell is not None:
        row, col = active_cell
        if key >= pygame.K_0 and key <= pygame.K_9:  # Только числа
            grid[row][col] = key - pygame.K_0  # Преобразование к числу

# Основной игровой цикл
while True:
    screen.fill(WHITE)

    draw_grid()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            handle_click(event.pos)
        elif event.type == pygame.KEYDOWN:
            handle_key_press(event.key)

    pygame.display.flip()
