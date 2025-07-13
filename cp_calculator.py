import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

from joblib import Parallel, delayed
from itertools import product

import numpy as np

from tqdm import tqdm
from math import ceil

INIT_KERNEL_CP = 110
GROW_KERNEL_CP = 11
MERGE_KERNEL_CP = 70
PEEL_KERNEL_CP = 21

def Init_CP(I, d):
    CP_Area = I * INIT_KERNEL_CP
    CP_Time = max(d**3 // I, 1) * INIT_KERNEL_CP

    return CP_Area, CP_Time

def Grow_CP(G, E_GM, d):
    CP_Area = (G * GROW_KERNEL_CP + MERGE_KERNEL_CP) * E_GM
    CP_Time = (max(d**3 // G, 1) * GROW_KERNEL_CP + MERGE_KERNEL_CP) * E_GM

    return CP_Area, CP_Time

def Peel_CP(C, P, E_P, d):
    CP_Area = C * P * PEEL_KERNEL_CP * E_P
    CP_Time = max((max(d**3 // P, 1) // C), 1) * PEEL_KERNEL_CP * E_P

    return CP_Area, CP_Time

def CP_Total(I, G, E_GM, C, P, E_P, d):
    init_area, init_time = Init_CP(I, d)
    grow_area, grow_time = Grow_CP(G, E_GM, d)
    peel_area, peel_time = Peel_CP(C, P, E_P, d)

    total_area = init_area + grow_area + peel_area
    total_time = init_time + grow_time + peel_time

    return I, G, E_GM, C, P, E_P, total_area, total_time

def CP_Total_dict(factorsDict, d):
    I = factorsDict['I']
    G = factorsDict['G']
    E_GM = factorsDict['E_GM']
    C = factorsDict['C']
    P = factorsDict['P']
    E_P = factorsDict['E_P']

    return CP_Total(I, G, E_GM, C, P, E_P, d)

def get_range_from_factor(factor, d, steps=None):
    if steps is None:
        if factor == 'I':
            return range(1, ceil((d**3 + 1) / 10))
        elif factor == 'G':
            return range(1, d**2 + 1)
        elif factor == 'E_GM':
            return range(1, d + 1)
        elif factor == 'C':
            return range(1, d + 1)
        elif factor == 'P':
            return range(1, d**2 + 1)
        elif factor == 'E_P':
            return range(1, d + 1)
        else:
            raise ValueError(f"Unknown factor: {factor}")
    else:
        if factor == 'I':
            return np.linspace(1, ceil((d**3 + 1) / 10), steps, dtype=int).tolist()
        elif factor == 'G':
            return np.linspace(1, d**2 + 1, steps, dtype=int).tolist()
        elif factor == 'E_GM':
            return np.linspace(1, d + 1, steps, dtype=int).tolist()
        elif factor == 'C':
            return np.linspace(1, d + 1, steps, dtype=int).tolist()
        elif factor == 'P':
            return np.linspace(1, d**2 + 1, steps, dtype=int).tolist()
        elif factor == 'E_P':
            return np.linspace(1, d + 1, steps, dtype=int).tolist()
        else:
            raise ValueError(f"Unknown factor: {factor}")

def full_factorial_exp():
    outputFrame = pd.DataFrame(columns=['d', 'I', 'G', 'E_GM', 'C', 'P', 'E_P', 'Workload', 'Area', 'Time'])

    for d in tqdm(range(1, 21 + 1, 2)):
        total_area = []
        total_time = [] 
        
        I_range = range(1, ceil(d**3+1 / 10), ceil(d**2/2))
        G_range = range(1, d**2+1, ceil(d/2))
        E_GM_range = range(1, d+1)
        E_P_range  = range(1, d+1)
        C_range = range(1, d+1)
        P_range = range(1, d**2+1, d)
        
        I_G_C_P = product(I_range, G_range, E_GM_range, C_range, P_range, E_P_range)

        results = Parallel(n_jobs=-1)(delayed(CP_Total)(I, G, E_GM, C, P, E_P, d) for I, G, E_GM, C, P, E_P in I_G_C_P)
        for result in results:
            I, G, E_GM, C, P, E_P, area, time = result
            outputFrame = outputFrame._append({
                'd': d,
                'I': I,
                'G': G,
                'E_GM': E_GM,
                'C': C,
                'P': P,
                'E_P': E_P,
                'Workload': d**3,
                'Area': area,
                'Time': time
            }, ignore_index=True)

        outputFrame.to_csv(f'results/cp_calculator_output.csv', index=False)

def single_factor_plot(distance, factor, steps=None):
    factor_range = get_range_from_factor(factor, distance, steps)

    factors_dict = {
        'I': 1,
        'G': 1,
        'E_GM': 1,
        'C': 1,
        'P': 1,
        'E_P': 1
    }

    factors_dict[factor] = factor_range
    cp_area, cp_time = [], []

    for value in factor_range:
        factors_dict[factor] = value
        area, time = CP_Total_dict(factors_dict, distance)[-2:]
        cp_area.append(area)
        cp_time.append(time)

    font = {'family' : 'normal',
            'size'   : 12}

    matplotlib.rc('font', **font)

    plt.figure(figsize=(12, 6))

    splot = plt.subplot(1, 2, 1)
    plt.plot(factor_range, cp_area, marker='o', color='blue')
    plt.title(f'CP Area vs {factor} (d={distance})')
    plt.xlabel(factor)
    plt.ylabel('Area')
    plt.grid()
    splot.figure.set_dpi(180)

    splot = plt.subplot(1, 2, 2)
    plt.plot(factor_range, cp_time, marker='o', color='orange')
    plt.title(f'CP Time vs {factor} (d={distance})')
    plt.xlabel(factor)
    plt.ylabel('Time')
    plt.grid()
    splot.figure.set_dpi(180)

if __name__ == "__main__":
    distance = 21

    for factor in ['I', 'G', 'E_GM', 'C', 'P', 'E_P']:
        single_factor_plot(distance, factor, 30)

    plt.show()