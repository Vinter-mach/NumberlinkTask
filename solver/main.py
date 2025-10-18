import solve_in_average as solver
import fast_solve as fast_solver
from ortools.sat.python import cp_model
import sys

from copy import deepcopy

n, m = map(int, input().split())

matrix = []
max_value = None
for i in range(n):
    matrix.append(list(map(int, input().split())))

for i in range(n):
    for j in range(m):
        max_value = matrix[i][j] if max_value is None else max(max_value, matrix[i][j])

sample_matrix = deepcopy(matrix)

second_solve = fast_solver.FastSolver(sample_matrix, n, m, max_value)

res = second_solve.try_solve()

if res is None:
    print("I can't solve it")
else:
    widths = [max(len(str(res[i][j])) for i in range(n)) for j in range(m)]
    border = '+' + '+'.join('-' * (w + 2) for w in widths) + '+'
    print(border)
    for i in range(n):
        row_str = '|' + '|'.join(f' {str(res[i][j][0]).rjust(widths[j])} ' for j in range(m)) + '|'
        print(row_str)
        print(border)
