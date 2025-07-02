import matplotlib.pyplot as plt
import pandas as pd

from joblib import Parallel, delayed
from itertools import product

from tqdm import tqdm
from math import ceil

INIT_KERNEL_CP = 110
GROW_KERNEL_CP = 11
PEEL_KERNEL_CP = 21

def Init_CP(I, d):
    CP_Area = I * INIT_KERNEL_CP
    CP_Time = max(d**3 // I, 1) * INIT_KERNEL_CP

    return CP_Area, CP_Time

def Grow_CP(G, E_GM, d):
    CP_Area = G * GROW_KERNEL_CP * E_GM
    CP_Time = max(d**3 // G, 1) * GROW_KERNEL_CP * E_GM

    return CP_Area, CP_Time

def Peel_CP(C, P, d):
    CP_Area = C * P * PEEL_KERNEL_CP
    CP_Time = max(d**3 // P, 1) * PEEL_KERNEL_CP * C

    return CP_Area, CP_Time

def CP_Total(I, G, E_GM, C, P, d):
    init_area, init_time = Init_CP(I, d)
    grow_area, grow_time = Grow_CP(G, E_GM, d)
    peel_area, peel_time = Peel_CP(C, P, d)

    total_area = init_area + grow_area + peel_area
    total_time = init_time + grow_time + peel_time

    return I, G, E_GM, C, P, total_area, total_time


outputFrame = pd.DataFrame(columns=['d', 'I', 'G', 'E_GM', 'C', 'P', 'Workload', 'Area', 'Time'])

for d in tqdm(range(1, 21 + 1, 2)):
    total_area = []
    total_time = [] 
    
    I_range = range(1, ceil(d**3+1 / 10), ceil(d**2/2))
    G_range = range(1, d**2+1, ceil(d/2))
    E_GM_range = range(1, d+1)
    C_range = range(1, d+1)
    # P_range = range(1, d**2+1, d)
    P_range = range(1, 2)
    
    I_G_C_P = product(I_range, G_range, E_GM_range, C_range, P_range)

    results = Parallel(n_jobs=-1)(delayed(CP_Total)(I, G, E_GM, C, P, d) for I, G, E_GM, C, P in I_G_C_P)
    for result in results:
        I, G, E_GM, C, P, area, time = result
        outputFrame = outputFrame._append({
            'd': d,
            'I': I,
            'G': G,
            'E_GM': E_GM,
            'C': C,
            'P': P,
            'Workload': d**3,
            'Area': area,
            'Time': time
        }, ignore_index=True)

    outputFrame.to_csv(f'cp_calculator_output.csv', index=False)

    