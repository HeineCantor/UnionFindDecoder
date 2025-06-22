import matplotlib.pyplot as plt

INIT_KERNEL_CP = 110
GROW_KERNEL_CP = 11

# CP_Total(I, G, E_GM, C, P, d) = Init_CP(I, d) + Grow_CP(G, E_GM, d) + Peel_CP(C, P, d)

def Init_CP(I, d):
    CP_Area = I * INIT_KERNEL_CP
    CP_Time = max(d**3 // I, 1) * INIT_KERNEL_CP

    return CP_Area, CP_Time

def Grow_CP(G, E_GM, d):
    CP_Area = G * GROW_KERNEL_CP * E_GM
    CP_Time = max(d**3 // G, 1) * GROW_KERNEL_CP * E_GM

    return CP_Area, CP_Time

def Peel_CP(C, P, d):
    CP_Area = C * P * INIT_KERNEL_CP
    CP_Time = max(d**3 // P, 1) * INIT_KERNEL_CP * C

    return CP_Area, CP_Time

def CP_Total(I, G, E_GM, C, P, d):
    init_area, init_time = Init_CP(I, d)
    grow_area, grow_time = Grow_CP(G, E_GM, d)
    peel_area, peel_time = Peel_CP(C, P, d)

    total_area = init_area + grow_area + peel_area
    total_time = init_time + grow_time + peel_time

    return total_area, total_time

if __name__ == "__main__":
    I = 150
    G = 50
    E_GM = 15
    C = 30
    P = 400
    d = 21

    total_area, total_time = CP_Total(I, G, E_GM, C, P, d)
    print(f"Total CP Area: {total_area}")
    print(f"Total CP Time: {total_time}")