from ortools.sat.python import cp_model
from copy import deepcopy


class FastSolver:
    def __init__(self, matrix, line_count, column_count, max_value):
        self.matrix = matrix
        self.max_value = max_value
        self.line_count = line_count
        self.column_count = column_count
        self.req = {}

        self.model = cp_model.CpModel()
        self.variables = {}
        self.condition = {}
        self.test = {}

        self.delta = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        self.left = [1, 4, 5, 7]
        self.right = [1, 3, 6, 7]
        self.over = [2, 3, 4, 7]
        self.under = [2, 5, 6, 7]
        # 0 - left, 1 - right, 2 - over, 3 - under (connection)

    def is_in_matrix(self, position):
        return (
                -1 < position[0] < self.line_count and -1 < position[1] < self.column_count
        )

    def create_point_conditions(self, point_name, a, j):
        return [
            self.model.NewBoolVar(f"condition {point_name} point is {i + 1}")
            for i in range(7)
        ]

    def create_point_not_conditions(self, point_name):
        return [
            self.model.NewBoolVar(f"not condition {point_name} point is {i + 1}")
            for i in range(7)
        ]

    def make_block_1(
            self,
            current_point_not_condition,
            left_point_condition,
            right_point_condition,
            value_bool,
    ):
        self.model.AddBoolOr(
            [
                current_point_not_condition[0],
                left_point_condition[0],
                left_point_condition[3],
                left_point_condition[4],
                left_point_condition[6],
            ]
        )

        self.model.AddBoolOr(
            [
                current_point_not_condition[0],
                right_point_condition[0],
                right_point_condition[2],
                right_point_condition[5],
                right_point_condition[6],
            ]
        )

        self.model.AddBoolOr(
            [
                current_point_not_condition[0],
                value_bool[0],
            ]
        )

        self.model.AddBoolOr(
            [
                current_point_not_condition[0],
                value_bool[1],
            ]
        )

    def make_block_2(
            self,
            current_point_not_condition,
            over_point_condition,
            under_point_condition,
            value_bool,
    ):
        self.model.AddBoolOr(
            [
                current_point_not_condition[1],
                over_point_condition[1],
                over_point_condition[2],
                over_point_condition[3],
                over_point_condition[6],
            ]
        )

        self.model.AddBoolOr(
            [
                current_point_not_condition[1],
                under_point_condition[1],
                under_point_condition[4],
                under_point_condition[5],
                under_point_condition[6],
            ]
        )

        self.model.AddBoolOr(
            [
                current_point_not_condition[1],
                value_bool[2],
            ]
        )

        self.model.AddBoolOr(
            [
                current_point_not_condition[1],
                value_bool[3],
            ]
        )

    def make_block_3(
            self,
            current_point_not_condition,
            left_point_condition,
            under_point_condition,
            value_bool,
    ):
        self.model.AddBoolOr(
            [
                current_point_not_condition[2],
                left_point_condition[0],
                left_point_condition[3],
                left_point_condition[4],
                left_point_condition[6],
            ]
        )

        self.model.AddBoolOr(
            [
                current_point_not_condition[2],
                under_point_condition[1],
                under_point_condition[4],
                under_point_condition[5],
                under_point_condition[6],
            ]
        )

        self.model.AddBoolOr(
            [
                current_point_not_condition[2],
                value_bool[0],
            ]
        )

        self.model.AddBoolOr(
            [
                current_point_not_condition[2],
                value_bool[3],
            ]
        )

    def make_block_4(
            self,
            current_point_not_condition,
            right_point_condition,
            under_point_condition,
            value_bool,
    ):
        self.model.AddBoolOr(
            [
                current_point_not_condition[3],
                right_point_condition[0],
                right_point_condition[2],
                right_point_condition[5],
                right_point_condition[6],
            ]
        )

        self.model.AddBoolOr(
            [
                current_point_not_condition[3],
                under_point_condition[1],
                under_point_condition[4],
                under_point_condition[5],
                under_point_condition[6],
            ]
        )

        self.model.AddBoolOr(
            [
                current_point_not_condition[3],
                value_bool[1],
            ]
        )

        self.model.AddBoolOr(
            [
                current_point_not_condition[3],
                value_bool[3],
            ]
        )

    def make_block_5(
            self,
            current_point_not_condition,
            right_point_condition,
            over_point_condition,
            value_bool,
    ):
        self.model.AddBoolOr(
            [
                current_point_not_condition[4],
                right_point_condition[0],
                right_point_condition[2],
                right_point_condition[5],
                right_point_condition[6],
            ]
        )

        self.model.AddBoolOr(
            [
                current_point_not_condition[4],
                over_point_condition[1],
                over_point_condition[2],
                over_point_condition[3],
                over_point_condition[6],
            ]
        )

        self.model.AddBoolOr(
            [
                current_point_not_condition[4],
                value_bool[1],
            ]
        )

        self.model.AddBoolOr(
            [
                current_point_not_condition[4],
                value_bool[2],
            ]
        )

    def make_block_6(
            self,
            current_point_not_condition,
            left_point_condition,
            over_point_condition,
            value_bool,
    ):
        self.model.AddBoolOr(
            [
                current_point_not_condition[5],
                left_point_condition[0],
                left_point_condition[3],
                left_point_condition[4],
                left_point_condition[6],
            ]
        )

        self.model.AddBoolOr(
            [
                current_point_not_condition[5],
                over_point_condition[1],
                over_point_condition[2],
                over_point_condition[3],
                over_point_condition[6],
            ]
        )

        self.model.AddBoolOr(
            [
                current_point_not_condition[5],
                value_bool[0],
            ]
        )

        self.model.AddBoolOr(
            [
                current_point_not_condition[5],
                value_bool[2],
            ]
        )

    def model_prepare_var_make(self, i, j):
        value_bool = [
            self.model.NewBoolVar("value left same"),
            self.model.NewBoolVar("value right same"),
            self.model.NewBoolVar("value over same"),
            self.model.NewBoolVar("value under same"),
        ]

        current_point_condition = self.create_point_conditions("current", i, j)
        current_point_not_condition = self.create_point_not_conditions("current")
        left_point_condition = self.create_point_conditions("left", i, j)
        right_point_condition = self.create_point_conditions("right", i, j)
        under_point_condition = self.create_point_conditions("under", i, j)
        over_point_condition = self.create_point_conditions("over", i, j)

        if j > 0:
            self.model.Add(
                self.variables[(i, j)] == self.variables[(i, j - 1)]
            ).OnlyEnforceIf(value_bool[0])
        if j < self.column_count - 1:
            self.model.Add(
                self.variables[(i, j)] == self.variables[(i, j + 1)]
            ).OnlyEnforceIf(value_bool[1])
        if i > 0:
            self.model.Add(
                self.variables[(i, j)] == self.variables[(i - 1, j)]
            ).OnlyEnforceIf(value_bool[2])
        if i < self.line_count - 1:
            self.model.Add(
                self.variables[(i, j)] == self.variables[(i + 1, j)]
            ).OnlyEnforceIf(value_bool[3])

        for num in current_point_condition:
            self.model.Add(self.condition[(i, j)] == int(num.name[-1])).OnlyEnforceIf(
                num
            )

        for num in current_point_not_condition:
            self.model.Add(self.condition[(i, j)] != int(num.name[-1])).OnlyEnforceIf(
                num
            )

        if j > 0:
            for num in left_point_condition:
                self.model.Add(
                    self.condition[(i, j - 1)] == int(num.name[-1])
                ).OnlyEnforceIf(num)
        if j < self.column_count - 1:
            for num in right_point_condition:
                self.model.Add(
                    self.condition[(i, j + 1)] == int(num.name[-1])
                ).OnlyEnforceIf(num)
        if i > 0:
            for num in over_point_condition:
                self.model.Add(
                    self.condition[(i - 1, j)] == int(num.name[-1])
                ).OnlyEnforceIf(num)
        if i < self.line_count - 1:
            for num in under_point_condition:
                self.model.Add(
                    self.condition[(i + 1, j)] == int(num.name[-1])
                ).OnlyEnforceIf(num)

        # for 1 condition
        if j != 0 and j != self.column_count - 1:
            self.make_block_1(
                current_point_not_condition,
                left_point_condition,
                right_point_condition,
                value_bool,
            )

        # for 2 condition
        if i != 0 and i != self.line_count - 1:
            self.make_block_2(
                current_point_not_condition,
                over_point_condition,
                under_point_condition,
                value_bool,
            )

        # for 3 condition
        if j != 0 and i != self.column_count - 1:
            self.make_block_3(
                current_point_not_condition,
                left_point_condition,
                under_point_condition,
                value_bool,
            )

        # for 4 condition
        if j != self.column_count - 1 and i != self.line_count - 1:
            self.make_block_4(
                current_point_not_condition,
                left_point_condition,
                under_point_condition,
                value_bool,
            )
        # for 5 condition
        if j != self.column_count - 1 and i != 0:
            self.make_block_5(
                current_point_not_condition,
                right_point_condition,
                over_point_condition,
                value_bool,
            )
        # for 6 condition
        if j != 0 and i != 0:
            self.make_block_6(
                current_point_not_condition,
                left_point_condition,
                over_point_condition,
                value_bool,
            )

        self.model.Add(self.condition[(i, j)] != 1).OnlyEnforceIf(j == 0)
        self.model.Add(self.condition[(i, j)] != 3).OnlyEnforceIf(j == 0)
        self.model.Add(self.condition[(i, j)] != 6).OnlyEnforceIf(j == 0)

        self.model.Add(self.condition[(i, j)] != 1).OnlyEnforceIf(
            j == self.column_count - 1
        )
        self.model.Add(self.condition[(i, j)] != 4).OnlyEnforceIf(
            j == self.column_count - 1
        )
        self.model.Add(self.condition[(i, j)] != 5).OnlyEnforceIf(
            j == self.column_count - 1
        )

        left_request = False if j == 0 else self.model.NewBoolVar("left request")
        right_request = False if j == self.column_count - 1 else self.model.NewBoolVar("right request")
        over_request = False if i == 0 else self.model.NewBoolVar("over request")
        under_request = False if i == self.column_count - 1 else self.model.NewBoolVar("under request")

        self.req[(i, j)] = [left_request, right_request, over_request, under_request, current_point_condition[6]]

        if j > 0:
            self.model.AddBoolOr([left_point_condition[0], left_point_condition[3], left_point_condition[4],
                                  left_point_condition[6]]).OnlyEnforceIf(left_request)
        if j < self.column_count - 1:
            self.model.AddBoolOr([right_point_condition[0], right_point_condition[2], right_point_condition[5],
                                  right_point_condition[6]]).OnlyEnforceIf(right_request)
        if i > 0:
            self.model.AddBoolOr([over_point_condition[1], over_point_condition[2], over_point_condition[3],
                                  over_point_condition[6]]).OnlyEnforceIf(over_request)
        if i < self.line_count - 1:
            self.model.AddBoolOr([under_point_condition[1], under_point_condition[4], under_point_condition[5],
                                  under_point_condition[6]]).OnlyEnforceIf(under_request)

        self.model.Add((left_request + right_request + over_request + under_request) == 1).OnlyEnforceIf(
            current_point_condition[6])

        self.model.Add(self.condition[(i, j)] != 2).OnlyEnforceIf(i == 0)
        self.model.Add(self.condition[(i, j)] != 5).OnlyEnforceIf(i == 0)
        self.model.Add(self.condition[(i, j)] != 6).OnlyEnforceIf(i == 0)

        self.model.Add(self.condition[(i, j)] != 2).OnlyEnforceIf(
            i == self.line_count - 1
        )
        self.model.Add(self.condition[(i, j)] != 3).OnlyEnforceIf(
            i == self.line_count - 1
        )
        self.model.Add(self.condition[(i, j)] != 4).OnlyEnforceIf(
            i == self.line_count - 1
        )

    def model_prepare(self):
        start_finish_values = {}

        for i in range(self.line_count):
            for j in range(self.column_count):

                if self.matrix[i][j] != 0:

                    if self.matrix[i][j] not in start_finish_values:
                        start_finish_values[self.matrix[i][j]] = list()

                    start_finish_values[self.matrix[i][j]].append((i, j))

                    self.variables[(i, j)] = self.model.NewIntVar(
                        self.matrix[i][j], self.matrix[i][j], f"({i},{j})"
                    )
                    self.condition[(i, j)] = self.model.NewIntVar(7, 7, f"_({i},{j})")
                    continue

                self.variables[(i, j)] = self.model.NewIntVar(
                    1, self.max_value, f"({i},{j})"
                )
                self.condition[(i, j)] = self.model.NewIntVar(1, 6, f"_({i},{j})")

        # !cond[i][j] == 1 or (((cond[i][j - 1] in left or cond[i][j + 1] in right)) and value[i][j] == value[i - 1][j] and value[i][j] == value[i + 1][j])
        # (!cond[i][j] == 1 or cond[i][j - 1] in left) and (!cond[i][j] == 1 or cond[i][j + 1] in right) and (!cond[i][j] == 1 or value[i][j] == value[i - 1][j]) and (!cond[i][j] == 1 or value[i][j] == value[i + 1][j])
        # a = self.model.new_constant()

        for i in range(self.line_count):
            for j in range(self.column_count):
                self.model_prepare_var_make(i, j)

    def try_solve(self):

        self.model_prepare()

        solver = cp_model.CpSolver()

        status = solver.solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            result = []
            for i in range(self.line_count):
                row = []
                for j in range(self.column_count):
                    for el in self.req[(i, j)]:
                        print(solver.value(el), end=" ")
                    print()
                    row.append([solver.value(self.variables[(i, j)]), solver.value(self.condition[(i, j)])])
                    # row.append(solver.value(self.variables[(i, j)]))
                result.append(deepcopy(row))
            return result

        return None
