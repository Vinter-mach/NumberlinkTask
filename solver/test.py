from ortools.sat.python import cp_model

# Create the model
model = cp_model.CpModel()

# Create integer variables
x = model.NewIntVar(0, 10, 'x')
y = model.NewIntVar(0, 10, 'y')

# Add a constraint that x should not be equal to 1


# Create a Boolean variable
a = model.NewBoolVar("a")
b = model.NewBoolVar("b")
c = model.NewBoolVar("c")
#c = model.NewIntVarFromDomain(cp_model.Domain.FromValues([2, 3, 4]), "c")
# Add a conditional constraint: x == 1 is enforced only if 'a' is true
model.AddImplication(a, c)
model.AddBoolXOr

# Add the OR constraint: a must be true or another condition (in this case, we don't want "False" here)
# Since `False` is not a valid literal, you should think about what the second condition is.
# If you don't need a second condition, just add `a` as the Boolean OR.
#model.AddBoolOr([a])

# Create a solver and solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Output the result
if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
    print(f"c: {solver.Value(c)}")
    print(f"a: {solver.Value(a)}")
else:
    print("No feasible solution found.")
