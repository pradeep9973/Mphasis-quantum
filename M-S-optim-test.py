import singularity.optimization as sop

# Define variables
x1 = sop.Variable("x1")
x2 = sop.Variable("x2")
x3 = sop.Variable("x3")

# Define the objective function
total_value = 2 * x1 + 3 * x2 + 6 * x3 + 2 * x1 * x2 + 4 * x1 * x3 + 3 * x2 * x3
objective = sop.Objective(total_value, "maximize")

# Define the constraint
penalty_strength = 10
capacity = 10
total_weight = 4 * x1 + 5 * x2 + 1 * x3
capacity_constraint = sop.Constraint(
    lhs=total_weight,
    operator="<=",
    rhs=capacity,
    penalty_strength=penalty_strength,
    name="capacity_constraint",
)

# Create the model
knapsack = sop.Model(objective, [capacity_constraint])

# Optimize the model
result = knapsack.optimize(solver="simulated_annealing", num_solutions=5)
result = knapsack.optimize(solver="simulated_annealing", num_solutions=5, timeout=60)
