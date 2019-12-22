# -*- coding: utf-8 -*-

import cplex
from cplex.exceptions import CplexError
import sys

def lp_solver(obj, ub, lb, rhs, rows,name_col):
    my_obj = obj
    my_ub = ub
    for i in range(len(my_ub)):
        if my_ub[i] == -1:
           my_ub[i] = cplex.infinity 
    my_lb = lb
    
    my_rhs = rhs
    my_rows = rows
    my_sense = ''
    for i in range(len(my_rhs)):
        my_sense = my_sense + "L"

    my_prob = cplex.Cplex()
    my_prob.objective.set_sense(my_prob.objective.sense.minimize)
    my_prob.variables.add(obj = my_obj, ub = my_ub, lb = my_lb, names = name_col)
    my_prob.linear_constraints.add(lin_expr=my_rows, senses=my_sense, rhs = my_rhs)
    try:
        my_prob.solve()
        solution = my_prob.solution.get_values()
        value = my_prob.solution.get_objective_value() 
        return solution, value
    except CplexError as exc:
        print(min(my_rhs))
        print(exc)
        return

if __name__ == '__main__':
    obj = [1,2,3]
    ub = [40, -1, -1]
    lb = [0 for i in range(3)]
    rhs = [20,30]
    names_col = ['%d'%i for i in range(len(obj))]
    rows = [[[i for i in range(3)],[-1,1,1]],[[i for i in range(3)],[1,-3,1]]]
    solution,value = lp_solver(obj,ub,lb,rhs,rows,names_col)
    pass