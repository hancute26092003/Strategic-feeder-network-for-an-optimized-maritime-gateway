# -*- coding: utf-8 -*-
"""
Created on Mon Jun  9 13:34:56 2025

@author: quynh
"""
import pandas as pd

#DATA_PATH       = r"C:\Users\quynh\opl\Thesis\DATA.xlsx"
#SHEET_NAME      = r"data4_thailand_16"
#p               = 16 # number of origin port


m               = 10 # population size
maxIteration    = 1
num_remove_hub  = 2
num_remove_ship = 1
initial_temp    = 1000
stopping_temp   = 1
cycle_length    = 1

rho             = 0.1 # reaction factor
cooling_rate    = 0.98


#Đọc data
def readData_port(DATA_PATH, SHEET_NAME):
    #Đọc data
    data                = pd.read_excel(DATA_PATH, sheet_name=SHEET_NAME)
    #hub
    hub_p               = pd.DataFrame(data, columns=["hub_port"]) #tạo bảng dữ liệu hub_port
    hub_port            = [int(x) for x in hub_p.dropna()["hub_port"].tolist()] #loại bỏ các dòng có giá trị NaN(trống) và chuyển thành list
    #origin
    origin              = pd.DataFrame(data, columns=["assigned_origin"])
    origin_port         = [int(x) for x in origin.dropna()["assigned_origin"].tolist()]
    #demand
    demand              = pd.DataFrame(data, columns=["demand"])
    demand              = demand.dropna()["demand"].tolist()
    #destination port
    destination         = pd.DataFrame(data, columns=["destination"])
    destination_port    = destination.dropna()["destination"].tolist()
    destination_port    = destination_port[0]
    #bảng data distance origin - hub 1
    dist_origin_hub     = pd.DataFrame(data, columns=["origin", "hub1_origin", "distance"]).dropna()
    dist_origin_hub_dict = {(row['origin'], row['hub1_origin']): row['distance'] for _, row in dist_origin_hub.iterrows()}
    
    #bảng data distance hub1 - hub2
    dist_hub1_hub2       = pd.DataFrame(data, columns=["hub1", "hub2", "distance_hub"]).dropna()
    dist_hub1_hub2_dict  = {(row['hub1'], row['hub2']): row['distance_hub'] for _, row in dist_hub1_hub2.iterrows()}
    #bảng data distance hub2 - destination port
    dist_hub2_dest       = pd.DataFrame(data, columns=["hub2_dest", "destination_port", "distance_dest"]).dropna()
    dist_hub2_dest_dict  =  {(row['hub2_dest'], row['destination_port']): row['distance_dest'] for _, row in dist_hub2_dest.iterrows()}
     #h, o, d, dist_origin, dist_hub, dist_dest = readData()
    #print(h, o, d, dist_origin, dist_hub, dist_dest)       
    return hub_port, origin_port, destination_port, dist_origin_hub_dict, dist_hub1_hub2_dict, dist_hub2_dest_dict, demand

def readData_ship(DATA_PATH, SHEET_NAME):
    #Đọc data
    data                = pd.read_excel(DATA_PATH, sheet_name=SHEET_NAME)
    #ship origin - mainline
    ship_type     = [1,2,3,4]
    ship_cap = pd.DataFrame(data, columns=["ship_cap"])
    ship_cap = ship_cap.dropna()["ship_cap"].tolist()
    ship_cap = pd.Series(ship_cap, index=range(1, len(ship_cap) + 1))
    FC    = pd.DataFrame(data, columns=["fixed_cost"])
    FC    = FC.dropna()["fixed_cost"].tolist()
    ship = dict(zip(ship_type, zip(ship_cap, FC)))
    
    #ship mainline
    ship_main_type = [1,2]
    ship_main_cap = pd.DataFrame(data, columns=["ship_main"])
    ship_main_cap = ship_main_cap.dropna()["ship_main"].tolist()
    FCM       = pd.DataFrame(data, columns=["fixed_cost_main"])
    FCM       = FCM.dropna()["fixed_cost_main"].tolist()
    ship_main = dict(zip(ship_main_type, zip(ship_main_cap, FCM)))

    #cost
    dist_cost = pd.DataFrame(data, columns=["transport_cost"])
    dist_cost = dist_cost.dropna()["transport_cost"].tolist()
    dist_cost = dist_cost[0]
    transshipment_cost = pd.DataFrame(data, columns=["transshipment_cost"])
    transshipment_cost = transshipment_cost.dropna()["transshipment_cost"].tolist()
    transshipment_cost = transshipment_cost[0]
    return ship, ship_type, ship_cap, FC,ship_main, ship_main_type, ship_main_cap, FCM, dist_cost, transshipment_cost

