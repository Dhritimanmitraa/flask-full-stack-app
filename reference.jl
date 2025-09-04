
from sympy import symbols, Eq, solve
x, y = symbols('x y')

weight_A = 3*x
weight_B = 5*x

weight_A_after = weight_A * 1.20
weight_B_after = weight_B * (1 + y/100)

total_weight_after = weight_A_after + weight_B_after

eq1 = Eq(total_weight_after, 80)

eq2 = Eq(total_weight_after, 1.25 * (weight_A + weight_B))

# Using the second equation to express total_weight_before
# total_weight_before = weight_A + weight_B
total_weight_before = weight_A + weight_B

# Substitute total_weight_after from eq1 in eq2 and solve for y
solutions = solve(eq1.subs(total_weight_after, total_weight_after) & eq2, (x, y))

# Instead of complex solve, use substitution directly
# total original weight = 3x + 5x = 8x
# total increased weight = 80
# total increased weight = 1.25 * (original weight)
# => 80 = 1.25 * 8x => x = 80 / (1.25 * 8)
x_val = 80 / (1.25 * 8)

# now solve for y using total increased weight:
# 3x * 1.20 + 5x * (1 + y/100) = 80
# substitute x_val
lhs = 3 * x_val * 1.20 + 5 * x_val * (1 + y/100)

eq_y = Eq(lhs, 80)

from sympy import solve
y_val = solve(eq_y, y)[0]
y_val.evalf()