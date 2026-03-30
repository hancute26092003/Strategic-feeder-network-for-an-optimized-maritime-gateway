# -*- coding: utf-8 -*-
"""
Created on Mon Jun  9 13:38:34 2025

@author: quynh
"""
from collections import Counter
import random
import time
import math
import numpy as np
import pandas as pd
import subprocess
import itertools
from configuration_data1 import *
import time

start_time = time.time()

OPL_RUN=r"C:\Desktop\setting\opl\bin\x64_win64\oplrun.exe"
MODFILE=r"C:\Users\quynh\opl\Thesis\Thesis.mod"
DATFILE=r"C:\Users\quynh\opl\Thesis\data1_latvia_10.dat"
result_file = r"C:\Users\quynh\opl\Thesis\Result.txt"
subprocess.run([OPL_RUN,MODFILE,DATFILE])

MODFILE_phase2=r"C:\Users\quynh\opl\Thesis\phase2.mod"
DATFILE_phase2=r"C:\Users\quynh\opl\Thesis\phase2.dat"
result_file_phase2 = r"C:\Users\quynh\opl\Thesis\Result_phase2.txt"
subprocess.run([OPL_RUN,MODFILE_phase2,DATFILE_phase2])



#Gọi Cplex cho initial solution
def Initial_Solution(result_file, ship_type, p,o,h,d, dist_origin,dist_hub,dist_dest,FC, dist_cost, transshipment_cost, demand):
    #phase 2
    with open(result_file_phase2, 'r') as f:
        lines = f.readlines()
    phase2_obj = float(lines[0].strip().replace("Objective:", "").strip())
    #phase 1
    with open(result_file, 'r') as f:
        lines = f.readlines() # Đọc file và lưu vào lines
       
    if p < 40 and len(lines) >= 4:
        initial_obj = float(lines[0].strip().replace("Objective:", "").strip())
        initial_line2 = lines[2].strip() # Lấy dòng thứ ba = solution of ship type 
        initial_line1 = lines[1].strip()  # Lấy dòng thứ hai = solution of hub port
        initial_solution_hub = list(map(int, initial_line1.split()))
        initial_solution_ship = list(map(int,initial_line2.split()))
    else:
        initial_line1 = [random.choice(h) for _ in range(p)]
        initial_line2 = [random.choice(ship_type) for _ in range(p)]
        distance = distance_calculation(demand,initial_line1,o,h,d, dist_origin,dist_hub,dist_dest)
        initial_obj =  objective(initial_line2,o, FC, distance, dist_cost, transshipment_cost, demand, phase2_obj)
        initial_solution_hub = initial_line1
        initial_solution_ship = initial_line2
        
    
    return initial_solution_hub, initial_solution_ship, initial_obj, phase2_obj


#Lặp lần 1 là initial solution, những lần còn lại là random
def get_solution_hub(gen, chromhub0, m, p, hub_port):
    if gen == 0:
        pop_hub = [chromhub0[:] for _ in range(m)]
        return pop_hub
    else:
        return initialize_hub(m, p, hub_port)
    
def get_solution_ship(gen,chromship0, m, p, ship_type):
    if gen == 0:
        pop_ship = [chromship0[:] for _ in range(m)]
        return pop_ship
    else:
        return initialize_ship(m, p, ship_type)


#___________________________________________________________________________________________________________________________


# random 
def initialize_hub(m, p, hub_port): 
    pop_hub = []
    for _ in range(m):
        chromhub = [random.choice(hub_port) for _ in range(p)]
        pop_hub.append(chromhub)
    return pop_hub

def initialize_ship(m, p, ship): 
    pop_ship = []
    for _ in range(m):
        chromship = [random.choice(ship) for _ in range(p)]
        pop_ship.append(chromship)
    return pop_ship


# distance
def distance_calculation(demand,solution_hub, o,h,d, dist_origin,dist_hub,dist_dest):
    dist1 = 0
    #Tính origin - hub1
    for i in range(len(o)):
        ori = o[i]
        hub1 = solution_hub[i]
        key1 = (ori, hub1)
        #Tính origin - hub1
        if key1 in dist_origin:
            dist1 += dist_origin[key1] 
        else:
            dist1 += 0

        #Tính mainroute  
    dist_main = 0 
    for i in range(len(h)-1):
        hub1 = h[i]
        hub2 = h[i+1]
        key2 = (hub1, hub2)
        if key2 in dist_hub:
            dist_main += dist_hub[key2]
        else:
            dist_main +=0
        #Tính hub 2 - destination port 
    
    L = 0 
    for i in range(len(o)):
        L += demand[i]
    dist2 = 0
    dest = d
    min_dist = float('inf')
    best_hub2 = None
    for i in range(len(h)):
        hub2 = h[i]
        key3 = (hub2,dest)
        if key3 in dist_dest:
            if dist_dest[key3] < min_dist:
                min_dist = dist_dest[key3]
                best_hub2 = hub2
                dist2 = dist_dest[key3]
                #dist2 = 1103.3
                
    total_distance = dist1 + dist_main + dist2*len(o)
    return total_distance

    
# objective function
def objective(solution_ship,o, FC, total_distance, dist_cost, transshipment_cost, demand, phase2_obj):   
    L = 0 
    for i in range(len(o)):
        L += demand[i]
    #Tính cost cho loại tàu từ hub1 - dest & origin - hub1 
    #C1_1 = 21000*len(o)
    C1_1 = 0
    for i in range(len(solution_ship)):
        s = solution_ship[i]
        C1_1 += FC[s-1] 
    # Tính cost cho loại tàu main route 
    CapM = 25000
    FCM = 47749
    UM = 1
    C1_2 = FCM * UM  
    # Transportation cost (2 way)
    C2 = total_distance * dist_cost 
    # Lấy transportation cost từ phase 2
    C3 = phase2_obj
    # Tính cost cho transshipment
    C4 = transshipment_cost * L
    TC = C1_1 + C1_2 + C2 + C3 + C4
   

    return TC

# evaluation
def distance_origin_hub1(o,sol_hub, dist_origin):
    total_dist1 = 0
    for j in range(len(o)):
        ori = o[j]
        hub1 = sol_hub[j]
        key =(ori,hub1)
        if key in dist_origin:
            total_dist1 += dist_origin.get(key,0)
        else:
            total_dist1 +=  0
    return total_dist1

def cost_ship(sol_ship, FC, ship_type):
    cost_ship = 0
    for i in range(len(sol_ship)):
        s = sol_ship[i]
        if s in ship_type:
            cost_ship += FC[s-1]
        else:
            cost_ship += 0
    return cost_ship 


# check feasibility
def check_feasibility_hub(solution_hub, h, o):
    corrected_chrom_hub = solution_hub.copy() 
   
    hub_counts = Counter()
    corrected_chrom_hub = []

    for hub in solution_hub:
        if hub_counts[hub] < 30 :
            corrected_chrom_hub.append(hub)
            hub_counts[hub] += 1
        else:
            # Chọn hub khác chưa dùng quá 2 lần
            candidates = [h for h in h if hub_counts[h] < 30]
            replacement = random.choice(candidates)
            corrected_chrom_hub.append(replacement)
            hub_counts[replacement] += 1

    return corrected_chrom_hub


def check_feasibility_ship(solution_ship,ship_type, ship_cap, demand):
    corrected_chrom_ship = solution_ship.copy()
    for i in range(len(corrected_chrom_ship)):
        s = corrected_chrom_ship[i]
        if s in ship_type:
            while ship_cap[s] < demand[i] and s < max(ship_type):
                s += 1
                #print("Tăng loại tàu lên:", s, "với capacity:", ship_cap[s], 'để đáp ứng', demand[i])
            corrected_chrom_ship[i] = s
            #print("Cập nhật loại tàu tại index", i, "thành:", corrected_chrom_ship[i])
    return corrected_chrom_ship

#Removal 
def removal_operators():
    def random_removal(o,dist_origin, ship_type,FC, corrected_chrom_hub,corrected_chrom_ship, num_remove_hub, num_remove_ship):
        # HUB 
        new_sol_hub = corrected_chrom_hub.copy()
        all_hub = list(set(new_sol_hub))  # lọc các hub duy nhất
        hub_removed = random.sample(all_hub, num_remove_hub)
        # Thay vì lọc bỏ, gán None vào vị trí các hub bị remove
        last_hub_removal = []
        for i in range(len(new_sol_hub)):
            if new_sol_hub[i] in hub_removed:
                new_sol_hub[i] = None
            
            last_hub_removal.append(new_sol_hub[i])
                
        
        
        #none_positions = [i for i, hub in enumerate(new_sol_hub) if hub is None]
        # SHIP
        new_sol_ship = corrected_chrom_ship.copy()
        all_ship = new_sol_ship  # lọc các hub duy nhất
        ship_removed = random.sample(all_ship, num_remove_ship)
        # Thay vì lọc bỏ, gán None vào vị trí các hub bị remove
        last_ship_removal = []
        for j in range(len(new_sol_ship)):
            if new_sol_ship[j] in ship_removed:
                new_sol_ship[j] = None
            
            last_ship_removal.append(new_sol_ship[j])
        
         
        #none_positions_ship = [j for j, ship in enumerate(new_sol_ship) if ship is None]
        return new_sol_hub, hub_removed, new_sol_ship, ship_removed, last_hub_removal, last_ship_removal
    
    def worst_removal(o,dist_origin, ship_type,FC, corrected_chrom_hub,corrected_chrom_ship, num_remove_hub, num_remove_ship):
        # HUB 
        new_sol_hub = corrected_chrom_hub.copy()
        all_hub = new_sol_hub  # lọc các hub duy nhất
        ranked_hub = []
        for i in range(len(o)):
            ori = o[i]
            hub1 = all_hub[i]
            key = (ori, hub1)
            if key in dist_origin:
                distance = dist_origin[key]
                ranked_hub.append((i, ori, hub1, distance))
        ranked_hub.sort(key=lambda x:x[3], reverse=True)
        hub_removed = [item[2] for item in ranked_hub[:num_remove_hub]]
        # Thay vì lọc bỏ, gán None vào vị trí các hub bị remove
        last_hub_removal = []
        for i in range(len(new_sol_hub)):
            if new_sol_hub[i] in hub_removed:
                new_sol_hub[i] = None 
            last_hub_removal.append(new_sol_hub[i])
        
        # SHIP
        new_sol_ship = corrected_chrom_ship.copy()
        all_ship = new_sol_ship 
        ranked_ship = []
        for i in range(len(all_ship)):
            s = all_ship[i]
            if s in ship_type:
                cost = FC[s-1]
                ranked_ship.append((i,s, cost))
        ranked_ship.sort(key=lambda x:x[2], reverse=True)    
        ship_removed = [item[1] for item in ranked_ship[:num_remove_ship]]
        # Thay vì lọc bỏ, gán None vào vị trí các hub bị remove
        last_ship_removal = []
        for j in range(len(new_sol_ship)):
            if new_sol_ship[j] in ship_removed:
                new_sol_ship[j] = None
            
            last_ship_removal.append(new_sol_ship[j])
                
        #none_positions_ship = [j for j, ship in enumerate(new_sol_ship) if ship is None]
        return new_sol_hub, hub_removed, new_sol_ship, ship_removed, last_hub_removal, last_ship_removal
    
    return [random_removal, worst_removal]
    
    
    
    
#Repair 
def repair_operators():
    def basic_greedy_insertion(FC,hub_removed, new_sol_hub, o, dist_origin, new_sol_ship, ship_removed,ship_type): 
            # HUB
            minimum_dist1 = float('inf')
            while None in new_sol_hub:
                best_dist1 = float('inf')
                best_position = None
                best_hub = None
                for i in hub_removed:
                    for h, val in enumerate(new_sol_hub):
                        if val is None:
                            temp_hub = new_sol_hub.copy()
                            temp_hub[h] = i
                            new_dist1 = distance_origin_hub1(o,temp_hub, dist_origin)
                            if new_dist1 < best_dist1:
                                best_dist1 = new_dist1
                                best_position = h
                                best_hub  = i
                            #print(f"Temp sau khi thay hub '{i}' vào vị trí {h} thì ta có gen mới: {temp_hub} -> new_dist1 = {new_dist1}")    
                new_sol_hub[best_position] = best_hub
                minimum_dist1 = best_dist1
            total_dist1 = distance_origin_hub1(o,new_sol_hub, dist_origin)
            #print(f'Hub solution sau repair{new_sol_hub} với total distance {total_dist1}')         
            
            # SHIP
            minimum_cost_ship = float('inf')
            while None in new_sol_ship:
                best_cost_ship = float('inf')
                best_position_ship = None
                best_ship = None
                for i in ship_removed:
                    for s, val in enumerate(new_sol_ship):
                        if val is None:
                            temp_ship = new_sol_ship.copy()
                            temp_ship[s] = i

                            new_cost_ship = cost_ship(temp_ship, FC, ship_type)

                            if new_cost_ship < best_cost_ship:
                                best_cost_ship = new_cost_ship
                                best_position_ship = s
                                best_ship = i
                            #print(f"Temp sau khi thay ship '{i}' vào vị trí {s} thì ta có gen mới: {temp_ship} -> cost = {new_cost_ship}")
                new_sol_ship[best_position_ship] = best_ship
                minimum_cost_ship = best_cost_ship
            total_cost_ship = cost_ship(new_sol_ship, FC, ship_type)
            #print(f'Ship solution sau repair{new_sol_ship} với fixed cost {total_cost_ship}')
            return new_sol_hub, new_sol_ship
    
    def regret_insertion(FC,hub_removed, new_sol_hub, o, dist_origin, new_sol_ship, ship_removed,ship_type): 
                # HUB
                while None in new_sol_hub:
                    regret_list = []
                    #print(f"\n Current new_sol_hub: {new_sol_hub}")
                    #print(f"Hub candidates to insert: {hub_removed}")
                    for i in hub_removed:
                        insertion_costs = []
                        for h, val in enumerate(new_sol_hub):
                            if val is None:
                                temp_hub = new_sol_hub.copy()
                                temp_hub[h] = i
                                new_dist = distance_origin_hub1(o, temp_hub, dist_origin)
                                insertion_costs.append((new_dist, h))  # (cost, position)
                        #print(f" Hub {i} insertion options (cost, pos): {insertion_costs}")
                        # Cần ít nhất 2 vị trí để tính regret-2
                        if len(insertion_costs) >= 2:
                            insertion_costs.sort()
                            regret = insertion_costs[1][0] - insertion_costs[0][0]
                            regret_list.append((regret, insertion_costs[0][0], i, insertion_costs[0][1]))  # (regret, best_cost, hub, position)
                            #print(f"  Regret-2 cho hub {i}: regret = {regret}, best_cost = {insertion_costs[0][0]}, position = {insertion_costs[0][1]}")
                        elif len(insertion_costs) == 1:
                            regret_list.append((0, insertion_costs[0][0], i, insertion_costs[0][1]))
                            #print(f"  Chỉ có 1 vị trí cho hub {i} → regret = 0")
                            
                    # Chọn (hub, pos) có regret cao nhất
                    regret_list.sort(reverse=True)
                    _, _, chosen_hub, chosen_pos = regret_list[0]
                    #print(f"Chọn hub {chosen_hub} cho vị trí {chosen_pos} (regret cao nhất)\n")
                    new_sol_hub[chosen_pos] = chosen_hub
                total_dist = distance_origin_hub1(o, new_sol_hub, dist_origin)

                # SHIP
                while None in new_sol_ship:
                    regret_list_ship = []
                    #print(f"\n Current new_sol_ship: {new_sol_ship}")
                    #print(f"Ship candidates to insert: {ship_removed}")
                    for i in ship_removed:
                        insertion_costs_ship = []
                        for s, val in enumerate(new_sol_ship):
                            if val is None:
                                temp_ship = new_sol_ship.copy()
                                temp_ship[s] = i
                                new_cost_ship = cost_ship(temp_ship, FC, ship_type)
                                insertion_costs_ship.append((new_cost_ship, s))  # (cost, position)
                        #print(f" Ship {i} insertion options (cost, pos): {insertion_costs_ship}")
                        # Cần ít nhất 2 vị trí để tính regret-2
                        if len(insertion_costs_ship) >= 2:
                            insertion_costs_ship.sort()
                            regret_ship = insertion_costs_ship[1][0] - insertion_costs_ship[0][0]
                            regret_list_ship.append((regret_ship, insertion_costs_ship[0][0], i, insertion_costs_ship[0][1]))  # (regret, best_cost, hub, position)
                            #print(f"  Regret-2 cho hub {i}: regret = {regret_ship}, best_cost = {insertion_costs_ship[0][0]}, position = {insertion_costs_ship[0][1]}")
                        elif len(insertion_costs_ship) == 1:
                            regret_list_ship.append((0, insertion_costs_ship[0][0], i, insertion_costs_ship[0][1]))
                            #print(f"  Chỉ có 1 vị trí cho ship {i} → regret = 0")
                            
                    # Chọn (ship, pos) có regret cao nhất
                    regret_list_ship.sort(reverse=True)
                    _, _, chosen_ship, chosen_pos_ship = regret_list_ship[0]
                    #print(f"Chọn ship {chosen_ship} cho vị trí {chosen_pos_ship} (regret cao nhất)\n")
                    new_sol_ship[chosen_pos_ship] = chosen_ship
                total_cost_ship = cost_ship(new_sol_ship, FC, ship_type)
                return new_sol_hub, new_sol_ship
    
    return [basic_greedy_insertion, regret_insertion]
    


# Local search 
def local_search(ship_type, ship_cap, demand,h, FC, new_sol_hub, new_sol_ship, dist_origin, o, initial_temp, cooling_rate, stopping_temp):
    #swap 2 position randomly---------
    if len(new_sol_hub) < 2: 
        return new_sol_hub
    current_solution_hub = check_feasibility_hub(new_sol_hub, h, o)
    current_distance = distance_origin_hub1(o, current_solution_hub, dist_origin)
    best_solution_hub = current_solution_hub.copy()
    best_distance = current_distance
    #print(f'Feasibility trước khi local search hub {best_solution_hub} với {best_distance}')

    if len(new_sol_ship) < 2:
        return new_sol_ship
    current_solution_ship = check_feasibility_ship(new_sol_ship, ship_type, ship_cap, demand)
    current_cost = cost_ship(current_solution_ship, FC, ship_type)
    best_solution_ship = current_solution_ship.copy()
    best_cost = current_cost
    #print(f'Feasibility trước khi local search ship {best_solution_ship} với {best_cost}')
    
    #Simulated annealing to escape local optimum
    T = initial_temp
    while T > stopping_temp:
        # HUB 
        for i in range(len(current_solution_hub)):
            for j in range(i+1, len(current_solution_hub)):
                neighbor = current_solution_hub.copy()
                #print(f'Trước khi swap thì mình có solution của hub là {neighbor}')
                neighbor[i], neighbor[j] = neighbor[j], neighbor[i] 
                #print(f'Swap {i} và {j} thì mình có solution mới của hub là {neighbor}')
                #check feasibility
                neighbor          = check_feasibility_hub(neighbor, h, o)
                neighbor_distance = distance_origin_hub1(o,neighbor, dist_origin)
                #print(f'Feasible hub rùi nè {neighbor} với dist {neighbor_distance}') 
                delta = neighbor_distance - current_distance
                #print("HUB neighbor:", neighbor, "distance:", neighbor_distance, "delta:", delta)
                if delta < 0 or random.uniform(0,1) < math.exp(-delta / T):
                    current_solution_hub = neighbor
                    current_distance = neighbor_distance
                    if current_distance < best_distance:
                        best_solution_hub = current_solution_hub.copy()
                        best_distance = current_distance
                    #print(f'SA_________________________________________{best_solution_hub} with {best_distance}')
        # SHIP
        for i in range(len(current_solution_ship)):
            for j in range(i+1, len(current_solution_ship)):
                neighbor_ship = current_solution_ship.copy()
                #print(f'Trước khi swap thì mình có solution của ship là {neighbor_ship}')
                neighbor_ship[i], neighbor_ship[j] = neighbor_ship[j], neighbor_ship[i]
                #print(f'Swap {i} và {j} thì mình có solution mới của ship là {neighbor_ship}')
                #check feasibility
                neighbor_ship = check_feasibility_ship(neighbor_ship,ship_type, ship_cap, demand)    
                neighbor_cost = cost_ship(neighbor_ship, FC, ship_type)
                #print(f'Feasible ship rùi nè {neighbor_ship} với cost {neighbor_cost}') 
                delta_ship = neighbor_cost - current_cost
                #print("SHIP neighbor:", neighbor_ship, "cost:", neighbor_cost, "delta:", delta_ship)
                if delta_ship < 0 or random.uniform(0,1) < math.exp(-delta / T):
                    current_solution_ship = neighbor_ship
                    current_cost = neighbor_cost
                    if current_cost < best_cost:
                        best_solution_ship = current_solution_ship.copy()
                        best_cost = current_cost
                    #print(f'SA_________________________________________{best_solution_ship} with {best_cost}')
        T *= cooling_rate
    #print("neighbor hub tốt nhất", best_solution_hub, "với distance", best_distance) 
    #print("neighbor ship tốt nhất", best_solution_ship, "với distance", best_cost) 
    return best_solution_hub, best_distance, best_solution_ship, best_cost

# p = number of origin port
# m = population size
def LNS(pop_hub, pop_ship, removal_ops, weights_removal, repair_ops, weights_repair, num_remove_hub, num_remove_ship, o,d, dist_origin, ship_type, FC,ship_cap, demand,h,dist_hub,dist_dest,dist_cost, transshipment_cost,phase2_obj,initial_temp, cooling_rate, stopping_temp):
    # population
    best_TC = float('inf')
    best_hub = None
    best_ship = None
    for solution_hub, solution_ship in zip(pop_hub, pop_ship):
        # Removal
        removal_op = random.choices(removal_ops, weights = weights_removal)
        removal_op = removal_op[0]
        repair_op = random.choices(repair_ops, weights = weights_repair)
        repair_op = repair_op[0]
        #print(f'Removal được chọn là {removal_op}')
        #print(f'Repair được chọn là {repair_op}')
        removal_result      = removal_op(o, dist_origin, ship_type, FC, solution_hub, solution_ship, num_remove_hub, num_remove_ship)
        new_hub             = removal_result[0]
        hub_removed         = removal_result[1]
        new_ship            = removal_result[2]
        ship_removed        = removal_result[3]
        hub_after_remove    = removal_result[4]
        ship_after_remove   = removal_result[5]
        #print(f'Apply remove {hub_after_remove} with {hub_removed} and {ship_after_remove} with {ship_removed}')
        #print(f'Finish remove {new_hub} and {new_ship}')
        # Repair
        repair_hub          = repair_op(FC,hub_removed, new_hub, o, dist_origin, new_ship, ship_removed,ship_type)[0]
        repair_ship         = repair_op(FC,hub_removed, new_hub, o, dist_origin, new_ship, ship_removed,ship_type)[1]
        #print(f'__________Finish repair {repair_hub} and {repair_ship}')

        # Local search    
        local_search_swap_SA          = local_search(ship_type, ship_cap, demand,h, FC, repair_hub, repair_ship, dist_origin, o, initial_temp, cooling_rate, stopping_temp)
        local_best_solution_hub       = local_search_swap_SA[0]
        local_best_distance           = local_search_swap_SA[1]
        local_best_solution_ship      = local_search_swap_SA[2]
        local_best_cost               = local_search_swap_SA[3]
        total_distance                = distance_calculation(demand,local_best_solution_hub, o,h,d, dist_origin,dist_hub,dist_dest)
        local_best_TC                 = objective(local_best_solution_ship,o, FC, total_distance, dist_cost, transshipment_cost, demand, phase2_obj)
        #print(f'_________Hub Done Local search & SA {local_best_solution_hub} with {local_best_distance}')
        #print(f'_________Ship Done Local search & SA {local_best_solution_ship} with {local_best_cost}')
        if local_best_TC < best_TC:
            best_TC             = local_best_TC
            best_hub            = local_best_solution_hub
            best_ship           = local_best_solution_ship
        print(f'After a population, the best cost is {best_TC}')
    return best_TC, best_hub, best_ship, removal_op, repair_op


def update_weights(s_removal,u_removal,s_repair,u_repair,reward,removal_ops, repair_ops, weights_removal, weights_repair, removal_op, repair_op, improved, rho):
    
    for idx_removal in range(len(removal_ops)):
        if u_removal[idx_removal] > 0:
            weights_removal[idx_removal] = (1 - rho) * weights_removal[idx_removal] + rho * (s_removal[idx_removal] / u_removal[idx_removal])
        else:
            weights_removal[idx_removal] = (1 - rho) * weights_removal[idx_removal]
    
    for idx_repair in range(len(repair_ops)):
        if u_repair[idx_repair] > 0:
            weights_repair[idx_repair] = (1 - rho) * weights_repair[idx_repair] + rho * (s_repair[idx_repair] / u_repair[idx_repair])
        else:
            weights_repair[idx_repair] = (1 - rho) * weights_repair[idx_repair]
            
    # Normalize weights
    total_removal = sum(weights_removal)
    total_repair  = sum(weights_repair)
    weights_removal = [w / total_removal for w in weights_removal]
    weights_repair  = [w / total_repair  for w in weights_repair]
    return weights_removal, weights_repair

def ALNS(DATA_PATH, SHEET_NAME,result_file,cycle_length, p,m,maxIteration, num_remove_hub,num_remove_ship, rho, initial_temp, cooling_rate, stopping_temp):
    # Input data
    h, o, d, dist_origin, dist_hub, dist_dest, demand = readData_port(DATA_PATH, SHEET_NAME)
    ship, ship_type, ship_cap, FC,ship_main, ship_main_type, ship_main_cap, FCM, dist_cost, transshipment_cost = readData_ship(DATA_PATH, SHEET_NAME)
    # initial solution
    initial_solution            = Initial_Solution(result_file, ship_type,p,o,h,d, dist_origin,dist_hub,dist_dest,FC, dist_cost, transshipment_cost, demand)
    initial_hub                 = initial_solution[0]
    initial_ship                = initial_solution[1]
    initial_obj                 = initial_solution[2]
    phase2_obj                  = initial_solution[3]
    # global optimum
    global_best_hub             = initial_hub
    global_best_ship            = initial_ship
    global_best_TC              = initial_obj 
  
    
    removal_ops                 = removal_operators()
    repair_ops                  = repair_operators()
    weights_removal             = [1.0] * len(removal_ops)
    weights_repair              = [1.0] * len(repair_ops)
    s_removal                   = [0.0] * len(removal_ops)
    u_removal                   = [0.0] * len(removal_ops)
    s_repair                    = [0.0] * len(repair_ops)
    u_repair                    = [0.0] * len(repair_ops)
        

    # is iteration < max_iteration?
    for iteration in range(maxIteration):
        print(f'Initial weight of iteration for removal method is {weights_removal}')
        print(f'Initial weight of iteration for repair method is {weights_repair}')
        pop_hub   = get_solution_hub(iteration, initial_hub, m, p, h)
        pop_ship  = get_solution_ship(iteration,initial_ship, m, p, ship_type)
        
        
        best_TC, best_hub, best_ship, removal_op, repair_op = LNS(pop_hub, pop_ship, removal_ops, weights_removal, repair_ops, weights_repair, num_remove_hub, num_remove_ship, o,d, dist_origin, ship_type, FC,ship_cap, demand,h,dist_hub,dist_dest,dist_cost, transshipment_cost,phase2_obj,initial_temp, cooling_rate, stopping_temp)
        
        reward                      = 0
        improved = best_TC < global_best_TC
        if improved:
            reward = 2
            print(f" Improved solution found! Old cost: {global_best_TC}, New cost: {best_TC}")
            global_best_TC  = best_TC
            global_best_hub = best_hub
            global_best_ship = best_ship
        elif best_TC < initial_obj:
            reward = 1
            print(f" Better than initial, but not best so far. Current: {best_TC}")
        else:
            reward = 0
            print(f" No improvement. Best so far: {global_best_TC}, current: {best_TC}")
        
        idx_removal = removal_ops.index(removal_op)
        idx_repair  = repair_ops.index(repair_op)
        
        s_removal[idx_removal] += reward
        u_removal[idx_removal] += 1

        s_repair[idx_repair]   += reward
        u_repair[idx_repair]   += 1
        print(f"[Iteration {iteration}] Reward: {reward}")
        print(f"[Iteration {iteration}] Removal op: {removal_op}, idx: {idx_removal}, s: {s_removal[idx_removal]}, u: {u_removal[idx_removal]}")
        print(f"[Iteration {iteration}] Repair op:  {repair_op}, idx: {idx_repair},  s: {s_repair[idx_repair]}, u: {u_repair[idx_repair]}")
        if (iteration + 1) % cycle_length == 0: 
            print("="*30)
            print(f"[UPDATE] Before update weights (iteration {iteration+1}):")
            print(f"s_removal: {s_removal}")
            print(f"u_removal: {u_removal}")
            print(f"s_repair : {s_repair}")
            print(f"u_repair : {u_repair}")
            print(f"weights_removal (before): {weights_removal}")
            print(f"weights_repair  (before): {weights_repair}")
            weights_removal, weights_repair = update_weights(
                    s_removal,u_removal,s_repair,u_repair,reward,removal_ops, repair_ops, 
                weights_removal, weights_repair, removal_op, repair_op, improved, rho
            )
            print(f"weights_removal (after): {weights_removal}")
            print(f"weights_repair  (after): {weights_repair}")
            s_removal                   = [0.0] * len(removal_ops)
            u_removal                   = [0.0] * len(removal_ops)
            s_repair                    = [0.0] * len(repair_ops)
            u_repair                    = [0.0] * len(repair_ops)
                
        print(f'After iteration {iteration} we have hub {global_best_hub} and ship {global_best_ship} with total cost {global_best_TC}')
        print("-" * 50)
    return global_best_TC, global_best_hub, global_best_ship,o
    
#ALNS(DATA_PATH, SHEET_NAME,result_file, cycle_length, p,m,maxIteration, num_remove_hub,num_remove_ship, rho, initial_temp, cooling_rate, stopping_temp)      
end_time = time.time()
run_time = end_time - start_time
print(f"Running time: {end_time - start_time:.4f} second")


