import copy
import time

delta = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def check_in_field(x, y, line_count, column_count):
    return -1 < x < line_count and -1 < y < column_count


def have_way(all_matrix, matrix, line_count, column_count, cur_vertex, visited, start_vertex, finish_vertex):
    if not check_in_field(cur_vertex[0], cur_vertex[1], line_count, column_count):
        return False
    if visited[cur_vertex[0]][cur_vertex[1]]:
        return False
    if cur_vertex == finish_vertex:
        return True
    if cur_vertex != start_vertex and matrix[cur_vertex[0]][cur_vertex[1]] != 0:
        return False
    visited[cur_vertex[0]][cur_vertex[1]] = True
    all_matrix[cur_vertex[0]][cur_vertex[1]] = 1
    result = False
    for i in range(len(delta)):
        next_vertex = (cur_vertex[0] + delta[i][0], cur_vertex[1] + delta[i][1])
        result |= have_way(all_matrix, matrix, line_count, column_count, next_vertex, visited, start_vertex,
                           finish_vertex)
    return result


def check_is_not_break(matrix, line_count, column_count, start_and_finish):
    all_matrix = copy.deepcopy(matrix)
    checked = []
    for i in range(line_count):
        for j in range(column_count):
            if matrix[i][j] != 0 and matrix[i][j] not in checked:
                checked.append(matrix[i][j])
                visited = [[False] * column_count for _ in range(line_count)]
                start_vertex = start_and_finish[matrix[i][j]][0]
                finish_vertex = start_and_finish[matrix[i][j]][1]
                if not have_way(all_matrix, matrix, line_count, column_count, start_vertex, visited,
                                start_vertex, finish_vertex):
                    return False

    for i in range(line_count):
        for j in range(column_count):
            if all_matrix[i][j] == 0:
                return False
    return True


def dfs(sample_matrix, matrix, line_count, column_count, finish, current_vertex, line_number, visited, current_path,
        all_path, start_and_finish):
    if not check_in_field(current_vertex[0], current_vertex[1], line_count, column_count):
        return
    if visited[current_vertex[0]][current_vertex[1]]:
        return
    if (matrix[current_vertex[0]][current_vertex[1]] != 0 and
            matrix[current_vertex[0]][current_vertex[1]] != line_number):
        return
    if not check_is_not_break(matrix, line_count, column_count, start_and_finish):
        return
    if current_vertex == finish and len(current_path) != 0:
        current_path.append(current_vertex)
        before = start_and_finish[line_number][0]
        start_and_finish[line_number][0] = current_vertex
        if check_is_not_break(matrix, line_count, column_count, start_and_finish):
            all_path.append(current_path.copy())
        start_and_finish[line_number][0] = before
        current_path.pop()
        return

    current_path.append(current_vertex)
    visited[current_vertex[0]][current_vertex[1]] = True
    matrix[current_vertex[0]][current_vertex[1]] = line_number
    before = start_and_finish[line_number][0]
    start_and_finish[line_number][0] = current_vertex

    for i in range(len(delta)):
        next_vertex = (current_vertex[0] + delta[i][0], current_vertex[1] + delta[i][1])
        dfs(sample_matrix, matrix, line_count, column_count, finish, next_vertex, line_number, visited, current_path,
            all_path, start_and_finish)

    matrix[current_vertex[0]][current_vertex[1]] = sample_matrix[current_vertex[0]][current_vertex[1]]
    visited[current_vertex[0]][current_vertex[1]] = False
    start_and_finish[line_number][0] = before
    current_path.pop()


start = time.monotonic()
n, m = map(int, input().split())

matrix = []

for i in range(n):
    matrix.append(list(map(int, input().split())))

visited = [[False] * m for _ in range(n)]

paths_for_number = dict()
sample_matrix = copy.deepcopy(matrix)

start_and_finish = dict()

for i in range(len(matrix)):
    for j in range(len(matrix[i])):
        if matrix[i][j] != 0:
            if matrix[i][j] not in start_and_finish:
                start_and_finish[matrix[i][j]] = list()
            start_and_finish[matrix[i][j]].append((i, j))

for i in range(len(matrix)):
    for j in range(len(matrix[i])):
        if matrix[i][j] == 0:
            continue
        if matrix[i][j] in paths_for_number:
            continue
        all_path = []
        current_path = []
        finish = start_and_finish[matrix[i][j]][-1]
        dfs(sample_matrix, matrix, n, m, finish, (i, j), matrix[i][j], visited, current_path, all_path,
            start_and_finish)
        paths_for_number[matrix[i][j]] = all_path
finish = time.monotonic()
print(finish - start)

for key in paths_for_number:
    print(key)
    for path in paths_for_number[key]:
        print(*path)
