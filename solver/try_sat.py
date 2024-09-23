from ortools.sat.python import cp_model

matrix = []
for i in range(9):
    matrix.append(list(map(int, input().split())))

model = cp_model.CpModel()

position = {}

for i in range(9):
    for j in range(9):
        if matrix[i][j] != 0:
            position[f'({i}, {j})'] = model.new_int_var(matrix[i][j], matrix[i][j], f'({i}, {j})')
            continue
        position[f'({i}, {j})'] = model.new_int_var(1, 9, f'({i}, {j})')

# check square constraints
for delta_x in range(3):
    for delta_y in range(3):
        position_in_square = []
        for x in range(3):
            for y in range(3):
                position_in_square.append(f'({x + 3 * delta_x}, {y + 3 * delta_y})')
        for i in range(len(position_in_square)):
            for j in range(i + 1, len(position_in_square)):
                model.add(position[position_in_square[i]] != position[position_in_square[j]])

# check vertical and horizontal constraints
for i in range(9):
    position_in_vertical = []
    position_in_horizontal = []
    for j in range(9):
        position_in_vertical.append(f'({j}, {i})')
        position_in_horizontal.append(f'({i}, {j})')
    for k in range(len(position_in_vertical)):
        for m in range(k + 1, len(position_in_vertical)):
            model.add(position[position_in_vertical[k]] != position[position_in_vertical[m]])
            model.add(position[position_in_horizontal[k]] != position[position_in_horizontal[m]])

# check diagonal constraints
# for i in range(18):
#     diag_x = i
#     diag_y = 0
#     if i >= 9:
#         diag_x, diag_y = diag_y, diag_x
#     position_in_diagonal = []
#     while -1 < diag_x < 9 and -1 < diag_y < 9:
#         position_in_diagonal.append(f'({diag_x}, {diag_y})')
#         diag_x += 1
#         diag_y += 1
#     for k in range(len(position_in_diagonal)):
#         for m in range(k + 1, len(position_in_diagonal)):
#             model.add(position[position_in_diagonal[k]] != position[position_in_diagonal[m]])

solver = cp_model.CpSolver()
status = solver.solve(model)
print(status)
for i in range(9):
    print()
    for j in range(9):
        if matrix[i][j] == 0:
            print("\033[31m" + f'{solver.value(position[f'({i}, {j})'])}' + "\033[0m", end=" ")
            continue
        print(f'{solver.value(position[f'({i}, {j})'])}', end=" ")
