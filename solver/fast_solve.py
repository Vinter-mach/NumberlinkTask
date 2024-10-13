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
        self.numbers = {}
        self.condition = {}
        self.origin_values = {}
        self.origin_points = {_: [] for _ in range(1, self.max_value + 1)}

        self.delta = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        self.left = [1, 4, 5]
        self.right = [1, 3, 6]
        self.over = [2, 3, 4]
        self.under = [2, 5, 6]

        # requirement for every condition
        self.requirement = {_: ConditionRequirement([], [], [], []) for _ in range(1, self.condition_count + 1)}
        self.update_requirement()

        # point condition bool
        self.point_condition = None

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

    def check_equivalence(self, element, element_request, element_list):
        if element is None:
            return

        self.model.AddBoolOr(
            element_request.Not() if i == len(element_list) else element.condition[element_list[i]]
            for i in range(len(element_list) + 1))

        for el in element_list:
            self.model.AddBoolOr([element.condition[el].Not(), element_request])

    def check_is_same_less(self, expression, side_element, cur_i, cur_j):
        self.model.Add(
            self.numbers[(side_element.i, side_element.j)] == self.numbers[(cur_i, cur_j)] - 1).OnlyEnforceIf(
            expression)
        self.model.Add(
            self.numbers[(side_element.i, side_element.j)] != self.numbers[(cur_i, cur_j)] - 1).OnlyEnforceIf(
            expression.Not())

    def check_is_same_more(self, expression, side_element, cur_i, cur_j):
        self.model.Add(
            self.numbers[(side_element.i, side_element.j)] == self.numbers[(cur_i, cur_j)] + 1).OnlyEnforceIf(
            expression)
        self.model.Add(
            self.numbers[(side_element.i, side_element.j)] != self.numbers[(cur_i, cur_j)] + 1).OnlyEnforceIf(
            expression.Not())

    def create_element_bool_vars(self, direction, cur_i, cur_j):
        return (
            self.model.NewBoolVar(f"{direction}_element l {cur_i, cur_j}"),
            self.model.NewBoolVar(f"{direction}_element m {cur_i, cur_j}")
        )

    def check_side_element(self, element, less_var, more_var, cur_i, cur_j):
        if element is not None:
            self.check_is_same_more(more_var, element, cur_i, cur_j)
            self.check_is_same_less(less_var, element, cur_i, cur_j)

    def add_pair_conditions(self, element1_less, element1_more, element2_less, element2_more, condition):
        if element1_less is not None and element2_less is not None:
            self.model.AddBoolOr([element1_less, element1_more]).OnlyEnforceIf(condition)
            self.model.AddBoolOr([element1_less, element2_less]).OnlyEnforceIf(condition)
            self.model.AddBoolOr([element1_more, element2_more]).OnlyEnforceIf(condition)
            self.model.AddBoolOr([element2_less, element2_more]).OnlyEnforceIf(condition)
            self.model.Add(
                element1_less + element1_more + element2_more + element2_less == 2
            ).OnlyEnforceIf(condition)

    def check_numbers(self, current_element, left_element, right_element, under_element, over_element):
        cur_i = current_element.i
        cur_j = current_element.j

        left_element_less, left_element_more = self.create_element_bool_vars("left", cur_i, cur_j)
        right_element_less, right_element_more = self.create_element_bool_vars("right", cur_i, cur_j)
        under_element_less, under_element_more = self.create_element_bool_vars("under", cur_i, cur_j)
        over_element_less, over_element_more = self.create_element_bool_vars("over", cur_i, cur_j)

        self.check_side_element(left_element, left_element_less, left_element_more, cur_i, cur_j)
        self.check_side_element(right_element, right_element_less, right_element_more, cur_i, cur_j)
        self.check_side_element(under_element, under_element_less, under_element_more, cur_i, cur_j)
        self.check_side_element(over_element, over_element_less, over_element_more, cur_i, cur_j)

        self.add_pair_conditions(left_element_less, left_element_more, right_element_less, right_element_more,
                                 current_element.condition[1])
        self.add_pair_conditions(under_element_less, under_element_more, over_element_less, over_element_more,
                                 current_element.condition[2])
        self.add_pair_conditions(under_element_less, under_element_more, right_element_less, right_element_more,
                                 current_element.condition[4])
        self.add_pair_conditions(under_element_less, under_element_more, left_element_less, left_element_more,
                                 current_element.condition[3])
        self.add_pair_conditions(over_element_less, over_element_more, right_element_less, right_element_more,
                                 current_element.condition[5])
        self.add_pair_conditions(over_element_less, over_element_more, left_element_less, left_element_more,
                                 current_element.condition[6])

    def check_for_origin_point(self, current_element, left_element, right_element, under_element, over_element):
        cur_i, cur_j = current_element.i, current_element.j
        left_request = self.model.NewBoolVar(f"{cur_i},{cur_j} left request")
        right_request = self.model.NewBoolVar(f"{cur_i},{cur_j} right request")
        under_request = self.model.NewBoolVar(f"{cur_i},{cur_j} under request")
        over_request = self.model.NewBoolVar(f"{cur_i},{cur_j} over request")

        self.origin_values[(cur_i, cur_j)] = {"left": left_request, "right": right_request, "under": under_request,
                                              "over": over_request}

        self.check_equivalence(left_element, left_request, self.left)
        self.check_equivalence(right_element, right_request, self.right)
        self.check_equivalence(under_element, under_request, self.under)
        self.check_equivalence(over_element, over_request, self.over)

        self.model.Add((left_request + right_request + under_request + over_request) == 1).OnlyEnforceIf(
            current_element.condition[7])

    def check_for_point(self, current_element, left_element, right_element, under_element, over_element,
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

        self.check_for_origin_point(current_element, left_element, right_element, under_element, over_element)

    def check_number_in_origin_point(self):
        for key in self.origin_points:
            self.model.Add(self.numbers[self.origin_points[key][0]] == 1)

            self.model.Add(
                self.numbers[self.origin_points[key][1]] ==
                sum(self.point_condition[i][j].value[key]
                    for (i, j) in self.variables.keys()))

    def make_restrictions(self):
        for i in range(self.line_count):
            for j in range(self.column_count):
                current_element = self.point_condition[i][j]
                left_element = None if j == 0 else self.point_condition[i][j - 1]
                right_element = None if j == self.column_count - 1 else self.point_condition[i][j + 1]
                under_element = None if i == self.line_count - 1 else self.point_condition[i + 1][j]
                over_element = None if i == 0 else self.point_condition[i - 1][j]

                for idx in range(1, self.condition_count):
                    self.check_for_point(current_element, left_element, right_element, under_element, over_element,
                                         idx)
                self.check_for_origin_point(current_element, left_element, right_element, under_element, over_element)
                self.check_numbers(current_element, left_element, right_element, under_element, over_element)

        self.check_number_in_origin_point()

    def generate_condition_for_point(self, i, j):
        if self.matrix[i][j] != 0:
            self.condition[(i, j)] = self.model.NewIntVar(7, 7, f"_({i},{j})")
            return

        self.condition[(i, j)] = self.model.NewIntVar(1, 6, f"_({i},{j})")

    def model_prepare(self):
        for i in range(self.line_count):
            for j in range(self.column_count):

                self.generate_condition_for_point(i, j)
                self.numbers[(i, j)] = self.model.NewIntVar(1, self.line_count * self.column_count, f"n({i},{j})")

                if self.matrix[i][j] != 0:
                    self.origin_points[self.matrix[i][j]].append((i, j))
                    self.variables[(i, j)] = self.model.NewIntVar(self.matrix[i][j], self.matrix[i][j], f"({i},{j})")
                else:
                    self.variables[(i, j)] = self.model.NewIntVar(1, self.max_value, f"({i},{j})")

        self.point_condition = [[PointCondition(i, j, self) for j in range(self.line_count)] for i in
                                range(self.column_count)]

        self.make_restrictions()

    def try_solve(self):
        self.model_prepare()

        solver = cp_model.CpSolver()

        status = solver.solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            result = []
            for i in range(self.line_count):
                row = []
                for j in range(self.column_count):
                    # row.append(solver.value(self.variables[(i, j)]))
                    row.append([solver.value(self.variables[(i, j)]), solver.value(self.condition[(i, j)]),
                                solver.value(self.numbers[(i, j)])])
                    print(i,
                          j,
                          [solver.value(self.point_condition[i][j].condition[el]) for el in
                           range(1, self.condition_count + 1)],
                          [solver.value(self.point_condition[i][j].value[el]) for el in range(1, self.max_value + 1)],
                          0 if self.matrix[i][j] == 0 else [
                              (key, solver.value(self.origin_values[(i, j)][key])) for key in
                              self.origin_values[(i, j)]],
                          )
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
