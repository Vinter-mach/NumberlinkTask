import copy
import time


class Solver:
    def __init__(self, matrix, line_count, column_count):
        self.delta = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        self.matrix = matrix
        self.answer = None
        self.sample_matrix = copy.deepcopy(self.matrix)
        self.line_count = line_count
        self.column_count = column_count
        self.paths_for_number = dict()
        self.start_and_finish = dict()

        self.get_all_paths()

    def check_in_field(self, x, y):
        return -1 < x < self.line_count and -1 < y < self.column_count

    def have_way(self, all_matrix, visited, start_vertex, finish_vertex):
        if start_vertex == finish_vertex:
            return True

        list_next_vertex = [start_vertex]
        result = False

        while list_next_vertex:
            current_vertex = list_next_vertex.pop()

            if current_vertex == finish_vertex:
                result = True

            visited[current_vertex[0]][current_vertex[1]] = True
            all_matrix[current_vertex[0]][current_vertex[1]] = 1

            for i in range(len(self.delta)):
                next_vertex = (current_vertex[0] + self.delta[i][0], current_vertex[1] + self.delta[i][1])

                if next_vertex == finish_vertex:
                    result = True

                if (not self.check_in_field(next_vertex[0], next_vertex[1]) or
                        visited[next_vertex[0]][next_vertex[1]] or
                        (next_vertex != start_vertex and self.matrix[next_vertex[0]][next_vertex[1]] != 0)):
                    continue

                list_next_vertex.append(next_vertex)
        return result

    def check_is_not_break(self, start_and_finish):
        all_matrix = copy.deepcopy(self.matrix)
        checked = []

        for i in range(self.line_count):
            for j in range(self.column_count):
                if self.matrix[i][j] != 0 and self.matrix[i][j] not in checked:
                    checked.append(self.matrix[i][j])
                    visited = [[False] * self.column_count for _ in range(self.line_count)]
                    start_vertex = start_and_finish[self.matrix[i][j]][0]
                    finish_vertex = start_and_finish[self.matrix[i][j]][1]

                    if not self.have_way(all_matrix, visited, start_vertex, finish_vertex):
                        return False

        for i in range(self.line_count):
            for j in range(self.column_count):
                if all_matrix[i][j] == 0:
                    return False

        return True

    def dfs(self, finish, current_vertex, line_number, visited, current_path,
            all_path, start_and_finish):
        if (not self.check_in_field(current_vertex[0], current_vertex[1]) or
                visited[current_vertex[0]][current_vertex[1]] or
                not self.check_is_not_break(start_and_finish)):
            return

        if (self.matrix[current_vertex[0]][current_vertex[1]] != 0 and
                self.matrix[current_vertex[0]][current_vertex[1]] != line_number):
            return

        if current_vertex == finish and len(current_path) != 0:
            current_path.append(current_vertex)
            before = start_and_finish[line_number][0]
            start_and_finish[line_number][0] = current_vertex

            if self.check_is_not_break(start_and_finish):
                all_path.append(current_path.copy())

            start_and_finish[line_number][0] = before
            current_path.pop()

            return

        current_path.append(current_vertex)
        visited[current_vertex[0]][current_vertex[1]] = True
        self.matrix[current_vertex[0]][current_vertex[1]] = line_number
        before = start_and_finish[line_number][0]
        start_and_finish[line_number][0] = current_vertex

        for i in range(len(self.delta)):
            next_vertex = (current_vertex[0] + self.delta[i][0], current_vertex[1] + self.delta[i][1])
            self.dfs(finish, next_vertex, line_number, visited,
                     current_path,
                     all_path, start_and_finish)

        self.matrix[current_vertex[0]][current_vertex[1]] = self.sample_matrix[current_vertex[0]][current_vertex[1]]
        visited[current_vertex[0]][current_vertex[1]] = False
        start_and_finish[line_number][0] = before
        current_path.pop()

    def match_paths(self, current_number: int, current_path):
        if current_number == len(self.paths_for_number) + 1:
            for i in range(len(current_path)):
                cur_num = current_path[i][0]
                cur_path = self.paths_for_number[cur_num][current_path[i][1]]
                for j in range(len(cur_path)):
                    if self.matrix[cur_path[j][0]][cur_path[j][1]] != 0 and j != 0 and j != len(cur_path) - 1:
                        self.matrix = copy.deepcopy(self.sample_matrix)
                        return False
                    self.matrix[cur_path[j][0]][cur_path[j][1]] = cur_num
            for i in range(self.line_count):
                for j in range(self.column_count):
                    if self.matrix[i][j] == 0:
                        return False
            return True

        for i in range(len(self.paths_for_number[current_number])):
            current_path.append((current_number, i))
            if self.match_paths(current_number + 1, current_path):
                return True
            current_path.pop()

    def get_local_result(self, current_number: int):
        current_path = []
        return self.match_paths(current_number, current_path)

    def get_answer(self):
        may_result = self.get_local_result(1)
        if not may_result:
            print("Oh no, I can't to solve it")
            return

        for i in range(self.line_count):
            for j in range(self.column_count):
                print(self.matrix[i][j], end=" ")
            print()

    def get_all_paths(self):
        visited = [[False] * self.column_count for _ in range(self.line_count)]

        for i in range(self.line_count):
            for j in range(self.column_count):
                if self.matrix[i][j] != 0:
                    if self.matrix[i][j] not in self.start_and_finish:
                        self.start_and_finish[self.matrix[i][j]] = list()
                    self.start_and_finish[self.matrix[i][j]].append((i, j))

        for i in range(self.line_count):
            for j in range(self.column_count):
                if self.matrix[i][j] == 0:
                    continue
                if self.matrix[i][j] in self.paths_for_number:
                    continue

                all_path = []
                current_path = []
                finish = self.start_and_finish[self.matrix[i][j]][-1]
                self.dfs(finish, (i, j), self.matrix[i][j], visited, current_path, all_path,
                         self.start_and_finish)

                self.paths_for_number[self.matrix[i][j]] = all_path

        return self.paths_for_number
