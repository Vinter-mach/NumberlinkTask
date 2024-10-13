import os
import pygame
import pygbutton
from datetime import datetime

from solver.cellinfo import CellInfo
from solver.fast_solve import FastSolver
from validator import InputValidator

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

SQUARE_SIZE, MARGIN = 40, 2
font = pygame.font.SysFont('Arial', 18)
pygbutton.PYGBUTTON_FONT = font
BG_COLOR = (200, 100, 220)


class SolverUi:

    def __init__(self):
        self.WIDTH = InputValidator.verified_pos_int("Введите ширину ", False)
        self.HEIGHT = InputValidator.verified_pos_int("Введите высоту ", False)
        self.COUNT = InputValidator.verified_pos_int("Введите количество различных цветов ", True)
        while self.COUNT > (self.WIDTH * self.HEIGHT) // 2:
            print("Цветов не может быть бльше чем половина клеток")
            self.COUNT = InputValidator.verified_pos_int("Введите количество различных цветов ", True)

        self.grid = [[CellInfo(0, 0)
                      for _ in range(self.HEIGHT)] for _ in range(self.WIDTH)]

        pygame.init()
        self.S_WIDTH, self.S_HEIGHT \
            = (self.WIDTH + 2) * SQUARE_SIZE + (self.WIDTH + 1) * MARGIN, (self.HEIGHT + 3) * SQUARE_SIZE + (
                self.HEIGHT + 1) * MARGIN
        self.screen = pygame.display.set_mode([self.S_WIDTH, self.S_HEIGHT])
        self.clock = pygame.time.Clock()

        # состояния
        self.DONE = False  # закончилась ли программа
        self.ADDING_COLORS = True  # активно ли состояние заполнения цветов
        self.CUR_LOC = None  # текущая выбранная позиция
        self.COLOR_POSITIONS = []  # позиции для каждого нажатия
        self.PRINTED = False
        self.SOLVE_ATTEMPTED = False
        self.SOLVE_FAILED = False

        self.addButton = pygbutton.PygButton(
            ((SQUARE_SIZE + (self.WIDTH + 1) * (MARGIN + SQUARE_SIZE)) // 2 - SQUARE_SIZE,
             (self.HEIGHT + 1) * (MARGIN + SQUARE_SIZE) + SQUARE_SIZE // 2,
             2 * SQUARE_SIZE, SQUARE_SIZE), "Добавить")

        self.solveButton = pygbutton.PygButton(((SQUARE_SIZE + (self.WIDTH + 1) * (MARGIN + SQUARE_SIZE)) // 2 -
                                                SQUARE_SIZE,
                                                (self.HEIGHT + 1) * (MARGIN + SQUARE_SIZE) + SQUARE_SIZE // 2,
                                                2 * SQUARE_SIZE, SQUARE_SIZE), "Решить")

        self.jpgButton = pygbutton.PygButton(((SQUARE_SIZE + (self.WIDTH + 1) * (MARGIN + SQUARE_SIZE) -
                                               (font.size("Сохранить")[0] + SQUARE_SIZE)) // 2,
                                              (self.HEIGHT + 1) * (MARGIN + SQUARE_SIZE) + SQUARE_SIZE // 2,
                                              font.size("Сохранить")[0] + SQUARE_SIZE, SQUARE_SIZE),
                                             "Сохранить")

        self.solveButton.visible = False
        self.jpgButton.visible = False
        self.buttons = [self.addButton, self.solveButton, self.jpgButton]

    def add_new_number_location(self):
        if len(self.COLOR_POSITIONS) < 2 * self.COUNT and self.CUR_LOC and self.CUR_LOC not in self.COLOR_POSITIONS:
            self.COLOR_POSITIONS.append(self.CUR_LOC)
            if len(self.COLOR_POSITIONS) % 2 == 0:
                print(f"New number: {self.COLOR_POSITIONS[-1]}, {self.COLOR_POSITIONS[-2]}")
            self.PRINTED = False
            self.grid[self.CUR_LOC[0]][self.CUR_LOC[1]].color = (len(self.COLOR_POSITIONS) + 1) // 2
        self.CUR_LOC = None

    def solve(self):
        solver_matrix = []
        for i in range(self.HEIGHT):
            line = []
            for j in range(self.WIDTH):
                line.append(self.grid[j][i].color)
            solver_matrix.append(line)

        fastSolver = FastSolver(solver_matrix, self.HEIGHT, self.WIDTH, self.COUNT)
        res = fastSolver.try_solve()

        # отладочный вывод
        # for i in range(self.HEIGHT):
        #     for j in range(self.WIDTH):
        #         print(res[i][j].state, end = ' ')
        #     print()

        if not res:
            return False

        for i in range(self.HEIGHT):
            for j in range(self.WIDTH):
                self.grid[j][i] = res[i][j]

        # отладочный вывод
        # for i in range(len(self.grid)):
        #     for j in range(len(self.grid[0])):
        #         print(self.grid[i][j].state, end = ' ')
        #     print()


        return True

    def is_exit_event(self, event):
        if event.type == pygame.QUIT:
            return True
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return True
        return False

    def run(self):
        while not self.DONE:
            for event in pygame.event.get():
                if self.is_exit_event(event):
                    self.DONE = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    # локация клика
                    if self.ADDING_COLORS:
                        if (SQUARE_SIZE + MARGIN) < pos[0] < (self.WIDTH + 1) * SQUARE_SIZE + self.WIDTH * MARGIN and \
                                ((SQUARE_SIZE + MARGIN) < pos[1] < (
                                        self.HEIGHT + 1) * SQUARE_SIZE + self.HEIGHT * MARGIN):
                            self.CUR_LOC = pos[0] // (SQUARE_SIZE + MARGIN) - 1, pos[1] // (SQUARE_SIZE + MARGIN) - 1

                # ивенты кнопок
                if 'click' in self.addButton.handleEvent(event):
                    if self.ADDING_COLORS:
                        self.add_new_number_location()
                elif 'click' in self.solveButton.handleEvent(event):
                    self.CUR_LOC, self.PRINTED = None, False
                    self.SOLVE_FAILED = not self.solve()
                    self.SOLVE_ATTEMPTED = True
                    self.solveButton.visible = False
                elif 'click' in self.jpgButton.handleEvent(event):
                    if not os.path.exists(os.path.join('Solutions')):
                        os.makedirs(os.path.join('Solutions'))
                    fname = os.path.join('Solutions') + datetime.now().strftime("/%m-%d-%Y-%H.%M.%S.jpg")
                    pygame.image.save(self.screen.subsurface(pygame.Rect(SQUARE_SIZE, SQUARE_SIZE,
                                                                         self.WIDTH * (SQUARE_SIZE + MARGIN) + MARGIN,
                                                                         self.HEIGHT * (
                                                                                     SQUARE_SIZE + MARGIN) + MARGIN)),
                                      fname)

            # Если все цвета добавлены
            if self.ADDING_COLORS and len(self.COLOR_POSITIONS) == 2 * self.COUNT:
                self.ADDING_COLORS = False
                self.addButton.visible = False
                self.solveButton.visible = True

            if not self.PRINTED and self.ADDING_COLORS:
                print(
                    f"Selecting cells for {len(self.COLOR_POSITIONS) // 2 + 1},"
                    f" cell #{len(self.COLOR_POSITIONS) % 2 + 1}.")
                self.PRINTED = True

            self.screen.fill(BG_COLOR)
            pygame.draw.rect(self.screen, (0, 0, 0), [SQUARE_SIZE, SQUARE_SIZE,
                                                      self.WIDTH * SQUARE_SIZE + (self.WIDTH + 1) * MARGIN,
                                                      self.HEIGHT * SQUARE_SIZE + (self.HEIGHT + 1) * MARGIN])

            # отрисовка поля
            for y in range(self.HEIGHT):
                for x in range(self.WIDTH):
                    pygame.draw.rect(self.screen, (255, 255, 255),
                                     [(x + 1) * (SQUARE_SIZE + MARGIN), (y + 1) * (SQUARE_SIZE + MARGIN),
                                      SQUARE_SIZE, SQUARE_SIZE])
                    # отрисовка стартовых цветов
                    if self.grid[x][y].color is not None:
                        text_surface = font.render(f"{self.grid[x][y].color}", True, (0, 0, 0))
                        text_size = font.size(f"{self.grid[x][y].color}")
                        self.screen.blit(text_surface,
                                         ((MARGIN + SQUARE_SIZE) * (x + 1) + (SQUARE_SIZE - text_size[0]) // 2,
                                          (MARGIN + SQUARE_SIZE) * (y + 1) + (SQUARE_SIZE - text_size[1]) // 2))

            for y in range(self.HEIGHT):
                for x in range(self.WIDTH):
                    # рисуем решение
                    p1 = [(x + 1) * (MARGIN + SQUARE_SIZE) + SQUARE_SIZE // 2, (y + 1) *
                          (MARGIN + SQUARE_SIZE) + SQUARE_SIZE // 2]

                    if self.grid[x][y].state == 1 or self.grid[x][y].state == 3 or self.grid[x][y].state == 6:
                        # left
                        p2 = p1.copy()
                        p2[0] = p2[0] - SQUARE_SIZE
                        pygame.draw.line(self.screen, (255, 0, 0), p1, p2, MARGIN)

                    if self.grid[x][y].state == 1 or self.grid[x][y].state == 4 or self.grid[x][y].state == 5:
                        # right
                        p2 = p1.copy()
                        p2[0] = p2[0] + SQUARE_SIZE
                        pygame.draw.line(self.screen, (255, 0, 0), p1, p2, MARGIN)

                    if self.grid[x][y].state == 2 or self.grid[x][y].state == 5 or self.grid[x][y].state == 6:
                        # top
                        p2 = p1.copy()
                        p2[1] = p2[1] - SQUARE_SIZE
                        pygame.draw.line(self.screen, (255, 0, 0), p1, p2, MARGIN)

                    if self.grid[x][y].state == 2 or self.grid[x][y].state == 3 or self.grid[x][y].state == 4:
                        # bottom
                        p2 = p1.copy()
                        p2[1] = p2[1] + SQUARE_SIZE
                        pygame.draw.line(self.screen, (255, 0, 0), p1, p2, MARGIN)

            if self.SOLVE_ATTEMPTED:
                if self.SOLVE_FAILED:
                    red_surface = pygame.Surface((self.WIDTH * (SQUARE_SIZE + MARGIN) + MARGIN,
                                                  self.HEIGHT * (SQUARE_SIZE + MARGIN) + MARGIN))
                    red_surface.set_alpha(75)
                    red_surface.fill((255, 0, 0))
                    self.screen.blit(red_surface, (SQUARE_SIZE, SQUARE_SIZE))

                    for button in self.buttons:
                        button.visible = False

                    text_surface = font.render("Пазл не решаем", True, (0, 0, 0))
                    text_size = font.size("Пазл не решаем")
                    self.screen.blit(text_surface,
                                     ((self.S_WIDTH - text_size[0]) // 2,
                                      self.S_HEIGHT - SQUARE_SIZE - text_size[1] // 2))
                else:
                    self.jpgButton.visible = True
            if self.CUR_LOC:
                x, y = self.CUR_LOC
                pygame.draw.rect(self.screen, (255, 0, 0), [(x + 1) * (SQUARE_SIZE + MARGIN) - MARGIN,
                                                            (y + 1) * (SQUARE_SIZE + MARGIN) - MARGIN,
                                                            SQUARE_SIZE + 1.5 * MARGIN,
                                                            SQUARE_SIZE + 1.5 * MARGIN], MARGIN)
            for button in self.buttons:
                button.draw(self.screen)
            self.clock.tick(60)
            pygame.display.flip()

        pygame.quit()
