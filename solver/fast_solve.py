from ortools.sat.python import cp_model
from copy import deepcopy


class FastSolver:
    def __init__(self, matrix, line_count, column_count, max_value):
        self.matrix = matrix
        self.max_value = max_value
        self.line_count = line_count

        self.column_count = column_count
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()

        self.variables = dict()
        self.delta = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    def is_in_matrix(self, position):
        return -1 < position[0] < self.line_count and -1 < position[1] < self.column_count

    def get_count_same_value(self, position, value):
        counter = 0
        for d in self.delta:
            new_position = (position[0] + d[0], position[1] + d[1])
            if self.is_in_matrix(new_position) and self.matrix[new_position[0]][new_position[1]] == value:
                counter += 1
        return counter

    def model_prepare(s):
        start_finish_values = dict()
        for i in range(s.line_count):
            for j in range(s.column_count):
                if s.matrix[i][j] != 0:
                    if s.matrix[i][j] not in start_finish_values:
                        start_finish_values = list()
                    start_finish_values.append((i, j))
                    s.variables[(i, j)] = s.model.new_int_var(s.matrix[i][j], s.matrix[i][j], f'({i}, {j})')
                s.variables[(i, j)] = s.model.new_int_var(1, s.max_value, f'({i}, {j})')

        for element in start_finish_values:
            for pos in start_finish_values[element]:
                s.model.add(s.get_count_same_value(pos, s.matrix[pos[0]][pos[1]]) == 1)

        for i in range(s.line_count):
            for j in range(s.column_count):
                if (i, j) in start_finish_values[s.matrix[i][j]]:
                    continue
                s.model.add(s.get_count_same_value((i, j), s.matrix[i][j]) == 2)

    def try_solve(self):
        status = self.solver.solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            result = []
            for i in range(self.line_count):
                row = []
                for j in range(self.column_count):
                    row.append(self.solver.value(self.variables[(i, j)]))
                result.append(deepcopy(row))
            return result

        return None
