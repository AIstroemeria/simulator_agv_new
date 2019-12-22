import cplex
from cplex.exceptions import CplexError
import sys


if __name__ == "__main__":
    my_obj = [1,2,3]
    my_ub = [40, cplex.infinity, cplex.infinity]
    my_sense = "LL"
    my_rhs = [20,30]
    my_colnames = ["x1", "x2", "x3"]
    my_rownames = ["c1", "c2"]

    my_prob = cplex.Cplex()
    my_prob.objective.set_sense(my_prob.objective.sense.maximize)
    my_prob.variables.add(obj = my_obj, ub = my_ub)
    rows = [[[i for i in range(3)],[-1,1,1]],[[i for i in range(3)],[1,-3,1]]]
    my_prob.linear_constraints.add(lin_expr=rows, senses=my_sense, rhs = my_rhs)

    my_prob.solve()
    numrows = my_prob.linear_constraints.get_num()
    numcols = my_prob.variables.get_num()

    print
    # solution.get_status() returns an integer code
    print("Solution status = " , my_prob.solution.get_status(), ":")
    # the following line prints the corresponding string
    print(my_prob.solution.status[my_prob.solution.get_status()])
    print("Solution value  = ", my_prob.solution.get_objective_value())
    slack = my_prob.solution.get_linear_slacks()
    pi    = my_prob.solution.get_dual_values()
    x     = my_prob.solution.get_values()
    dj    = my_prob.solution.get_reduced_costs()
    for i in range(numrows):
        print("Row %d:  Slack = %10f  Pi = %10f" % (i, slack[i], pi[i]))
    for j in range(numcols):
        print("Column %d:  Value = %10f Reduced cost = %10f" % (j, x[j], dj[j]))
