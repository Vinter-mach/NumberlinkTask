import ortools.sat.python.cp_model
from ortools.sat.python import cp_model
from copy import deepcopy


class FastSolver:
    def __init__(self, matrix, line_count, column_count, max_value):
        self.matrix = matrix
        self.max_value = max_value
        self.condition_count = 7
        self.line_count = line_count
        self.column_count = column_count

        self.model = cp_model.CpModel()
        self.variables = {}
        self.condition = {}
        self.start_finish_values = {}

        self.delta = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        self.left = [1, 4, 5]
        self.right = [1, 3, 6]
        self.over = [2, 3, 4]
        self.under = [2, 5, 6]

        # requirement for every condition
        self.requirement = {i: ConditionRequirement([], [], [], []) for i in range(1, self.condition_count + 1)}
        self.update_requirement()

        # point condition bool
        self.point_condition = []

    def update_requirement(self):

        for i in range(1, self.condition_count):
            if i in self.right:
                self.requirement[i].left = self.left
            if i in self.left:
                self.requirement[i].right = self.right
            if i in self.under:
                self.requirement[i].over = self.over
            if i in self.over:
                self.requirement[i].under = self.under

    def is_in_matrix(self, position):
        return (
                -1 < position[0] < self.line_count and -1 < position[1] < self.column_count
        )

    def is_not_edge(self, i, j):
        return 0 < i < self.line_count - 1 and 0 < j < self.column_count - 1

    def check_exist_element(self, current_element, number_of_condition, requirement_for_condition, side_element):
        self.model.AddBoolOr(
            [current_element.condition[number_of_condition].Not(), len(requirement_for_condition) == 0,
             side_element is not None])

    def is_same_value_if_cond(self, requirement_values, current_element, side_element):
        for el in requirement_values:
            self.model.Add(self.variables[(current_element.i, current_element.j)] == self.variables[
                (side_element.i, side_element.j)]).OnlyEnforceIf(current_element.condition[el])

    def is_suitable_condition(self, current_condition, requirement_condition, current_element, side_element):
        for idx in current_condition:
            self.model.AddBoolOr(side_element.condition[el] for el in requirement_condition + [7]).OnlyEnforceIf(
                current_element.condition[idx])

    def is_condition_carried_out(self, current_element, left_element, right_element, under_element, over_element,
                                 number_of_condition):
        element_conditions = {
            'left': (self.left, self.right, left_element, self.requirement[number_of_condition].left),
            'right': (self.right, self.left, right_element, self.requirement[number_of_condition].right),
            'under': (self.under, self.over, under_element, self.requirement[number_of_condition].under),
            'over': (self.over, self.under, over_element, self.requirement[number_of_condition].over),
        }

        for direction, (
                current_condition, requirement_value, element, requirement_exist_around) in element_conditions.items():

            self.check_exist_element(current_element, number_of_condition, requirement_exist_around, element)

            if element is not None:
                self.is_same_value_if_cond(requirement_value, current_element, element)
                self.is_suitable_condition(requirement_value, current_condition, current_element, element)

    def model_prepare_var_make(self, i, j):
        if self.matrix[i][j] == 0:
            for idx in range(1, self.condition_count):
                current_element = self.point_condition[i][j]
                left_element = None if j == 0 else self.point_condition[i][j - 1]
                right_element = None if j == self.column_count - 1 else self.point_condition[i][j + 1]
                under_element = None if i == self.line_count - 1 else self.point_condition[i + 1][j]
                over_element = None if i == 0 else self.point_condition[i - 1][j]

                self.is_condition_carried_out(current_element, left_element, right_element, under_element, over_element,
                                              idx)
            return

    def generate_condition_for_point(self, i, j):
        if i == 0 and j == 1:
            self.condition[(i, j)] = self.model.NewIntVar(1, 1, f"_({i},{j})")
            return

        if self.matrix[i][j] != 0:
            self.condition[(i, j)] = self.model.NewIntVar(7, 7, f"_({i},{j})")
            return

        self.condition[(i, j)] = self.model.NewIntVar(1, 6, f"_({i},{j})")
        return None
        if self.is_not_edge(i, j):
            self.condition[(i, j)] = self.model.NewIntVar(1, 6, f"_({i},{j})")
            return

        if 0 < i < self.line_count - 1:
            if j == 0:
                self.condition[(i, j)] = self.model.NewIntVarFromDomain(
                    cp_model.Domain.FromValues([2, 4, 5]), f"_({i},{j})")
            else:
                self.condition[(i, j)] = self.model.NewIntVarFromDomain(
                    cp_model.Domain.FromValues([2, 3, 6]), f"_({i},{j})")

        else:
            if i == 0:
                if 0 < j < self.column_count - 1:
                    self.condition[(i, j)] = self.model.NewIntVarFromDomain(
                        cp_model.Domain.FromValues([1, 3, 4]), f"_({i},{j})")
                else:
                    if j == 0:
                        self.condition[(i, j)] = self.model.NewIntVar(4, 4, f"_({i},{j})")
                    else:
                        self.condition[(i, j)] = self.model.NewIntVar(2, 2, f"_({i},{j})")
            else:
                if 0 < j < self.column_count - 1:
                    self.condition[(i, j)] = self.model.NewIntVarFromDomain(
                        cp_model.Domain.FromValues([1, 5, 6]), f"_({i},{j})")
                else:
                    if j == 0:
                        self.condition[(i, j)] = self.model.NewIntVar(5, 5, f"_({i},{j})")
                    else:
                        self.condition[(i, j)] = self.model.NewIntVar(6, 6, f"_({i},{j})")

    def model_prepare(self):
        for i in range(self.line_count):
            row = []
            for j in range(self.column_count):

                self.generate_condition_for_point(i, j)

                if self.matrix[i][j] != 0:
                    self.variables[(i, j)] = self.model.NewIntVar(self.matrix[i][j], self.matrix[i][j], f"({i},{j})")
                else:
                    self.variables[(i, j)] = self.model.NewIntVar(1, self.max_value, f"({i},{j})")

                row.append(PointCondition(i, j, self))
            self.point_condition.append(row)

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
                    row.append([solver.value(self.variables[(i, j)]), solver.value(self.condition[(i, j)])])
                    print(i,
                          j,
                          [solver.value(self.point_condition[i][j].condition[el]) for el in
                           range(1, self.condition_count + 1)],
                          [solver.value(self.point_condition[i][j].value[el]) for el in range(1, self.max_value + 1)])
                result.append(deepcopy(row))
            return result

        return None


class ConditionRequirement:

    def __init__(self, left, right, under, over):
        self.left = left
        self.right = right
        self.under = under
        self.over = over


class PointCondition:
    def __init__(self, i: int, j: int, solver: FastSolver):
        self.i = i
        self.j = j
        self.solverSat = solver
        self.value = None
        self.condition = None

        # all conditions can't be false because we have checked correctness
        self.init_variable_state()

    def init_variable_state(self):
        # set point value
        self.value = {i: self.solverSat.model.NewBoolVar(f"{self.i, self.j} value is {i}") for i in
                      range(1, self.solverSat.max_value + 1)}

        # set point condition
        self.condition = {i: self.solverSat.model.NewBoolVar(
            f"{self.i, self.j} condition is {i}") for i in range(1, self.solverSat.condition_count + 1)}

        self.check_correctness(dict_bool_var=self.value, needed_variables=self.solverSat.variables)
        self.check_correctness(dict_bool_var=self.condition, needed_variables=self.solverSat.condition)

    def check_correctness(self, dict_bool_var: dict, needed_variables: dict):
        for idx in range(len(dict_bool_var)):
            self.solverSat.model.Add(needed_variables[(self.i, self.j)] == idx + 1).OnlyEnforceIf(
                dict_bool_var[idx + 1])
            self.solverSat.model.Add(needed_variables[(self.i, self.j)] != idx + 1).OnlyEnforceIf(
                dict_bool_var[idx + 1].Not())
