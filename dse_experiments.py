import uf_arch.uf_arch as uf
import stim
import numpy as np
from tqdm import tqdm
import pandas as pd
import matplotlib.pyplot as plt

from error_models import SuperconductiveEM

SHOTS = 1000

MIN_DISTANCE = 3
MAX_DISTANCE = 31
DISTANCE_RANGE = range(MIN_DISTANCE, MAX_DISTANCE + 1, 2)

MIN_ERROR_RATE = 0.001
MAX_ERROR_RATE = 0.1
ERROR_RATE_STEP = 10
ERROR_RATE_RANGE = np.linspace(MIN_ERROR_RATE, MAX_ERROR_RATE, ERROR_RATE_STEP)

RESULTS_DIR = "results"
RESULTS_PATH = f"{RESULTS_DIR}/experiment_results.csv"

def execExperiment():
    experimentFrame = pd.DataFrame(columns=["repetition", "distance", "base_error_rate", "num_grow_merge_iters", "boundaries_per_iter", "odd_clusters_per_iter", "merges_per_iter"])

    for distance in DISTANCE_RANGE:
        for base_error_rate in ERROR_RATE_RANGE:
            print(f"Distance: {distance}, Base Error Rate: {base_error_rate}")

            errorModel = SuperconductiveEM(base_error_rate)
            stimErrorModel = errorModel.toStim()

            ufDecoder = uf.UnionFindDecoder(distance, distance+1, uf.CodeType.ROTATED, 1, 1)

            rotatedCode = stim.Circuit.generated(
                    "surface_code:rotated_memory_z",
                    rounds=distance,
                    distance=distance,
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

            for k, sample in enumerate(tqdm(samples)):
                sample = list(sample)
                firstRound = sample[:distance+1]
                innerRounds = sample[distance+1:-(distance+1)]
                lastRound = sample[-(distance+1):]

                innerOnlyZ = []

                for i, round in enumerate(innerRounds):
                    coord = detCoords[i+4]
                    if (coord[0] // 2) % 2 == 0 and (coord[1] // 2) % 2 == 0 or (coord[0] // 2) % 2 == 1 and (coord[1] // 2) % 2 == 1:
                        innerOnlyZ.append(round)

                z_sample = firstRound + innerOnlyZ + lastRound
                
                ufDecoder.decode(z_sample)
                stats = ufDecoder.get_stats()

                experimentFrame.loc[len(experimentFrame)] = {
                    "repetition": k,
                    "distance": distance,
                    "base_error_rate": base_error_rate,
                    "num_grow_merge_iters": stats.num_grow_merge_iters,
                    "boundaries_per_iter": stats.boundaries_per_iter,
                    "odd_clusters_per_iter": stats.odd_clusters_per_iter,
                    "merges_per_iter": stats.merges_per_iter,
                }

        # Save the experimentFrame to a CSV file
        experimentFrame.to_csv(RESULTS_PATH, index=False)

    # Final saving
    experimentFrame.to_csv(RESULTS_PATH, index=False)

def plotExperimentResults():
    experimentFrame = pd.read_csv(RESULTS_PATH)

    plt.figure()

    for distance in DISTANCE_RANGE:
        # Aggregate on repetitions
        aggregatedFrame = experimentFrame[experimentFrame["distance"] == distance]
        avgGrowMergeIters = aggregatedFrame.groupby("base_error_rate")["num_grow_merge_iters"].mean()
        #maxGrowMergeIters = aggregatedFrame.groupby("base_error_rate")["num_grow_merge_iters"].max()
        
        plt.plot(avgGrowMergeIters.index, avgGrowMergeIters.values, label=f"d={distance}")

    plt.xlabel("Base Error Rate")
    plt.ylabel("Average number of Grow-Merge Iterations")
    plt.yticks(np.arange(0, 15, 2))
    plt.title(f"Average number of Grow-Merge Iterations vs Base Error Rate ({SHOTS} shots)")
    plt.legend()
    plt.grid()

    plt.figure()

    for distance in DISTANCE_RANGE:
        # Aggregate on repetitions
        aggregatedFrame = experimentFrame[experimentFrame["distance"] == distance]
        maxGrowMergeIters = aggregatedFrame.groupby("base_error_rate")["num_grow_merge_iters"].max()
        
        plt.plot(maxGrowMergeIters.index, maxGrowMergeIters.values, label=f"d={distance}")

    plt.xlabel("Base Error Rate")
    plt.ylabel("Max number of Grow-Merge Iterations")
    plt.yticks(np.arange(0, 30, 2))
    plt.title(f"Max number of Grow-Merge Iterations vs Base Error Rate ({SHOTS} shots)")
    plt.legend()
    plt.grid()

    plt.figure()

    for distance in DISTANCE_RANGE:
        # Aggregate on repetitions
        aggregatedFrame = experimentFrame[experimentFrame["distance"] == distance]
        
        # get all the lists in the column "boundaries_per_iter" grouped by "base_error_rate"
        boundariesPerIter = aggregatedFrame.groupby("base_error_rate")["boundaries_per_iter"].apply(list)
        
        # for each base_error_rate, make all the internal lists the same size by padding with 0s
        for collection in boundariesPerIter:
            collection = [eval(element) for element in collection]
            maxLength = max(len(x) for x in collection)
            collection = [x + [0] * (maxLength - len(x)) for x in collection]
            collection = np.array(collection)
            avgBoundariesPerIter = np.mean(collection, axis=0)
            plt.plot(avgBoundariesPerIter, label=f"d={distance}")
            current_error_rate = boundariesPerIter.index[0]
            break

    plt.xlabel("Iteration")
    plt.ylabel("Average number of boundaries per iteration")
    plt.title(f"Average number of boundaries per iteration vs Base Error Rate at {current_error_rate} error rate ({SHOTS} shots)")
    plt.legend()
    plt.grid()

    plt.figure()

    for distance in DISTANCE_RANGE:
        # Aggregate on repetitions
        aggregatedFrame = experimentFrame[experimentFrame["distance"] == distance]
        
        # get all the lists in the column "boundaries_per_iter" grouped by "base_error_rate"
        boundariesPerIter = aggregatedFrame.groupby("base_error_rate")["odd_clusters_per_iter"].apply(list)
        
        # for each base_error_rate, make all the internal lists the same size by padding with 0s
        for collection in boundariesPerIter:
            collection = [eval(element) for element in collection]
            maxLength = max(len(x) for x in collection)
            collection = [x + [0] * (maxLength - len(x)) for x in collection]
            collection = np.array(collection)
            avgBoundariesPerIter = np.mean(collection, axis=0)
            plt.plot(avgBoundariesPerIter, label=f"d={distance}")
            current_error_rate = boundariesPerIter.index[0]
            break

    plt.xlabel("Iteration")
    plt.ylabel("Average number of odd clusters per iteration")
    plt.title(f"Average number of odd clusters per iteration vs Base Error Rate at {current_error_rate} error rate ({SHOTS} shots)")
    plt.legend()
    plt.grid()

    plt.figure()

    for distance in DISTANCE_RANGE:
        # Aggregate on repetitions
        aggregatedFrame = experimentFrame[experimentFrame["distance"] == distance]
        
        # get all the lists in the column "boundaries_per_iter" grouped by "base_error_rate"
        boundariesPerIter = aggregatedFrame.groupby("base_error_rate")["merges_per_iter"].apply(list)
        
        # for each base_error_rate, make all the internal lists the same size by padding with 0s
        for collection in boundariesPerIter:
            collection = [eval(element) for element in collection]
            maxLength = max(len(x) for x in collection)
            collection = [x + [0] * (maxLength - len(x)) for x in collection]
            collection = np.array(collection)
            avgBoundariesPerIter = np.mean(collection, axis=0)
            plt.plot(avgBoundariesPerIter, label=f"d={distance}")
            current_error_rate = boundariesPerIter.index[0]
            break

    plt.xlabel("Iteration")
    plt.ylabel("Average number of merges per iteration")
    plt.title(f"Average number of merges per iteration vs Base Error Rate at {current_error_rate} error rate ({SHOTS} shots)")
    plt.legend()
    plt.grid()

    plt.show()

if __name__ == "__main__":
    # execExperiment()
    plotExperimentResults()
