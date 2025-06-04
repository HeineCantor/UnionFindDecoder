BASE_COST = 15

INIT_CLUSTER_BASE_COST = 7
INITIALIZER_COST = 100

GROW_BASE_COST = 15
GROWER_COST = 10

FIND_BASE_COST = 5
MERGE_BASE_COST = 70 + 2 * FIND_BASE_COST

PEEL_BASE_COST = 120

N_init = 10
N_grow = 5
N_peel = 1
E_gm = -1

def calculate_costs(N_init, N_grow, N_peel, E_gm):
    init_cost = INIT_CLUSTER_BASE_COST + INITIALIZER_COST * N_init
    grow_cost = GROW_BASE_COST + GROWER_COST * N_grow
    merge_cost = MERGE_BASE_COST
    peel_cost = PEEL_BASE_COST

    cost = init_cost + grow_cost + merge_cost + peel_cost

    return cost

print("N_init:", N_init)
print("N_grow:", N_grow)
print("N_peel:", N_peel)
print("E_gm:", E_gm)

print("\nCost breakdown:")
print("  Initialization cost:", INIT_CLUSTER_BASE_COST + INITIALIZER_COST * N_init)
print("  Growth cost:", GROW_BASE_COST + GROWER_COST * N_grow)
print("  Merge cost:", MERGE_BASE_COST)
print("  Peel cost:", PEEL_BASE_COST)
print("Total cost:", calculate_costs(N_init, N_grow, N_peel, E_gm))

