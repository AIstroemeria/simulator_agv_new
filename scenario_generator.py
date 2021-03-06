# -*- coding: utf-8 -*-
import copy
import aa_spr
import os
from demand_generator import *
from path_generator import *
import numpy as np
#from lp_solver import *
#import cplex
#from cplex.exceptions import CplexError
import gurobipy as gp
from gurobipy import GRB
import json

def scenario_generator(de,wh,rhy,pla):
    total_demand_rate = de
    workingtime = wh*3600
    rythmn = rhy
    capatity = pla

    data={}
    with open("./data.json",'r',encoding='utf-8') as json_file: 
        data=json.load(json_file)
    pre_matrix = data['pre']
    dis_matrix = data['dis']

    longest_path = 0
    for i in range(m+n):
        for j in range(m+n,2*(m+n)+noj):
            if pre_matrix[i][j] != -1 and dis_matrix[i][j] > longest_path:
                longest_path = dis_matrix[i][j]
    for i in range(2*(m+n),2*(m+n)+noj):
        for j in range(m+n,2*(m+n)+noj):
            if pre_matrix[i][j] != -1 and dis_matrix[i][j] > longest_path:
                longest_path = dis_matrix[i][j]
    
    Ts = np.zeros(m+n+noj)
    for i in range(m+n+noj):
        if i in range(m,m+n):
            Ts[i] = 5
        elif i in range(m+n+m*(n-1),m+n+noj):
            Ts[i] = 5
        else:
            pass


    max_inter = int(np.ceil(longest_path/rythmn))
    demand = np.zeros((m+n+noj,m+n+noj))
    order = [[] for i in range(int(workingtime/rythmn))]  # return request
    remainning_order = 0

    cost = rythmn*np.ones((m+n+noj,m+n+noj))
    lw = np.zeros((m+n+noj,m+n+noj)) # addition cost for keep waiting
    N_ea = []
    for i in range(max_inter):
        N_ea.append([])
        for start in range(len(edges)):
            N_ea[i].append([])
            for item in edges[start]:
                N_ea[i][start].append([item[0],capatity])

    total_car_num = 0
    total_waiting_time = 0
    
    res = []

    for iter in range(int(workingtime/rythmn)):

        if iter < (workingtime/(2*rythmn)) :
            new_demand = demand_generator(m, n, noj, rythmn, total_demand_rate)
            remainning_order = remainning_order + sum(sum(new_demand)) 
            total_car_num = total_car_num + sum(sum(new_demand))
            demand = demand + new_demand
        else:
            pass
        
        for ords in order[iter]:
            demand[ords[0]][ords[1]] = demand[ords[0]][ords[1]] + ords[2]

        if sum(sum(demand)) == 0:
            continue
        obj = []
        name_col = []
        ub = []
        lb = []
        rows = []
        rho = []
        use_path = {}

        for i in range(m+n+noj):
            for j in range(m+n+noj):
                if demand[i][j] != 0:
                    obj.append(-cost[i][j])
                    name_col.append('f_%d_%d' % (i,j))
                    ub.append(demand[i][j])
                    lb.append(0)

                    if i < m+n:
                        i_temp = i
                    else:
                        i_temp = i + m + n
                    j_temp = j + m + n
                    pre_node = j_temp
                    while pre_node != i_temp:
                        temp = int(pre_matrix[i_temp][pre_node])
                        e = int(np.floor((dis_matrix[i_temp][temp]+Ts[i])/rythmn))
                        key = '%d_%d_%d'%(e,temp,pre_node)
                        if key in use_path.keys():
                            use_path[key] = use_path[key] + [(i,j)]
                        else:
                            use_path[key] = [(i,j)]
                        pre_node = temp
                    
        for start_node in range(len(edges)):
            for item in edges[start_node]:
                if item[0] == start_node:
                    continue
                for interval in range(max_inter):
                    end_node = item[0]
                    key = '%d_%d_%d' % (interval,start_node,end_node)
                    if key in use_path.keys():
                        row1 = []
                        row2 = []
                        for od in use_path[key]:
                            row1.append('f_%d_%d'%(od[0],od[1]))
                            row2.append(1)
                        rows.append([row1,row2])
                        for edge in N_ea[interval][start_node]:
                            if edge[0] == end_node:
                                rho.append(edge[1])
                                break
        
        while True:
            # for some reason, we need to change the lp_solver
            '''
            solution,value = lp_solver(obj,ub,lb,rho,rows,name_col)
            '''
            # matlab lpsolver has some bugs that not easy to solve. try gurobi instead 
            '''
            eng = matlab.engine.start_matlab()
            c = matlab.double(obj)
            A = eng.zeros(len(rho),len(name_col))
            for k in range(len(rows)):
                constrain = rows[k]
                for i in range(len(constrain[0])):
                    x_index = name_col.index(constrain[0][i])
                    A[k][x_index] = int(constrain[1][i])
            A = matlab.double(A)
            b = eng.zeros(len(rho),1)
            for i in range(len(rho)):
                b[i][0] = rho[i]
            Lb = matlab.double(lb)
            Ub = matlab.double(ub)
            solution = eng.linprog(c, A, b, matlab.double([]),matlab.double([]),Lb, Ub)
            solution = np.array(solution).T[0]
            '''
            model = gp.Model("problem")
            allvar = {}
            for i in range(len(name_col)):
                allvar[name_col[i]] = model.addVar(lb = lb[i], ub = ub[i], name = name_col[i])
            for i in range(len(rho)):
                model.addConstr(gp.quicksum(allvar[rows[i][0][j]]*rows[i][1][j] for j in range(len(rows[i][0]))) <= rho[i],'c_%d' % i)
            model.setObjective(gp.quicksum(allvar[name_col[i]]*obj[i] for i in range(len(obj))), GRB.MINIMIZE)
            model.optimize()

            solution = []
            for v in model.getVars():
                solution.append(v.x)

            most_frac = 0
            most_frac_index = -1
            for i in range(len(solution)):
                frac = solution[i] - np.floor(solution[i])
                frac = min([frac,1-frac])
                if frac > 0.001:
                    if frac > most_frac:
                        most_frac = frac
                        most_frac_index = i
            if most_frac_index == -1:
                break
            else:
                if np.round(solution[most_frac_index]) > solution[most_frac_index]:
                    lb[most_frac_index] = np.round(solution[most_frac_index])
                else:
                    ub[most_frac_index] = np.round(solution[most_frac_index])

        solution = np.round(solution)
        waiting_num = sum(ub) - sum(solution)
        total_waiting_time = total_waiting_time + waiting_num*rythmn

        new_N_ea = []
        for i in range(max_inter):
            new_N_ea.append(copy.copy(N_ea[i]))

        # renwe demand, remainning room, and save data
        temp_res = []

        paraindex = 0
        for i in range(m+n+noj):
            if paraindex == len(solution):
                break
            for j in range(m+n+noj):
                if demand[i][j] != 0:
                    # renwe demand
                    ############# Set the target of agv
                    if i <= m+n:
                        status = 0
                    else:
                        status = 1
                    #############
                    temp_res.append([i,j,demand[i][j],solution[paraindex],status])
                    demand[i][j] = demand[i][j] -solution[paraindex]
                    if demand[i][j] == 0:
                        lw[i][j] = 0
                    else:
                        lw[i][j] = lw[i][j] + 1
                    
                    # renew remainning room
                    if solution[paraindex] != 0:

                        if i < m+n:
                            i_temp = i
                        else:
                            i_temp = i + m + n
                        j_temp = j + m + n
                        pre_node = j_temp
                        while pre_node != i_temp:
                            temp = int(pre_matrix[i_temp][pre_node])
                            e = int(np.floor((dis_matrix[i_temp][temp]+Ts[i])/rythmn))
                            for edgeindex in range(len(new_N_ea[e][temp])):
                                if new_N_ea[e][temp][edgeindex][0] == pre_node:
                                    new_N_ea[e][temp][edgeindex][1] = new_N_ea[e][temp][edgeindex][1] - solution[paraindex]
                            pre_node = temp
                            
                        # add new order for return
                        if i < m+n and j >= m+n:
                            buffer_time = 10   # 装卸货时间
                            arrive_time = int(np.ceil(iter + 1 + (dis_matrix[i_temp][j_temp]+buffer_time)/rythmn))
                            if np.mod(i,2)==0:
                                order[arrive_time].append([j,i+1,solution[paraindex]])
                            else:
                                order[arrive_time].append([j,i-1,solution[paraindex]])
                        else:
                            remainning_order = remainning_order - solution[paraindex]

                    paraindex = paraindex + 1
                    if paraindex == len(solution):
                        break

        new_N_ea.append([])
        for start in range(len(edges)):
            new_N_ea[-1].append([])
            for num in edges[start]:
                new_N_ea[-1][start].append([num[0],capatity])
        N_ea = new_N_ea[1:]

        res.append(temp_res)

        #renew cost
        cost = rythmn*(1+lw)

        process = '|'
        for i in range(30):
            if i < 30*iter/(workingtime/rythmn):
                process = process + "#"
            else:
                process = process + ' '
        process = process + '|  %d'%np.round(100*iter/(3600/rythmn)) + '%'
        process1 = 'total car num: %d  ;  total waiting time %d ' %(total_car_num, total_waiting_time)
        print('')
        print('')
        print(iter)
        print(process)
        print(process1)

        if iter >= ((workingtime/(2*rythmn))-1) and sum(sum(demand))==0 and remainning_order == 0:
            print("demand satisfied at interval %d" %iter)
            temp = 0
            filename = "./res"+str(temp)+".json"
            while True:
                if os.path.exists(filename):
                    temp = temp + 1
                    filename = "./res"+str(temp)+".json"
                else:
                    break    
            with open(filename,'w',encoding='utf-8') as json_file:
                json.dump(res,json_file,ensure_ascii=False)
            break
    
    return 0