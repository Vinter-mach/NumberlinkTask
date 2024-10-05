import solve_in_average as solver
import fast_solve as fast_solver
from ortools.sat.python import cp_model

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

#solv = solver.Solver(matrix, n, m)
second_solve = fast_solver.FastSolver(sample_matrix, n, m, max_value)

#solv.get_answer()

res = second_solve.try_solve()

print("second solve:")

if res is None:
    print("I can't solve it")
else:
    for i in range(n):
        for j in range(m):
            print(res[i][j], end=" ")
        print()
