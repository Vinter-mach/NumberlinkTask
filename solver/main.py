import solve_in_average as solver

n, m = map(int, input().split())

matrix = []

for i in range(n):
    matrix.append(list(map(int, input().split())))

solv = solver.Solver(matrix, n, m)

solv.get_answer()
