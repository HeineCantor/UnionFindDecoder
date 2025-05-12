import uf_arch.uf_arch as uf
import stim
import numpy as np
from tqdm import tqdm

from error_models import SuperconductiveEM

DISTANCE = 21
ROUNDS = DISTANCE

SYNDROME_SIZE = (DISTANCE + 1) * (DISTANCE - 1) // 2 * ROUNDS
SHOTS = 1000

def print_stats(stats):
    print("Number of iterations: ", stats.num_grow_merge_iters)
    print("Boundaries per iter: ", stats.boundaries_per_iter)
    print("Merges per iter: ", stats.merges_per_iter)
    print("Odd clusters per iter: ", stats.odd_clusters_per_iter)

base_error_rate = 0.01

errorModel = SuperconductiveEM(base_error_rate)
stimErrorModel = errorModel.toStim()

ufDecoder = uf.UnionFindDecoder(DISTANCE, ROUNDS+1, uf.CodeType.ROTATED, 1, 1)

rotatedCode = stim.Circuit.generated(
        "surface_code:rotated_memory_z",
        rounds=ROUNDS,
        distance=DISTANCE,
        before_round_data_depolarization=stimErrorModel["before_round_data_depolarization"],
        before_measure_flip_probability=stimErrorModel["before_measure_flip_probability"],
        after_clifford_depolarization=stimErrorModel["after_clifford_depolarization"],
        after_reset_flip_probability=stimErrorModel["after_reset_flip_probability"],
    )

sampler = rotatedCode.compile_detector_sampler()
samples, observables = sampler.sample(shots=SHOTS, separate_observables=True)

dem = rotatedCode.detector_error_model(decompose_errors=True)
detCoords = dem.get_detector_coordinates()

statsList = []

for sample in tqdm(samples):
    sample = list(sample)
    firstRound = sample[:DISTANCE+1]
    innerRounds = sample[DISTANCE+1:-(DISTANCE+1)]
    lastRound = sample[-(DISTANCE+1):]

    innerOnlyZ = []

    for i, round in enumerate(innerRounds):
        coord = detCoords[i+4]
        if (coord[0] // 2) % 2 == 0 and (coord[1] // 2) % 2 == 0 or (coord[0] // 2) % 2 == 1 and (coord[1] // 2) % 2 == 1:
            innerOnlyZ.append(round)

    z_sample = firstRound + innerOnlyZ + lastRound
    
    ufDecoder.decode(z_sample)
    statsList.append(ufDecoder.get_stats())

# Aggregate the stats
numberOfIterations = sorted([s.num_grow_merge_iters for s in statsList])

print(f"Median number of iterations: {np.median(numberOfIterations)}")
print(f"Mean number of iterations: {np.mean(numberOfIterations)}")
print(f"Max number of iterations: {np.max(numberOfIterations)}")
print(f"Min number of iterations: {np.min(numberOfIterations)}")