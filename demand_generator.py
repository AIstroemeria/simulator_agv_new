import numpy as np
import random

def demand_generator(m, n, noj, rythmn, total_demand_rate):
    demand_para = total_demand_rate/(((m+n)*noj)*3600)
    demands = np.zeros((m+n+noj,m+n+noj)) 
    '''
    for i in range(m+n+noj):
        for j in range(m+n+noj):
            if i >= m+n and i==j:
                pass
            else:
                time = rythmn
                counts = -1
                while time > 0:
                    counts = counts + 1
                    time = time + np.log(random.random())/demand_para
                demands[i][j] = counts
    '''
    for i in range(m+n):
        for j_t in range(noj):
            j = j_t + m + n
            time = rythmn
            counts = -1
            while time > 0:
                counts = counts + 1
                time = time + np.log(random.random())/demand_para
            demands[i][j] = counts

    
    return demands

if __name__ == "__main__":
    total = np.zeros([1,72])
    rythmn = 2
    for i in range(int(3600/rythmn)):
        res = demand_generator(6,6,60,rythmn,4000)
        total = total + np.sum(res,axis=1)
    print(total)
    print(sum(sum(total)))